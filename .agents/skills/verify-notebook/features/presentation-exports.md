# Notebook exports

Generate tables, figures, and interpretation from the executed notebook.

## Sub-features

- `exports-figures` covers the entrance diagram and result figures.
- `exports-tables` covers the main, supplementary, and timing-test statistics.
- `exports-interpretation` covers the staffing tradeoff and evidence limits.

## How to get to it (user POV)

Run all cells. Inspect the main results, morning comparison, timing sensitivity,
and final interpretation in the executed notebook and HTML evidence.

## Driving it with verify_notebook.py

Preconditions: uv environment ready, doctor passed, and the campus input files available.

Run the shared verification command. Require seven valid figures and the
main, supplementary, and timing CSVs. Read `results/recommendation.md` alongside
the raw results. Check the units, intervals, and scheduled guard-hours.
Visually inspect changed figures before publishing notebook outputs.

The exact command is:

```bash
uv run --locked python Group8_Parking_Booth_Simulation/tools/verify_notebook.py
```

Read the action log and resulting exports from the same evidence directory. Confirm evidence remains after scratch cleanup.

## Gotchas

Image decoding does not establish readable layout. Do not use historical exports
as current results. Do not claim measured inputs, a confirmed layout, financial
savings, or instructor approval.
Publication uses the separately authorized `--publish` operation.
