from pathlib import Path

from fmc_estimator.cell_arc import parse_cell_arc_point, parse_cell_arc_points


ROOT = Path(__file__).resolve().parents[1]


def test_parse_cell_arc_points_from_csv():
    rows = parse_cell_arc_points(ROOT / "cell_arc_pt.csv")

    assert len(rows) == 51
    first = rows[0]
    assert first.feature_kind == "pre_run_feature"
    assert first.cell == "SDFQSXG0MZD4BWP130HPNPN3P48CPD"
    assert first.drive == "D4"
    assert first.arc == "hold"
    assert first.constr_pin == "SI"
    assert first.constr_dir == "rise"
    assert first.rel_pin == "CP"
    assert first.rel_dir == "rise"
    assert first.when_pins == "D_SE"
    assert first.rel_slew_idx == 3
    assert first.constr_slew_idx == 3
    assert first.dir_name == "hold_SDFQSXG0MZD4BWP130HPNPN3P48CPD_SI_rise_CP_rise_D_SE_3-3"


def test_parse_d4_si_fall_row():
    rows = parse_cell_arc_points(ROOT / "cell_arc_pt.csv")
    row = next(
        item
        for item in rows
        if item.cell == "SDFSRPQSXGMZD4BWP130HPNPN3P48CPD"
        and item.dir_name.endswith("SI_fall_CP_rise_notCD_D_SDN_SE_2-4")
    )

    assert row.cell == "SDFSRPQSXGMZD4BWP130HPNPN3P48CPD"
    assert row.drive == "D4"
    assert row.constr_pin == "SI"
    assert row.constr_dir == "fall"
    assert row.rel_slew_idx == 2
    assert row.constr_slew_idx == 4


def test_parse_prediction_hold_cell_arc_pt_from_folder_name():
    row = parse_cell_arc_point(
        "hold_SDFSRPQSXGMZD4BWP130HPNPN3P48CPD_SI_fall_CP_rise_notCD_D_SDN_SE_2-4"
    )

    assert row.format_variant == "underscore"
    assert row.cell == "SDFSRPQSXGMZD4BWP130HPNPN3P48CPD"
    assert row.drive == "D4"
    assert row.arc == "hold"
    assert row.constr_pin == "SI"
    assert row.constr_dir == "fall"
    assert row.rel_pin == "CP"
    assert row.rel_dir == "rise"
    assert row.when_pins == "notCD_D_SDN_SE"
    assert row.when_condition == "!CD_D_SDN_SE"
    assert row.table_row_idx == 2
    assert row.table_col_idx == 4


def test_parse_aiqc_hash_cell_arc_pt():
    row = parse_cell_arc_point("CMPE42D1BWP240H8P57CPD#B#A&!C&CIX&D#fall_3_5")

    assert row.format_variant == "hash"
    assert row.cell == "CMPE42D1BWP240H8P57CPD"
    assert row.drive == "D1"
    assert row.out_pin == "B"
    assert row.arc == "fall"
    assert row.when_condition == "A&!C&CIX&D"
    assert row.table_row_idx == 3
    assert row.table_col_idx == 5


def test_parse_min_pulse_width_cell_arc_pt_with_prefix():
    row = parse_cell_arc_point("lib_char_auto_min_pulse_width_CKLNQOPPZPDMZD4BWP130HPNPN3P48CPD_CP_rise_CP_rise_E_notTE_1-1")

    assert row.format_variant == "underscore"
    assert row.arc == "min_pulse_width"
    assert row.cell == "CKLNQOPPZPDMZD4BWP130HPNPN3P48CPD"
    assert row.drive == "D4"
    assert row.rel_pin == "CP"
    assert row.rel_dir == "rise"
    assert row.constr_pin == "CP"
    assert row.constr_dir == "rise"
    assert row.when_pins == "E_notTE"
    assert row.when_condition == "E_!TE"
    assert row.table_row_idx == 1
    assert row.table_col_idx == 1
