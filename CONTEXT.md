# Parking entrance terminology

These terms distinguish the people, equipment, and measurements in the parking
entrance study. Definitions do not establish the actual gate layout or staffing.

The study terms follow the
[Week 1 introduction](<materials/CSS142P_Week_01_Introduction_to_Modelling_and_Simulation - Tagged.pdf>),
with examples from this project. Read
[Understanding the parking study](parking-study-explained.md) for the longer
explanation and [the branch progress report](branch-progress-report.md) for status.

## Language

### Study basics

**System**:
The actual campus parking entrance, including cars, guards, equipment, and their interactions.
_Avoid_: Treating the simulated entrance as the actual entrance.

**Model**:
A selected description of the entrance using rules and assumptions to answer a decision question.
_Avoid_: Treating every model rule as a confirmed campus fact.

**Simulation**:
Computer experiments on the model that produce estimates of entrance performance.
_Avoid_: Treating simulated results as direct observations of the campus.

**Decision question**:
The staffing choice the study informs, using measures of delay and queueing under stated conditions.
_Avoid_: Describing the entrance without naming the choice being compared.

**System boundary**:
The parts and time period represented by the model, with explicit exclusions such as parking-space availability and exit traffic.
_Avoid_: Assuming that every part of campus parking is represented.

**Assumption**:
A selected rule or condition used to describe the entrance, such as the shared-reader arrangement or an empty start.
_Avoid_: Presenting a provisional choice as a confirmed fact.

### Parts of the model

**Entity**:
One car represented in the entrance model.
_Avoid_: Using a car and a guard as interchangeable entities in this study.

**Attribute**:
A value describing a car, such as its sticker status or arrival time.
_Avoid_: Confusing a car's attribute with the state of the whole entrance.

**Resource**:
A person, position, or device with limited capacity that cars must share, such as a guard or entrance stop.
_Avoid_: Assuming that another guard provides another entrance stop or ID reader.

**State variable**:
A value describing the entrance now, such as the approach-queue count or whether the entrance stop is occupied.
_Avoid_: Treating a changing state as a fixed input.

**Event**:
An occurrence that can change the entrance state, such as a car arrival, check completion, entry, or refusal.
_Avoid_: Treating an event as a duration such as an activity time.

**Input**:
A value or policy supplied to the model, such as arrival rates, activity-time assumptions, K, or a staffing schedule.
_Avoid_: Calling a calculated delay an input.

**Input estimate**:
An input value based on judgment or an approximate source, rather than an established measurement for this entrance.
_Avoid_: Calling an estimate collected campus data.

**Output**:
A result calculated from simulated behavior, such as delay or maximum approach queue.
_Avoid_: Treating an output as proof that the selected inputs are accurate.

**Performance measure**:
A numerical output used to compare staffing alternatives, with a stated unit and calculation.
_Avoid_: Using an undefined label such as "efficiency."

### Entrance components

**Booth**:
A physical hut or service station at an entrance. In the submitted proposal,
each modelled booth is an independent position that processes one car at a time.
_Avoid_: Using booth as another name for guard or ID reader.

**Guard**:
A person who checks parking stickers and handles refusals.
_Avoid_: Treating the number of guards as the number of independent entrances.

**ID reader**:
The device at which a driver taps an ID before entry.
_Avoid_: Using reader as another name for guard or booth.

**Entrance stop**:
The position occupied by a car during its final entrance processing.
_Avoid_: Assuming each guard has a separate entrance stop.

**Pre-check position**:
The position before the entrance stop where a guard can check a car's sticker.
_Avoid_: Calling this a second independent booth.

**Approach queue**:
Cars on the approach before the entrance stop, including a car at the pre-check
position in the current model. It excludes the car at the entrance stop.
_Avoid_: Calling all of these cars idle; a car can be receiving a sticker check.

### Time and queue measures

**Activity time**:
Time spent on the car's sticker check, ID tap and barrier operation, move-up,
or refusal, as applicable.
_Avoid_: Including time spent waiting for access to a position.

**Delay**:
Time from a car's arrival to its departure minus its own activity time.
_Avoid_: Treating this as identical to waiting before the first check.

**Initial waiting time**:
Time from arrival until the car's processing first starts. This is the waiting
measure described in the submitted single-stage booth proposal.
_Avoid_: Substituting total delay without stating the changed definition.

**Spillover threshold, K**:
The approach-queue count at which the study defines the line as reaching the
street. The chosen count and whether spillover starts at that count must be explicit.
_Avoid_: Presenting an estimated K as a measured road dimension.

**Spillover duration**:
The total time the approach queue meets or exceeds the chosen spillover threshold.
_Avoid_: Treating simulated spillover as an observed street blockage.

### Staffing and demand

**Staffing schedule**:
The number of guards or independent service positions available over the day,
with the resource named explicitly.
_Avoid_: Using an unqualified label such as "two servers" in the presentation.

**Demand level**:
The expected number of arriving cars relative to the study's baseline arrival
profile. The required levels are 80%, 100%, and 120% of that profile.
_Avoid_: Describing a 20% demand increase as a 20% increase in processing time.

**Guard utilization**:
Active sticker-check and refusal time divided by available guard-time for the
stated schedule, including time needed to finish final guard activity after closing.
_Avoid_: Calling this reader occupancy or booth utilization.

**Guard-hours**:
The sum of scheduled working hours across the guards. The proposed schedules
contain 12, 14, and 15 guard-hours before any overtime.
_Avoid_: Presenting guard-hours as a monetary cost without a wage assumption.

### Experiments and evidence

**Scenario**:
One set of conditions being tested, combining a staffing schedule and a demand level in the main study.
_Avoid_: Calling a schedule alone one of the nine complete study combinations.

**Run**:
One execution of the model under stated conditions. In the main experiment, a run represents one operating day.
_Avoid_: Calling one simulated day the whole experiment.

**Replication**:
An independent repeat under the same scenario conditions, used to measure variation between simulated days.
_Avoid_: Treating matching-input runs across different schedules as independent replications of one scenario.

**Experiment**:
A planned comparison of scenarios using repeated runs and consistent performance measures.
_Avoid_: Treating one run as enough evidence for a random system.

**Verification**:
Evidence that the program follows the model's rules and calculates its results correctly, using tests, traces, and known answers.
_Avoid_: Treating passing program checks as proof that the model matches the campus.

**Validation**:
Evidence that the model represents the actual entrance well enough for its intended decision, using data comparisons, sensitivity analysis, or knowledgeable review.
_Avoid_: Treating a declared assumption or a successful run as sufficient validation.
