"""
build_arrival_proxy.py
======================
Builds data/proxy_sfpark_entries.csv: real per-vehicle garage entry times from
the public SFpark evaluation data (San Francisco Municipal Transportation
Agency, garage payment transactions, 2011-2013).

Why a proxy: the group has no access to the Mapua gate or its records. The
proxy is used ONLY to test the form of the arrival process (assumption A1:
Poisson arrivals with a rate that is constant within each 15-minute
interval). It never sets campus volumes, because a downtown pay garage does
not have a campus class-start peak.

The source file is about 812 MB. It is streamed in chunks; only weekday
entries between 07:00 and 19:00 at one garage are kept.

Usage (from Group8_Parking_Booth_Simulation/):
    python tools/build_arrival_proxy.py --survey          # entries per garage, to choose one
    python tools/build_arrival_proxy.py                   # default garage
    python tools/build_arrival_proxy.py --facility "Civic Center Garage"
    python tools/build_arrival_proxy.py --source path/to/downloaded.csv   # faster: download once
"""
import argparse
import sys

import pandas as pd

SOURCE_URL = ("https://safitwebapps.blob.core.windows.net/$web/streets/sfpark/"
              "SFpark_GarageData_PaymentTransactions_20112013.csv")
SOURCE_NOTE = ("SFpark evaluation data, SFMTA: garage payment transactions 2011-2013 "
               "(https://www.sfmta.com/getting-around/drive-park/demand-responsive-pricing/sfpark-evaluation)")
OUT = "data/proxy_sfpark_entries.csv"
DEFAULT_FACILITY = "Civic Center Garage"


def weekday_window(chunk: pd.DataFrame) -> pd.DataFrame:
    t = pd.to_datetime(chunk["entry_datetime"], format="%d-%b-%Y %H:%M:%S", errors="coerce")
    keep = t.notna() & (t.dt.dayofweek < 5) & (t.dt.hour >= 7) & (t.dt.hour < 19)
    return pd.DataFrame({"facility_name": chunk.loc[keep, "facility_name"], "entry_datetime": t[keep]})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facility", default=DEFAULT_FACILITY)
    ap.add_argument("--survey", action="store_true", help="only count weekday 07:00-10:00 entries per garage")
    ap.add_argument("--source", default=SOURCE_URL,
                    help="path to an already-downloaded copy of the CSV (default: stream from the URL)")
    args = ap.parse_args()

    reader = pd.read_csv(args.source, usecols=["facility_name", "entry_datetime"], chunksize=500_000,
                         dtype=str)
    parts, survey, rows = [], {}, 0
    for i, chunk in enumerate(reader):
        rows += len(chunk)
        w = weekday_window(chunk)
        if args.survey:
            morning = w[w["entry_datetime"].dt.hour < 10]
            for k, v in morning["facility_name"].value_counts().items():
                survey[k] = survey.get(k, 0) + v
        else:
            parts.append(w[w["facility_name"] == args.facility])
        print(f"  chunk {i + 1}: {rows:,} rows read", file=sys.stderr, flush=True)

    if args.survey:
        print(pd.Series(survey).sort_values(ascending=False).to_string())
        return

    out = pd.concat(parts).sort_values("entry_datetime")
    if out.empty:
        sys.exit(f"No rows for facility {args.facility!r}; run --survey to list names.")
    out["entry_datetime"] = out["entry_datetime"].dt.strftime("%Y-%m-%d %H:%M")
    with open(OUT, "w", encoding="utf8", newline="") as fh:
        fh.write(f"# Source: {SOURCE_NOTE}\n")
        fh.write(f"# Filter: facility = {args.facility}; weekdays; entries 07:00-18:59; minute resolution\n")
        out.to_csv(fh, index=False)
    days = out["entry_datetime"].str[:10].nunique()
    print(f"Wrote {OUT}: {len(out):,} entries over {days} weekdays at {args.facility}")


if __name__ == "__main__":
    main()
