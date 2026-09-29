# Parking Entrance: Discrete-Event Simulation
CSS142P Modelling and Simulation · Group 8 · Mapúa University

**The gate.** A car stops at one position. The guard checks its parking sticker, then the driver taps a University ID at the **one** reader and the barrier lifts. Cars without a sticker are refused and turn out of the lane.

**The question.** On a high-traffic day, is one guard enough? How much can traffic grow before the line reaches Pablo Ocampo Sr. Extension? Is a second guard (07:00–09:00 or 07:00–10:00) worth its guard-hours? The second guard shares the one reader, so it can only pre-check stickers upstream.

> **All campus inputs are estimates.** The group has no access to the gate or its records. Every value, with its basis and source, is in `data/input_parameters.csv`. Real public data (SFpark) is used only to test the form of the arrival process, never campus volumes.

## Run it
```bash
pip install simpy numpy scipy pandas matplotlib jupyter
jupyter notebook Parking_Booth_Simulation.ipynb    # then Kernel > Restart & Run All (a few minutes)
python parking_sim.py                              # quick 30-replication baseline, no notebook
```
**Google Colab:** clone the repository, `%cd` into `Group8_Parking_Booth_Simulation`, open the notebook and choose *Run all*. The first cell installs SimPy if it is missing. The notebook never creates or rewrites input files.

Tested with Python 3.12 and SimPy 4.1.2; the code also runs on Python 3.10+.

## Files
| Path | What it is |
|---|---|
| `Parking_Booth_Simulation.ipynb` | The full study: input modelling (incl. the real-data arrival test) → conceptual model → verification → experiment design → replication planning → results → stress test and fluid cross-check → validation → sensitivity → result statement |
| `parking_sim.py` | The model: input loading, arrival generation, common random numbers, the SimPy entrance model, measures, experiment driver, output-analysis helpers, arrival-assumption tests, the fluid-flow cross-check (Euler / RK4) |
| `data/input_parameters.csv` | Every activity-time estimate, the no-sticker share and K, each with its `basis` and `source`. **The single source of truth.** Edit values here; no code changes are needed. |
| `data/arrival_rates.csv` | Estimated arrivals per hour for each 15-minute interval, 07:00–19:00 |
| `data/proxy_sfpark_entries.csv` | Real per-vehicle entry times (one San Francisco garage, weekdays 07:00–19:00), used only to test the arrival assumption |
| `tools/build_arrival_proxy.py` | Rebuilds the proxy file from the public SFpark data (about 812 MB). Not part of the model. |
| `results/` | Every table the notebook produces, as CSV |
| `figures/` | Every figure the notebook produces, as PNG, including the conceptual model diagram |

## Inputs
| Input | Estimate | Basis |
|---|---|---|
| Arrivals | about 214 cars 07:00–10:00, peak 100 cars/hour, about 402 a day | Group estimate |
| Sticker check C | lognormal, mean 4 s, SD 2 s | Group estimate |
| ID tap + barrier T | lognormal, mean 4 s, SD 2 s | Group estimate; card/RFID reads take about 1–3 s |
| Move-up M | lognormal, mean 3 s, SD 1 s | Estimate |
| Refusal R | lognormal, mean 45 s, SD 15 s | Estimate |
| No-sticker share | 5% | Estimate |
| K | 8 cars | Estimate. **Measure it on Google Maps / Street View:** approach length ÷ (car length + gap). |

**Rebuilding the arrival proxy:**

```bash
python tools/build_arrival_proxy.py --survey      # entries per garage
python tools/build_arrival_proxy.py               # streams the file from the SFMTA
```

Add `--source path/to/downloaded.csv` to either command to use a downloaded copy. Source: [SFpark evaluation data, SFMTA](https://www.sfmta.com/getting-around/drive-park/demand-responsive-pricing/sfpark-evaluation).

## Results files
| File | Contents |
|---|---|
| `arrival_rates_and_load.csv` | Estimated rate and one-guard load ρ per 15-min interval |
| `proxy_uniformity_test.csv`, `proxy_dispersion_by_slot.csv` | Tests of the Poisson-arrival assumption on the SFpark data |
| `verification_checks.csv` | V1–V13: hand traces, D/D/1, conservation, sanity, FIFO, Little's law, guard-2 closing, CRN, M/M/1 and M/G/1 known answers, Lindley recursion, two-station hand trace, equivalences, throughput bound |
| `replication_planning.csv` | Week 7 replications-needed calculation, pilot and final *n* |
| `replications_raw.csv` | Every measure for every replication and configuration (headline *n*) |
| `summary_by_config.csv` | Mean, SD, SE and 95% CI per measure per configuration, with guard-hours |
| `paired_differences.csv` | Paired-t CIs for B−A, C−A and C−B, with a Bonferroni column and the extra guard-hours |
| `spillover_probability.csv` | Monte Carlo estimate of P(a high-traffic day has spillover), Wilson CI |
| `queue_profile_by_interval.csv` | Mean and 95th-percentile queue per 15 min |
| `stress_test.csv`, `headroom_by_K.csv` | Demand ×1 to ×5 for all configurations; the first multiple with P(spillover day) ≥ 10%, for K from 5 to 12 |
| `fluid_step_size.csv`, `fluid_vs_des.csv` | Euler vs RK4 step-size test; fluid model against the DES at demand ×3 |
| `validation_checks.csv` | Face validity, extreme conditions, published ranges |
| `demand_scenarios.csv`, `sensitivity_demand_processing.csv`, `sensitivity_by_config.csv` | Demand ×0.8 / 1.0 / 1.2 × processing time ×0.8 / 1.0 / 1.2 |
| `sensitivity_distribution.csv`, `sensitivity_K.csv` | Lognormal vs gamma vs exponential; K from 5 to 12 |
| `evidence_summary.csv` | The five kinds of evidence a credible study reports |
