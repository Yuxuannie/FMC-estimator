from pathlib import Path
from shutil import copyfile

from fmc_estimator.cell_arc import parse_cell_arc_points
from fmc_estimator.fmc_command import parse_fmc_command_file
from fmc_estimator.manifest import (
    build_manifest_row,
    build_manifest_rows_from_directory,
    build_manifest_rows_from_subfolders,
)
from fmc_estimator.spice import parse_spice_deck


ROOT = Path(__file__).resolve().parents[1]


def test_build_manifest_row_uses_only_pre_run_sources():
    cell_arc = next(
        row
        for row in parse_cell_arc_points(ROOT / "cell_arc_pt.csv")
        if row.dir_name == "hold_SDFSRPQSXGMZD4BWP130HPNPN3P48CPD_SI_fall_CP_rise_notCD_D_SDN_SE_2-4"
    )
    command = parse_fmc_command_file(ROOT / "fmc2.csh")
    spice = parse_spice_deck(ROOT / "mc_sim.sp")

    manifest = build_manifest_row(cell_arc=cell_arc, command=command, spice=spice)

    assert manifest.feature_kind == "pre_run_feature"
    assert manifest.task_id == "hold_SDFSRPQSXGMZD4BWP130HPNPN3P48CPD_SI_fall_CP_rise_notCD_D_SDN_SE_2-4"
    assert manifest.cell_arc.cell == "SDFSRPQSXGMZD4BWP130HPNPN3P48CPD"
    assert manifest.command.values["input_deck"] == "./mc_sim.sp"
    assert manifest.spice.params["constr_pin_slew"] == "0.5336n"
    assert manifest.spice.measurements == ["cp2q_del1", "cp2q_del2", "cp2d"]


def test_build_manifest_rows_from_directory_matches_subfolder_decks(tmp_path):
    target_dir = "hold_SDFSRPQSXGMZD4BWP130HPNPN3P48CPD_SI_fall_CP_rise_notCD_D_SDN_SE_2-4"
    deck_dir = tmp_path / target_dir
    deck_dir.mkdir()
    copyfile(ROOT / "mc_sim.sp", deck_dir / "mc_sim.sp")

    rows, missing = build_manifest_rows_from_directory(
        root_dir=tmp_path,
        cell_arc_points=parse_cell_arc_points(ROOT / "cell_arc_pt.csv"),
        command=parse_fmc_command_file(ROOT / "fmc2.csh"),
    )

    assert missing
    assert len(rows) == 1
    assert rows[0].task_id == target_dir
    assert rows[0].spice.deck_path == "mc_sim.sp"
    assert rows[0].command.values["input_deck"] == "./mc_sim.sp"


def test_build_manifest_rows_from_subfolders_without_cell_arc_csv(tmp_path):
    target_dir = "hold_SDFSRPQSXGMZD4BWP130HPNPN3P48CPD_SI_fall_CP_rise_notCD_D_SDN_SE_2-4"
    deck_dir = tmp_path / target_dir
    deck_dir.mkdir()
    copyfile(ROOT / "mc_sim.sp", deck_dir / "mc_sim.sp")
    (tmp_path / "notes.txt").write_text("not a task folder")

    rows, skipped = build_manifest_rows_from_subfolders(
        root_dir=tmp_path,
        command=parse_fmc_command_file(ROOT / "fmc2.csh"),
    )

    assert skipped == []
    assert len(rows) == 1
    assert rows[0].task_id == target_dir
    assert rows[0].cell_arc.dir_name == target_dir
    assert rows[0].cell_arc.cell == "SDFSRPQSXGMZD4BWP130HPNPN3P48CPD"
    assert rows[0].cell_arc.drive == "D4"
    assert rows[0].cell_arc.arc == "hold"
    assert rows[0].cell_arc.constr_pin == "SI"
    assert rows[0].cell_arc.constr_dir == "fall"
    assert rows[0].cell_arc.rel_pin == "CP"
    assert rows[0].cell_arc.rel_dir == "rise"
    assert rows[0].cell_arc.when_pins == "notCD_D_SDN_SE"
    assert rows[0].cell_arc.rel_slew_idx == 2
    assert rows[0].cell_arc.constr_slew_idx == 4
