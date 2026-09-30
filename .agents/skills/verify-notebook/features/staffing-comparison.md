# Staffing comparison

Compare schedules A, B, and C using final replicated days and explicit measurement definitions.

## Sub-features

- `staffing-results` covers normal-demand means, SDs, intervals, and scheduled guard-hours.
- `staffing-paired` covers B minus A, C minus A, and C minus B.
- `staffing-precision` covers pilot planning and achieved final precision.

## How to get to it (user POV)

Open notebook sections 5 and 6. The CLI `uv run --locked python parking_sim.py`, from the project folder, is a separate 30-day normal-demand summary only.

## Driving it with verify_notebook.py

Preconditions: uv environment ready, doctor passed, and the campus input files available.

Run the shared verification command. Require all nine scenarios in
`summary_by_config.csv`, with n matching `replications_raw.csv`.
Check `replication_followup.csv` targets and `paired_differences.csv`.
Inspect `supplementary_summary.csv` and `supplementary_paired_differences.csv`
for morning delay, initial waiting, and effective guard-hours. Require means,
SDs, n, and intervals recalculated from the daily values.
Inspect `morning_comparison.png` for readable units and morning versus all-day bars.

The exact command is:

```bash
uv run --locked python Group8_Parking_Booth_Simulation/tools/verify_notebook.py
```

Read the action log and resulting exports from the same evidence directory. Confirm evidence remains after scratch cleanup.

## Gotchas

Delay is seconds, queue is cars, guard utilization is stored as a fraction and displayed as percent, and spillover is minutes. Guard work counts checks and refusals. A fractional mean daily maximum is valid. The CLI does not write or prove the full study exports.
