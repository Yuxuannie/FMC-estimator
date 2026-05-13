"""Parse SPICE decks into pre-run feature records."""

from __future__ import annotations

import re
from pathlib import Path

from .schema import SpiceDeckFeatures


HEADER_LINE_RE = re.compile(r"^\*\s+(?P<body>.+)$")
INCLUDE_RE = re.compile(r"^\.(?:inc|include)\s+['\"]?(?P<path>[^'\"]+)['\"]?", re.IGNORECASE)
LIB_RE = re.compile(r"^\.lib\s+(.+)$", re.IGNORECASE)
PARAM_RE = re.compile(r"^\.param\s+(?P<name>[A-Za-z_][\w]*)\s*=\s*(?P<value>.+)$", re.IGNORECASE)
MEASURE_RE = re.compile(r"^\.meas(?:ure)?\s+(?P<name>\S+)", re.IGNORECASE)
ANALYSIS_PREFIXES = (".tran", ".dc", ".ac", ".op")


def parse_spice_deck(path: str | Path) -> SpiceDeckFeatures:
    deck_path = Path(path)
    includes: list[str] = []
    libs: list[str] = []
    params: dict[str, str] = {}
    measurements: list[str] = []
    analyses: list[str] = []
    instances: list[str] = []
    header_metadata: dict[str, str] = {}
    options: list[str] = []
    temps: list[str] = []

    for raw_line in deck_path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("*"):
            header_metadata.update(_parse_header_metadata(line))
            continue

        lower = line.lower()
        if include_match := INCLUDE_RE.match(line):
            includes.append(include_match.group("path"))
        elif lib_match := LIB_RE.match(line):
            libs.append(lib_match.group(1).strip())
        elif param_match := PARAM_RE.match(line):
            params[param_match.group("name")] = _strip_quotes(param_match.group("value").strip())
        elif lower.startswith(".options"):
            options.append(line)
        elif lower.startswith(".temp"):
            temps.append(line.split(maxsplit=1)[1].strip())
        elif measure_match := MEASURE_RE.match(line):
            measurements.append(measure_match.group("name"))
        elif lower.startswith(ANALYSIS_PREFIXES):
            analyses.append(line)
        elif line[0].upper() == "X":
            instances.append(line)

    return SpiceDeckFeatures(
        deck_path=deck_path.name,
        includes=includes,
        libs=libs,
        params=params,
        measurements=measurements,
        analyses=analyses,
        instances=instances,
        header_metadata=header_metadata,
        options=options,
        temps=temps,
    )


def _parse_header_metadata(line: str) -> dict[str, str]:
    match = HEADER_LINE_RE.match(line)
    if not match:
        return {}
    body = match.group("body")
    if "|" not in body:
        return {}

    metadata: dict[str, str] = {}
    parts = [part.strip() for part in body.split("|")]
    if len(parts) == 2:
        left_tokens = parts[0].split()
        if len(left_tokens) == 1:
            return {left_tokens[0]: parts[1]}
        if left_tokens[0] == "MEAS_DEGRADE_PER":
            suffix = "_".join(left_tokens[1:])
            return {f"MEAS_DEGRADE_PER_{suffix}": parts[1]}

    for part in parts:
        tokens = part.strip().split(maxsplit=1)
        if len(tokens) == 2:
            metadata[tokens[0]] = tokens[1].strip()
    return metadata


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
