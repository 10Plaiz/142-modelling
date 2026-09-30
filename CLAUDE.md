# Project guidance

The working project is `Group8_Parking_Booth_Simulation/`. It models assumed
guards sharing one ID reader. The three schedules use one guard all day and
a second guard until 09:00 or 10:00. See `CONTEXT.md` for terminology.

## Reproduction

From the repository root:

```bash
uv sync --locked
uv run --locked python Group8_Parking_Booth_Simulation/tools/verify_notebook.py --doctor
uv run --locked python Group8_Parking_Booth_Simulation/tools/verify_notebook.py
```

The verifier runs the actual notebook in isolated scratch space, checks outputs,
and retains evidence under `artifacts/notebook-verification/`. Use `--publish`
to refresh working exports only after a passing run. Previous generated exports
are preserved in `Group8_Parking_Booth_Simulation/archive/pre-presentation/`.

For interactive use, launch the notebook with `uv run --locked jupyter lab`
from the repository root and use the project .venv kernel. The notebook's working
directory is `Group8_Parking_Booth_Simulation/`.

## Model and evidence

- All campus inputs are estimates. Preserve input values, basis, and sources
  unless an approved task changes them. No field validation is available.
- The single reader, pre-check rule, refusal path, and empty start are assumptions.
- A car can have a check, ID tap and barrier activity, move-up, or refusal.
- Total delay and initial waiting are different measures. Internal time is minutes;
  displayed delays are seconds.
- The approach queue includes the pre-check position and excludes the entrance stop.
- Guard utilization counts checks and refusals. Stop occupancy is a separate measure.
- Guard 2 starts no new check at or after closing and finishes activity in progress.
- Independent random streams drive arrivals, sticker status, and activities.
  Keep each day's cars identical across staffing schedules.
- The main experiment has nine combinations: three schedules and 80%, 100%, or
  120% arrival demand. Other assumptions stay fixed in that comparison.
- All reported tables, figures, PDFs, and conclusions must come from the same
  final experiment. Historical archived outputs are not current evidence.

## Documents

`materials/Modeling_Proposal.pdf` is the original submitted proposal. `Modeling Proposal.md`
describes the revised study and discloses model, input, and measure changes.
Instructor acceptance of those changes is not established. The user cannot
seek clarification before presentation, so this is recorded as a limitation,
not a prerequisite for local work.

`branch-progress-report.md` records this branch's work. `progress-report.md`
is the historical PR #2 handoff. `study-plan.md` records the organization plan.

No model tests, public-data downloads, or mathematical cross-checks count as
passed without actual execution evidence. The optional SFpark and fluid helpers
are retained but do not establish the current study's conclusions.
