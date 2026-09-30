"""
parking_sim.py
==============
Discrete-event simulation of the vehicle entrance at the Mapua University
Makati campus parking lot.

CSS142P Modelling and Simulation - Group 8
(Ariola, Bauza, Caliliw, Jimenez)

Assumed gate. A car stops at one position. The guard checks its parking sticker,
then the driver taps a University ID at the one reader and the barrier lifts.
Cars without a sticker (about 5%) are refused there and turn out of the lane.
A second guard can be posted one car-length upstream to pre-check stickers
while the car ahead taps. The reader is never duplicated, so the second guard
adds checking capacity, not a second lane.

Time unit : minutes after 07:00  (t = 0 is 07:00, t = 120 is 09:00,
            t = 180 is 10:00, t = 720 is 19:00). Activity inputs are given in
            seconds in data/input_parameters.csv and converted on load.
World view: process interaction (SimPy 4.1).

Model classification
    Dynamic       - delay depends on the order and timing of arrivals.
    Stochastic    - interarrival and activity times are random.
    Discrete      - the queue on the approach and the status of the stop,
                    the pre-check spot and each guard change only at events.
    Terminating   - one operating day with a natural start (07:00) and end
                    (19:00 arrivals stop, the line is cleared), so no warm-up.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from pathlib import Path

import numpy as np
import pandas as pd
import simpy
from scipy import stats

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
INTERVAL = 15.0          # minutes per arrival-rate interval
DAY_LENGTH = 720.0       # minutes, 07:00-19:00
MORNING_END = 180.0      # 10:00; end of the window used for morning measures
OPEN_CLOCK = 7 * 60      # 07:00 in minutes after midnight
ACTIVITIES = ["check", "tap", "moveup", "refusal"]   # C, T, M, R


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
# Configurations (staffing plans)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    name: str
    guard2_close: float | None = None    # minutes after 07:00; None = no second guard
    guard_hours: float = 12.0            # staffed guard-hours per day (the cost side)


ONE_GUARD = Config("A: 1 guard", None, 12.0)
GUARD2_TO_09 = Config("B: 2nd guard 07-09", clock_to_min("09:00"), 14.0)
GUARD2_TO_10 = Config("C: 2nd guard 07-10", clock_to_min("10:00"), 15.0)
CONFIGS = [ONE_GUARD, GUARD2_TO_09, GUARD2_TO_10]

# Paired comparisons (A - B) reported for the decision: does a second guard
# help at all, and does keeping it one more hour add anything?
COMPARISONS = [(ONE_GUARD, GUARD2_TO_09), (ONE_GUARD, GUARD2_TO_10),
               (GUARD2_TO_09, GUARD2_TO_10)]


# --------------------------------------------------------------------------
# Inputs: one source of truth in data/
# --------------------------------------------------------------------------
def lognormal_params(mean: float, sd: float):
    """(mu, sigma) of the underlying normal, by the method of moments."""
    s2 = math.log(1 + (sd / mean) ** 2)
    return math.log(mean) - s2 / 2, math.sqrt(s2)


def make_dist(family: str, mean: float, sd: float):
    """Frozen scipy distribution with the stated mean (and SD where the
    family allows it; the exponential's SD always equals its mean)."""
    if family == "lognormal":
        mu, sigma = lognormal_params(mean, sd)
        return stats.lognorm(sigma, scale=math.exp(mu))
    if family == "gamma":
        k = (mean / sd) ** 2
        return stats.gamma(k, scale=mean / k)
    if family == "exponential":
        return stats.expon(scale=mean)
    raise ValueError(family)


@dataclass
class ActivityModel:
    """Activity-time model. Times are in minutes.

    Every car carries one uniform U per activity; its time is X = F^-1(U).
    Driving every car with its own U keeps common random numbers intact across
    configurations, demand scenarios, processing-time scales and even
    alternative distribution families.
    """
    dists: dict                 # {"check": frozen, "tap": ..., "moveup": ..., "refusal": ...}
    share_nonsticker: float
    scale: float = 1.0

    def times(self, u: dict) -> dict:
        return {a: np.maximum(self.dists[a].ppf(u[a]), 1e-9) * self.scale for a in ACTIVITIES}

    def with_scale(self, s: float) -> "ActivityModel":
        return ActivityModel(self.dists, self.share_nonsticker, self.scale * s)

    def moments(self, admitted_at_stop: bool):
        """(E[S], E[S^2]) of the time a car holds the stop.
        admitted_at_stop=False: one-guard mode, mixture of C+T+M and C+R.
        admitted_at_stop=True : pre-checked sticker car, T+M only."""
        m = {a: self.dists[a].mean() * self.scale for a in ACTIVITIES}
        v = {a: self.dists[a].var() * self.scale ** 2 for a in ACTIVITIES}

        def sum_moments(parts):
            mu = sum(m[a] for a in parts)
            return mu, sum(v[a] for a in parts) + mu ** 2

        if admitted_at_stop:
            return sum_moments(["tap", "moveup"])
        p = self.share_nonsticker
        m1, s1 = sum_moments(["check", "tap", "moveup"])
        m2, s2 = sum_moments(["check", "refusal"])
        return (1 - p) * m1 + p * m2, (1 - p) * s1 + p * s2

    def precheck_moments(self):
        """(E[S], E[S^2]) of the time a car holds the pre-check spot for guard 2."""
        m = {a: self.dists[a].mean() * self.scale for a in ACTIVITIES}
        v = {a: self.dists[a].var() * self.scale ** 2 for a in ACTIVITIES}
        p = self.share_nonsticker
        m1, s1 = m["check"], v["check"] + m["check"] ** 2
        m2 = m["check"] + m["refusal"]
        s2 = v["check"] + v["refusal"] + m2 ** 2
        return (1 - p) * m1 + p * m2, (1 - p) * s1 + p * s2


def load_inputs(data_dir="data", family="lognormal"):
    """Read data/arrival_rates.csv and data/input_parameters.csv.

    Returns (rates per minute for each 15-min interval, parameter table, K,
    ActivityModel). Nothing is ever written back to data/.
    """
    data_dir = Path(data_dir)
    arr = pd.read_csv(data_dir / "arrival_rates.csv")
    rates = arr["arrivals_per_hour"].to_numpy(float) / 60.0
    expected_slots = [min_to_clock(i * INTERVAL) for i in range(48)]
    if arr["interval_start"].tolist() != expected_slots:
        raise ValueError("Arrival inputs must contain all 48 ordered 15-minute slots from 07:00 to 18:45")
    if not np.isfinite(rates).all() or (rates < 0).any():
        raise ValueError("Arrival rates must be finite and nonnegative")
    params = pd.read_csv(data_dir / "input_parameters.csv")
    p = params.set_index("parameter")["value"].astype(float)
    if params["parameter"].duplicated().any() or not np.isfinite(p).all():
        raise ValueError("Input parameters must be unique and finite")
    for activity in ACTIVITIES:
        if p[f"{activity}_mean_sec"] <= 0 or p[f"{activity}_sd_sec"] <= 0:
            raise ValueError("Activity means and standard deviations must be positive")
    if not 0 <= p["nonsticker_share"] <= 1:
        raise ValueError("The no-sticker share must be between zero and one")
    if p["K_waiting_spaces"] < 1 or not p["K_waiting_spaces"].is_integer():
        raise ValueError("The spillover threshold must be a positive integer")
    dists = {a: make_dist(family, p[f"{a}_mean_sec"] / 60, p[f"{a}_sd_sec"] / 60) for a in ACTIVITIES}
    model = ActivityModel(dists, float(p["nonsticker_share"]))
    return rates, params, int(p["K_waiting_spaces"]), model


# --------------------------------------------------------------------------
# Random inputs with common random numbers
# --------------------------------------------------------------------------
STREAMS = ["arrivals", "type"] + ACTIVITIES


def arrival_times(rates: np.ndarray, unit_exp_cumsum: np.ndarray, demand: float = 1.0,
                  interval: float = INTERVAL) -> np.ndarray:
    """Non-homogeneous Poisson process with a piecewise-constant rate,
    generated by inverting the cumulative rate function Lambda(t).

    unit_exp_cumsum are the event times of a unit-rate Poisson process. The
    same unit-rate events drive every demand scale, so demand scenarios share
    common random numbers too: car i at demand x1.2 comes from the same
    random number as car i at demand x1.0.
    """
    rate = np.asarray(rates, dtype=float) * demand
    cum = np.concatenate([[0.0], np.cumsum(rate * interval)])
    s = unit_exp_cumsum[unit_exp_cumsum < cum[-1]]
    idx = np.searchsorted(cum, s, side="right") - 1
    return idx * interval + (s - cum[idx]) / rate[idx]


def replication_inputs(seed: int, rates, model: ActivityModel, demand: float = 1.0):
    """One independent stream per random input, all derived from one seed.

    Returns (arrival times, is_nonsticker, activity times dict)."""
    ss = dict(zip(STREAMS, np.random.SeedSequence(seed).spawn(len(STREAMS))))
    total = float(np.sum(rates) * INTERVAL * demand)
    gen = np.random.default_rng(ss["arrivals"])
    e = np.cumsum(gen.exponential(1.0, int(total * 1.3) + 100))
    while e[-1] < total:                                   # always enough unit-rate events
        e = np.concatenate([e, e[-1] + np.cumsum(gen.exponential(1.0, 500))])
    arrivals = arrival_times(rates, e, demand)
    n = len(arrivals)
    nonsticker = np.random.default_rng(ss["type"]).random(n) < model.share_nonsticker
    u = {a: np.random.default_rng(ss[a]).random(n) for a in ACTIVITIES}
    return arrivals, nonsticker, model.times(u)


# --------------------------------------------------------------------------
# The discrete-event model
# --------------------------------------------------------------------------
@dataclass
class DayResult:
    arrival: np.ndarray
    nonsticker: np.ndarray
    at_stop: np.ndarray          # time the car reaches the stop (NaN if refused at pre-check)
    depart: np.ndarray           # time the car leaves (entered, or turned away)
    activity: np.ndarray         # the car's own activity time (C+T+M or C+R), minutes
    stop_hold: np.ndarray        # time the car holds the stop (NaN if never there)
    approach_time: np.ndarray    # time spent on the approach, arrival until the stop or refusal
    prechecked: np.ndarray       # checked by guard 2
    check_start: np.ndarray      # when the sticker check started
    trace_t: np.ndarray          # queue-on-approach step function
    trace_q: np.ndarray
    guard_busy: dict             # {1: minutes, 2: minutes}
    guard_last: dict             # last moment each guard finished work
    config: Config
    snapshot_close: dict = field(default_factory=dict)   # state at 19:00


def simulate_day(arrivals, nonsticker, acts: dict, config: Config,
                 day_length: float = DAY_LENGTH) -> DayResult:
    """Run one operating day. Arrivals stop at day_length (they are generated
    only before it); cars already on the approach are processed.

    One guard (or guard 2 off duty): the car at the stop gets C, then T + M
    (sticker) or R (no sticker, turned away).
    Guard 2 on duty and the stop occupied: the car behind the stop is
    pre-checked at the pre-check spot (C, or C + R and turned away), then keeps
    that spot until the stop frees (blocking, no buffer), and at the stop
    needs only T + M. If the stop is free the car drives straight up.
    """
    env = simpy.Environment()
    n = len(arrivals)
    C, T, M, R = (np.asarray(acts[a]) for a in ACTIVITIES)
    stop = simpy.Resource(env, capacity=1)
    precheck = simpy.Resource(env, capacity=1) if config.guard2_close is not None else None

    at_stop = np.full(n, np.nan)
    depart = np.full(n, np.nan)
    stop_hold = np.full(n, np.nan)
    approach_time = np.full(n, np.nan)
    check_start = np.full(n, np.nan)
    prechecked = np.zeros(n, dtype=bool)
    activity = np.where(nonsticker, C + R, C + T + M)
    busy, last = {1: 0.0, 2: 0.0}, {1: 0.0, 2: 0.0}
    state = {"on_approach": 0, "arrived": 0, "at_stop": 0, "entered": 0, "refused": 0}
    trace_t, trace_q = [0.0], [0]

    def log_q():
        trace_t.append(env.now)
        trace_q.append(state["on_approach"])

    def leave_approach(i):
        state["on_approach"] -= 1
        approach_time[i] = env.now - arrivals[i]
        log_q()

    def car(i):
        # event: ARRIVAL
        state["arrived"] += 1
        state["on_approach"] += 1
        log_q()
        checked = False
        if precheck is not None:
            spot = precheck.request()
            yield spot                                    # reach the spot behind the stop
            # Guard 2 pre-checks only while on duty AND the stop is occupied;
            # with the stop free the car drives straight up and guard 1 checks it.
            if env.now < config.guard2_close and stop.count > 0:
                check_start[i] = env.now
                prechecked[i] = True
                yield env.timeout(C[i])
                busy[2] += C[i]
                if nonsticker[i]:                         # event: REFUSED at pre-check
                    yield env.timeout(R[i])
                    busy[2] += R[i]
                    last[2] = env.now
                    precheck.release(spot)
                    leave_approach(i)
                    depart[i] = env.now
                    state["refused"] += 1
                    return
                last[2] = env.now
                checked = True
            req = stop.request()
            yield req                                     # blocking: still holding the spot
            precheck.release(spot)
        else:
            req = stop.request()
            yield req
        # event: ARRIVES AT STOP (leaves the approach queue)
        leave_approach(i)
        at_stop[i] = env.now
        state["at_stop"] += 1
        if not checked:
            check_start[i] = env.now
            yield env.timeout(C[i])                       # guard 1 checks the sticker
            busy[1] += C[i]
            if nonsticker[i]:                             # event: REFUSED at the stop
                yield env.timeout(R[i])
                busy[1] += R[i]
                last[1] = env.now
                stop.release(req)
                stop_hold[i] = env.now - at_stop[i]
                depart[i] = env.now
                state["at_stop"] -= 1
                state["refused"] += 1
                return
            last[1] = env.now
        yield env.timeout(T[i] + M[i])                    # ID tap, barrier, move-up
        stop.release(req)                                 # event: ENTERS
        stop_hold[i] = env.now - at_stop[i]
        depart[i] = env.now
        state["at_stop"] -= 1
        state["entered"] += 1

    def source():
        for i in range(n):
            yield env.timeout(arrivals[i] - env.now)
            env.process(car(i))

    snap = {}

    def snapshot():
        yield env.timeout(day_length)
        snap.update(time=env.now, **state)

    env.process(source())
    env.process(snapshot())
    env.run()

    return DayResult(np.asarray(arrivals), np.asarray(nonsticker), at_stop, depart, activity,
                     stop_hold, approach_time, prechecked, check_start,
                     np.asarray(trace_t), np.asarray(trace_q), busy, last, config, snap)


# --------------------------------------------------------------------------
# Performance measures
# --------------------------------------------------------------------------
def _segments(res: DayResult):
    """Queue-length step function as (t0, t1, q) segments."""
    t = res.trace_t
    end = max(t[-1], DAY_LENGTH)
    t1 = np.append(t[1:], end)
    return t, t1, res.trace_q


def queue_time_above(res: DayResult, K: int, window=None) -> float:
    """Total time the queue on the approach holds at least K vehicles
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
    """Delay = time in system minus the car's own activity time: always an
    output of the model, never sampled."""
    delay = (res.depart - res.arrival) - res.activity
    initial_wait = res.check_start - res.arrival
    n = len(delay)
    t_end = float(np.nanmax(res.depart)) if n else DAY_LENGTH
    t0, t1, q = _segments(res)
    area = float(np.sum((t1 - t0) * q))
    cfg = res.config

    on_duty = {1: max(DAY_LENGTH, res.guard_last[1])}
    if cfg.guard2_close is not None:
        on_duty[2] = max(cfg.guard2_close, res.guard_last[2])
    guard_busy = sum(res.guard_busy[g] for g in on_duty)
    stop_busy = float(np.nansum(res.stop_hold))
    morning = res.arrival < MORNING_END
    spill = queue_time_above(res, K)

    return {
        # proposal measures
        "avg_delay_sec": float(delay.mean()) * 60 if n else 0.0,
        "avg_initial_wait_sec": float(initial_wait.mean()) * 60 if n else 0.0,
        "max_queue_veh": int(q.max()),
        "guard_utilization": guard_busy / sum(on_duty.values()),
        "spillover_min": spill,
        # supplementary measures
        "any_spillover": int(spill > 0),
        "avg_delay_morning_sec": float(delay[morning].mean()) * 60 if morning.any() else 0.0,
        "p90_delay_sec": float(np.percentile(delay, 90)) * 60 if n else 0.0,
        "max_delay_sec": float(delay.max()) * 60 if n else 0.0,
        "stop_occupancy": stop_busy / max(DAY_LENGTH, t_end),
        "spillover_morning_min": queue_time_above(res, K, (0.0, MORNING_END)),
        "guard_hours": cfg.guard_hours,
        "effective_guard_hours": sum(on_duty.values()) / 60,
        "n_vehicles": n,
        "n_refused": int(res.nonsticker.sum()),
        "time_avg_queue_Lq": area / max(DAY_LENGTH, t_end),
        "last_departure_clock": min_to_clock(t_end),
        # kept for the Little's-law identity check
        "_queue_area": area,
        "_sum_approach": float(np.nansum(res.approach_time)),
    }


# --------------------------------------------------------------------------
# Experiment driver with common random numbers
# --------------------------------------------------------------------------
def run_experiment(seeds, rates, model, K, configs=CONFIGS, demand=1.0,
                   keep_days=False, extra_K=()):
    rows, days = [], {}
    for seed in seeds:
        arrivals, nonsticker, acts = replication_inputs(seed, rates, model, demand)
        for cfg in configs:
            res = simulate_day(arrivals, nonsticker, acts, cfg)
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
# Input modelling on the real proxy data (tests assumption A1)
# --------------------------------------------------------------------------
def load_proxy(path="data/proxy_sfpark_entries.csv") -> pd.DataFrame:
    df = pd.read_csv(path, comment="#")
    df["entry_datetime"] = pd.to_datetime(df["entry_datetime"])
    df["date"] = df["entry_datetime"].dt.date
    df["minute_of_day"] = df["entry_datetime"].dt.hour * 60 + df["entry_datetime"].dt.minute
    return df


def uniformity_test(minutes_of_day: np.ndarray, interval: int = 15) -> dict:
    """Under a Poisson process whose rate is constant within each interval,
    arrivals are uniformly spread over the minutes of that interval.
    Chi-square test of minute-within-interval against the uniform."""
    pos = np.asarray(minutes_of_day, dtype=int) % interval
    observed = np.bincount(pos, minlength=interval)
    expected = np.full(interval, observed.sum() / interval)
    chi2 = float(((observed - expected) ** 2 / expected).sum())
    dof = interval - 1
    return {"n": int(observed.sum()), "chi2": chi2, "dof": dof, "p_value": float(stats.chi2.sf(chi2, dof)),
            "crit_5pct": float(stats.chi2.ppf(0.95, dof)), "observed": observed}


def dispersion_test(counts: np.ndarray) -> dict:
    """Index-of-dispersion test for one slot observed on d days.
    Poisson counts have variance = mean, so D = sum (x - xbar)^2 / xbar
    follows chi-square(d - 1). Returns the variance/mean ratio and p-value."""
    x = np.asarray(counts, dtype=float)
    d, xbar = len(x), x.mean()
    if xbar == 0 or d < 2:
        return {"days": d, "mean": xbar, "var_to_mean": np.nan, "D": np.nan, "p_value": np.nan}
    D = float(((x - xbar) ** 2).sum() / xbar)
    p_hi = stats.chi2.sf(D, d - 1)
    p_lo = stats.chi2.cdf(D, d - 1)
    return {"days": d, "mean": xbar, "var_to_mean": float(x.var(ddof=1) / xbar), "D": D,
            "p_value": float(min(1.0, 2 * min(p_hi, p_lo)))}            # two-sided


# --------------------------------------------------------------------------
# Queueing-theory benchmarks for verification
# --------------------------------------------------------------------------
def mm1_wq(lam, mu):
    rho = lam / mu
    return rho / (mu - lam)


def pk_wq(lam, es, es2):
    """Pollaczek-Khinchine mean delay for M/G/1."""
    rho = lam * es
    return lam * es2 / (2 * (1 - rho))


def lindley_delays(arrivals, service) -> np.ndarray:
    """W_i = max(0, W_{i-1} + S_{i-1} - (A_i - A_{i-1})): an independent
    calculation of every car's delay in a single-server FIFO queue."""
    w = np.zeros(len(arrivals))
    for i in range(1, len(arrivals)):
        w[i] = max(0.0, w[i - 1] + service[i - 1] - (arrivals[i] - arrivals[i - 1]))
    return w


# --------------------------------------------------------------------------
# Continuous cross-check: fluid-flow approximation (FFA)
#
#   dx/dt = lambda_b(t) - rho(x) / E[S_b(t)]
#
# x is the expected number of vehicles at the bottleneck station (waiting +
# being served), treated as a continuous level. With one guard the bottleneck
# is the stop (C+T+M or C+R). While guard 2 pre-checks, the model uses
# whichever station, pre-check or stop, carries the higher load. rho(x) is the
# utilization at which a steady-state M/G/1 queue holds x vehicles on average
# (Pollaczek-Khinchine, inverted in closed form). It is an approximation used
# to cross-check the DES, not to replace it.
# --------------------------------------------------------------------------
def rho_for_level(x: float, scv: float) -> float:
    """Invert L(rho) = rho + a rho^2 / (1 - rho) = x, a = (1 + scv)/2, for rho in [0, 1)."""
    if x <= 0:
        return 0.0
    a = (1 + scv) / 2
    return 2 * x / ((1 + x) + math.sqrt((1 + x) ** 2 + 4 * (a - 1) * x))


def fluid_rhs_factory(rates, config: Config, model: ActivityModel, demand: float = 1.0,
                      deterministic=False):
    """Build f(t, x). The station moments depend only on simulation time t
    (whether guard 2 is on duty), so there is a single definition of the
    service window."""
    rates = np.asarray(rates) * demand
    p = model.share_nonsticker
    one = model.moments(admitted_at_stop=False)
    stop2 = model.moments(admitted_at_stop=True)
    pre2 = model.precheck_moments()

    def station(t):
        """(arrival-rate multiplier, E[S], SCV) of the bottleneck station at time t."""
        if config.guard2_close is not None and t < config.guard2_close:
            loads = [(1 - p, *stop2), (1.0, *pre2)]      # stop sees sticker cars only
            mult, es, es2 = max(loads, key=lambda z: z[0] * z[1])
        else:
            mult, (es, es2) = 1.0, one
        return mult, es, es2 / es ** 2 - 1

    def busy(t, x):
        _, _, scv = station(t)
        return rho_for_level(x, scv)

    def f(t, x):
        j = min(int(t // INTERVAL), len(rates) - 1)
        mult, es, scv = station(t)
        lam = rates[j] * mult
        if deterministic:
            return lam - 1 / es if x > 1e-12 else max(lam - 1 / es, 0.0)
        return lam - rho_for_level(x, scv) / es

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
    """Convert the level x(t) into vehicles waiting, Lq(t)."""
    if deterministic:
        return x                          # the fluid backlog is all queue
    return np.array([xi - f.busy(ti, xi) for ti, xi in zip(t, x)])


# --------------------------------------------------------------------------
# Command-line entry point: quick baseline experiment without the notebook
#   python parking_sim.py
# --------------------------------------------------------------------------
if __name__ == "__main__":
    rates, params, K, model = load_inputs("data")
    df = run_experiment(range(1, 31), rates, model, K)
    es, _ = model.moments(admitted_at_stop=False)
    print(f"ESTIMATED inputs (no gate data)   K = {K}   mean time at stop = {es * 60:.1f} s   "
          f"replications = 30\n")
    for cfg in CONFIGS:
        sub = df[df.config == cfg.name]
        print(f"{cfg.name}   ({cfg.guard_hours:g} guard-hours)")
        for col in ["avg_delay_sec", "max_queue_veh", "guard_utilization", "spillover_min"]:
            c = ci_mean(sub[col])
            print(f"  {col:<18} {c['mean']:8.3f}  95% CI [{c['ci_low']:.3f}, {c['ci_high']:.3f}]")
    print("\nFull study, model checks and demand sensitivity: Parking_Booth_Simulation.ipynb")
