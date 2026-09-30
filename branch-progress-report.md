# Progress report: preparing the parking study for presentation

Branch: `feature/parking-presentation-ready`  
Updated: 30 September 2026

The notebook runs from beginning to end in a reproducible Python environment.
Its tables and figures come from the same verified notebook experiment.
The report, slides, notes, and ZIP retain their earlier versions.
The core experiment meets the general course minimums. Full conformity with the
submitted proposal and final submission instructions is not established.

For an explanation without programming knowledge, read
[Understanding the parking study](parking-study-explained.md).
It applies the Week 1 lessons to this project. Use [CONTEXT.md](CONTEXT.md)
for the terms used throughout the study.

## Current status

| Area | Status and meaning |
| --- | --- |
| Program execution | Passed. All 13 code cells in the 24-cell notebook executed. The initial rewrite had 22 cells. |
| Main experiment | Complete. Three schedules and three demand levels, with 30 days per combination, give 270 main-study days. |
| Calculations and checks | Passed. All 30 recorded checks and stated precision targets passed. The verifier recalculated the core, supplementary, and activity-test statistics. |
| Current revised proposal | Input-source wording and supplementary-statistics claims now match the notebook. Academic acceptance remains unresolved. |
| Submitted proposal and professor's comment | Partly aligned. The time windows and demand factors match, but shared-reader guards differ from independent booths and estimates replace planned measurements. |
| Report and citations | Need correction. Required report sections are combined, and references lack a consistent recognized citation style. |
| Real entrance and instructor acceptance | Not established. The assumed layout has limited supporting evidence. Field validation and acceptance of the revision remain unknown. |
| Delivery package | All six required material types are present and ZIP integrity passed. Its progress report is stale. |

A correct program can test an unsuitable description of the real entrance.
The Week 1 explanation separates those questions. Neither a passing run nor an
updated proposal proves that the professor accepted the changed study.

## Completed notebook improvement

The agreed scope focused on the notebook and supporting repository files.
It excluded report formatting, slides, speaker notes, and ZIP updates.

- Revised explanations use short sentences and the terms in `CONTEXT.md`.
- The input table identifies estimates, known origins, and missing justification.
- Morning delay and initial waiting now have means, SDs, n, confidence intervals,
  and paired comparisons. A figure compares morning and all-day delay.
- Activity-time sensitivity scales all four activities to 80%, 100%, and 120%
  at normal arrival demand. It uses the existing model helper and precision rule.
- The main experiment has 270 days. The timing table has 270 rows, including
  90 reused normal cases. The timing test adds 180 simulated days.
- The final interpretation shows time benefits and extra guard-hours. It no
  longer presents A as a uniquely preferred staffing choice.
- Notebook execution and verification are separate from PDF generation.
  Publication updates the notebook, result tables, and figures.

The [improved run](artifacts/notebook-verification/20260929T234315-3yjoyvt2/manifest.json)
passed all 30 checks. Both experiments met precision targets with 30 days per case.
The verifier recalculated interval statistics and rejected deliberately corrupted
means and duplicate rows. The three changed figures were visually inspected.

The README documents describe file purposes and reproduction commands.
Temporary work status belongs in this report. The repository's existing paths
are mapped to the course's recommended deliverable types without relocating files.
Presentation artifacts and the ZIP were excluded from publication.

## Starting point and decision reasons

[PR #2's progress report](progress-report.md) is a historical handoff, not the
current status. It describes work that was later merged as `19c04cb`.
Its statements about uncommitted files describe that earlier working session.
This branch starts from that merged revision and leaves the handoff unchanged.

PR #2 had already added schedules A, B, and C, estimated inputs, and the
shared-reader model. This branch did not introduce schedule C or replace the
gate model. Its first task was to make the notebook use the model already merged.

| Decision | Reason and review evidence |
| --- | --- |
| Keep PR #2's event rules and campus input values | Repairs the notebook mismatch without silently redesigning the entrance. The model diff adds input checks and measures, not new gate operations. Both campus CSVs match the branch starting point. The assumed layout remains unconfirmed. |
| Repair obsolete notebook calls and archive old exports | The old notebook required removed functions and unavailable measurement files. Current results must come from the current model. Historical outputs remain available for comparison, not validation. |
| Use uv and a locked Python 3.12 environment | The repository lacked a consistent environment. The lockfile records dependencies used by the successful execution. It does not prove installation on another computer. |
| Run the notebook in an isolated fresh kernel | Saved outputs cannot prove that Run All works. The runner preserves execution evidence and checks exports before optional publication. The verification skill describes how to use that runner. |
| Keep schedules A, B, and C with arrival demand at 80%, 100%, and 120% | These match the requested time windows and demand factors. They do not settle the independent-booth versus shared-reader difference. |
| Add morning results and initial-wait intervals | The extra staffing targets the morning. All-day averages can hide its benefit. Initial waiting also distinguishes waiting before the check from total delay between activities. |
| Add a separate activity-time sensitivity test | Activity times are estimates. Scaling them by ±20% tests that uncertainty without changing the required arrival comparison. Reusing normal cases avoids duplicate simulation. Distribution-family and capacity tests remain outside this scoped improvement. |
| Remove fitting and field-comparison claims without observations | Estimated means and SDs are not stopwatch samples. Old generated records are not independent campus observations. The notebook explains assumed distributions and validation limits instead. |
| Report benefits and guard-hours without choosing a unique optimum | No agreed waiting target or cost rule establishes whether fractions of a second justify extra staffing. The results support a conditional tradeoff, not a proven best schedule. |
| Separate notebook verification from document generation | PDF generation is not needed to verify the notebook. The approved improvement excluded report formatting, slides, notes, and ZIP refreshes. Earlier artifacts remain unchanged. |
| Keep stable file descriptions in README documents | Reproduction commands and file purposes belong there. Temporary status, decisions, and unresolved work belong in this branch report. |

The cell reduction was an implementation choice, not a course requirement.
The review below records what was retained, removed, and later restored.
The latest sticker-and-ID clarification was deferred. This cleanup does not
change admission rules or add invalid-ID cases.

## Study question and assumed entrance

The current study asks how much a second guard reduces delay, and whether that
guard should stay until 09:00 or 10:00, under the stated entrance and input assumptions.

| Schedule | Staffing | Scheduled guard-hours |
| --- | --- | --- |
| A | One guard from 07:00 to 19:00. | 12 |
| B | A, plus a second guard from 07:00 to 09:00. | 14 |
| C | A, plus a second guard from 07:00 to 10:00. | 15 |

Each schedule uses 80%, 100%, and 120% of expected baseline arrival demand.
A replication is one repeated simulated operating day. Different seeds produce
independent days. Matching cars within a day make schedule comparisons fair.

The model assumes one entrance stop and one shared ID reader. While a car
occupies the stop, guard 2 can check the next car's sticker. The checked car
holds its pre-check position until the stop is free. A car without a sticker
is refused and turns out. These operating rules are assumptions.

A booth is a hut or service station. In the submitted proposal, each booth
processes a car independently. A guard is a person, and an ID reader is a device.
Two guards do not automatically create two independent entrances.

## Proposal, professor's comment, and implementation

| Record | What it says and how it relates to the current study |
| --- | --- |
| [Submitted proposal](materials/Modeling_Proposal.pdf) | Describes independent booths and plans gate records, stopwatch timings, fitted processing-time distributions, and measured approach capacity. Preserve it as the record reviewed by the professor. |
| Professor's comment | Requests one booth, two booths from 07:00 to 09:00, and two booths from 07:00 to 10:00, with existing data and ±20% arrival demand. The requested time windows and demand factors are implemented. |
| Group's entrance description | Reports sticker checks before drivers tap IDs. It does not confirm the number of readers or every operating rule. |
| PR #2, commit `19c04cb` | Adopted one stop, one reader, and a second guard checking the next car. Its [progress report](progress-report.md) records the revision. Python and proposal changes left the notebook and saved results using the older study. |
| This branch | Repairs that mismatch while retaining PR #2's event rules. No campus input values were changed. Older generated records are not treated as real observations. |
| [Revised proposal](<Modeling Proposal.md>) | Describes the implemented model and discloses changes from the submission. It does not establish acceptance of those changes. |

The reported professor's comment was:

> Compare one booth, two booths from 7–9 AM, and two booths from 7–10 AM. Use the existing data and test arrival demand at ±20%.

Shared-reader guards are not equivalent to independent booths. The current CSVs
are unchanged from PR #2, so the branch reuses the repository's existing inputs.
That does not establish what the professor meant by "existing data."
Professor clarification was unavailable before presentation.

## Review against course instructions

The review compared the course PDFs, submitted and revised proposals, current
notebook and model, generated PDFs, CSV results, and local delivery package.

| Requirement or concern | Finding |
| --- | --- |
| General experiment scope | Meets the core minimums in the [project guidelines](materials/CSS142P_Final_Project_Requirements_and_Guidelines.pdf), page 2: one main discrete-event method, one baseline and two alternatives, measurable indicators, at least 30 replications per scenario, and sensitivity analysis. |
| Conceptual model and analysis | Diagram, assumptions, numerical comparisons, uncertainty plots, sensitivity, checks, and a conditional recommendation are present. |
| Report structure | Page 3 requires separate named sections. The generated report combines problem, boundary, and inputs; method, experiment, and checks; and validation, recommendation, and limits. Reorganize the existing content. |
| Citations | Page 3 requires one recognized citation style and credit for external sources and methods. Filenames and bare documentation URLs do not satisfy that requirement. |
| Input defensibility | Documented synthetic data is allowed on page 2. The [proposal format](materials/CSS142P_Final_Project_Proposal_Format.pdf), page 4, also requires inputs that can be observed or defended. Estimates need reasons and sources. |
| Arrival profile | The PR #2 progress report attributes it to a Study B group estimate, about 214 morning arrivals and 402 daily arrivals. Its 48 selected rates lack a documented derivation. The CSV contains times and rates, not basis or source columns. |
| Revised proposal claims | The review found overstated source and supplementary-statistics claims. The source wording is corrected. Supplementary tables now contain means, SDs, n, and intervals. |
| Proposal authority | Proposal Format page 5 says the approved proposal becomes the final-report specification. Disclosing departures is necessary but does not establish approval. |
| Revised proposal format | It uses the supplied field-table approach but lacks the exact section headings from page 1 and changes the "Members (full names)" label. Exact headings and labels would remove ambiguity if this revision is submitted. |
| Required package | All six deliverable types and the required filename pattern are present. The suggested folder layout is recommended, not mandatory. |
| Presentation | Slides and notes cover the study. A slide refers to results on the "next slides" although those results appear earlier. Rehearsal and the live demonstration remain pending. |

The course requires one sensitivity analysis, not every analysis from the old
notebook. The ±20% demand experiment meets that general minimum. Fluid modelling,
SFpark tests, additional sensitivity analyses, and a particular cell count are
not general course requirements. Earlier proposal commitments remain a separate
alignment question.

## What changed on this branch

| Change | Purpose or limit |
| --- | --- |
| Added uv configuration, Python 3.12 selection, and `uv.lock` | Recreates consistent dependencies. The local `.venv` contains installed tools and stays out of Git. Another computer recreates it rather than copying it. |
| Rebuilt the notebook | Uses the current model and all nine combinations. Reports means, variability, confidence intervals, paired differences, sensitivity, and limitations. |
| Added input rejection and supplementary measures | Rejects invalid values and reports initial waiting and effective guard-hours. Core PR #2 event rules remain in place. |
| Added the notebook verification runner and skill | Executes the actual notebook, preserves evidence, and checks exports. It does not introduce another simulation. |
| Generated presentation materials | An earlier branch pass produced a nine-page report, nine-page slide deck, and speaker notes from that pass's results. They do not include the latest notebook additions. Report and slides are required deliverables; automatic generation is an implementation choice. |
| Updated project documents | Aligns the revised proposal, instructions, and study plan with the implemented experiment. Reference PDFs are under `materials/`. |
| Preserved historical exports | Older files remain under `Group8_Parking_Booth_Simulation/archive/pre-presentation/`. They must not be mixed with current results. |
| Prepared a local ZIP | Includes reproduction files and verification evidence. Its progress report needs refreshing after document changes. |

The agreed branch workflow included environment setup, notebook repair,
verification, aligned documentation, and creation of the verification skill.
uv and that skill are workflow choices, not course requirements.
Run logs, input hashes, executed notebooks, and archived exports support review.
Unrelated notes and course materials were not edited.

## Review of the notebook reduction and implementation choices

The reduction review compared the earlier notebook at `19c04cb`, proposal
commitments, model helpers, and preserved evidence. That review did not run a
new simulation. The later requirements review included a fresh execution.

Repair was necessary. Reducing the notebook to exactly 22 cells was not.
The older notebook called obsolete model functions and expected unavailable
gate logs, stopwatch samples, and site measurements.

The old version had 26 code cells and 26 explanation cells. The initial rewrite
had 12 code cells and 10 explanation cells. Its notebook code went from 430 to 323
lines, with some plotting moved into `tools/build_presentation.py`.
Cell count alone does not measure how much analysis was retained.

| Area | Retained, adapted, removed, or unfinished |
| --- | --- |
| Three schedules and ±20% demand | Retained. All nine combinations have 30 simulated days each. |
| Intervals, paired differences, and the extra-hour comparison | Retained. B to C remains compared at each demand level. |
| Replication planning and checks | Adapted and expanded. The initial rewrite passed 27 checks. The current notebook passes 30 checks and both experiments' precision targets. |
| Fitting stopwatch distributions | Removed because samples are unavailable. Estimated moments are not observed samples to fit. |
| Real queue comparison | Removed the old setup. No completed field validation was lost. Real observations remain unavailable. |
| Processing-time, distribution-family, and capacity sensitivity | Removed in the initial rewrite. The improvement restores a focused activity-time test. Distribution-family and capacity sensitivity remain outside the active notebook. |
| Fluid comparison and numerical step-size checks | Removed. These supplied an extra cross-check. The old booth-based version would need adaptation. |
| Morning results | Initially kept only in raw outputs. The improvement adds notebook summaries, intervals, paired comparisons, and a figure. Presentation coverage remains unchanged. |
| Wider headroom sweep and SFpark arrival test | Unfinished PR #2 proposal commitments, not completed sections removed from the 52-cell notebook. High-demand and slow-reader checks do not replace them. |

Other choices needing review remain recorded:

- The initial verification workflow required PDF generation. The notebook
  improvement removes that coupling.
- `CLAUDE.md` received a broad rewrite. Correcting outdated commands and model
  descriptions did not require replacing the whole guidance document.
- The earlier draft retained A without an agreed waiting target or cost rule.
  The improved interpretation reports the tradeoff without a uniquely preferred schedule.

The initial reduction remains part of the review record. The improved notebook
has 24 cells. Activity-time sensitivity and morning uncertainty are now included.
Distribution-family sensitivity, capacity sensitivity, and an adapted fluid
comparison remain optional additions. They need a reason tied to the study
question and separate verification. They are not completed work or general
course requirements.

## Verification evidence

The current notebook matches the
[30-check run](artifacts/notebook-verification/20260929T234315-3yjoyvt2/manifest.json).
That run executed all 13 code cells and verified the main and activity-time
experiments. Its generated tables and figures match the published files.
Model, input, and rendering-helper hashes stayed unchanged during the notebook
improvement. The earlier PDFs, notes, and ZIP also stayed unchanged.

Evidence directories are local and ignored by Git. The counts and findings in
this report remain reviewable in Git; the full logs require the local evidence
or a new run using the reproduction command below.

The earlier [published run](artifacts/notebook-verification/20260929T213055-vmthhbvy/manifest.json)
passed 27 checks. The
[later review run](artifacts/notebook-verification/20260929T222419-zzw4uw8z/manifest.json)
also passed, without publishing replacements.

Every code cell executed in the later run. All nine combinations completed with
30 days each. Precision targets passed. Fresh raw runs, summaries, paired
differences, and check tables matched the published files. Input hashes and
canonical notebook and model source hashes stayed unchanged during that review.

Checks cover hand-calculated examples, invalid-input rejection, empty demand,
vehicle accounting, FIFO order, queue-area accounting, closing rules, matching
inputs, per-car Lindley calculations, known-answer queue benchmarks, and extreme
demand or a slow reader. Independent recalculation confirmed all 36 core summary
rows and all 36 paired rows, including Bonferroni intervals.

Figures decode. Both PDFs open as nine-page documents. Representative pages were
visually inspected. Logs, executed notebooks, HTML, CSVs, figures, and PDFs survive
cleanup of scratch directories and kernels.

Verification supports the program's rules and calculations. Field validation
remains unavailable. Simulation intervals do not account for all input uncertainty.
Installation on another computer and the live presentation have not been verified.
The local decision log remains unfinished and is not a completed audit record.

## Results and their limits

At normal estimated demand, the existing raw results show:

| Schedule | Mean all-day delay | Mean delay for 07:00 to 10:00 arrivals | Extra scheduled guard-hours versus A |
| --- | --- | --- | --- |
| A | 2.57 seconds | 3.98 seconds | 0 |
| B | 1.80 seconds | 2.54 seconds | 2 |
| C | 1.70 seconds | 2.35 seconds | 3 |

B saves about 0.77 seconds per car across the day. C saves about 0.87 seconds.
Extending B to C saves about 0.10 seconds. Its paired 95% interval for C minus B
is approximately -0.13 to -0.08 seconds. The largest mean delay across the nine
combinations is 3.21 seconds.

Morning values average the daily morning means in
[the raw table](Group8_Parking_Booth_Simulation/results/replications_raw.csv).
They come from existing main-experiment outputs. The improved notebook reports
their uncertainty in supplementary tables. All-day averages
can reduce the apparent size of a morning staffing benefit.

No spillover occurred in the main sample. For zero events in 30 days, a
combination's 95% Wilson upper probability limit is about 11.35%. Zero observed
events do not prove zero risk.

The earlier draft retained A under the estimated inputs. The improved notebook
reports the staffing tradeoff without choosing an unsupported optimum. Additional
staffing saves time, but no acceptable waiting target, wages, or financial rule
establishes which benefit justifies the extra guard-hours. The draft is not a
uniquely determined optimum or a conclusion approved by the group.

Measurement definitions remain explicit:

- Total delay excludes the car's own activity time and includes waiting between stages.
- Initial waiting ends when the first sticker check starts. Supplementary tables report its mean, variability, intervals, and paired differences separately.
- The approach queue includes a car at the pre-check position and excludes the entrance stop.
- Spillover duration uses the estimated threshold K = 8. It is not observed street blockage.
- Guard utilization counts active checks and refusals, not reader occupancy or physical presence.

The model cannot prove real-campus staffing needs, actual congestion, complaints,
or wage savings. Uniform demand scaling also does not test a later or longer peak.

## Next work and presentation preparation

These tasks remain pending. This document update does not implement them.

1. Resolve how the final study addresses the booth-versus-guard difference.
   A literal independent-booth comparison needs a different model. Keeping the
   current study requires an explicit revision statement, not a claim of acceptance.
2. Correct report section order and citations. Explain input estimates and their
   known sources without inventing measurements or a derivation.
3. Refresh the ZIP after accepted changes. Review names, submission details,
   slides, and demonstration timing. Review branch changes before a future PR.

For rehearsal, open the
[speaker notes](Group8_Parking_Booth_Simulation/presentation/talk-track.md),
[slides](Group8_Parking_Booth_Simulation/presentation/Parking_Study_Presentation.pdf),
[report](Group8_Parking_Booth_Simulation/presentation/Parking_Study_Report.pdf),
and [executed notebook](Group8_Parking_Booth_Simulation/Parking_Booth_Simulation.ipynb).
Explain the question, entrance, inputs, checks, results, and limitations in that order.
Keep the executed notebook available if a live rerun takes too long.

Reproduction from the repository root uses:

```bash
uv sync --locked
uv run --locked python Group8_Parking_Booth_Simulation/tools/verify_notebook.py
```

The existing
[delivery ZIP](artifacts/submission/CSS142P_FinalProject_8_ParkingEntrance.zip)
has passed integrity checking and includes the report, model, inputs, results,
presentation, README, reproduction files, and published verification evidence.
It excludes the virtual environment, historical result archive, and unrelated
notes or lecture handouts. It predates these report updates and the new explanation.
The package has not been rebuilt or tested by execution after extraction.

## Local cleanup and review scope

The cleanup records completed branch work in scoped local commits. It does not
push the branch, open a PR, submit files, or refresh generated outputs.
Commit history separates environment and model support, the executable notebook
and its evidence files, earlier presentation artifacts, and project documentation.

User-supplied course materials, `Final_Project_Guidelines.md`, and the unrelated
diagram files remain untouched and uncommitted. Documents link to those local
reference materials, so a checkout without them will not contain every source
used in the review. Including those references is a separate repository decision.
The ignored `.venv`, execution evidence, local ZIP, and unfinished decision log
remain local. No unfinished decision-log cleanup is included.

Before committing, the cleanup rechecked the current saved exports with the
verifier and compared them with the successful run's hashes. All checks passed.
Both input CSVs also matched PR #2. All 11 retired tracked exports had exact
copies in the historical archive. Local document links resolved, and
`git diff --check` passed. This was an export and preservation check, not a new
simulation run. No model or notebook source changed during cleanup.
