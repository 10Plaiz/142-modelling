# Combined study review

One place for the comparison between the two Group 8 parking studies. It merges the earlier per-repo notes and adds a correction pass over the group's own side-by-side table.

|  | Study A | Study B |
|---|---|---|
| Repository | `10Plaiz/142-modelling`, folder `Group8_Parking_Booth_Simulation` | `Tofuu24/CSS142P_FinalProject_8`, branch `master` |
| Reviewed at | commit `40a966d`, PR 1 merged | branch tip, 27-cell notebook |
| Where the model lives | `parking_sim.py`, 619 lines, plus a 52-cell notebook | the notebook alone, 27 cells |
| Input data | Placeholders from `tools/make_placeholder_data.py` | Group estimates in `data/input_parameters.csv` |
| Measured at the real gate | No | No |

Three notes now exist on disk. This file supersedes the other two:

- `repo-analysis-notes.md` describes Study A on its own.
- `friend-notebook-review.md` describes Study B on its own.
- This file is the merged comparison, and it also corrects the group's table.

**Both studies were run locally to check their numbers.** Study A reproduces its committed `results/` exactly. Study B's code cells were extracted and run in an empty folder, and its six result files came out byte-identical. Details are in section 9.

**The caveat that applies to every number below:** neither set of inputs was measured at the gate. Study A uses synthetic placeholders. Study B uses recollections. Nothing here is a finding about the real parking lot.

## 1. The two systems

Both simulate the same physical gate. Both are discrete-event simulations with common random numbers over 30 replications. What differs is what is standing at the gate.

**Study A.** A single entry booth staffed 07:00 to 19:00. An attendant issues a ticket or checks an ID. Vehicles queue on the approach, and every vehicle that arrives joins the queue and is processed.

**Study B.** A wide lane with a guard who checks a parking sticker. Only sticker cars may enter. Five percent of arrivals have no sticker, and the guard refuses them, which occupies the guard and the lane for a mean of 45 seconds. Exiting cars share the lane but need no check.

| | Study A | Study B |
|---|---|---|
| Server | Attendant in a booth | Guard in a lane |
| What is checked | Ticket or ID | Parking sticker |
| Refused cars | Not modelled | 5% of arrivals, at a mean of 45 s of guard time each |
| Car types | One | Two, sticker and no sticker |
| Processing time | 29.5 s, one lognormal | 9.85 s, a mixture |
| Peak window | 07:00 to 09:00 | 07:00 to 10:00 |
| K, the spillover threshold | 5 vehicles | 8 vehicles |
| Configurations | 1 booth, 2 booths 07-09, 2 booths 07-10 | 1 guard, 2 guards 07-09, 2 guards 07-10 |
| Daily entries | 453, from the placeholder gate log | 402, estimated |

The non-sticker refusal is real system structure that Study A does not have. It is also what makes Study B's processing time a mixture distribution rather than a single family. That is harder to model and harder to verify, and Study B does both.

## 2. Why the two studies reach opposite answers

They do not disagree about the code. They disagree about the inputs, and the gaps multiply.

| | Study A | Study B | Ratio |
|---|---|---|---|
| Peak arrival rate | 168 cars/hour | 100 cars/hour | 1.7x |
| Mean processing time | 29.5 s | 9.85 s | 3.0x |
| Capacity of one server | 122 cars/hour | 365 cars/hour | 3.0x |
| Peak utilization | 1.38, above capacity | 0.27 | 5.1x |
| Spillover at base demand | 71.2 min/day | 0.0 min/day | not comparable |
| Maximum queue | 26.8 cars | 3.3 cars | 8.1x |

Study A's peak arrival rate of 168 cars per hour is above what one booth can process, so the queue must grow. Study B's peak of 100 cars per hour is about a quarter of what one guard can process. One of these systems is saturated at the peak and the other is comfortably idle. The two studies are not measuring the same operational situation.

Neither input set was measured. Study A's numbers are synthetic. Study B's come from the group's memory of the campus. The honest conclusion is that nobody knows which situation is real, and one morning of counting settles it.

**The K values are the biggest unexamined number in the pair.** Study A sets K = 5. Study B sets K = 8. Both are estimates. K is the threshold that defines spillover, and spillover is the headline measure in both studies, so this single number decides whether either study reports a problem at all. Neither limitations section mentions that the other study uses a different value.

## 3. The group's comparison table, corrected

The group's own `US vs THEM` table is solid work and most of it checks out. Three rows need correcting, one needs a nuance, and several important rows are missing entirely.

| Claim in the group's table | Verdict | What is actually true |
|---|---|---|
| How the gate works: A issues a ticket or checks an ID; B checks a sticker and turns away 5% | Correct | Confirmed in both. |
| Where inputs come from: A placeholders, B group estimates with no site access | Correct | Confirmed. Study A even flags itself through `measured_on == "PLACEHOLDER"`. |
| Average processing time: A about 29 s, capacity about 122 cars/h; B about 9.9 s, capacity about 365 cars/h | Correct | Study A's fitted mean is 29.51 s, giving 122.0 cars/h. Study B's mixture mean is 9.85 s, giving 365.5 cars/h. Both figures are right. |
| Peak arrivals: A about 168 cars/h, above one booth's capacity; B 100 cars/h, about 27% of one guard's capacity | Correct | Study A's peak interval is 42 vehicles in 15 minutes, which is 168 cars/h against 122 cars/h of capacity, a load factor of 1.38. Study B's is 100 against 365, or 0.27. |
| Result for one server: A has 71 min of spillover a day and needs a second booth; B has 0 min and needs no second guard until about 2.5x demand | Correct | Study A: 71.2 min, 95% CI 64.8 to 77.5. Study B: 0.0 min in all five scenarios, first reaching 1+ min at demand x2.5. |
| 3 configurations plus ±20% demand | **Needs correction** | True for both, but the row implies that only Study B varies processing time. Study A varies it too, across x0.85, x1.00 and x1.15. The difference is ±15% against ±20%, not present against absent. |
| Stress test: A has only one extreme case at x1.5; B has x1 to x5 | **Needs correction** | Study A also runs a near-zero case at x0.05 traffic, where wait and spillover both collapse to about zero. That is an extreme condition, and it passed. The real point stands and should be stated plainly: Study A has two isolated extremes, Study B has a systematic growth sweep. |
| Guard-hours, the cost per option: A not shown; B yes | Correct, and a real gap in Study A | Study B reports 12, 14 and 15 guard-hours for A, B and C. Study A computes utilization on staffed time but never reports the staffed hours themselves, so a reader cannot see the cost of the second server anywhere in its outputs. |
| Two kinds of car: A no; B yes | Correct | Study A models one vehicle type. Study B models sticker and no-sticker with different processing distributions. |
| Fitting distributions to data: A full chi-square, KS and AIC; B none, lognormal assumed | **Needs nuance** | Study A runs the full selection pipeline across exponential, lognormal and triangular. Study B does not compare families, but it is not quite "none": it derives the lognormal parameters from the stated mean and standard deviation by the method of moments, and its verification uses the correct second moment of the mixture. The fair statement is that Study B has no data to fit, so it cannot run a selection procedure, and it does not claim to. |
| Verification: A 11 checks; B 2 checks | Correct on counts | Add the quality note. Study A's eleven are broader, covering conservation, first-come-first-served order, Little's law and the common-random-numbers identity. Study B's two are more rigorous individually, and its Lindley recursion check has no equivalent in Study A. Counting checks is not the same as measuring their strength. |
| Validation: A has a snapshot plan, extreme conditions and face validity; B has none | Correct, with one addition that matters | Neither study has validated against the real system. Study A has the machinery built and the extreme-condition part has run, but `validation_comparison.csv` holds no observed values and the notebook prints "Pending field snapshots". Study B has no validation section at all, and the word "valid" appears once in its whole notebook. |
| Were 30 replications enough: A yes, checked with the Week 7 rule; B not checked | **Needs correction, and it matters** | Study A checked, and the answer was **no**. The Week 7 rule asked for 77 replications for average wait, then 153, and the notebook ran the follow-up to 154 before the half-width fell to 0.2497 against a target of 0.25. The headline results are still the 30-replication ones. The correct line is that Study A noticed the shortfall and ran more, while Study B did not check. |
| Continuous model and Monte Carlo probability: A has the fluid model and P(spillover) with an interval; B has neither | Correct | Study A also reports the probability of any spillover with a Wilson interval: 1.00 for one booth, and 0.53 for each two-booth option. |
| Easy to run: A needs local Jupyter; B runs in Colab and creates its own inputs | Correct, with one addition | Study A also runs headless. `python parking_sim.py` prints a 30-replication summary with confidence intervals and needs no Jupyter at all. |

### What the group's table leaves out

These are real differences the table does not mention, and they are the ones a grader is most likely to notice.

| Item | Study A | Study B |
|---|---|---|
| K, the spillover threshold | 5 vehicles | 8 vehicles |
| Proposal document in the repo | Yes, 11 parts | No. Its README cites "Proposal, Part 6" but the file is not there. |
| Conceptual model | A table of entity, resource, state, events, activity, delay and study type | None. The word "conceptual" does not appear in the notebook. |
| Assumptions declared | Eight, each marked confirmed or provisional and mapped to the test that probes it | None marked. The README lists five in prose. |
| Model classification | Dynamic, stochastic, discrete, terminating, with a reason for each | None stated. "terminating" and "warm-up" never appear. |
| Multiple-comparison correction | Bonferroni across three comparisons | None across 45 comparisons |
| Independent second model | A fluid-flow model solved with Euler and Runge-Kutta, with a step-size test | None |
| Replication follow-up | Ran to 154 and reported the achieved half-width | Stays at 30 with no precision check |
| Input provenance bug | None | Cell 5 rebuilds `data/input_parameters.csv` with four shorter `basis` strings if the file is missing |
| README accuracy | Consistent with the code | Claims per-car agreement with the Lindley recursion, but the code compares means only |
| Repository hygiene | Stale duplicate copies of the model and notebook in the repo root, and a committed `.pyc` | Clean, and `.gitignore` covers compiled files |
| Report, presentation and zip | Absent | Absent |
| Conceptual model diagram | Absent | Absent |

Three of these deserve a sentence each.

**The multiple-comparison difference is a real analytical gap in Study B.** Study B reports 45 paired intervals at 95% and marks 29 as significant, with no correction and no acknowledgement. With 45 simultaneous intervals, roughly two false positives are expected by chance alone, and a grader who teaches output analysis will look for exactly this. Study A added a Bonferroni column after only three comparisons.

**The input provenance bug in Study B is small but costly in a graded submission.** The numbers never change, so no result is affected, but the text that justifies each input quietly loses detail when the notebook runs in Colab. One of the lost strings says to replace K with a Google Maps measurement. The rubric scores "justified inputs and assumptions", so losing the justification is a real cost.

**The duplicate files in Study A are a submission risk.** A marker who opens `parking_sim.py` at the repo root gets the old model with no fluid section and only two configurations. Nothing in the file says it is stale.

## 4. Scoring against the published rubric

The brief's rubric, scored from outside. This is my assessment, not the professor's. The report and the presentation are in neither repo, so both lose that share of the communication points.

| Criterion | Points | Study A | Study B |
|---|---|---|---|
| Problem framing: decision question, stakeholder, scope, boundary, conceptual model, measures | 15 | 14 | 10 |
| Model construction: method, justified inputs and assumptions, correct implementation, documentation | 25 | 20 | 19 |
| Experiment design: baseline and alternatives, controlled conditions, seeds, replications, scenario logic, reproducibility | 20 | 18 | 17 |
| Analysis: verification, validation, uncertainty, confidence intervals, sensitivity, recommendation, limitations | 25 | 21 | 16 |
| Communication: report, visuals, presentation, demonstration, citations | 15 | 11 | 11 |
| **Total** | **100** | **84** | **73** |

Where the eleven-point gap comes from:

- **Problem framing, 4 points.** A proposal document, a conceptual model, eight marked assumptions and a method classification, against none of those things.
- **Analysis, 5 points.** Validation machinery, a multiplicity correction, a second independent model, a precision calculation and seven named limitations, against two sentences of limitations and no validation.
- **Model construction, 1 point.** Study B is more realistic and verifies more rigorously, but its README overstates one check and its input file has two disagreeing sources. Study A's inputs are synthetic, which is its own problem, and its repo carries stale duplicate copies.
- **Experiment design, 1 point.** The replications-needed calculation and the follow-up to 154.
- **Communication, tied.** Study A has six figures, a proposal and a printed result statement. Study B has a cleaner README and runs in Colab with no setup. Neither has a conceptual diagram, a report or a presentation.

Eleven points is about a letter grade, and it is worth saying plainly what the gap is not: it is not the simulation. Study B's model is the more faithful one. The gap is documentation, validation and output analysis.

## 5. What each study has, and what both lack

**Only Study A has:**

- An 11-part proposal with the decision question, scope, out-of-scope list and eight assumptions marked confirmed or provisional.
- A conceptual model covering entity, resource, state, events, activity, delay and study type.
- The classification, dynamic, stochastic, discrete, terminating, with the reason for each.
- An input-modelling pipeline: Mann-Whitney U test, maximum-likelihood fits of three families, chi-square rejection at 5%, AIC selection, KS reported.
- Eleven verification checks, including conservation at 19:00, first-come-first-served order and Little's law.
- An independent fluid-flow model as a cross-check, solved with Euler and Runge-Kutta with a step-size halving test.
- A replications-needed calculation and a documented follow-up to 154 runs.
- Bonferroni correction across three paired comparisons.
- A Wilson interval on the probability of spillover.
- Seven named limitations.

**Only Study B has:**

- Two car types, with the refused-car path modelled. This is real system structure.
- A mixture processing distribution, and a verification that uses its correct second moment.
- The Lindley recursion check, which validates the event logic against an independent calculation from the same inputs.
- A stress test from x1 to x5 demand, producing an actionable threshold: one guard fails at about 2.5 times current traffic.
- Guard-hours reported per configuration, 12, 14 and 15, which is the cost side of the decision.
- An arrival generator that inverts the cumulative rate function, a cleaner derivation than a per-interval restart.
- Common random numbers layered across demand levels as well as across configurations.
- Colab-ready execution, with a self-creating input file.
- A clean `.gitignore` with no compiled files committed.

**Both lack:**

- Any measured input. Nothing was observed at the real gate.
- Any validation against the real system.
- The report PDF, the presentation, and the zip package the brief requires.
- A conceptual model diagram. Both use prose and tables only.
- A reconciliation of the two K values, 5 and 8.
- A cost comparison in money. Study B reports guard-hours and Study A explicitly leaves the wage judgement outside the model, but neither converts hours into a recommendation.

## 6. What Study A must change

Ordered by impact on the grade.

1. **Do the validation.** `validation_comparison.csv` holds no observed values and the notebook prints "Pending field snapshots". Count the vehicles waiting every five minutes for one morning, on a different day from the arrival data, then rerun section 7. Until this is done the study cannot claim validation at all.
2. **Collect the real inputs.** Four of the five files in `data/` are placeholders, and `peak_arrival_tally.csv` is empty. An empty tally means the peak rates come from booth passages, which are capped by booth capacity, so true peak demand is understated. The README already documents the collection protocol.
3. **Delete the stale root copies** of `parking_sim.py`, 505 lines, and `Parking_Booth_Simulation.ipynb`, 46 cells. Both predate the fluid model and the third configuration. A marker cannot tell which file is the model, and will not try.
4. **Untrack the `.pyc`** at `Group8_Parking_Booth_Simulation/__pycache__/parking_sim.cpython-312.pyc`, and add `__pycache__/` to `.gitignore`.
5. **Fix the replication story.** The headline results are n = 30 while the notebook's own planning section says 154 are needed for the stated precision. Either promote the 154-run results to the headline, or label the 30-run numbers preliminary everywhere they appear.
6. **Report the staffed hours.** The paired differences show utilization on staffed time, but the staffed hours themselves never appear in a table, so a reader cannot see what the second server costs. Add a booth-hours column, as Study B does with guard-hours.
7. **Add a demand stress test** from x1 to x5. It is the strongest robustness statement available for a model whose inputs are uncertain, and Study B is currently the only one of the two with it.
8. **Add a conceptual model diagram.** The brief asks for a diagram, flowchart, process map, or state model. The current table is arguably an equivalent representation, but a diagram removes the ambiguity at little cost.
9. **Produce the missing deliverables:** the report PDF, the presentation, and the zip package the brief requires.
10. **Fix the fluid model's window inconsistency** before peak and off-peak processing times are ever fitted separately. `ServiceModel.times` chooses the distribution by arrival time, and `fluid_rhs_factory.window` by simulation time.
11. **Consider modelling the refused-car path.** If the real gate turns away vehicles without a sticker, Study A's single vehicle type is missing the structure that makes Study B's model realistic.

## 7. What Study B must change

Ordered by impact on the grade.

1. **Add validation. This is the one that decides the grade.** There is none, and the notebook never names the gap. One morning of counting the line every five minutes, compared against the 2.5th to 97.5th percentile band of simulated days, closes the largest hole in the study. The rubric scores verification and validation separately.
2. **Remove the two sources of truth for the inputs.** Cell 5 rebuilds `data/input_parameters.csv` if it is missing, with four shorter `basis` strings: `sticker_mean_sec`, `nonsticker_share`, `nonsticker_mean_sec` and `K_waiting_spaces`. The numbers agree, so no result changes, but the justification text degrades silently in the Colab path. Delete the fallback, or generate the file from one shared definition.
3. **Correct for multiple comparisons.** There are 45 paired intervals, judged at 95% with no correction, and 29 are flagged significant. Add a Bonferroni or Benjamini-Hochberg column, plus one sentence explaining that the flags are now conservative.
4. **Compare all the measures.** Six are tracked, `avg_wait_sec`, `avg_wait_peak_sec`, `max_wait_sec`, `max_queue`, `spillover_min` and `utilization`, but only three enter the paired differences. Add the total wait and the utilization, because utilization is the cost side of the decision.
5. **Make the README match the code.** README section 7 says "the model's per-car waits match the Lindley recursion exactly". The code computes `abs(out["avg_wait_sec"] - w.mean() * 60)`, a mean against a mean. Take `np.abs(wait - w).max()` instead. It is one line, and it is strictly stronger.
6. **Measure K.** Its own `basis` field says to replace it with a Google Maps measurement. K decides whether the answer is "the line reaches the street" or "it does not", and every base-demand scenario sits at exactly zero minutes, so the conclusion rests entirely on this one estimate.
7. **Add configuration C to the stress test.** High demand is precisely when the 07:00 to 10:00 option matters, and it is the only configuration omitted.
8. **Add the conceptual model material:** the dynamic, stochastic, discrete classification, an entity, resource, event, activity and delay table, assumptions marked confirmed or provisional, and a statement that this is a terminating study with no warm-up. The word "conceptual" appears zero times in the notebook today.
9. **Add the proposal document to the repo.** The README cites "Proposal, Part 6" as the basis for the replication count, but no proposal file exists there.
10. **Add a replications-needed calculation.** Thirty satisfies the brief's letter, but the half-width on the longest wait is about 7 seconds on a mean of 60, roughly 12% relative, and nobody asks whether that is tight enough.
11. **Resolve the lane contradiction.** The README says the wide lane lets two cars be checked side by side, and also that the same lane serves entering and exiting cars. The two-guard results depend on which reading holds.
12. **Produce the missing deliverables:** the report PDF, the presentation, and the zip package the brief requires.

## 8. What both must change

1. **Measure the gate.** Neither study has an observed input. Someone must record the 15-minute arrival counts, the processing times by stopwatch, the share of cars refused and their handling time, and the approach length for K. Both notebooks accept these without code changes.
2. **Reconcile K.** Study A uses 5 vehicles and Study B uses 8. One is wrong. This single number decides whether either study reports a problem, and it appears in neither limitations section.
3. **Decide which study is being submitted.** Two contradictory answers to the same question, submitted side by side, is worse than one answer with its uncertainty stated honestly. The group should either merge into one study, or state which is the deliverable and what the other one is for.
4. **Produce the report and the presentation.** Neither repo contains either, and those are the largest unearned block of points in the rubric.
5. **Add a conceptual model diagram.** Neither has one. The brief asks for a diagram, flowchart, process map or state model.
6. **Meet the packaging requirement.** The brief asks for one zip named `CSS142P_FinalProject_TeamNumber_ProjectTitle.zip` containing the report, the model, the data, the results, the presentation and the README. Neither repo follows the recommended folder structure either.
7. **Standardize the vocabulary.** Study A says configuration, Study B says scenario and config. The rubric is written in the course's words. See section 10.
8. **If the group merges, take the best of each.** Model and verification from Study B, because the mixture and the Lindley check are stronger. Analysis scaffolding from Study A: the proposal, the conceptual model, the assumptions table, the precision calculation, the multiplicity correction and the fluid cross-check. Stress test and guard-hours from Study B. Validation is new work either way.

## 9. How the numbers were checked

**Study A.** SimPy 4.1.2 was installed and `python3 parking_sim.py` was run inside `Group8_Parking_Booth_Simulation/`. It reproduced the committed values exactly for all three configurations:

```text
Service model: lognormal (pooled)   K = 5   replications = 30
1 booth all day          avg_wait_min 2.720   95% CI [2.320, 3.120]
                         spillover_min 71.189 95% CI [64.836, 77.543]
2 booths 07:00-09:00     avg_wait_min 0.113   95% CI [0.102, 0.123]
                         spillover_min 0.334  95% CI [0.031, 0.636]
2 booths 07:00-10:00     avg_wait_min 0.099   95% CI [0.088, 0.109]
                         spillover_min 0.331  95% CI [0.028, 0.634]
```

Also read directly from the committed data: 453 daily entries, a peak interval of 42 vehicles in 15 minutes, a peak load factor of 1.377 on one booth, a mean processing time of 29.51 s from the fitted distribution and 29.41 s from the raw timings, and a capacity of 122.0 cars per hour.

**Study B.** The 13 code cells were extracted to a script, the `%pip` magic was stripped and `IPython.display.display` was shimmed. It was run in an empty folder on Python 3.12 with SimPy 4.1.2 and Matplotlib 3.11.2 on the Agg backend. It completed with no errors and regenerated all six result files and all three figures.

Byte comparison against the committed files:

| File | Result |
|---|---|
| `results/paired_differences.csv` | identical |
| `results/queue_profile_base_demand.csv` | identical |
| `results/replications.csv` | identical |
| `results/stress_test.csv` | identical |
| `results/summary_by_scenario.csv` | identical |
| `results/verification_mg1.csv` | identical |
| `data/arrival_rates.csv` | identical |
| `data/input_parameters.csv` | differs in four `basis` strings, numeric values identical |

Also confirmed from the run: base-demand peak wait 2.4 s for one guard, spillover 0.0 minutes in all five scenarios, first 1+ minute of spillover at demand x2.5, the verification row at 75% utilization with Pollaczek-Khinchine 28.706 s against simulated 28.396 s and a half-width of 0.804 s, guard-hours of 12, 14 and 15, and a stress test covering only configurations A and B.

## 10. Words to use consistently

Study A says configuration. Study B says scenario and config. The rubric is written in the course's vocabulary, so that is the set to standardize on.

| Use this | Avoid | Meaning |
|---|---|---|
| configuration | option, case | A staffing plan: one server, or two servers until 09:00 or 10:00. |
| entity | agent, actor | One vehicle. |
| resource | server, station | The booth or guard, which serves one vehicle at a time. |
| event | step, action | A moment when something changes: arrival, processing start, processing completion, second server closes. |
| activity | duration | A delay the model samples, such as processing time. |
| delay | waiting | A time the model produces as output, such as time in queue. Never sampled. |
| replication | run, trial, iteration | One independent repetition of one simulated day. 30 per configuration. |
| common random numbers | same seeds | Giving every configuration the same arrivals and processing times, so differences reflect staffing only. |
| terminating study | transient, short run | A study with a natural start and end, 07:00 to clearance, with no warm-up discarded. |
| warm-up | burn-in | Simulated time discarded before measurement. Study A discards none, and uses warm-up only in the M/M/c known-answer tests. |
| verification | testing | Checking the model is built correctly. |
| validation | testing | Checking the model matches the real system. Not the same thing as verification. |
| sensitivity analysis | what-if | Rerunning with changed inputs to test whether the recommendation survives. |
| measure | metric, KPI | One of the reported quantities: average wait, maximum queue, utilization, spillover. |
| spillover | overflow, backup | Total time the waiting queue holds at least K vehicles. |
| K | threshold | How many vehicles fit on the approach before the tail reaches the road. |
| paired difference | delta, gap | One configuration's per-replication result minus another's, on the same day. |

One trap. Study B uses the word "scenario" for an input condition, such as demand x1.2, which is a different thing from a configuration. If the studies are merged, rename the input conditions to demand scenarios, and keep configuration for the staffing plan.
