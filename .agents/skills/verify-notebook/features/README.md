# Parking notebook verification map

The primary entry point is Run All on
`Group8_Parking_Booth_Simulation/Parking_Booth_Simulation.ipynb`. The scripted
equivalent executes every cell in a fresh .venv kernel, including model checks,
experiments, tables, figures, and interpretation.

## Preconditions

- Run from the repository root after `uv sync --locked`.
- Require the read-only `verify_notebook.py --doctor` command to pass.
- Keep campus input CSVs unchanged unless the task authorizes input changes.
- Treat the shared-reader arrangement and input values as assumptions.

## Proof conventions

Run `uv run --locked python Group8_Parking_Booth_Simulation/tools/verify_notebook.py`.
Each run retains a unique directory under `artifacts/notebook-verification/`.
Read the executed notebook or HTML along with the manifest and relevant CSVs.
An error, skipped code cell, missing combination, or failed check is a failure.
Do not substitute the CLI baseline for the notebook recipes.

The interactive Jupyter entry point uses the same notebook and project kernel.
Headless execution proves the cells and exports, not Jupyter menu interaction.

## Features

- [Model checks](model-checks.md): fixed examples, known answers, invalid and empty inputs, and daily invariants.
- [Staffing comparison](staffing-comparison.md): all-day and morning statistics, initial waiting, paired differences, precision, and guard-hours.
- [Sensitivity](demand-sensitivity.md): separate arrival-demand and activity-time comparisons.
- [Notebook exports](presentation-exports.md): figures, CSVs, and consistent interpretation.
