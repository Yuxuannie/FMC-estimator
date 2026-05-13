# Phase 1 Parser Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tested parser foundation that separates pre-run FMC estimator features from post-run training labels for one `cell_arc_pt` run.

**Architecture:** The package exposes small parser modules for FMC command scripts, FMC OCR/log text, SPICE decks, and `cell_arc_pt.csv` rows. Runtime labels come only from completed log text; prediction features come from pre-run files such as `mc_sim.sp`, `fmc2.csh`, and cell arc metadata.

**Tech Stack:** Python 3.11-compatible standard library, dataclasses, pytest.

---

### File Structure

- Create `pyproject.toml`: package metadata and pytest configuration.
- Create `src/fmc_estimator/__init__.py`: public package marker.
- Create `src/fmc_estimator/schema.py`: dataclasses for parsed records.
- Create `src/fmc_estimator/fmc_command.py`: parse `fmc` invocation flags from csh scripts.
- Create `src/fmc_estimator/fmc_log.py`: parse run config, sample events, results, and timing labels from OCR/log text.
- Create `src/fmc_estimator/spice.py`: parse SPICE deck pre-run features.
- Create `src/fmc_estimator/cell_arc.py`: parse `cell_arc_pt.csv` rows.
- Create `src/fmc_estimator/manifest.py`: combine pre-run sources into one feature row per `cell_arc_pt`.
- Create `src/fmc_estimator/cli.py`: JSON smoke-test command.
- Create `tests/test_*.py`: focused parser tests from the provided files.
- Create `docs/parser_spec.md`: field inventory and leakage boundary.

### Task 1: Package Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/fmc_estimator/__init__.py`

- [ ] Add package metadata and pytest settings.
- [ ] Run `python -m pytest`; expected initial result is collection with no tests or import errors.

### Task 2: Schemas

**Files:**
- Create: `src/fmc_estimator/schema.py`
- Test: `tests/test_schema.py`

- [ ] Write failing tests that instantiate `FmcTimingLabel` and `SpiceDeckFeatures`.
- [ ] Implement dataclasses with explicit `feature_kind`/label separation.
- [ ] Run `python -m pytest tests/test_schema.py -v`; expected pass.

### Task 3: FMC Command Parser

**Files:**
- Create: `src/fmc_estimator/fmc_command.py`
- Test: `tests/test_fmc_command.py`

- [ ] Write failing tests against `fmc2.csh` that parse `-i`, `-t`, `-ns`, `-ncpu_sens`, `-ncpu_retrain`, `-opt_meas_name`, `-sim_type`, `-relin`, `-finfet`, `-node`, `-lsf_q`, `-hspice_cshrc`, and `-hspice_ver`.
- [ ] Implement shell-like token parsing for the first uncommented `fmc` command.
- [ ] Run `python -m pytest tests/test_fmc_command.py -v`; expected pass.

### Task 4: SPICE Deck Parser

**Files:**
- Create: `src/fmc_estimator/spice.py`
- Test: `tests/test_spice.py`

- [ ] Write failing tests against `mc_sim.sp` for header metadata, includes, params, temp, measurements, tran line, and top-level instance.
- [ ] Implement line-oriented SPICE parsing with comment header support.
- [ ] Run `python -m pytest tests/test_spice.py -v`; expected pass.

### Task 5: Cell Arc Parser

**Files:**
- Create: `src/fmc_estimator/cell_arc.py`
- Test: `tests/test_cell_arc.py`

- [ ] Write failing tests against `cell_arc_pt.csv` for the first and D4 SI fall rows.
- [ ] Implement CSV parsing into `CellArcPoint`.
- [ ] Run `python -m pytest tests/test_cell_arc.py -v`; expected pass.

### Task 6: FMC Log Parser

**Files:**
- Create: `src/fmc_estimator/fmc_log.py`
- Test: `tests/test_fmc_log.py`

- [ ] Write failing tests against `fmc.log` for option config values, sample counts, total wall time, total effort CPU-hours, client count, SIM_RESULTS, and parameter result rows.
- [ ] Implement robust regex parsers that tolerate OCR markdown fences and spacing.
- [ ] Run `python -m pytest tests/test_fmc_log.py -v`; expected pass.

### Task 7: Manifest Builder

**Files:**
- Create: `src/fmc_estimator/manifest.py`
- Test: `tests/test_manifest.py`

- [ ] Write failing tests that combine one `CellArcPoint`, `mc_sim.sp`, and `fmc2.csh` into a pre-run feature row.
- [ ] Implement one-row manifest creation without reading `fmc.log`.
- [ ] Run `python -m pytest tests/test_manifest.py -v`; expected pass.

### Task 8: CLI and Docs

**Files:**
- Create: `src/fmc_estimator/cli.py`
- Create: `docs/parser_spec.md`
- Modify: `pyproject.toml`
- Test: `tests/test_cli.py`

- [ ] Write failing CLI test for JSON output.
- [ ] Implement `python -m fmc_estimator.cli` with `parse-log` and `manifest` subcommands.
- [ ] Document pre-run features vs post-run labels.
- [ ] Run full `python -m pytest -v`; expected pass.
