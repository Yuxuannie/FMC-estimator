from pathlib import Path

from fmc_estimator.fmc_log import parse_fmc_log


ROOT = Path(__file__).resolve().parents[1]


def test_parse_fmc_log_config_and_timing_labels():
    parsed = parse_fmc_log(ROOT / "fmc.log")

    assert parsed.run_config.source == "fmc.log"
    assert parsed.run_config.feature_kind == "post_run_metadata"
    assert parsed.run_config.values["SPICE_DECK"] == "./mc_sim.sp"
    assert parsed.run_config.values["SIMULATOR_TYPE"] == "hspice"
    assert parsed.run_config.values["HSPICE_VERSION"] == "V-2023.12-SP2-2"
    assert parsed.run_config.values["BATCH_SIZE"] == 5
    assert parsed.run_config.values["NSAMPL"] == 5
    assert parsed.run_config.values["MAX_NSIMS"] == 596

    label = parsed.timing_label
    assert label.feature_kind == "post_run_label"
    assert label.status == "complete"
    assert label.num_sensitivity_samples == 142
    assert label.num_convergence_samples == 400
    assert label.num_total_samples == 542
    assert label.total_wall_time_hrs == 0.758002
    assert label.sensitivity_effort_cpu_hrs == 1.22525
    assert label.convergence_effort_cpu_hrs == 2.86888
    assert label.total_effort_cpu_hrs == 4.09413
    assert label.initial_num_clients_used == 5
    assert label.num_clients_used_for_convergence == 5


def test_parse_fmc_log_sample_events_and_results():
    parsed = parse_fmc_log(ROOT / "fmc.log")

    first_sample = next(event for event in parsed.sample_events if event.sample_id == "NOMINAL")
    assert first_sample.event_type == "sample_first_simulated"

    dispatched = next(
        event
        for event in parsed.sample_events
        if event.sample_id == "x1.xout0_1:parl1:3.0" and event.event_type == "sample_dispatched"
    )
    assert dispatched.client_id == 0

    sim_result = next(result for result in parsed.sample_results if result.sample_id is None)
    assert sim_result.values == (-2.412656e-10, 1.5966189273333553e-07, 0.0)

    parameter_result = next(
        result for result in parsed.sample_results if result.sample_id == "x1.xout0_3:parl1:3.0"
    )
    assert parameter_result.values == (-2.411026e-10, 1.5966196949097114e-07, 0.0)


def test_parse_fmc_log_client_job_ids():
    parsed = parse_fmc_log(ROOT / "fmc.log")

    job_ids = [event.job_id for event in parsed.client_events if event.event_type == "client_job_id"]
    assert job_ids == ["59183785", "59183793", "59183801", "59183819", "59183844"]
