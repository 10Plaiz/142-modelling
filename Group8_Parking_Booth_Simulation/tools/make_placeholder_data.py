"""
Generates PLACEHOLDER input files in the exact format the group's real
observations will use. Replace every file in data/ with real observations
before reporting results. Run once; not part of the model.
"""
import numpy as np, pandas as pd

rng = np.random.default_rng(20260914)

# ---- 1. Gate entry log: one high-traffic day, 07:00-19:00 --------------
# Vehicles per 15-minute interval used to synthesise the day (placeholder).
profile = [22, 30, 36, 34, 30, 26, 22, 18,          # 07:00-09:00 peak
           12, 11, 10, 9, 9, 8, 8, 8,               # 09:00-11:00
           9, 10, 12, 13, 12, 10, 9, 8,             # 11:00-13:00 lunch bump
           8, 7, 7, 6, 6, 6, 6, 5,                  # 13:00-15:00
           5, 5, 5, 4, 4, 4, 4, 4,                  # 15:00-17:00
           4, 3, 3, 3, 2, 2, 2, 1]                  # 17:00-19:00
rows = []
for j, expected in enumerate(profile):
    n = rng.poisson(expected)
    t = np.sort(rng.uniform(j * 15, (j + 1) * 15, n))   # Poisson process within interval
    rows += list(t)
rows = np.sort(np.array(rows))
clock = pd.to_datetime("2026-09-21 07:00:00") + pd.to_timedelta(rows, unit="min")
pd.DataFrame({"vehicle_no": np.arange(1, len(rows) + 1),
              "entry_timestamp": clock.strftime("%H:%M:%S")}
             ).to_csv("data/gate_entry_log.csv", index=False)

# ---- 2. Stopwatch service times (seconds): 30 peak + 30 off-peak -------
peak = np.round(rng.lognormal(np.log(24), 0.35, 30), 1)
off = np.round(rng.lognormal(np.log(28), 0.40, 30), 1)
pd.DataFrame({"obs_no": np.arange(1, 61),
              "window": ["peak"] * 30 + ["offpeak"] * 30,
              "service_sec": np.concatenate([peak, off])}
             ).to_csv("data/service_times.csv", index=False)

# ---- 3. Site measurement for approach capacity K -----------------------
pd.DataFrame([{"approach_length_m": 30.0, "avg_vehicle_length_m": 4.6,
               "avg_gap_m": 1.4, "measured_on": "PLACEHOLDER"}]
             ).to_csv("data/site_measurements.csv", index=False)

# ---- 4. Templates (left EMPTY on purpose: to be filled on site) ---------
starts = pd.date_range("07:00", "08:45", freq="15min").strftime("%H:%M")
pd.DataFrame({"interval_start": starts, "arrivals_tallied": ""}
             ).to_csv("data/peak_arrival_tally.csv", index=False)
snaps = pd.date_range("07:05", "09:00", freq="5min").strftime("%H:%M")
pd.DataFrame({"snapshot_time": snaps, "queue_length_observed": ""}
             ).to_csv("data/validation_observations.csv", index=False)
print(len(rows), "arrivals;", peak.mean(), off.mean())
