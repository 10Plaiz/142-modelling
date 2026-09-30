"""Render presentation and report artifacts from the notebook's final tables."""
from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

COLORS = ["#185e87", "#c06924", "#568055"]
INK = "#173042"


def draw_entrance():
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.set(xlim=(0, 11), ylim=(0, 4))
    ax.axis("off")
    boxes = [(.2, 2, 1.7, "Arrive\nand queue"), (2.5, 2, 2.3, "Sticker check\nGuard 1 or 2"),
             (5.5, 2, 2.3, "ONE entrance stop\nID tap + move-up"), (8.6, 2, 2, "Enter lot"),
             (2.5, .3, 2.3, "No sticker:\nrefuse and turn out")]
    for x, y, width, label in boxes:
        ax.add_patch(FancyBboxPatch((x, y), width, .85, boxstyle="round,pad=0.08",
                                   facecolor="#eef4f7", edgecolor=INK))
        ax.text(x+width/2, y+.425, label, ha="center", va="center", color=INK, fontsize=11)
    for start, end in [((1.9, 2.425), (2.4, 2.425)), ((4.8, 2.425), (5.4, 2.425)),
                       ((7.8, 2.425), (8.5, 2.425)), ((3.65, 1.9), (3.65, 1.25))]:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=16, color=INK))
    ax.text(.2, 3.5, "Assumed entrance, not a confirmed campus layout", fontsize=15, weight="bold", color=INK)
    ax.text(5.5, .72, "Guard 2 checks only the next car while the stop is occupied.\nThat car keeps its pre-check position until the stop is free.",
            fontsize=10, color=INK, va="center")
    fig.tight_layout()
    return fig


def draw_results(summary):
    fig, axes = plt.subplots(2, 2, figsize=(10, 6))
    metrics = [("avg_delay_sec", "Average total delay", "Seconds"),
               ("max_queue_veh", "Mean daily maximum queue", "Cars"),
               ("guard_utilization", "Active guard utilization", "Percent"),
               ("spillover_min", "Spillover duration", "Minutes")]
    for ax, (metric, title, unit) in zip(axes.flat, metrics):
        sub = summary[(summary.demand == 1.) & (summary.measure == metric)]
        factor = 100 if metric == "guard_utilization" else 1
        ax.bar(["A: 12 h", "B: 14 h", "C: 15 h"], sub["mean"]*factor,
               yerr=sub.half_width*factor, capsize=5, color=COLORS)
        ax.set(title=title, ylabel=unit)
        if np.allclose(sub["mean"], 0):
            ax.set_ylim(0, 1)
            ax.text(.5, .5, "No spillover observed\nin these simulated days", transform=ax.transAxes, ha="center")
    n = int(summary.n.iloc[0])
    fig.suptitle(f"Estimated normal demand | {n} days per schedule | bars show mean and 95% CI", color=INK)
    fig.tight_layout()
    return fig


def draw_sensitivity(summary):
    fig, ax = plt.subplots(figsize=(10, 4))
    names = list(summary.configuration.drop_duplicates())
    for name, color in zip(names, COLORS):
        sub = summary[(summary.configuration == name) & (summary.measure == "avg_delay_sec")].sort_values("demand")
        ax.errorbar(sub.demand*100, sub["mean"], yerr=sub.half_width, label=name, color=color,
                    marker="o", capsize=5, linewidth=2)
    ax.set(xlabel="Arrival demand, percent of baseline estimate", ylabel="Average total delay, seconds",
           title="Do the staffing comparisons change when arrivals change?")
    ax.set_xticks([80, 100, 120]); ax.legend()
    fig.tight_layout()
    return fig


def recommendation(summary, paired, probabilities):
    normal = summary[(summary.demand == 1.) & (summary.measure == "avg_delay_sec")]
    a, b, c = normal["mean"].tolist()
    extra = paired[(paired.demand == 1.) & (paired.measure == "avg_delay_sec")].iloc[-1]
    all_delay = summary[summary.measure == "avg_delay_sec"]
    zero = int(probabilities.spillover_days.sum()) == 0
    spill = ("No spillover was observed in the nine study combinations. This does not prove zero risk. "
             if zero else "Spillover occurred in some study combinations; inspect the probability table before a decision. ")
    return (
        "### Conditional recommendation\n\n"
        f"At estimated normal demand, average total delay was {a:.2f} seconds for A, {b:.2f} for B, "
        f"and {c:.2f} for C. B saved {a-b:.2f} seconds per car for 2 additional scheduled guard-hours. "
        f"C saved {a-c:.2f} seconds for 3 additional guard-hours. Extending B to C saved {b-c:.2f} seconds; "
        f"its paired 95% interval for C minus B was [{extra.ci_low:.2f}, {extra.ci_high:.2f}] seconds.\n\n"
        f"Across 80%, 100%, and 120% demand, the largest mean delay was {all_delay['mean'].max():.2f} seconds. "
        + spill +
        "Under these estimates, retain A as the starting staffing choice: the experiment has not established "
        "a need for more guards. Additional staffing has a measured time benefit, but its financial value "
        "was not modelled. This recommendation applies to the assumed arrangement and inputs. It is not "
        "a verified staffing recommendation for the real campus."
    )


def _text_page(title, paragraphs, *, landscape=True, number=None):
    fig = plt.figure(figsize=(13.33, 7.5) if landscape else (8.27, 11.69), facecolor="white")
    fig.text(.06, .91, title, fontsize=25 if landscape else 20, weight="bold", color=INK)
    y = .81
    for paragraph in paragraphs:
        lines = textwrap.wrap(paragraph, width=93 if landscape else 80)
        fig.text(.06, y, "\n".join(lines), fontsize=16 if landscape else 11.5,
                 color=INK, va="top", linespacing=1.5)
        y -= len(lines) * (.043 if landscape else .024) + .035
    fig.text(.06, .035, "Group 8 | CSS142P | Estimated inputs; assumed layout", fontsize=9, color="#65717a")
    if number is not None:
        fig.text(.94, .035, str(number), fontsize=9, color="#65717a", ha="right")
    return fig


def _table_page(title, summary, *, landscape=True):
    normal = summary[summary.demand == 1.]
    rows = []
    for name in normal.configuration.drop_duplicates():
        sub = normal[normal.configuration == name].set_index("measure")
        rows.append([name.split(":")[0], str(int(sub.scheduled_guard_hours.iloc[0])),
                     f"{sub.loc['avg_delay_sec','mean']:.2f}", f"{sub.loc['max_queue_veh','mean']:.2f}",
                     f"{sub.loc['guard_utilization','mean']*100:.2f}%", f"{sub.loc['spillover_min','mean']:.2f}"])
    fig = _text_page(title, [f"Normal demand. {int(normal.n.iloc[0])} simulated days per schedule. Full confidence intervals are in the notebook and CSV exports."], landscape=landscape)
    ax = fig.add_axes([.05, .3 if landscape else .45, .9, .3]); ax.axis("off")
    table = ax.table(cellText=rows, colLabels=["Schedule", "Guard-hours", "Delay (s)", "Max queue", "Guard use", "Spillover (min)"], loc="center", cellLoc="center")
    table.auto_set_font_size(False); table.set_fontsize(12 if landscape else 9); table.scale(1, 2)
    for (row, _), cell in table.get_celld().items():
        cell.set_edgecolor("#d8e1e6")
        if row == 0:
            cell.set_facecolor(INK); cell.set_text_props(color="white", weight="bold")
    return fig


def build_documents(summary, paired, probabilities, checks, parameters, extremes, n, K, conclusion, output, figures):
    """Create a PDF deck, report, and speaker notes from final notebook results."""
    output, figures = Path(output), Path(figures)
    output.mkdir(exist_ok=True)
    a_delay = summary[(summary.demand == 1.) & (summary.measure == "avg_delay_sec")]["mean"].iloc[0]
    max_upper = probabilities.ci_high.max()*100
    passed = int(checks["pass"].sum())
    slides = [
        ("Should a second guard work during the morning?", ["Compare one guard all day, plus a second guard until 09:00, or plus a second guard until 10:00.",
          "Test 20% fewer arrivals, normal demand, and 20% more arrivals. The aim is to measure the staffing benefit under stated assumptions.",
          "The submitted proposal described independent booths and planned field measurements. This revision uses guards sharing one reader and estimated inputs."]),
        ("Inputs are estimates, not field measurements", ["Expected arrivals: about 402 cars/day, peaking at 100 cars/hour. Sticker check: 4 seconds; ID tap and barrier: 4 seconds; move-up: 3 seconds.",
          "An estimated 5% of cars have no sticker. Refusal averages 45 seconds. The spillover threshold is 8 cars on the approach.",
          "All values and their basis remain in the input CSVs. The arrival and activity distributions are assumptions; no campus fit was performed."]),
        ("How we checked the program", [f"{passed} recorded checks passed, including hand-calculated examples, car accounting, arrival order, closing rules, and one-reader limits.",
          "Independent queue calculations checked each car's one-guard delay. Separate M/M/1 and M/G/1 benchmarks checked mean waiting under known conditions.",
          f"Nine combinations were run with {n} days each. Matching inputs make staffing comparisons fair. Empty demand, high demand, and a slow reader were also tested."]),
        ("What the evidence supports", [f"At normal estimated demand, A averaged {a_delay:.2f} seconds of total delay. The next slides show the measured staffing benefits and confidence intervals.",
          f"The largest Wilson upper limit for spillover probability among study combinations is {max_upper:.1f}%. Zero observed events do not imply zero risk.",
          "Confidence intervals describe variation between simulated days. They do not establish that estimated inputs match the campus."]),
        ("Recommendation and limitations", [conclusion.split("\n\n")[-1],
          "The layout, pre-check policy, refusal share, and approach capacity are not confirmed. No real queue measurements were available for validation.",
          "Do not treat these results as proof of existing congestion, or as a financial case for hiring. Measure the inputs if access becomes available."]),
    ]
    with PdfPages(output / "Parking_Study_Presentation.pdf") as pdf:
        page = 1
        def save(fig):
            nonlocal page
            pdf.savefig(fig); plt.close(fig); page += 1
        save(_text_page(*slides[0], number=page))
        save(draw_entrance())
        save(_text_page(*slides[1], number=page))
        save(_text_page(*slides[2], number=page))
        save(_table_page("Schedule comparison at normal demand", summary))
        save(draw_results(summary))
        save(draw_sensitivity(summary))
        save(_text_page(*slides[3], number=page))
        save(_text_page(*slides[4], number=page))

    with PdfPages(output / "Parking_Study_Report.pdf") as pdf:
        def save_report(title, paragraphs):
            fig = _text_page(title, paragraphs, landscape=False)
            pdf.savefig(fig); plt.close(fig)
        save_report("Parking entrance staffing study", ["CSS142P Modelling and Simulation | Group 8 | 30 September 2026",
            "Executive summary", *conclusion.split("\n\n")[1:],
            "This report is a study under explicit assumptions. It does not establish that the revised scope was accepted by the instructor."])
        save_report("Problem, boundary, and inputs", ["The decision is which of three guard schedules to use under the assumed entrance arrangement. A has 12 scheduled guard-hours, B has 14, and C has 15.",
            "Each operating day starts empty at 07:00. Arrivals stop at 19:00 and remaining cars are processed. The model excludes parking-space limits, exit traffic, abandonment, and reader failures.",
            "Inputs are documented group estimates: approximately 402 arrivals/day, a 100/hour peak, activity means of 4 seconds checking, 4 seconds tapping and barrier operation, 3 seconds moving, and 45 seconds refusal. Activity standard deviations are 2, 2, 1, and 15 seconds. The no-sticker share is 5%; K is 8.",
            "Lognormal activity parameters come from those means and standard deviations. Arrivals use a piecewise-constant Poisson process. Neither assumption is a fit to campus observations.",
            "The revised model replaces independent booths with one stop and a pre-check position. The supplied progress report is the basis for this choice; the physical arrangement remains unconfirmed."])
        fig = draw_entrance(); pdf.savefig(fig); plt.close(fig)
        save_report("Method, experiment, and checks", ["SimPy implements a discrete-event model. A car is admitted after checking, tapping, and moving, or refused after checking and refusal activity. Guard 2 checks only the next car while the stop is occupied; it starts no new check after its scheduled closing.",
            f"The experiment crosses three schedules with demand factors 0.8, 1.0, and 1.2. Seeds 1 to {n} give independent days. Each schedule receives identical cars within a seed and demand level. Processing distributions and other inputs remain fixed during demand sensitivity.",
            "Total delay is time in the system minus the car's own activity time. Initial waiting is reported separately. The approach queue includes the pre-check position. Guard utilization counts active checks and refusals, with available time extended to finish final guard activity.",
            f"{passed} recorded checks passed. Hand traces, deterministic and empty cases, conservation, FIFO, queue-area accounting, closing rules, reproducibility, per-car Lindley comparisons, known-answer queues, and reader holding-time bounds are exported in verification_checks.csv.",
            "Means, standard deviations, and 95% t intervals describe the simulation output. Paired staffing differences also include Bonferroni intervals across three comparisons per measure and demand. Replication precision is recorded for all nine combinations."])
        fig = _table_page("Results at normal demand", summary, landscape=False); pdf.savefig(fig); plt.close(fig)
        fig = draw_results(summary); pdf.savefig(fig); plt.close(fig)
        fig = draw_sensitivity(summary); pdf.savefig(fig); plt.close(fig)
        save_report("Validation, recommendation, and limits", [conclusion.split("\n\n")[-1],
            "Field validation was unavailable. Tests of zero or low demand, demand multiplied by five, and a reader ten times slower checked reasonable responses. These cases are not observations of the campus.",
            "The output intervals cover simulation sampling variation. Estimated activity times, arrival volumes, K, refusal behavior, and the shared-reader policy may be inaccurate. Changing these assumptions can change the conclusion.",
            "Uniform demand scaling preserves the timing of the peak. It does not test a peak that moves later or lasts longer. Financial cost and the acceptable waiting-time target were not specified.",
            "The optional public-data downloader and fluid approximation were not used to validate the presented results. No actual street blockage or complaints have been established."])
        save_report("Sources and reproduction", ["Primary project records: Modeling_Proposal.pdf; CSS142P_Final_Project_Proposal_Format.pdf; CSS142P_Final_Project_Requirements_and_Guidelines.pdf; the user's professor comment; and progress-report.md describing PR #2.",
            "Input estimates and their attributed sources: data/input_parameters.csv and data/arrival_rates.csv. The input CSV cites a commercial RFID timing range; it is background attribution, not independently established campus timing. The model's 4-second tap estimate also includes the barrier cycle.",
            "SimPy documentation: https://simpy.readthedocs.io/ . NumPy random streams: https://numpy.org/doc/stable/reference/random/parallel.html . SciPy statistical functions: https://docs.scipy.org/doc/scipy/reference/stats.html .",
            "Environment and notebook execution: https://docs.astral.sh/uv/guides/projects/ and https://nbclient.readthedocs.io/en/latest/client.html . Exact package versions are recorded in uv.lock.",
            "From the repository root: uv sync --locked. Then uv run --locked python Group8_Parking_Booth_Simulation/tools/verify_notebook.py. This executes a fresh notebook copy, checks the exports, and preserves evidence. Add --publish only to refresh the working notebook and generated exports."])

    notes = f"""# Presentation talk track

Use Parking_Study_Presentation.pdf. Aim for eight minutes of explanation and two minutes of demonstration.

1. **Decision.** We compare three guard schedules, with normal arrivals and 20% fewer or more cars. Our submitted proposal used booths; this revision explicitly assumes guards sharing one reader.
2. **Entrance diagram.** Follow one car from arrival to sticker checking, then ID tapping and entry. A refused car turns out. Explain the assumed advance-check rule.
3. **Inputs.** These are estimates, not measurements. Do not say the group collected gate logs or stopwatch timings. K = {K} is the selected spillover threshold.
4. **Checks.** {passed} checks passed. Explain the three-car hand trace rather than reciting formulas. Verification checks the program; field validation remains unavailable.
5. **Result table.** Read the delay benefit alongside 12, 14, and 15 scheduled guard-hours. A averaged {a_delay:.2f} seconds at normal demand. A daily maximum averaged over days can be fractional.
6. **Result chart.** Error bars are 95% confidence intervals across simulated days. Guard utilization counts checks and refusals, not all the time the reader is occupied.
7. **Demand chart.** The activity assumptions stay fixed. Only expected arrivals change. Describe how the size of the benefit changes across demand levels.
8. **Evidence limits.** Zero observed spillover does not establish zero risk. Intervals describe simulated-day variation; they do not validate estimated inputs.
9. **Conclusion.** Read the conditional recommendation. Do not claim a wage saving, existing street congestion, or instructor approval of the revision.

## Demonstration

Open the executed notebook and show the inputs, checks, comparison table, and final conclusion. The same run generated the CSVs and both PDFs. For live execution, use the project .venv kernel and Restart Kernel and Run All Cells. A full run takes longer than the allotted demonstration; keep the already executed notebook available.

## Questions to prepare for

- Why guards instead of booths? The group described sticker checks before ID tapping. We retained the requested schedules but explicitly assumed a shared entrance. This is a disclosed revision.
- Where is the real data? No campus observations were available. Inputs are estimates with their basis recorded. Old placeholder files were synthetic too.
- Why repeat the days? Arrivals and activity times vary. We ran {n} days per combination and reported uncertainty.
- Is one guard definitely enough? The recommendation holds under these assumptions. The study cannot prove real-campus capacity without input and queue measurements.
- Does 20% more demand mean exactly 20% more cars in every run? No. It scales the expected arrival rates. Actual counts remain random.
- Can a second guard slightly increase the reported queue maximum? The pre-check car remains on the approach while it receives service. The queue definition counts it, so a shorter total delay does not guarantee a smaller maximum approach count.
"""
    (output / "talk-track.md").write_text(notes)
