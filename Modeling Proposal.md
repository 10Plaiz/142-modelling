# Final project proposal: revised study

CSS142P Modelling and Simulation | Group 8 | Mapúa University

This revision describes the study prepared for presentation on 30 September 2026.
The submitted [Modeling_Proposal.pdf](materials/Modeling_Proposal.pdf) remains the original
submission record. Instructor acceptance of the changes below is not established.
Professor clarification was unavailable before presentation.

| Field | Entry |
| --- | --- |
| Working title | Staffing comparison for an assumed shared-reader parking entrance at the Mapúa University Makati campus |
| Group number | 8 |
| Members, full names | Ariola, Jon Luigi Bauza, Xyrelle John Caliliw, Marl Zeldrix Jimenez, Justine Leee |
| Date | Submitted 14 September 2026; revised 30 September 2026 |
| The system in one line | Cars queue for a sticker check and ID tap; one reader admits cars individually, while an optional second guard checks the next car ahead. This entrance arrangement is assumed. |
| Part 1: problem and decision | The decision is which guard schedule offers a useful reduction in delay and queueing under the stated entrance and input assumptions. Compare A, one guard all day; B, a second guard from 07:00 to 09:00; and C, a second guard from 07:00 to 10:00. Repeat each at 80%, 100%, and 120% arrival demand. Report the benefit alongside 12, 14, and 15 scheduled guard-hours. No observed street blockage, complaints, wage saving, or confirmed staffing shortage is claimed. Campus parking management is the intended decision-maker. |
| Part 2: entities | Cars seeking entry. Each has an arrival time, sticker status, and its own check, tap, move-up, and refusal times. For example, a car arrives at 07:42, waits, has its sticker checked, taps its ID, and enters. A car without a sticker is refused. |
| Part 2: resources | One entrance stop and one ID reader. An optional pre-check position holds one car ahead of the stop. Guard 1 works 07:00 to 19:00. Guard 2 works only until 09:00 in B or 10:00 in C. Guard 2 checks only while the stop is occupied. The pre-checked car keeps its position until the stop becomes available. |
| Part 2: arrivals | A Poisson process with a rate constant within each 15-minute interval. Rates come from the current estimated arrival profile, approximately 100 cars/day with a peak of 25/hour, consistent with a basement lot of under 100 slots where most cars park all day. The demand comparison scales these rates only; other inputs remain fixed. |
| Part 2: run start and stop | One operating day starts empty at 07:00. Arrivals stop at 19:00. Remaining cars finish processing. This is a terminating study with no discarded warm-up. A second guard finishes its active check or refusal after closing but starts no new check at or after closing. |
| Part 2: out of scope | Parking-space availability, exit traffic, drivers declining to join or leaving the queue, reader breakdowns, and financial hiring costs. Every admitted car is assumed to find a space. |
| Part 3: model type | Discrete-event simulation using SimPy. |
| Part 3: why this type fits | Queue counts and occupied positions change at arrivals, check completions, entry or refusal, and resource transitions. Random arrivals and activities produce different days. The model tracks these events, rather than updating every car at fixed time steps. Waiting and delay are calculated outputs, not sampled inputs. |
| Part 4: measures, units, computation | Average total delay, seconds: mean departure minus arrival minus the car's own activity time. Maximum approach queue, cars: largest approach count during each day, including the pre-check position but excluding the car at the stop. Guard utilization, fraction: total active check and refusal time divided by available guard time, including completion of final guard activity after scheduled closing. Spillover duration, minutes: total time the approach count is at least K, with estimated K = 8. Initial waiting, seconds, is supplementary: arrival until the first check starts. Scheduled and effective guard-hours are reported separately from monetary cost. |
| Part 5: inputs and where each value comes from | No gate records, stopwatch samples, or independent queue observations are available. Inputs are documented group estimates in data/input_parameters.csv and data/arrival_rates.csv. Activity means and standard deviations are C, sticker check, 4 and 2 seconds; T, ID tap and barrier, 4 and 2; M, move-up, 3 and 1; R, refusal, 45 and 15. The no-sticker share is 5%; K is 8. Lognormal parameters are derived from these estimated moments. They are not fitted to field measurements. The parameter CSV records basis and source fields. The arrival profile is attributed to Study B's group estimate in progress-report.md; its selected rates lack a documented derivation. |
| Part 5: tools | Python 3.12, SimPy, NumPy, SciPy, pandas, and matplotlib. uv manages the isolated environment and uv.lock records exact dependency versions. Jupyter runs the study notebook. Seeds 1 to n are recorded; at least 30 independent days run per schedule-demand combination. All schedules share each day's generated cars for paired comparisons. |

## Assumptions and limits

The one-reader layout, pre-check policy, ability to turn out after refusal,
empty start, refusal share, activity distributions, and arrival process are
assumptions. Neither the friend's description nor the simulation establishes
every rule as a fact about the campus.

Input estimates cannot establish actual capacity. Confidence intervals describe
variation between simulated days under the chosen inputs. They do not remove
uncertainty about those inputs. Uniform demand scaling does not test a later
or longer morning peak.

The shared entrance is not equivalent to two independent booths. Total delay
also differs from waiting before the first service. Both changes are explicit.

## Experiment and evidence

The main experiment contains nine combinations: three schedules and demand
factors 0.8, 1.0, and 1.2. Activity assumptions, refusal share, and K stay fixed.
The four main measures and supplementary morning delay, initial waiting, and
effective guard-hours are reported with their mean, standard deviation, 95% confidence
interval, and replication count. Paired differences are B minus A, C minus A,
and C minus B. Bonferroni intervals accompany the three comparisons for each
measure and demand level.

A 30-day pilot checks interval half-widths against 1 second total delay, 1 car
maximum queue, 1 minute spillover, and 0.01 utilization. If needed, the study
increases replications and reports the final number and achieved precision.

The notebook also checks morning delay and initial-waiting precision at a
1-second target. A separate sensitivity test scales all four activity times
to 80%, 100%, and 120% at normal arrival demand. It keeps refusal share, K,
and entrance rules fixed, and checks precision using the same planning rule.
It reuses the normal timing cases from the main experiment when n matches.

Verification uses hand traces, deterministic and empty-input cases, vehicle
accounting, FIFO, the queue-area identity, closing rules, reproducible inputs,
known-answer M/M/1 and M/G/1 cases, per-car Lindley comparisons, and a single-reader
holding-time bound. Extreme demand and a slow reader check reasonable responses.
These checks verify the implementation; field validation remains unavailable.

Optional SFpark input testing, a continuous fluid approximation, and a wide
headroom sweep are not part of the presentation's main evidence. Related code
is retained, but those analyses are not claimed as completed.

## Changes from the submitted proposal

| Submitted commitment | Revised study and explanation |
| --- | --- |
| Independent booths, with a second booth 07:00 to 09:00. | Assumed guards sharing one reader; add the 07:00 to 10:00 schedule requested by the professor. |
| Gate logs, stopwatch measurements, and measured approach capacity. | Current documented estimates because the group reports that measurement access is unavailable. This does not establish that the professor's phrase "existing data" has been satisfied. |
| Ticket or ID processing. | Sticker checking followed by ID tapping, informed by the group's description. |
| Existing street blockage and complaints. | No such observations are established. Spillover is a simulated threshold measure. |
| Waiting before processing, minutes. | Total delay across stages, seconds; initial waiting is also reported to preserve the original distinction. |
| Two staffing configurations. | Three schedules, each at 80%, 100%, and 120% arrival demand. |

The professor's comment was: "Compare one booth, two booths from 7–9 AM, and
two booths from 7–10 AM. Use the existing data and test arrival demand at ±20%."
This revision retains the requested schedules and demand factors, while
disclosing the model and data changes.

Use [CONTEXT.md](CONTEXT.md) for terminology and the
[branch progress report](branch-progress-report.md) for implementation status.
