"""Parse FMC launcher scripts into pre-run configuration features."""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any

from .schema import FmcRunConfig


FLAG_NAMES = {
    "-i": "input_deck",
    "-o": "output_path",
    "-t": "target_type",
    "-ns": "nsamples",
    "-ncpu_sens": "ncpu_sens",
    "-ncpu_retrain": "ncpu_retrain",
    "-opt_meas_name": "opt_meas_name",
    "-mos_prefix": "mos_prefix",
    "-sim_type": "sim_type",
    "-relin": "relin",
    "-finfet": "finfet",
    "-node": "process_node",
    "-lsf_q": "lsf_queue",
    "-hspice_cshrc": "hspice_cshrc",
    "-hspice_ver": "hspice_version",
}

INT_KEYS = {"nsamples", "ncpu_sens", "ncpu_retrain", "finfet"}
FLOAT_KEYS = {"relin"}


def parse_fmc_command_file(path: str | Path) -> FmcRunConfig:
    file_path = Path(path)
    command = _find_fmc_command(file_path.read_text())
    values = parse_fmc_command(command)
    return FmcRunConfig(values=values, source=file_path.name)


def parse_fmc_command(command: str) -> dict[str, Any]:
    tokens = shlex.split(command)
    if not tokens or tokens[0] != "fmc":
        raise ValueError("Expected an fmc command")

    values: dict[str, Any] = {}
    index = 1
    while index < len(tokens):
        token = tokens[index]
        key = FLAG_NAMES.get(token)
        if key is None:
            index += 1
            continue
        if index + 1 >= len(tokens):
            raise ValueError(f"Missing value for {token}")
        values[key] = _coerce_value(key, tokens[index + 1])
        index += 2

    return values


def _find_fmc_command(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("fmc "):
            return stripped
    raise ValueError("No uncommented fmc command found")


def _coerce_value(key: str, value: str) -> Any:
    if key in INT_KEYS:
        return int(value)
    if key in FLOAT_KEYS:
        return float(value)
    return value
