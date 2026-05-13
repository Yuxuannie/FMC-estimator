from pathlib import Path

from fmc_estimator.fmc_command import parse_fmc_command_file


ROOT = Path(__file__).resolve().parents[1]


def test_parse_uncommented_fmc_command_from_csh_script():
    config = parse_fmc_command_file(ROOT / "fmc2.csh")

    assert config.feature_kind == "pre_run_feature"
    assert config.source == "fmc2.csh"
    assert config.values["input_deck"] == "./mc_sim.sp"
    assert config.values["output_path"] == "./"
    assert config.values["target_type"] == "constraint"
    assert config.values["nsamples"] == 25000
    assert config.values["ncpu_sens"] == 5
    assert config.values["ncpu_retrain"] == 5
    assert config.values["opt_meas_name"] == "cp2d"
    assert config.values["mos_prefix"] == "X"
    assert config.values["sim_type"] == "bisect"
    assert config.values["relin"] == 1.0e-13
    assert config.values["finfet"] == 1
    assert config.values["process_node"] == "n2"
    assert config.values["lsf_queue"] == "all"
    assert config.values["hspice_cshrc"] == "/tools/dotfile_new/cshrc.hspice"
    assert config.values["hspice_version"] == "V-2023.12-SP2-2"
