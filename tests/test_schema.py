from fmc_estimator.schema import FmcTimingLabel, SpiceDeckFeatures


def test_timing_label_marks_total_effort_as_post_run_label():
    label = FmcTimingLabel(
        total_effort_cpu_hrs=4.09413,
        total_wall_time_hrs=0.758002,
        num_total_samples=542,
        status="complete",
    )

    assert label.feature_kind == "post_run_label"
    assert label.total_effort_cpu_hrs == 4.09413
    assert label.num_total_samples == 542


def test_spice_deck_features_are_pre_run_features():
    features = SpiceDeckFeatures(
        deck_path="mc_sim.sp",
        includes=["cell.spi"],
        params={"cl": "0.002199p"},
        measurements=["cp2d"],
        analyses=[".tran 1p 5000n sweep monte=1 monte=1"],
        instances=["X1 SI D SE CP CD SDN Q VDD VSS VPP VBB CELL"],
        header_metadata={"CELL": "SDF"},
    )

    assert features.feature_kind == "pre_run_feature"
    assert features.params["cl"] == "0.002199p"
    assert features.measurements == ["cp2d"]
