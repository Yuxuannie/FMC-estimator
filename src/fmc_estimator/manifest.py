"""Build pre-run manifest rows for estimator prediction features."""

from __future__ import annotations

from pathlib import Path

from .cell_arc import parse_cell_arc_point
from .spice import parse_spice_deck
from .schema import CellArcPoint, FmcRunConfig, ManifestRow, SpiceDeckFeatures


def build_manifest_row(
    *,
    cell_arc: CellArcPoint,
    command: FmcRunConfig,
    spice: SpiceDeckFeatures,
) -> ManifestRow:
    if command.feature_kind != "pre_run_feature":
        raise ValueError("Manifest command config must come from pre-run sources")
    if spice.feature_kind != "pre_run_feature":
        raise ValueError("Manifest spice features must come from pre-run sources")
    return ManifestRow(task_id=cell_arc.dir_name, cell_arc=cell_arc, command=command, spice=spice)


def build_manifest_rows_from_directory(
    *,
    root_dir: str | Path,
    cell_arc_points: list[CellArcPoint],
    command: FmcRunConfig,
    deck_name: str = "mc_sim.sp",
) -> tuple[list[ManifestRow], list[str]]:
    root_path = Path(root_dir)
    rows: list[ManifestRow] = []
    missing: list[str] = []

    for cell_arc in cell_arc_points:
        deck_path = root_path / cell_arc.dir_name / deck_name
        if not deck_path.exists():
            missing.append(cell_arc.dir_name)
            continue

        rows.append(
            build_manifest_row(
                cell_arc=cell_arc,
                command=command,
                spice=parse_spice_deck(deck_path),
            )
        )

    return rows, missing


def build_manifest_rows_from_subfolders(
    *,
    root_dir: str | Path,
    command: FmcRunConfig,
    deck_name: str = "mc_sim.sp",
) -> tuple[list[ManifestRow], list[str]]:
    root_path = Path(root_dir)
    rows: list[ManifestRow] = []
    skipped: list[str] = []

    for child in sorted(root_path.iterdir()):
        if not child.is_dir():
            continue
        deck_path = child / deck_name
        if not deck_path.exists():
            skipped.append(child.name)
            continue

        spice = parse_spice_deck(deck_path)
        rows.append(
            build_manifest_row(
                cell_arc=infer_cell_arc_point(child.name, spice),
                command=command,
                spice=spice,
            )
        )

    return rows, skipped


def infer_cell_arc_point(dir_name: str, spice: SpiceDeckFeatures) -> CellArcPoint:
    parsed = parse_cell_arc_point(dir_name)
    metadata = spice.header_metadata
    cell = metadata.get("CELL") or parsed.cell

    return CellArcPoint(
        cell=cell,
        drive=_infer_drive(cell),
        arc=metadata.get("ARC_TYPE") or parsed.arc,
        constr_pin=metadata.get("CONSTR_PIN") or parsed.constr_pin,
        constr_dir=metadata.get("CONSTR_PIN_DIR") or parsed.constr_dir,
        rel_pin=metadata.get("REL_PIN") or parsed.rel_pin,
        rel_dir=metadata.get("REL_PIN_DIR") or parsed.rel_dir,
        when_pins=metadata.get("WHEN") or parsed.when_pins,
        rel_slew_idx=parsed.rel_slew_idx,
        constr_slew_idx=parsed.constr_slew_idx,
        timestamp=None,
        dir_name=dir_name,
        out_pin=parsed.out_pin,
        when_condition=parsed.when_condition,
        table_row_idx=parsed.table_row_idx,
        table_col_idx=parsed.table_col_idx,
        format_variant=parsed.format_variant,
    )


def _infer_drive(cell: str) -> str:
    import re

    match = re.search(r"(D\d+)(?=BWP|$)", cell)
    return match.group(1) if match else ""
