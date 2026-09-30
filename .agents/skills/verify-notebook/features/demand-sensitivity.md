# Arrival-demand and activity-time sensitivity

Repeat the same staffing comparison with 20% fewer arrivals and 20% more arrivals.
Separately test activity times scaled to 80%, 100%, and 120% at normal arrivals.

## Sub-features

- `demand-grid` covers all nine schedule-demand combinations.
- `demand-fixed` preserves activity assumptions and K during arrival scaling.
- `demand-conclusion` checks whether the practical recommendation changes.

## How to get to it (user POV)

Open notebook section 7 and the section 6 probability table. The diagram and input section identify the assumptions held fixed.
Section 8 tests activity-time estimates. This is separate from the arrival test.

## Driving it with verify_notebook.py

Preconditions: uv environment ready, doctor passed, and the campus input files available.

Run the shared verification command. Inspect `demand_scenarios.csv`, `replications_raw.csv`, `spillover_probability.csv`, and `figures/demand_sensitivity.png`. Require exactly demand factors 0.8, 1.0, and 1.2 crossed with all schedules, identical seed sets, and at least 30 days each. Read the notebook's interpretation and recommendation.

The exact command is:

```bash
uv run --locked python Group8_Parking_Booth_Simulation/tools/verify_notebook.py
```

Read the action log and resulting exports from the same evidence directory. Confirm evidence remains after scratch cleanup.

## Gotchas

Demand factors scale expected rates, not exact daily counts. Uniform scaling does not move or extend the peak. Zero observed spillover days have a positive uncertainty bound. High-demand reasonableness tests are separate from the required grid.

For the timing test, inspect `activity_replications_raw.csv`,
`activity_sensitivity.csv`, `activity_paired_differences.csv`, and
`activity_replication_planning.csv`. Require nine complete cases, matching seeds,
normal arrivals, and all stated precision targets met. The scale changes all
four activities, including refusals, while keeping sticker types and K fixed.
Require the 1.0 cases to match the main normal-demand results.
