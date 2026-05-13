import json
import os
import subprocess
import sys
from pathlib import Path
from shutil import copyfile


ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def test_cli_parse_log_outputs_timing_label_json():
    completed = subprocess.run(
        [sys.executable, "-m", "fmc_estimator.cli", "parse-log", str(ROOT / "fmc.log")],
        check=True,
        capture_output=True,
        env=ENV,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["timing_label"]["total_effort_cpu_hrs"] == 4.09413
    assert payload["timing_label"]["feature_kind"] == "post_run_label"
    assert payload["run_config"]["values"]["SPICE_DECK"] == "./mc_sim.sp"


def test_cli_manifest_outputs_pre_run_feature_json():
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "fmc_estimator.cli",
            "manifest",
            "--cell-arc-csv",
            str(ROOT / "cell_arc_pt.csv"),
            "--dir-name",
            "hold_SDFSRPQSXGMZD4BWP130HPNPN3P48CPD_SI_fall_CP_rise_notCD_D_SDN_SE_2-4",
            "--command",
            str(ROOT / "fmc2.csh"),
            "--spice",
            str(ROOT / "mc_sim.sp"),
        ],
        check=True,
        capture_output=True,
        env=ENV,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["feature_kind"] == "pre_run_feature"
    assert payload["task_id"] == "hold_SDFSRPQSXGMZD4BWP130HPNPN3P48CPD_SI_fall_CP_rise_notCD_D_SDN_SE_2-4"
    assert payload["command"]["values"]["nsamples"] == 25000
    assert payload["spice"]["params"]["cl"] == "0.002199p"


def test_cli_manifest_dir_writes_jsonl_and_summary(tmp_path):
    target_dir = "hold_SDFSRPQSXGMZD4BWP130HPNPN3P48CPD_SI_fall_CP_rise_notCD_D_SDN_SE_2-4"
    deck_dir = tmp_path / "runs" / target_dir
    deck_dir.mkdir(parents=True)
    copyfile(ROOT / "mc_sim.sp", deck_dir / "mc_sim.sp")
    output_path = tmp_path / "manifest.jsonl"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "fmc_estimator.cli",
            "manifest-dir",
            "--root-dir",
            str(tmp_path / "runs"),
            "--cell-arc-csv",
            str(ROOT / "cell_arc_pt.csv"),
            "--command",
            str(ROOT / "fmc2.csh"),
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        env=ENV,
        text=True,
    )

    summary = json.loads(completed.stdout)
    assert summary["rows_written"] == 1
    assert summary["missing_decks"] == 50
    assert summary["output"] == str(output_path)

    lines = output_path.read_text().splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["task_id"] == target_dir
    assert payload["feature_kind"] == "pre_run_feature"


def test_cli_manifest_dir_can_scan_subfolders_without_cell_arc_csv(tmp_path):
    target_dir = "hold_SDFSRPQSXGMZD4BWP130HPNPN3P48CPD_SI_fall_CP_rise_notCD_D_SDN_SE_2-4"
    deck_dir = tmp_path / "runs" / target_dir
    deck_dir.mkdir(parents=True)
    copyfile(ROOT / "mc_sim.sp", deck_dir / "mc_sim.sp")
    output_path = tmp_path / "manifest.jsonl"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "fmc_estimator.cli",
            "manifest-dir",
            "--root-dir",
            str(tmp_path / "runs"),
            "--command",
            str(ROOT / "fmc2.csh"),
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        env=ENV,
        text=True,
    )

    summary = json.loads(completed.stdout)
    assert summary["rows_written"] == 1
    assert summary["missing_decks"] == 0

    payload = json.loads(output_path.read_text())
    assert payload["task_id"] == target_dir
    assert payload["cell_arc"]["cell"] == "SDFSRPQSXGMZD4BWP130HPNPN3P48CPD"
    assert payload["cell_arc"]["rel_slew_idx"] == 2
    assert payload["cell_arc"]["constr_slew_idx"] == 4
