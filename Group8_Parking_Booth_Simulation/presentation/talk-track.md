# Presentation talk track

Use Parking_Study_Presentation.pdf. Aim for eight minutes of explanation and two minutes of demonstration.

1. **Decision.** We compare three guard schedules, with normal arrivals and 20% fewer or more cars. Our submitted proposal used booths; this revision explicitly assumes guards sharing one reader.
2. **Entrance diagram.** Follow one car from arrival to sticker checking, then ID tapping and entry. A refused car turns out. Explain the assumed advance-check rule.
3. **Inputs.** These are estimates, not measurements. Do not say the group collected gate logs or stopwatch timings. K = 8 is the selected spillover threshold.
4. **Checks.** 27 checks passed. Explain the three-car hand trace rather than reciting formulas. Verification checks the program; field validation remains unavailable.
5. **Result table.** Read the delay benefit alongside 12, 14, and 15 scheduled guard-hours. A averaged 2.57 seconds at normal demand. A daily maximum averaged over days can be fractional.
6. **Result chart.** Error bars are 95% confidence intervals across simulated days. Guard utilization counts checks and refusals, not all the time the reader is occupied.
7. **Demand chart.** The activity assumptions stay fixed. Only expected arrivals change. Describe how the size of the benefit changes across demand levels.
8. **Evidence limits.** Zero observed spillover does not establish zero risk. Intervals describe simulated-day variation; they do not validate estimated inputs.
9. **Conclusion.** Read the conditional recommendation. Do not claim a wage saving, existing street congestion, or instructor approval of the revision.

## Demonstration

Open the executed notebook and show the inputs, checks, comparison table, and final conclusion. The same run generated the CSVs and both PDFs. For live execution, use the project .venv kernel and Restart Kernel and Run All Cells. A full run takes longer than the allotted demonstration; keep the already executed notebook available.

## Questions to prepare for

- Why guards instead of booths? The group described sticker checks before ID tapping. We retained the requested schedules but explicitly assumed a shared entrance. This is a disclosed revision.
- Where is the real data? No campus observations were available. Inputs are estimates with their basis recorded. Old placeholder files were synthetic too.
- Why repeat the days? Arrivals and activity times vary. We ran 30 days per combination and reported uncertainty.
- Is one guard definitely enough? The recommendation holds under these assumptions. The study cannot prove real-campus capacity without input and queue measurements.
- Does 20% more demand mean exactly 20% more cars in every run? No. It scales the expected arrival rates. Actual counts remain random.
- Can a second guard slightly increase the reported queue maximum? The pre-check car remains on the approach while it receives service. The queue definition counts it, so a shorter total delay does not guarantee a smaller maximum approach count.
