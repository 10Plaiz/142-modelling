# Parking entrance staffing study

CSS142P Modelling and Simulation | Group 8 | Mapúa University

Compare one guard all day, a second guard 07:00 to 09:00, and a second guard
07:00 to 10:00. Each schedule is tested with 80%, 100%, and 120% arrival demand.

All campus inputs are estimates. The shared ID reader and advance sticker-check
arrangement are model assumptions. This revises the submitted independent-booth
proposal. Results are conditional on those assumptions; field validation and
instructor acceptance of the revision are not established.

## Run in Google Colab (no installation)

1. Open [Google Colab](https://colab.research.google.com), choose **File → Open notebook → GitHub**, and paste
   `https://github.com/10Plaiz/142-modelling`.
2. Select `Group8_Parking_Booth_Simulation/Parking_Booth_Simulation.ipynb`.
3. Choose **Runtime → Run all**. It takes about a minute.

The notebook's first code cell runs only in Colab. It clones this repository to get the model code, inputs,
and tools, then installs SimPy 4.1.2. Colab's own versions of NumPy, pandas, SciPy, and Matplotlib are used,
so the locked local environment below remains the reference setup.

## Set up and run

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python
3.12. Run these commands from the repository root:

```bash
uv sync --locked
uv run --locked python Group8_Parking_Booth_Simulation/tools/verify_notebook.py --doctor
uv run --locked python Group8_Parking_Booth_Simulation/tools/verify_notebook.py
```

The verifier executes the real notebook in a fresh kernel and isolated working
directory. It checks all nine main combinations, morning statistics, initial
waiting, and a separate activity-time test. It recalculates exported intervals
from raw daily results and verifies unchanged inputs. Evidence survives cleanup
under `artifacts/notebook-verification/`.

To refresh the working notebook and generated files after a passing run:

```bash
uv run --locked python Group8_Parking_Booth_Simulation/tools/verify_notebook.py --publish
```

Previous generated exports are preserved under `archive/pre-presentation/`.
Publication is a local copy operation; it does not push or submit anything.

For interactive Jupyter, start from the repository root:

```bash
uv run --locked jupyter lab Group8_Parking_Booth_Simulation/Parking_Booth_Simulation.ipynb
```

Choose the project's Python 3.12 environment. In VS Code, select
`.venv/bin/python` on Linux or `.venv\\Scripts\\python.exe` on Windows.
Use Restart Kernel and Run All Cells. The notebook runs from its own folder.
It produces `results/` and `figures/` and reads inputs without
rewriting them. Outside Colab, no automatic package install or public-data download occurs.

For the 30-day normal-demand CLI baseline:

```bash
cd Group8_Parking_Booth_Simulation
uv run --locked python parking_sim.py
```

The CLI is a smaller experiment. It does not replace full notebook verification.

## Files and evidence

| Path | Purpose |
| --- | --- |
| `Parking_Booth_Simulation.ipynb` | Study question, entrance, inputs, checks, precision planning, morning results, two separate sensitivity tests, and interpretation. |
| `parking_sim.py` | SimPy model, input loading, random streams, measures, and analysis helpers. |
| `data/input_parameters.csv` | Estimated activity moments, refusal share, and K, with basis and source. |
| `data/arrival_rates.csv` | Estimated hourly rates in all 48 fifteen-minute slots. |
| `results/verification_checks.csv` | Check names, expected and observed outcomes, and pass flags. |
| `results/replications_raw.csv` | Final replication output for every seed, schedule, and demand level. |
| `results/summary_by_config.csv` | Means, SDs, 95% t intervals, units, n, and scheduled guard-hours for all nine combinations. |
| `results/paired_differences.csv` | Alternative-minus-baseline differences, paired intervals, and Bonferroni intervals. |
| `results/replication_planning.csv`, `replication_followup.csv` | Pilot requirements and final achieved precision. |
| `results/spillover_probability.csv` | Spillover-day counts and Wilson intervals. Zero observed days do not imply zero risk. |
| `results/initial_wait_and_guard_hours.csv` | Initial waiting distinguished from total delay, plus effective guard-hours. |
| `results/supplementary_summary.csv`, `supplementary_paired_differences.csv` | Morning delay, initial waiting, and effective guard-hours with SDs, n, and confidence intervals. |
| `results/activity_replications_raw.csv`, `activity_sensitivity.csv`, `activity_paired_differences.csv` | Activities scaled to 80%, 100%, and 120% at normal arrivals, with matching days and interval statistics. |
| `results/activity_replication_planning.csv` | Achieved timing-test precision. Normal activity cases reuse the main experiment when n matches. |
| `results/input_provenance.csv` | Known input origins and missing justification. |
| `results/demand_scenarios.csv` | The required demand comparison, keeping other inputs fixed. |
| `results/extreme_conditions.csv` | Additional low-demand, high-demand, and slow-reader cases. |
| `results/headroom_sweep.csv` | Demand from 1x to 5x for schedules A and B: spillover, maximum queue, morning delay, and spillover-day probability, with intervals. Locates when one guard stops being enough. |
| `results/recommendation.md` | The computed recommendation: decision rule, evidence, when it would change, and limits. |
| `presentation/Parking_Study_Report.pdf` | Study report in PDF format. |
| `presentation/Parking_Study_Presentation.pdf` | Presentation of the study question, method, evidence, and limitations. |
| `presentation/talk-track.md` | Speaker notes and explanations of the study. |
| `tools/verify_notebook.py` | Read-only doctor, isolated Run All, output checks, evidence, and optional local publication. |
| `tools/build_presentation.py` | Figure and document rendering functions. |
| `tools/build_arrival_proxy.py` | Retained optional SFpark downloader. Not required or run for this study. |
| `archive/pre-presentation/` | Historical booth-study exports. Do not use them as current results. |

The notebook also saves a conceptual-model diagram, arrival profile, queue
profile, normal-demand comparison, and demand-sensitivity figure. It also saves
morning and activity-time comparison figures, and the headroom sweep figure.

## Interpretation

Total delay is elapsed time minus the car's own activity time. Initial waiting
is time before the first sticker check. Guard utilization includes active checks
and refusals, not all reader or stop occupancy. K = 8 defines spillover at a
queue count of at least eight, including the pre-check position.

A fractional mean maximum queue averages integer daily maxima. An error bar
describes uncertainty about a simulated mean, not a prediction band for each
day. Estimated inputs and the unconfirmed layout remain separate limitations.

Arrival sensitivity changes demand only. Activity sensitivity changes all four
activity times together at normal demand. It scales their means and SDs, while
preserving distribution shapes. Refusal share, K, and entrance rules stay fixed.

Optional proxy tests and the fluid approximation remain available in the model
code but are outside the notebook's evidence.

The uv lockfile records tested packages. Keep `.venv` out of Git. Recreate the
environment on another machine rather than copying it. The local workflow is
the reference reproduction path. In Colab, the notebook's first cell fetches the
project files and installs SimPy itself.
