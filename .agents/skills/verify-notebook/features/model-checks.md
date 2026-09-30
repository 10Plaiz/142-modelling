# Model checks

Run all documented checks against the actual SimPy entrance model.

## Sub-features

- `checks-fixed` covers hand traces and deterministic cases.
- `checks-random` covers final daily invariants, reproducibility, and known-answer queues.
- `checks-input` covers invalid inputs and no arrivals.

## How to get to it (user POV)

Open notebook section 4, section 5's final-run checks, section 8's scaling checks,
and section 9's additional cases. Run All exercises each entry in order.

## Driving it with verify_notebook.py

Preconditions: uv environment ready, doctor passed, and the campus input files available.

Run the shared verification command. Inspect `results/verification_checks.csv` and `known_answer_benchmarks.csv` in the printed evidence directory. Every pass flag must be true, including V1 through V13, the invalid-input checks, empty demand, and extreme conditions. The executed notebook must show the expected and observed outcomes.

The exact command is:

```bash
uv run --locked python Group8_Parking_Booth_Simulation/tools/verify_notebook.py
```

Read the action log and resulting exports from the same evidence directory. Confirm evidence remains after scratch cleanup.

## Gotchas

Known-answer tests discard warm-up only in their separate steady-state cases. Normal operating-day runs start empty and do not discard warm-up. Passing tests do not validate the campus input estimates.
