# FMC Estimator Parser Spec

This project is in phase 1: parse and classify available data before training an estimator. The production estimator must predict one runtime/resource label per `cell_arc_pt` without reading a future `fastmontecarlo.log`.

## Prediction-Time Features

These fields are available before FMC simulation starts and may be used as estimator inputs.

- `cell_arc_pt.csv`: `cell`, `drive`, `arc`, `constr_pin`, `constr_dir`, `rel_pin`, `rel_dir`, `when_pins`, `rel_slew_idx`, `constr_slew_idx`, `dir_name`.
- `cell_arc_pt` folder name: when `cell_arc_pt.csv` is not provided, the folder
  name is parsed directly. Supported forms:
  - Hash-delimited AIQC style:
    `CMPE42D1BWP240H8P57CPD#B#A&!C&CIX&D#fall_3_5`
  - Underscore prediction style:
    `hold_SDFSRPQSXGMZD4BWP130HPNPN3P48CPD_SI_fall_CP_rise_notCD_D_SDN_SE_2-4`
  - Min-pulse-width style with a prefix:
    `lib_char_auto_min_pulse_width_CKLNQOPPZPDMZD4BWP130HPNPN3P48CPD_CP_rise_CP_rise_E_notTE_1-1`
- `fmc2.csh`: `input_deck`, `output_path`, `target_type`, `nsamples`, `ncpu_sens`, `ncpu_retrain`, `opt_meas_name`, `mos_prefix`, `sim_type`, `relin`, `finfet`, `process_node`, `lsf_queue`, `hspice_cshrc`, `hspice_version`.
- `mc_sim.sp`: deck header metadata, include paths, params, options, temp, measurements, analysis directives, and top-level instances.

`when_pins` preserves the raw folder/CSV text. `when_condition` is a normalized
feature where leading `not` is converted to Liberty/STA-style `!`, such as
`notTE -> !TE` and `notCD_D_SDN_SE -> !CD_D_SDN_SE`.

The manifest builder combines these into one `ManifestRow` per selected `cell_arc_pt`. It intentionally does not accept or read `fmc.log`.

## Training Labels and Post-Run Metadata

These fields come from completed FMC log/OCR text and must not be used as prediction-time features.

- Runtime labels: `total_effort_cpu_hrs`, `sensitivity_effort_cpu_hrs`, `convergence_effort_cpu_hrs`, `total_wall_time_hrs`, sensitivity/convergence wall time.
- Completion labels: `status`, sample counts, clients used.
- Post-run metadata: sample lifecycle events, client job IDs, `SIM_RESULTS`, and parameter result rows.

For the current OCR sample, the primary target is:

```text
Total effort [CPU-hrs] = 4.09413
```

`Total wall time [hrs] = 0.758002` is retained as an auxiliary label.

## Local Smoke Commands

Run tests:

```bash
python -m pytest -v
```

Parse the completed log/OCR notes:

```bash
PYTHONPATH=src python -m fmc_estimator.cli parse-log fmc.log
```

Build one pre-run manifest row:

```bash
PYTHONPATH=src python -m fmc_estimator.cli manifest \
  --cell-arc-csv cell_arc_pt.csv \
  --dir-name hold_SDFSRPQSXGMZD4BWP130HPNPN3P48CPD_SI_fall_CP_rise_notCD_D_SDN_SE_2-4 \
  --command fmc2.csh \
  --spice mc_sim.sp
```

Build a pre-run manifest for a Linux run directory where every `cell_arc_pt`
sub-folder contains its own `mc_sim.sp` and the shared `fmc2.csh` lives outside
the sub-folders:

```bash
PYTHONPATH=src python -m fmc_estimator.cli manifest-dir \
  --root-dir /path/to/run_root \
  --command /path/to/fmc2.csh \
  --output /path/to/manifest.jsonl
```

The command scans each direct sub-folder under `/path/to/run_root`, reads
`<sub-folder>/mc_sim.sp`, and writes one JSON object per parsed `cell_arc_pt`
folder. It prints a
summary like this to stdout:

```json
{
  "missing_decks": 0,
  "missing_dir_names": [],
  "mode": "scan_subfolders",
  "output": "/path/to/manifest.jsonl",
  "rows_written": 51
}
```

If you also have `cell_arc_pt.csv`, pass `--cell-arc-csv /path/to/cell_arc_pt.csv`
to filter/order by that list and use its metadata. Without the CSV, metadata is
inferred from the sub-folder name and `mc_sim.sp` header. If `missing_decks` is
nonzero, the first 20 missing folder names are shown in `missing_dir_names`. That
summary is safe to share for debugging because it does not include sensitive deck
contents.
