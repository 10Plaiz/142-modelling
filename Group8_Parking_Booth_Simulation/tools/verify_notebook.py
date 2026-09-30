#!/usr/bin/env python3
"""Execute and check the real notebook in isolated scratch space."""
from argparse import ArgumentParser
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import traceback

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
import numpy as np
import pandas as pd
from PIL import Image
from scipy.stats import t

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parent
NOTEBOOK = "Parking_Booth_Simulation.ipynb"
INPUTS = ["arrival_rates.csv", "input_parameters.csv"]
sys.path.insert(0, str(PROJECT))
import parking_sim as ps


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def doctor():
    if sys.version_info[:2] != (3, 12) or Path(sys.prefix) != REPO / ".venv":
        raise RuntimeError("Run with uv run --locked from this repository's Python 3.12 environment")
    ps.load_inputs(PROJECT / "data")
    nb = nbformat.read(PROJECT / NOTEBOOK, as_version=4)
    nbformat.validate(nb)
    print(f"DOCTOR PASS: Python {sys.version.split()[0]}; {sys.executable}; valid notebook and campus inputs", flush=True)
    return nb


def check_statistics(table, raw, condition, *, paired=False):
    """Recalculate exported intervals directly from the daily observations."""
    key = "comparison" if paired else "configuration"
    assert not table.duplicated([condition, key, "measure"]).any(), "Duplicate statistical row"
    assert set(table[condition]) == set(raw[condition]), "Missing statistical input condition"
    for row in table.itertuples():
        group = raw[raw[condition] == getattr(row, condition)]
        if paired:
            alternative, baseline = row.comparison.split(" minus ")
            a = group[group.config == alternative].set_index("seed")[row.measure]
            b = group[group.config == baseline].set_index("seed")[row.measure]
            assert a.index.equals(b.index), "Paired seeds do not match"
            values = (a - b).to_numpy()
        else:
            values = group.loc[group.config == row.configuration, row.measure].to_numpy()
        assert len(values) >= 30 and row.n == len(values), "Invalid statistical sample size"
        mean, sd = values.mean(), values.std(ddof=1)
        se = sd / np.sqrt(len(values))
        width = t.ppf(.975, len(values)-1) * se
        assert np.allclose([row.mean, row.sd, row.ci_low, row.ci_high],
                           [mean, sd, mean-width, mean+width]), "Incorrect exported statistics"
        if paired:
            width = t.ppf(1-.05/6, len(values)-1) * se
            assert np.allclose([row.bonferroni_ci_low, row.bonferroni_ci_high],
                               [mean-width, mean+width]), "Incorrect adjusted paired interval"


def verify_exports(work, notebook):
    results = work / "results"
    raw = pd.read_csv(results / "replications_raw.csv")
    summary = pd.read_csv(results / "summary_by_config.csv")
    checks = pd.read_csv(results / "verification_checks.csv")
    probabilities = pd.read_csv(results / "spillover_probability.csv")
    planning = pd.read_csv(results / "replication_followup.csv")
    assert not checks.empty and checks["pass"].eq(True).all(), "A model check failed"
    assert planning.target_met.eq(True).all(), "One or more stated precision targets were not met"
    assert set(raw.demand) == {0.8, 1., 1.2}, "Missing required demand level"
    assert set(raw.config) == {c.name for c in ps.CONFIGS}, "Missing required schedule"
    assert not raw.duplicated(["demand", "config", "seed"]).any(), "Duplicate replication"
    sizes = raw.groupby(["demand", "config"]).size()
    assert len(sizes) == 9 and sizes.nunique() == 1 and sizes.min() >= 30, "Incomplete nine-combination study"
    n = int(sizes.iloc[0])
    for _, group in raw.groupby(["demand", "config"]):
        assert set(group.seed) == set(range(1, n+1)), "Missing or inconsistent recorded seed"
    metrics = ["avg_delay_sec", "max_queue_veh", "guard_utilization", "spillover_min"]
    assert np.isfinite(raw[metrics]).all().all(), "Nonfinite replication output"
    assert (raw[metrics] >= -1e-9).all().all(), "Negative performance measure"
    assert raw.guard_utilization.between(0, 1).all(), "Invalid guard utilization"
    assert len(summary) == 36 and not summary.duplicated(["demand", "configuration", "measure"]).any()
    assert set(summary.measure) == set(metrics)
    for row in summary.itertuples():
        values = raw.loc[(raw.demand == row.demand) & (raw.config == row.configuration), row.measure]
        assert row.n == n and np.isclose(row.mean, values.mean()), "Summary does not match raw replications"
        assert row.ci_low <= row.mean <= row.ci_high, "Invalid output confidence interval"
    assert len(probabilities) == 9
    for row in probabilities.itertuples():
        sub = raw[(raw.demand == row.demand) & (raw.config == row.configuration)]
        assert row.days == n and row.spillover_days == int((sub.spillover_min > 0).sum())
        assert 0 <= row.ci_low <= row.p_hat+1e-12 and row.p_hat <= row.ci_high+1e-12 <= 1+1e-12
    supplementary = pd.read_csv(results / "supplementary_summary.csv")
    supplementary_pairs = pd.read_csv(results / "supplementary_paired_differences.csv")
    pairs = pd.read_csv(results / "paired_differences.csv")
    extra_metrics = {"avg_delay_morning_sec", "avg_initial_wait_sec", "effective_guard_hours"}
    assert len(supplementary) == 27 and set(supplementary.measure) == extra_metrics
    assert len(supplementary_pairs) == 27 and set(supplementary_pairs.measure) == extra_metrics
    check_statistics(summary, raw, "demand")
    check_statistics(pairs, raw, "demand", paired=True)
    check_statistics(supplementary, raw, "demand")
    check_statistics(supplementary_pairs, raw, "demand", paired=True)
    activity = pd.read_csv(results / "activity_replications_raw.csv")
    activity_summary = pd.read_csv(results / "activity_sensitivity.csv")
    activity_pairs = pd.read_csv(results / "activity_paired_differences.csv")
    activity_plan = pd.read_csv(results / "activity_replication_planning.csv")
    assert set(activity.activity_scale) == {.8, 1., 1.2} and activity.demand.eq(1.).all()
    assert set(activity.config) == set(raw.config)
    assert not activity.duplicated(["activity_scale", "config", "seed"]).any()
    activity_sizes = activity.groupby(["activity_scale", "config"]).size()
    assert len(activity_sizes) == 9 and activity_sizes.nunique() == 1 and activity_sizes.min() >= 30
    for _, group in activity.groupby(["activity_scale", "config"]):
        assert set(group.seed) == set(range(1, len(group)+1)), "Invalid timing-test seeds"
    assert np.isfinite(activity[metrics + list(extra_metrics)]).all().all()
    assert (activity[metrics + list(extra_metrics)] >= -1e-9).all().all()
    assert activity.guard_utilization.between(0, 1).all()
    assert len(activity_summary) == 63 and len(activity_pairs) == 63
    assert set(activity_summary.measure) == set(metrics) | extra_metrics
    assert activity_plan.target_met.eq(True).all(), "Timing-test precision target unmet"
    normal = raw[raw.demand == 1.].set_index(["config", "seed"])
    timing_base = activity[activity.activity_scale == 1.].set_index(["config", "seed"])
    shared = normal.index.intersection(timing_base.index)
    assert len(shared) == len(normal)
    assert np.allclose(normal.loc[shared, metrics], timing_base.loc[shared, metrics]), "Timing baseline differs from main experiment"
    for seed, group in activity.groupby("seed"):
        assert group.n_vehicles.nunique() == 1 and group.n_refused.nunique() == 1, "Timing test changed arrivals or sticker types"
    check_statistics(activity_summary, activity, "activity_scale")
    check_statistics(activity_pairs, activity, "activity_scale", paired=True)
    expected_figures = ["conceptual_model.png", "arrival_profile.png", "measures_ci.png",
                        "demand_sensitivity.png", "queue_profile.png", "morning_comparison.png",
                        "activity_sensitivity.png"]
    for name in expected_figures:
        with Image.open(work / "figures" / name) as img:
            img.verify()
    assert (results / "input_provenance.csv").is_file()
    assert (results / "recommendation.md").is_file()
    for cell in notebook.cells:
        if cell.cell_type == "code":
            assert cell.execution_count is not None, "A code cell was skipped"
            assert not any(o.output_type == "error" for o in cell.outputs), "Notebook contains an execution error"
    return {"replications": len(raw), "days_per_combination": n, "combinations": 9,
            "passed_checks": len(checks), "precision_targets_met": True, "figure_count": len(expected_figures),
            "activity_test_rows": len(activity), "activity_days_per_combination": int(activity_sizes.min()),
            "activity_precision_targets_met": True}


def publish(evidence):
    """Preserve previous generated exports, then copy the checked run into place."""
    archive = PROJECT / "archive" / "pre-presentation"
    for folder in ["results", "figures"]:
        target = PROJECT / folder
        source = evidence / folder
        if not source.is_dir():
            continue
        target.mkdir(exist_ok=True)
        # Archive generated files only. No model source or input CSV is moved.
        for old in sorted(target.iterdir()):
            if old.is_file() and old.suffix in {".csv", ".png", ".pdf", ".md"}:
                saved = archive / folder / old.name
                saved.parent.mkdir(parents=True, exist_ok=True)
                if not saved.exists():
                    shutil.copy2(old, saved)
                if not (source / old.name).exists():
                    old.unlink()
        for item in source.iterdir():
            if item.is_file():
                shutil.copy2(item, target / item.name)
    shutil.copy2(evidence / NOTEBOOK, PROJECT / NOTEBOOK)
    print("Published verified notebook and exports; previous generated exports preserved under archive/pre-presentation", flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--doctor", action="store_true", help="Read-only environment, input, and notebook checks")
    parser.add_argument("--publish", action="store_true", help="Refresh working exports only after a passing run; archive prior generated files")
    args = parser.parse_args()
    if args.doctor and args.publish:
        parser.error("--doctor and --publish are separate operations")
    nb = doctor()
    if args.doctor:
        return
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    evidence = Path(tempfile.mkdtemp(prefix=run_id+"-", dir=_evidence_root()))
    status = {"status": "failed", "python": sys.executable, "command": sys.argv,
              "input_hashes": {name: digest(PROJECT / "data" / name) for name in INPUTS},
              "source_hashes": {name: digest(PROJECT / name) for name in [NOTEBOOK, "parking_sim.py", "tools/build_presentation.py"]}}
    started = time.monotonic()
    os.environ["PARKING_EXPECTED_PREFIX"] = sys.prefix
    os.environ["MPLBACKEND"] = "module://matplotlib_inline.backend_inline"
    log = evidence / "execution.log"
    log.write_text(f"Action: fresh-kernel Run All\nCommand: {' '.join(sys.argv)}\nPython: {sys.executable}\n")
    try:
        with tempfile.TemporaryDirectory(prefix="parking-notebook-") as scratch:
            work = Path(scratch)
            (work / "data").mkdir(); (work / "tools").mkdir()
            shutil.copy2(PROJECT / "parking_sim.py", work / "parking_sim.py")
            shutil.copy2(PROJECT / "tools" / "build_presentation.py", work / "tools" / "build_presentation.py")
            for name in INPUTS:
                shutil.copy2(PROJECT / "data" / name, work / "data" / name)
            for cell in nb.cells:
                if cell.cell_type == "code":
                    cell.outputs = []; cell.execution_count = None
                    cell.metadata.pop("execution", None)

            def record_cell(cell, cell_index, **kwargs):
                with log.open("a") as stream:
                    stream.write(f"Execute code cell {cell_index}: {cell.source.splitlines()[0]}\n")

            client = NotebookClient(nb, timeout=600, kernel_name="python3",
                                    resources={"metadata": {"path": str(work)}},
                                    on_cell_execute=record_cell)
            try:
                client.execute()
                status.update(verify_exports(work, nb))
                for name in INPUTS:
                    assert digest(work / "data" / name) == status["input_hashes"][name], "Scratch input changed"
                    assert digest(PROJECT / "data" / name) == status["input_hashes"][name], "Repository input changed"
                status["status"] = "passed"
            finally:
                nbformat.write(nb, evidence / NOTEBOOK)
                html, _ = HTMLExporter().from_notebook_node(nb)
                (evidence / "notebook.html").write_text(html)
                for folder in ["results", "figures"]:
                    if (work / folder).is_dir():
                        shutil.copytree(work / folder, evidence / folder)
                with log.open("a") as stream:
                    for i, cell in enumerate(nb.cells):
                        if cell.cell_type == "code":
                            for output in cell.outputs:
                                if output.output_type == "stream":
                                    stream.write(f"Cell {i} {output.name}: {output.text}\n")
                                elif output.output_type == "error":
                                    stream.write("\n".join(output.traceback)+"\n")
    except Exception:
        status["error"] = traceback.format_exc()
        with log.open("a") as stream:
            stream.write(status["error"])
        raise
    finally:
        status["seconds"] = round(time.monotonic()-started, 2)
        status["scratch_removed"] = True
        status["output_hashes"] = {str(p.relative_to(evidence)): digest(p) for p in evidence.rglob("*") if p.is_file()}
        (evidence / "manifest.json").write_text(json.dumps(status, indent=2)+"\n")
        print(f"Evidence: {evidence}\nStatus: {status['status']}; scratch removed", flush=True)
    if args.publish:
        publish(evidence)
    print(json.dumps({k: status[k] for k in ["status", "replications", "passed_checks", "days_per_combination"]}), flush=True)


def _evidence_root():
    root = REPO / "artifacts" / "notebook-verification"
    root.mkdir(parents=True, exist_ok=True)
    return root


if __name__ == "__main__":
    main()
