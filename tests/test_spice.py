from pathlib import Path

from fmc_estimator.spice import parse_spice_deck


ROOT = Path(__file__).resolve().parents[1]


def test_parse_mc_sim_spice_deck_features():
    features = parse_spice_deck(ROOT / "mc_sim.sp")

    assert features.feature_kind == "pre_run_feature"
    assert features.deck_path == "mc_sim.sp"
    assert features.header_metadata["CELL"] == "SDFSRPQSXGMZD4BWP130HPNPN3P48CPD"
    assert features.header_metadata["REL_PIN"] == "CP"
    assert features.header_metadata["CONSTR_PIN"] == "SI"
    assert features.header_metadata["ARC_TYPE"] == "hold"
    assert features.header_metadata["WHEN"] == "notCD_D_SDN_SE"
    assert features.header_metadata["OUTPUT_LOAD"] == "0.002199"
    assert features.header_metadata["CONSTR_CRITERIA"] == "pushout"
    assert features.header_metadata["OPT_RESULTS"] == "cp2q_del1 cp2q_del2"
    assert features.header_metadata["MEAS_DEGRADE_PER_cp2q_del1"] == "0.4"
    assert features.header_metadata["MEAS_DEGRADE_PER_cp2q_del2"] == ""
    assert features.header_metadata["CONSTR_PIN_PARAM"] == "constrained_pin_t02"
    assert len(features.includes) == 3
    assert features.includes[0].endswith("std_wv_c651.spi")
    assert features.includes[1].endswith("ssgnp_0p450v_m40c_cworst_CCworst_T.hold.inc")
    assert features.includes[2].endswith("SDFSRPQSXGMZD4BWP130HPNPN3P48CPD.spi")
    assert features.params["vdd_value"] == "0.450"
    assert features.params["cl"] == "0.002199p"
    assert features.params["rel_pin_slew"] == "0.4988n"
    assert features.params["constr_pin_slew"] == "0.5336n"
    assert features.temps == ["-40"]
    assert features.measurements == ["cp2q_del1", "cp2q_del2", "cp2d"]
    assert features.analyses == [".tran 1p 5000n sweep monte=1 monte=1"]
    assert features.instances == [
        "X1 SI D SE CP CD SDN Q VDD VSS VPP VBB SDFSRPQSXGMZD4BWP130HPNPN3P48CPD",
        "XVCP CP 0 stdvs_rise_fall_rise_fall_rise VDD='vdd_value' slew='rel_pin_slew' t01='related_pin_t01' t02='related_pin_t02' t03='related_pin_t03' t04='related_pin_t04' t05='related_pin_t05'",
        "XVSI SI 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'",
    ]
