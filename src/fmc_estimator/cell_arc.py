"""Parse cell_arc_pt CSV files into task identity features."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from .schema import CellArcPoint

ARC_TOKENS = {"delay", "slew", "hold", "setup", "recovery", "removal"}


def parse_cell_arc_points(path: str | Path) -> list[CellArcPoint]:
    with Path(path).open(newline="") as handle:
        return [_row_to_cell_arc(row) for row in csv.DictReader(handle)]


def parse_cell_arc_point(value: str) -> CellArcPoint:
    if "#" in value:
        return _parse_hash_cell_arc_point(value)
    return _parse_underscore_cell_arc_point(value)


def _row_to_cell_arc(row: dict[str, str]) -> CellArcPoint:
    when_pins = row["when_pins"]
    rel_slew_idx = int(row["rel_slew_idx"])
    constr_slew_idx = int(row["constr_slew_idx"])
    return CellArcPoint(
        cell=row["cell"],
        drive=row["drive"],
        arc=row["arc"],
        constr_pin=row["constr_pin"],
        constr_dir=row["constr_dir"],
        rel_pin=row["rel_pin"],
        rel_dir=row["rel_dir"],
        when_pins=when_pins,
        rel_slew_idx=rel_slew_idx,
        constr_slew_idx=constr_slew_idx,
        timestamp=row["timestamp"],
        dir_name=row["dir_name"],
        when_condition=_normalize_when_condition(when_pins),
        table_row_idx=rel_slew_idx,
        table_col_idx=constr_slew_idx,
        format_variant="csv",
    )


def _parse_hash_cell_arc_point(value: str) -> CellArcPoint:
    parts = value.split("#")
    if len(parts) != 4:
        raise ValueError(f"Unsupported hash cell_arc_pt format: {value}")

    cell, out_pin, when_pins, final = parts
    final_match = re.fullmatch(r"(?P<arc>[A-Za-z]+)_(?P<row>\d+)_(?P<col>\d+)", final)
    if not final_match:
        raise ValueError(f"Unsupported hash cell_arc_pt table point: {value}")
    row_idx = int(final_match.group("row"))
    col_idx = int(final_match.group("col"))

    return CellArcPoint(
        cell=cell,
        drive=_infer_drive(cell),
        arc=final_match.group("arc"),
        constr_pin="",
        constr_dir="",
        rel_pin="",
        rel_dir=final_match.group("arc"),
        when_pins=when_pins,
        rel_slew_idx=row_idx,
        constr_slew_idx=col_idx,
        timestamp=None,
        dir_name=value,
        out_pin=out_pin,
        when_condition=_normalize_when_condition(when_pins, separator="&"),
        table_row_idx=row_idx,
        table_col_idx=col_idx,
        format_variant="hash",
    )


def _parse_underscore_cell_arc_point(value: str) -> CellArcPoint:
    parts = value.split("_")
    arc_index = _find_arc_index(parts)
    if arc_index is None:
        raise ValueError(f"Unsupported underscore cell_arc_pt format: {value}")

    if parts[arc_index : arc_index + 3] == ["min", "pulse", "width"]:
        return _parse_min_pulse_width(value, parts, arc_index)
    return _parse_standard_underscore(value, parts, arc_index)


def _find_arc_index(parts: list[str]) -> int | None:
    for index, token in enumerate(parts):
        if parts[index : index + 3] == ["min", "pulse", "width"]:
            return index
        if token in ARC_TOKENS:
            return index
    return None


def _parse_standard_underscore(value: str, parts: list[str], arc_index: int) -> CellArcPoint:
    suffix = parts[arc_index:]
    if len(suffix) < 7:
        raise ValueError(f"Unsupported standard cell_arc_pt format: {value}")

    index_match = re.fullmatch(r"(?P<row>\d+)-(?P<col>\d+)|(?P<row2>\d+)_(?P<col2>\d+)", suffix[-1])
    if not index_match:
        raise ValueError(f"Missing table point in cell_arc_pt: {value}")

    row_idx = int(index_match.group("row") or index_match.group("row2"))
    col_idx = int(index_match.group("col") or index_match.group("col2"))
    cell = suffix[1]
    when_pins = "_".join(suffix[6:-1])

    return CellArcPoint(
        cell=cell,
        drive=_infer_drive(cell),
        arc=suffix[0],
        constr_pin=suffix[2],
        constr_dir=suffix[3],
        rel_pin=suffix[4],
        rel_dir=suffix[5],
        when_pins=when_pins,
        rel_slew_idx=row_idx,
        constr_slew_idx=col_idx,
        timestamp=None,
        dir_name=value,
        when_condition=_normalize_when_condition(when_pins),
        table_row_idx=row_idx,
        table_col_idx=col_idx,
        format_variant="underscore",
    )


def _parse_min_pulse_width(value: str, parts: list[str], arc_index: int) -> CellArcPoint:
    suffix = parts[arc_index:]
    if len(suffix) < 9:
        raise ValueError(f"Unsupported min_pulse_width cell_arc_pt format: {value}")

    point_match = re.fullmatch(r"(?P<row>\d+)-(?P<col>\d+)|(?P<row2>\d+)_(?P<col2>\d+)", suffix[-1])
    if not point_match:
        raise ValueError(f"Missing min_pulse_width table point in cell_arc_pt: {value}")

    row_idx = int(point_match.group("row") or point_match.group("row2"))
    col_idx = int(point_match.group("col") or point_match.group("col2"))
    cell = suffix[3]
    when_pins = "_".join(suffix[8:-1])

    return CellArcPoint(
        cell=cell,
        drive=_infer_drive(cell),
        arc="min_pulse_width",
        constr_pin=suffix[6],
        constr_dir=suffix[7],
        rel_pin=suffix[4],
        rel_dir=suffix[5],
        when_pins=when_pins,
        rel_slew_idx=row_idx,
        constr_slew_idx=col_idx,
        timestamp=None,
        dir_name=value,
        when_condition=_normalize_when_condition(when_pins),
        table_row_idx=row_idx,
        table_col_idx=col_idx,
        format_variant="underscore",
    )


def _normalize_when_condition(value: str, separator: str = "_") -> str | None:
    if not value or value.upper().replace("_", " ") == "NO CONDITION":
        return None
    tokens = value.split(separator)
    normalized = [re.sub(r"^not(?=[A-Z0-9])", "!", token) for token in tokens]
    return separator.join(normalized)


def _infer_drive(cell: str) -> str:
    match = re.search(r"(D\d+)(?=BWP|$)", cell)
    return match.group(1) if match else ""
