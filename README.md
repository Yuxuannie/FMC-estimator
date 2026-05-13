# FMC Estimator

Phase 1 parser foundation for a Fast Monte Carlo runtime estimator.

The estimator target is one runtime/resource label per `cell_arc_pt`. Production prediction must use only pre-run files such as `cell_arc_pt.csv`, `fmc2.csh`, and `mc_sim.sp`; completed FMC logs are parsed only for historical training labels and post-run metadata.

See [docs/parser_spec.md](docs/parser_spec.md) for the current schema boundary and smoke commands.

For a Linux FMC run root where each `cell_arc_pt` folder contains `mc_sim.sp`,
run:

```bash
PYTHONPATH=src python -m fmc_estimator.cli manifest-dir \
  --root-dir /path/to/run_root \
  --command /path/to/fmc2.csh \
  --output /path/to/manifest.jsonl
```

`cell_arc_pt.csv` is optional for this command. If provided with
`--cell-arc-csv`, it is used to filter/order folders and provide metadata; if it
is omitted, the parser scans sub-folders directly and infers metadata from each
folder name plus `mc_sim.sp`.
