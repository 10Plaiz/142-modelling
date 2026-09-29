"""
parking_sim.py
==============
Discrete-event simulation of the single-booth vehicle entry queue at the
Mapua University Makati campus parking lot.

CSS142P Modelling and Simulation - Group 8
(Ariola, Bauza, Caliliw, Jimenez)

Time unit : minutes after 07:00  (t = 0 is 07:00, t = 120 is 09:00,
            t = 720 is 19:00).
World view: process interaction (SimPy 4.1).

Model classification
    Dynamic       - waiting depends on the order and timing of arrivals.
    Stochastic    - interarrival and processing times are random.
    Discrete      - queue length and booth status change only at events
                    (arrival, processing start, processing completion,
                    second-booth closing at 09:00 or 10:00).
    Terminating   - one operating day with a natural start (07:00) and end
                    (19:00 arrivals stop, queue is cleared), so no warm-up.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np
import pandas as pd
import simpy
from scipy import stats
from scipy.optimize import brentq

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
INTERVAL = 15.0          # minutes per arrival-rate interval
N_INTERVALS = 48         # 07:00-19:00
DAY_LENGTH = 720.0       # minutes, 07:00-19:00
PEAK_END = 120.0         # 09:00
EXTENDED_END = 180.0     # 10:00
OPEN_CLOCK = 7 * 60      # 07:00 in minutes after midnight


def clock_to_min(hhmm: str) -> float:
    """'07:42' or '07:42:10' -> minutes after 07:00."""
    parts = [int(p) for p in str(hhmm).split(":")]
    h, m = parts[0], parts[1]
    s = parts[2] if len(parts) > 2 else 0
    return h * 60 + m + s / 60 - OPEN_CLOCK


def min_to_clock(t: float) -> str:
    total = OPEN_CLOCK + t
    return f"{int(total // 60):02d}:{int(round(total % 60)):02d}"


# --------------------------------------------------------------------------
# Scenario (configuration) definitions
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    name: str
    base_booths: int = 1            # booths open all day
    extra_booths: int = 0           # booths open only until extra_close
    extra_close: float | None = PEAK_END   # None = extra booths never close


ONE_BOOTH = Config("1 booth all day", base_booths=1, extra_booths=0)
TWO_BOOTH_PEAK = Config("2 booths 07:00-09:00", base_booths=1, extra_booths=1,
                        extra_close=PEAK_END)
TWO_BOOTH_EXTENDED = Config("2 booths 07:00-10:00", base_booths=1, extra_booths=1,
                            extra_close=EXTENDED_END)
CONFIGS = [ONE_BOOTH, TWO_BOOTH_PEAK, TWO_BOOTH_EXTENDED]

# Paired comparisons (A - B) reported for the decision: does a second booth
# help at all, and does keeping it open one more hour add anything?
COMPARISONS = [(ONE_BOOTH, TWO_BOOTH_PEAK), (ONE_BOOTH, TWO_BOOTH_EXTENDED),
               (TWO_BOOTH_PEAK, TWO_BOOTH_EXTENDED)]


# --------------------------------------------------------------------------
# Input modelling: arrivals
# --------------------------------------------------------------------------
def load_arrival_counts(log_path: str, tally_path: str | None = None) -> pd.DataFrame:
    """Count arrivals per 15-minute interval from the gate log.

    If a peak-hour tally file exists and contains numbers, those counts
    replace the gate-log counts for the same intervals (see README: the gate
    log records booth passage, which under-counts demand when a queue exists).
    """
    log = pd.read_csv(log_path)
    t = log["entry_timestamp"].map(clock_to_min).to_numpy()
    t = t[(t >= 0) & (t < DAY_LENGTH)]
    counts, _ = np.histogram(t, bins=np.arange(0, DAY_LENGTH + INTERVAL, INTERVAL))
    df = pd.DataFrame({
        "interval_start": [min_to_clock(j * INTERVAL) for j in range(N_INTERVALS)],
        "t_start_min": np.arange(N_INTERVALS) * INTERVAL,
        "count": counts,
        "source": "gate log",
    })
    if tally_path is not None:
        try:
            tally = pd.read_csv(tally_path)
            tally = tally.dropna(subset=["arrivals_tallied"])
            for _, row in tally.iterrows():
                j = int(clock_to_min(row["interval_start"]) // INTERVAL)
                df.loc[j, "count"] = int(row["arrivals_tallied"])
                df.loc[j, "source"] = "queue-tail tally"
        except FileNotFoundError:
            pass
    df["rate_per_min"] = df["count"] / INTERVAL
    return df


def generate_arrivals(rates: np.ndarray, rng: np.random.Generator,
                      interval: float = INTERVAL) -> np.ndarray:
    """Non-homogeneous Poisson process with a piecewise-constant rate.

    Within each interval, gaps are exponential with that interval's rate.
    When a gap overshoots the interval end, the process restarts at the
    boundary with the next rate. This is exact because the exponential
    distribution is memoryless.
    """
    times = []
    for j, lam in enumerate(rates):
        if lam <= 0:
            continue
        t, end = j * interval, (j + 1) * interval
        while True:
            t += rng.exponential(1.0 / lam)       # X = -(1/lam) ln(1-U)
            if t >= end:
                break
            times.append(t)
    return np.asarray(times)


# --------------------------------------------------------------------------
# Input modelling: processing (service) times
# --------------------------------------------------------------------------
CANDIDATES = ["exponential", "lognormal", "triangular"]
N_PARAMS = {"exponential": 1, "lognormal": 2, "triangular": 3}


def fit_distribution(x: np.ndarray, family: str):
    """Maximum-likelihood fit; returns a frozen scipy distribution."""
    x = np.asarray(x, dtype=float)
    if family == "exponential":
        loc, scale = stats.expon.fit(x, floc=0)
        return stats.expon(loc=0, scale=scale)
    if family == "lognormal":
        s, loc, scale = stats.lognorm.fit(x, floc=0)
        return stats.lognorm(s, loc=0, scale=scale)
    if family == "triangular":
        c, loc, scale = stats.triang.fit(x)
        d = stats.triang(c, loc=loc, scale=scale)
        if not np.all(np.isfinite(d.logpdf(x))):
            # fallback: bounds just outside the data, mode from the mean
            rng_ = x.max() - x.min()
            a, b = x.min() - 0.02 * rng_, x.max() + 0.02 * rng_
            mode = float(np.clip(3 * x.mean() - a - b, a, b))
            d = stats.triang((mode - a) / (b - a), loc=a, scale=b - a)
        return d
    raise ValueError(family)


def goodness_of_fit(x: np.ndarray, dist, family: str, n_bins: int | None = None) -> dict:
    """Chi-square (equiprobable bins), Kolmogorov-Smirnov, log-likelihood, AIC."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    k = n_bins or max(4, min(10, n // 5))           # expected >= 5 per bin
    edges = dist.ppf(np.linspace(0, 1, k + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    observed, _ = np.histogram(x, bins=edges)
    expected = np.full(k, n / k)
    chi2 = float(((observed - expected) ** 2 / expected).sum())
    p = N_PARAMS[family]
    dof = k - 1 - p
    chi2_p = float(stats.chi2.sf(chi2, dof)) if dof > 0 else float("nan")
    ks = stats.kstest(x, dist.cdf)
    ll = float(np.sum(dist.logpdf(x)))
    return {"family": family, "n": n, "bins": k, "chi2": chi2, "dof": dof,
            "chi2_p": chi2_p, "chi2_crit_5pct": float(stats.chi2.ppf(0.95, dof)) if dof > 0 else float("nan"),
            "ks_D": float(ks.statistic), "ks_p": float(ks.pvalue),
            "loglik": ll, "aic": 2 * p - 2 * ll,
            "fit_mean": float(dist.mean()), "fit_sd": float(dist.std()),
            "sample_mean": float(x.mean()), "sample_sd": float(x.std(ddof=1))}


def select_distribution(x: np.ndarray) -> tuple[str, pd.DataFrame]:
    """Among candidates not rejected by chi-square at 5%, pick the lowest AIC."""
    rows = [goodness_of_fit(x, fit_distribution(x, f), f) for f in CANDIDATES]
    table = pd.DataFrame(rows)
    ok = table[table["chi2_p"] >= 0.05]
    pool = ok if len(ok) else table
    best = pool.sort_values("aic").iloc[0]["family"]
    table["selected"] = table["family"] == best
    table["not_rejected_5pct"] = table["chi2_p"] >= 0.05
    return best, table


@dataclass
class ServiceModel:
    """Processing-time model. Times are in minutes.

    Each vehicle's time comes from the inverse CDF of the distribution for
    the window in which it arrives: X = F^-1(U). Driving every vehicle with
    its own U keeps common random numbers intact across configurations and
    even across alternative distribution families.
    """
    dists: dict                      # {"peak": frozen, "offpeak": frozen}
    scale: float = 1.0

    def times(self, u: np.ndarray, arrival_times: np.ndarray) -> np.ndarray:
        out = np.empty_like(u)
        peak = arrival_times < PEAK_END
        out[peak] = self.dists["peak"].ppf(u[peak])
        out[~peak] = self.dists["offpeak"].ppf(u[~peak])
        return np.maximum(out, 1e-6) * self.scale

    def with_scale(self, s: float) -> "ServiceModel":
        return ServiceModel(self.dists, self.scale * s)


# --------------------------------------------------------------------------
# The discrete-event model
# --------------------------------------------------------------------------
@dataclass
class Booth:
    booth_id: int
    extra: bool
    is_open: bool = True
    busy_time: float = 0.0
    n_served: int = 0
    last_finish: float = 0.0


@dataclass
class DayResult:
    arrival: np.ndarray
    start: np.ndarray
    finish: np.ndarray
    booth: np.ndarray
    q_before: np.ndarray             # vehicles already waiting when each arrived
    trace_t: np.ndarray              # queue-length step function
    trace_q: np.ndarray
    booths: list
    config: Config
    snapshot_close: dict = field(default_factory=dict)   # state at 19:00


def simulate_day(arrivals: np.ndarray, services: np.ndarray, config: Config,
                 day_length: float = DAY_LENGTH) -> DayResult:
    """Run one operating day. Arrivals stop at day_length (they are generated
    only before it); vehicles already queued are processed before the run ends.
    """
    env = simpy.Environment()
    n = len(arrivals)
    booths = [Booth(i + 1, extra=(i >= config.base_booths))
              for i in range(config.base_booths + config.extra_booths)]
    store = simpy.FilterStore(env, capacity=len(booths))
    store.items.extend(booths)

    start = np.full(n, np.nan)
    finish = np.full(n, np.nan)
    booth_of = np.zeros(n, dtype=int)
    q_before = np.zeros(n, dtype=int)
    state = {"q": 0, "arrived": 0, "finished": 0, "in_service": 0}
    trace_t, trace_q = [0.0], [0]

    def log_q():
        trace_t.append(env.now)
        trace_q.append(state["q"])

    def vehicle(i, s):
        # event: ARRIVAL
        state["arrived"] += 1
        q_before[i] = state["q"]
        state["q"] += 1
        log_q()
        booth = yield store.get(lambda b: b.is_open)     # wait for an open booth
        # event: PROCESSING START
        start[i] = env.now
        state["q"] -= 1
        state["in_service"] += 1
        log_q()
        booth_of[i] = booth.booth_id
        yield env.timeout(s)
        # event: PROCESSING COMPLETION
        finish[i] = env.now
        booth.busy_time += s
        booth.n_served += 1
        booth.last_finish = env.now
        state["in_service"] -= 1
        state["finished"] += 1
        yield store.put(booth)                          # release the booth

    def source():
        for i in range(n):
            yield env.timeout(arrivals[i] - env.now)
            env.process(vehicle(i, services[i]))

    def closer():
        # event: SECOND-BOOTH CLOSING. A booth serving a vehicle finishes it,
        # then is never offered to another vehicle (non-preemptive close).
        yield env.timeout(config.extra_close)
        for b in booths:
            if b.extra:
                b.is_open = False

    snap = {}

    def snapshot():
        yield env.timeout(day_length)
        snap.update(time=env.now, arrived=state["arrived"], finished=state["finished"],
                    waiting=state["q"], in_service=state["in_service"])

    env.process(source())
    env.process(snapshot())
    if config.extra_booths and config.extra_close is not None:
        env.process(closer())
    env.run()

    return DayResult(np.asarray(arrivals), start, finish, booth_of, q_before,
                     np.asarray(trace_t), np.asarray(trace_q), booths, config, snap)


# --------------------------------------------------------------------------
# Performance measures (Part 4 of the proposal + supplementary)
# --------------------------------------------------------------------------
def _segments(res: DayResult):
    """Queue-length step function as (t0, t1, q) segments."""
    t = res.trace_t
    end = max(t[-1], DAY_LENGTH)
    t1 = np.append(t[1:], end)
    return t, t1, res.trace_q


def queue_time_above(res: DayResult, K: int, window=None) -> float:
    """Total time the waiting queue holds at least K vehicles
    (optionally restricted to a time window (lo, hi))."""
    t0, t1, q = _segments(res)
    if window is not None:
        t0, t1 = np.clip(t0, *window), np.clip(t1, *window)
    return float(np.sum((t1 - t0)[q >= K]))


def queue_at_times(res: DayResult, times) -> np.ndarray:
    """Queue length just after each requested time."""
    idx = np.searchsorted(res.trace_t, np.asarray(times), side="right") - 1
    return res.trace_q[idx]


def mean_queue_by_interval(res: DayResult, edges=None) -> np.ndarray:
    """Time-average queue length in each 15-minute interval."""
    if edges is None:
        edges = np.arange(0, DAY_LENGTH + INTERVAL, INTERVAL)
    t0, t1, q = _segments(res)
    lo = np.maximum(t0[:, None], edges[None, :-1])
    hi = np.minimum(t1[:, None], edges[None, 1:])
    overlap = np.clip(hi - lo, 0, None)
    return (overlap * q[:, None]).sum(axis=0) / np.diff(edges)


def day_metrics(res: DayResult, K: int) -> dict:
    wait = res.start - res.arrival
    n = len(wait)
    t_end = float(np.nanmax(res.finish)) if n else DAY_LENGTH
    t0, t1, q = _segments(res)
    area = float(np.sum((t1 - t0) * q))

    # --- utilization over staffed booth-time (proposal definition) ---
    staffed = 0.0
    for b in res.booths:
        if b.extra and res.config.extra_close is not None:
            staffed += max(res.config.extra_close, b.last_finish)
        else:
            staffed += max(DAY_LENGTH, t_end)
    busy = sum(b.busy_time for b in res.booths)

    # --- supplementary: utilization inside the 07:00-09:00 window ---
    svc_lo = np.maximum(res.start, 0)
    svc_hi = np.minimum(res.finish, PEAK_END)
    busy_peak = float(np.sum(np.clip(svc_hi - svc_lo, 0, None)))
    booths_in_peak = res.config.base_booths + res.config.extra_booths
    peak_mask = res.arrival < PEAK_END

    return {
        # proposal measures
        "avg_wait_min": float(wait.mean()) if n else 0.0,
        "max_queue_veh": int(q.max()),
        "utilization": busy / staffed,
        "spillover_min": queue_time_above(res, K),
        # supplementary measures
        "spillover_peak_min": queue_time_above(res, K, (0.0, PEAK_END)),
        "n_vehicles": n,
        "p90_wait_min": float(np.percentile(wait, 90)) if n else 0.0,
        "max_wait_min": float(wait.max()) if n else 0.0,
        "avg_wait_peak_arrivals_min": float(wait[peak_mask].mean()) if peak_mask.any() else 0.0,
        "peak_utilization": busy_peak / (booths_in_peak * PEAK_END),
        "vehicles_queued_on_road": int(np.sum(res.q_before >= K)),
        "any_spillover": int(queue_time_above(res, K) > 0),
        "time_avg_queue_Lq": area / t_end,
        "last_departure_clock": min_to_clock(t_end),
        # kept for the Little's-law identity check
        "_queue_area": area,
        "_sum_wait": float(wait.sum()),
    }


# --------------------------------------------------------------------------
# Experiment driver with common random numbers
# --------------------------------------------------------------------------
def replication_inputs(seed: int, rates: np.ndarray, service_model: ServiceModel,
                       arrival_scale: float = 1.0):
    """Two independent streams per replication, both derived from one seed.
    Every configuration in the replication receives the SAME arrivals and the
    SAME per-vehicle processing times (common random numbers)."""
    arr_ss, svc_ss = np.random.SeedSequence(seed).spawn(2)
    arrivals = generate_arrivals(np.asarray(rates) * arrival_scale,
                                 np.random.default_rng(arr_ss))
    u = np.random.default_rng(svc_ss).random(len(arrivals))
    return arrivals, service_model.times(u, arrivals)


def run_experiment(seeds, rates, service_model, K, configs=CONFIGS,
                   arrival_scale=1.0, keep_days=False, extra_K=()):
    rows, days = [], {}
    for seed in seeds:
        arrivals, services = replication_inputs(seed, rates, service_model, arrival_scale)
        for cfg in configs:
            res = simulate_day(arrivals, services, cfg)
            m = day_metrics(res, K)
            for k2 in extra_K:
                m[f"spillover_min_K{k2}"] = queue_time_above(res, k2)
            m.update(seed=seed, config=cfg.name)
            rows.append(m)
            if keep_days:
                days[(seed, cfg.name)] = res
    df = pd.DataFrame(rows)
    return (df, days) if keep_days else df


# --------------------------------------------------------------------------
# Output analysis helpers (Week 7)
# --------------------------------------------------------------------------
def ci_mean(x, conf=0.95) -> dict:
    x = np.asarray(x, dtype=float)
    n = len(x)
    mean = x.mean()
    sd = x.std(ddof=1) if n > 1 else 0.0
    se = sd / math.sqrt(n)
    t = stats.t.ppf(0.5 + conf / 2, n - 1)
    hw = t * se
    return {"n": n, "mean": mean, "sd": sd, "se": se, "t": t,
            "half_width": hw, "ci_low": mean - hw, "ci_high": mean + hw}


def replications_needed(n_now: int, hw_now: float, hw_target: float) -> int:
    """Week 7 rule: n x (half-width now / half-width wanted)^2, rounded up."""
    if hw_target <= 0 or hw_now == 0:
        return n_now
    return int(math.ceil(n_now * (hw_now / hw_target) ** 2))


def wilson_interval(k: int, n: int, conf=0.95):
    z = stats.norm.ppf(0.5 + conf / 2)
    p = k / n
    denom = 1 + z ** 2 / n
    centre = (p + z ** 2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / denom
    return p, centre - half, centre + half


# --------------------------------------------------------------------------
# Queueing-theory benchmarks for verification
# --------------------------------------------------------------------------
def mm1_wq(lam, mu):
    rho = lam / mu
    return rho / (mu - lam)


def mmc_wq(lam, mu, c):
    """Erlang-C mean delay in queue for M/M/c."""
    a = lam / mu
    rho = a / c
    s = sum(a ** k / math.factorial(k) for k in range(c))
    top = a ** c / (math.factorial(c) * (1 - rho))
    pw = top / (s + top)
    return pw / (c * mu - lam)


# --------------------------------------------------------------------------
# Continuous cross-check: fluid-flow approximation (FFA)
#
#   dx/dt = lambda(t) - c(t) * mu(t) * rho(x)
#
# x is the expected number of vehicles in the system (waiting + at a booth),
# treated as a continuous level. rho(x) is the booth utilization that a
# steady-state queue would need to hold x vehicles on average, found by
# inverting L(rho) = c*rho + Lq(rho). Lq uses Erlang C scaled by
# (1 + SCV_service)/2 (Allen-Cunneen), which is exact Pollaczek-Khinchine
# for one booth. It is an approximation, used to cross-check the DES, not to
# replace it.
# --------------------------------------------------------------------------
def lq_approx(rho: float, c: int, scv: float) -> float:
    """Approximate M/G/c mean queue length at utilization rho < 1."""
    if rho <= 0:
        return 0.0
    lam = c * rho                       # mu = 1 without loss of generality
    return lam * mmc_wq(lam, 1.0, c) * (1 + scv) / 2


def rho_for_level(x: float, c: int, scv: float) -> float:
    """Invert L(rho) = c*rho + Lq(rho) = x for rho in [0, 1)."""
    if x <= 0:
        return 0.0
    if c == 1:
        # Pollaczek-Khinchine: x = rho + a rho^2/(1-rho), a = (1+scv)/2,
        # i.e. (a-1) rho^2 + (1+x) rho - x = 0; root in [0, 1), stable form
        a = (1 + scv) / 2
        return 2 * x / ((1 + x) + math.sqrt((1 + x) ** 2 + 4 * (a - 1) * x))
    return brentq(lambda r: c * r + lq_approx(r, c, scv) - x, 0.0, 1 - 1e-12)


def fluid_rhs_factory(rates, config: Config, service: ServiceModel, deterministic=False):
    """Build f(t, x) for the fluid model.

    E[S] and the squared coefficient of variation of S come from the same
    fitted distributions the DES uses (peak window before 09:00, off-peak
    after). With deterministic=True the booths drain at full rate whenever
    x > 0 (the Week 2 deterministic queue: no variability, so no queue
    until arrivals exceed capacity).
    """
    rates = np.asarray(rates)
    moments = {w: (d.mean() * service.scale, d.var() / d.mean() ** 2)   # (E[S], SCV)
               for w, d in service.dists.items()}

    def window(t):
        return moments["peak" if t < PEAK_END else "offpeak"]

    def booths(t):
        extra = config.extra_booths if (config.extra_close is None or t < config.extra_close) else 0
        return config.base_booths + extra

    def busy(t, x):
        """Expected number of busy booths when the level is x."""
        c = booths(t)
        return c * rho_for_level(x, c, window(t)[1])

    def f(t, x):
        j = min(int(t // INTERVAL), len(rates) - 1)
        mean_s, _ = window(t)
        if deterministic:
            cap = booths(t) / mean_s
            return rates[j] - cap if x > 1e-12 else max(rates[j] - cap, 0.0)
        return rates[j] - busy(t, x) / mean_s

    f.busy = busy
    return f


def integrate(f, x0: float, t_end: float, h: float, method: str = "rk4"):
    """Euler or classical fourth-order Runge-Kutta with a fixed step h.
    The level is floored at 0 after each step (a queue cannot be negative)."""
    n = int(round(t_end / h))
    t = np.arange(n + 1) * h
    x = np.empty(n + 1)
    x[0] = x0
    for i in range(n):
        ti, xi = t[i], x[i]
        if method == "euler":
            xn = xi + h * f(ti, xi)
        elif method == "rk4":
            # stages are floored at 0 so the rate is never asked about a negative level
            k1 = f(ti, xi)
            k2 = f(ti + h / 2, max(xi + h * k1 / 2, 0.0))
            k3 = f(ti + h / 2, max(xi + h * k2 / 2, 0.0))
            k4 = f(ti + h, max(xi + h * k3, 0.0))
            xn = xi + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        else:
            raise ValueError(method)
        x[i + 1] = max(xn, 0.0)
    return t, x


def fluid_queue(t, x, f, deterministic=False) -> np.ndarray:
    """Convert the system level x(t) into vehicles waiting, Lq(t)."""
    if deterministic:
        return x                          # the fluid backlog is all queue
    return np.array([xi - f.busy(ti, xi) for ti, xi in zip(t, x)])


# --------------------------------------------------------------------------
# Command-line entry point: quick baseline experiment without the notebook
#   python parking_sim.py
# --------------------------------------------------------------------------
if __name__ == "__main__":
    svc = pd.read_csv("data/service_times.csv")
    x = svc["service_sec"].to_numpy() / 60
    fam, _ = select_distribution(x)
    dist = fit_distribution(x, fam)
    service = ServiceModel({"peak": dist, "offpeak": dist})
    site = pd.read_csv("data/site_measurements.csv").iloc[0]
    K = int(site["approach_length_m"] // (site["avg_vehicle_length_m"] + site["avg_gap_m"]))
    rates = load_arrival_counts("data/gate_entry_log.csv", "data/peak_arrival_tally.csv")["rate_per_min"].to_numpy()
    df = run_experiment(range(1, 31), rates, service, K)
    print(f"Service model: {fam} (pooled)   K = {K}   replications = 30\n")
    for cfg in CONFIGS:
        sub = df[df.config == cfg.name]
        print(cfg.name)
        for col in ["avg_wait_min", "max_queue_veh", "utilization", "spillover_min"]:
            c = ci_mean(sub[col])
            print(f"  {col:<16} {c['mean']:8.3f}  95% CI [{c['ci_low']:.3f}, {c['ci_high']:.3f}]")
    print("\nFull study (input fitting, verification, validation, sensitivity): Parking_Booth_Simulation.ipynb")
