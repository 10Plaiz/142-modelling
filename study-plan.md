# Parking study: organization and presentation plan

See [branch-progress-report.md](branch-progress-report.md) for results, execution
evidence, and remaining human review. This plan defines the study's organization;
it is not evidence of instructor approval.

## Document roles

| Item | Role |
| --- | --- |
| [Submitted proposal](materials/Modeling_Proposal.pdf) | Unchanged record of the proposal reviewed by the professor. |
| [Proposal format](materials/CSS142P_Final_Project_Proposal_Format.pdf) | Required proposal structure and input justification. |
| [Project requirements](materials/CSS142P_Final_Project_Requirements_and_Guidelines.pdf) | Deliverables, experiment, evidence, and presentation requirements. |
| [Revised proposal](<Modeling Proposal.md>) | Describes the implemented study and discloses changes from the submission. |
| [PR #2 progress report](progress-report.md) | Historical explanation of the shared-reader revision. |
| [Terminology](CONTEXT.md) | Common definitions across the proposal, notebook, and slides. |
| [Branch progress report](branch-progress-report.md) | Current completion status and findings in plain language. |

The professor's comment, supplied by the user:

> Compare one booth, two booths from 7–9 AM, and two booths from 7–10 AM. Use the existing data and test arrival demand at ±20%.

## Study boundary

Retain PR #2's assumed shared-reader entrance. Compare one guard all day, an
additional guard until 09:00, and an additional guard until 10:00. Each runs at
80%, 100%, and 120% expected arrival demand. Keep activity distributions,
refusal share, queue definition, and K fixed during that demand comparison.

The study uses the existing estimated input CSVs without changing their values.
They are not the field measurements promised in the submitted proposal.
The friend's description supports the check-then-tap sequence, but does not
establish one reader or the particular advance-check policy.

The user approved proceeding with disclosed assumptions because professor
clarification was unavailable before presentation. No clarification request is
a prerequisite for the local implementation. Acceptance of the academic-scope
revision remains unknown.

## Reading order

The notebook uses this reading order:

| Section | Reader's question |
| --- | --- |
| Question and scope | What staffing decision are we comparing, and what changed from the submission? |
| Assumed entrance | What do the cars, guards, stop, reader, and pre-check position do? |
| Inputs and measures | Where did the numbers come from, and what does each output mean? |
| Checks and experiment | Does the program follow its rules, and how are the scenarios compared fairly? |
| Results and uncertainty | How large is the benefit, and how much do simulated days vary? |
| Demand sensitivity | Does the comparison change with 20% fewer or more expected arrivals? |
| Activity-time sensitivity | Does the comparison change when all activities take 20% less or more time at normal arrivals? |
| Recommendation and limits | What decision does the conditional evidence support, and what is still unknown? |

## Experiment and reporting rules

- Run at least 30 independent days per schedule-demand combination. Match cars
  and activity draws across schedules within a day and demand level.
- Record seeds, replication counts, controlled inputs, means, standard
  deviations, and 95% confidence intervals.
- Show paired alternative-minus-baseline differences and their uncertainty.
  Report the extra scheduled guard-hours beside the time saving.
- Distinguish total delay from initial waiting. Report delay in seconds,
  queue in cars, utilization as a fraction or labelled percentage, and
  spillover duration in minutes.
- Define spillover as approach count at least K, including the pre-check car.
  Treat K and the physical layout as assumptions.
- Distinguish checking the code from validating the campus model. Do not call
  estimates measurements or zero observed spillover zero risk.
- Keep older booth-study exports out of current result tables and slides.

The notebook records achieved precision for all nine combinations. Extra
public-data proxy analysis, a fluid approximation, and a broad headroom sweep
are outside the current presentation's evidence. Retained helper code does not
mean those analyses were completed.

## Completed sequence

1. Agreed the study direction and terminology on a feature branch.
2. Set up Python 3.12 with uv, an isolated environment, and a dependency lockfile.
3. Rebuilt the notebook and ran it in a fresh kernel with isolated output paths.
4. Verified the checks, nine combinations, precision, summaries, and input hashes.
5. Updated the revised proposal and generated the report, slides, and notes.
6. Created and proved the small `verify-notebook` skill against the working study.

## Presentation and handoff

Aim for eight minutes of explanation and two minutes of demonstration, followed
by questions. The speaker notes include explanations of estimates, repeated
days, confidence intervals, and the change from booths to guards.

Use the executed notebook for demonstration. Reproduction instructions live
in [the study README](Group8_Parking_Booth_Simulation/README.md). Review the branch
before committing or opening a PR. A local submission package is preparation,
not an external submission or evidence of instructor approval.
