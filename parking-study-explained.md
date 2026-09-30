# Understanding the parking study

This explanation applies the
[Week 1 introduction](<materials/CSS142P_Week_01_Introduction_to_Modelling_and_Simulation - Tagged.pdf>)
to the current parking project. Page numbers below refer to that PDF.
The [branch progress report](branch-progress-report.md) records current changes,
results, requirements findings, and pending work.

## The real entrance, the model, and the simulation

Page 3 separates three ideas:

| Term | Meaning in this project |
| --- | --- |
| System | The actual campus entrance, including cars, guards, ID readers, and its operating rules. |
| Model | A description of that entrance using selected rules and assumptions. |
| Simulation | Computer experiments that apply those rules and measure what happens. |

The current model assumes one entrance stop and one ID reader. A second guard
can check the next car's sticker while the stop is occupied. That car waits
at the pre-check position until the stop is free.

The simulation generates arriving cars and activity times, applies the rules,
and records delay, queue size, guard utilization, and spillover duration.
Its results describe the assumed model. Evidence is needed to connect those
results to the actual entrance.

## The question the current program answers

The current question is:

> Under the assumed entrance arrangement and estimated inputs, how much does
> a second guard reduce delay when that guard works until 09:00 or 10:00?

The baseline has one guard all day. The alternatives add a second guard from
07:00 to 09:00 or from 07:00 to 10:00. All schedules are tested at 80%, 100%,
and 120% of expected baseline arrival demand.

Page 14 explains why the question comes first. The question determines what
needs to be represented and what numbers will help the decision-maker.
Here, campus parking management would compare the time benefit with the extra
guard-hours. A waiting-time target or cost rule would help determine which
benefit is worth that extra staffing. Neither has been specified.

## Why booths and guards cannot be used as the same term

A guard is a person. An ID reader is a device. In the submitted proposal,
each booth is an independent service position that processes a car.

Two independent booths can process two cars at the same time. Two guards
sharing one reader can divide tasks, but cars still use one final entrance stop.
The second arrangement does not automatically provide the first arrangement's capacity.

The submitted proposal describes independent booths. PR #2 changed the model
to guards sharing one reader. The group reported sticker checks before ID taps,
but that account does not confirm all the assumed resources and rules.

Page 9 explains that the same real system can have different useful models.
The guard model can be useful for its stated question. Its usefulness does not
establish that it fulfills the submitted independent-booth proposal.
The revised Markdown explains the change. It does not establish instructor acceptance.

## The parts represented by the model

Pages 4, 8, and 12 describe the parts of a simulation:

| Term | Parking example |
| --- | --- |
| Entity | One arriving car. |
| Attribute | That car's sticker status or arrival time. |
| Resource | A guard, the entrance stop, or the pre-check position. The shared ID reader is represented through the single stop's processing rules. |
| State | How many cars are on the approach and which positions are occupied now. |
| Event | A car arrives, a sticker check finishes, or a car enters or is refused. |
| Input | Arrival rates, activity-time assumptions, the staffing schedule, or K. |
| Output | Delay, maximum approach queue, guard utilization, or spillover duration. |

An input is supplied to the model. An output is calculated from what happens.
For example, the estimated sticker-check time is an input. The resulting
delay is an output. The program does not choose a delay and present it as a result.

Use [CONTEXT.md](CONTEXT.md) for the full definitions. Total delay excludes
the car's own activity time. Initial waiting ends when the first check starts.
Those two measures can differ when a car waits between processing stages.
The spillover threshold, K, is the approach-queue count selected to represent
a line reaching the street. The current K = 8 is an estimate, not a site measurement.

## What a successful notebook run proves

Page 19 separates verification and validation:

| Question | Current evidence |
| --- | --- |
| Verification: does the program follow the model's rules? | Tests, hand calculations, known-answer cases, repeated execution, and checks of the exported statistics support this. |
| Validation: does the model represent the actual entrance well enough for the decision? | Campus comparisons and confirmation of the assumed layout are limited or unavailable. Real staffing conclusions remain uncertain. |

A program can follow every selected rule while those rules describe the
actual entrance poorly. Passing tests are evidence about the implementation.
They cannot confirm the number of campus ID readers or the true arrival rates.

Validation can use observations, comparison with real data, sensitivity analysis,
and review by someone who knows the process. Field measurements are one form
of validation. The current reasonableness checks provide narrower evidence.

## Why the estimates need an explanation

Pages 6, 11, and 17 warn that conclusions depend on inputs and assumptions.
An estimated value needs a source, a reason, and an explanation of its possible effect.

The project uses estimated arrivals, activity times, refusal share, and K.
The current parameter CSV includes basis and source fields. The arrival profile
is attributed to an earlier group estimate, but its selected rates lack a
documented derivation.

The final-project guidelines allow documented synthetic data. This allows an
educational comparison under assumptions. It does not turn estimates into
measured facts or fulfill the submitted proposal's measurement commitments.

If actual activity times are longer, the actual queue could be larger.
If the entrance has two independent readers, the benefit of a second service
position could differ from this shared-reader result.

## Why the program repeats days and changes demand

Pages 15 to 17 explain repeated experiments and uncertainty.
Cars do not arrive at identical times every day. Activity times also vary.
One simulated day could therefore give a misleading result.

The main study uses 30 days for each of nine schedule-demand combinations.
Different seeds generate independent days. Within each demand level and day,
the schedules receive matching cars to make staffing comparisons fair.

A confidence interval describes uncertainty in the estimated mean from these
simulated days. It does not cover every possible error in the input assumptions.
More repeated days can improve precision without improving inaccurate inputs.

The ±20% demand test asks whether the staffing comparison changes with fewer
or more expected arrivals. It changes arrival rates while keeping other inputs fixed.
It does not test a morning peak that moves later or lasts longer.

## Why a smaller notebook can still be useful

Pages 9 and 10 recommend the detail needed for the decision and an explicit boundary.
More code, more cells, and more methods do not automatically improve a study.

Repairing the old notebook was necessary because it no longer matched the model.
Choosing exactly 22 cells was an implementation choice.
Some explanations and plots were combined or moved, while some analyses were removed.

The required schedule comparisons and demand sensitivity remain.
Activity-time sensitivity tests the estimated timings. Distribution-family and
capacity sensitivity remain outside the active notebook. They test other
uncertain assumptions. The progress report records those losses and
unfinished commitments. Cell count alone cannot establish whether coverage is sufficient.

## How the findings guide the next work

The next work has two purposes:

- Resolve how the final study addresses the difference between independent
  booths and shared-reader guards. Describe any retained revision accurately.
- Correct the required report structure, citations, input explanations, and
  claims that exceed the evidence. Then refresh the delivery package and rehearse.

Morning results can help explain the targeted staffing benefit.
Additional sensitivity analyses can strengthen the study, but the course does
not require every removed analysis or another simulation method.

The current numerical results compare the schedules under the chosen assumptions.
Whether the same recommendation applies to the real entrance depends on how well
those assumptions represent that entrance.
