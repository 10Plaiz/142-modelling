# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

The CSS142P Modelling and Simulation final project for Group 8 at Mapúa University. It is a discrete-event simulation (DES) of the single vehicle entry booth at the Makati campus parking lot. The decision it supports: on high-traffic days, keep one booth all day, or staff a second booth from 07:00 to 09:00 or from 07:00 to 10:00. The sensitivity analysis also tests arrival demand at ±20%.

- `Modeling Proposal.md`: the project proposal, a single Field/Entry markdown table (Parts 1–11). It must stay consistent with what the code actually does. When a model, measure, check, or parameter changes, update the matching proposal row.
- `Group8_Parking_Booth_Simulation/`: **the working project.** Every command below runs from this directory, because the code reads `data/` and writes `results/` and `figures/` by relative path.
- `parking_sim.py` and `Parking_Booth_Simulation.ipynb` at the repository root are **older copies**: they predate the fluid-model section and have no `data/` next to them. Edit the files inside `Group8_Parking_Booth_Simulation/`.
- `review-materials-context/`: course lecture decks (PDF/PPTX, git-ignored). These define the expected methods and terminology, listed below.

## Commands

```bash
cd Group8_Parking_Booth_Simulation
pip install simpy numpy scipy pandas matplotlib jupyter
python parking_sim.py                              # quick 30-replication baseline, prints 95% CIs
jupyter notebook Parking_Booth_Simulation.ipynb    # full study; Kernel > Restart & Run All
```

The full notebook runs in about a minute and regenerates every CSV in `results/` and every PNG in `figures/`. After changing the model, rerun it top to bottom. The verification checks (V1–V9, section 3) live in the notebook and are the regression tests; `results/verification_checks.csv` must show every check passing. There is no separate test suite or linter. Tested with Python 3.12 and SimPy 4.1.2.

## Architecture

All model logic is in `parking_sim.py`. The notebook only calls it and holds the analysis narrative, so any number in the notebook can be regenerated from `data/`.

- **Time unit:** minutes after 07:00. `t = 0` is 07:00, `PEAK_END = 120` is 09:00, and `DAY_LENGTH = 720` is 19:00. Convert with `clock_to_min` and `min_to_clock`.
- **Inputs → rates:** `load_arrival_counts` bins the gate log into 48 intervals of 15 minutes. Rows in `peak_arrival_tally.csv` override the log for those intervals, because the gate log timestamps booth *passage*, which under-counts demand when a queue exists.
- **Arrivals:** `generate_arrivals` is a non-homogeneous Poisson process with a piecewise-constant rate. Exponential gaps restart at each interval boundary, which is exact because the exponential distribution is memoryless.
- **Service model:**
  - `fit_distribution`, `goodness_of_fit` and `select_distribution` fit exponential, lognormal and triangular distributions. The selection rule: lowest AIC among the fits the chi-square test does not reject at 5%.
  - `ServiceModel` maps one uniform U per vehicle through the inverse CDF of the distribution for that vehicle's arrival window (peak or off-peak).
- **Common random numbers (CRN) are a core invariant:**
  - `replication_inputs` derives two independent streams (arrivals and service U's) from one seed via `SeedSequence.spawn`.
  - Every configuration in a replication gets the *same* arrivals and service times. Verification check V8 enforces this.
  - Don't draw random numbers inside `simulate_day`, and don't change the stream layout without rechecking V8 and the paired-t analysis.
- **DES core:** `simulate_day` uses SimPy's process-interaction world view.
  - The booths are a `FilterStore` of `Booth` objects, all fed by one shared FIFO queue.
  - The second booth is flagged `extra`. At `extra_close` (09:00) it finishes its current vehicle, then accepts no more (a non-preemptive close).
  - `Config(base_booths, extra_booths, extra_close)` defines a scenario. `CONFIGS = [ONE_BOOTH, TWO_BOOTH_PEAK, TWO_BOOTH_EXTENDED]`: 1 booth, and a second booth until 09:00 or until 10:00.
  - `COMPARISONS` lists the three paired contrasts the notebook reports. Notebook cells iterate over `CONFIGS` and `COMPARISONS` rather than assuming two configurations, so a new scenario only needs adding there. Verification check V7 reads each configuration's own `extra_close`.
- **Measures:**
  - `day_metrics` returns the four proposal measures: `avg_wait_min`, `max_queue_veh`, `utilization` over *staffed* booth-time, and `spillover_min`, the time the waiting queue is at least K.
  - It also returns supplementary measures. Keys starting with `_` exist only for the Little's-law check.
  - K comes from `data/site_measurements.csv`: approach length ÷ (vehicle length + gap), rounded down.
- **Experiment and output analysis:**
  - `run_experiment` loops over seeds and configurations.
  - `ci_mean` gives t-intervals; the notebook computes paired-t intervals on per-seed differences.
  - `replications_needed` implements the Week 7 rule: n × (current half-width ÷ target half-width)².
  - `wilson_interval` is used for the Monte Carlo probability of spillover.
- **Analytic benchmarks:** `mm1_wq` and `mmc_wq` (Erlang C) serve as the known-answer verification checks.
- **Continuous cross-check (not the study model):**
  - `fluid_rhs_factory`, `integrate` (Euler/RK4) and `fluid_queue` implement the fluid-flow approximation dx/dt = λ(t) − c(t)·ρ(x)/E[S].
  - `rho_for_level` inverts the M/G/c mean queue length: closed-form Pollaczek–Khinchine for c = 1, and `brentq` on Erlang C × (1 + SCV)/2 for c > 1.
  - Service moments are cached per window; calling scipy `.mean()` inside the rate function is very slow.

## Data caveat

`data/` currently holds **placeholder** inputs generated by `tools/make_placeholder_data.py`, which is not part of the model. The notebook detects this through `measured_on == "PLACEHOLDER"` in `site_measurements.csv` and prints a warning. Treat every result as illustrative until real field data replaces the files; `README.md` lists the collection protocol and file formats. Never present placeholder results as findings, and keep proposal wording about data collection in the future tense until the real data exists. `validation_observations.csv` is for validation only and must never be used for fitting.

## Course conventions to follow

The course decks set the vocabulary and methods the project is graded against. Keep new work in these terms rather than inventing new ones:

- **Classification:** dynamic / stochastic / discrete, stated with reasons.
- **Study type:** a *terminating* study with no warm-up in the main experiment. Only the M/M/c known-answer tests use a warm-up.
- **Activity vs. delay:** processing time is an activity (sampled); waiting time is a delay (output, never sampled).
- **Reporting:** a single run is never a result. Report the mean with a 95% CI and n.
- **Verification vs. validation:** kept separate. Overlapping intervals mean "consistent with the model", never "proven correct".
- **Five kinds of evidence (Week 7):** precision, study design, verification, validation, and sensitivity.

Don't force in course topics that don't fit the system. For example, the course's hand-coded random-number generator (LCG) is deliberately replaced by NumPy's PCG64.
