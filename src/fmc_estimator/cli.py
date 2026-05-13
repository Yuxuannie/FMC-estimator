"""Command-line helpers for inspecting parsed FMC inputs."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from .cell_arc import parse_cell_arc_points
from .fmc_command import parse_fmc_command_file
from .fmc_log import parse_fmc_log
from .manifest import build_manifest_row, build_manifest_rows_from_directory, build_manifest_rows_from_subfolders
from .spice import parse_spice_deck


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fmc-estimator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_log_parser = subparsers.add_parser("parse-log")
    parse_log_parser.add_argument("log_path")

    manifest_parser = subparsers.add_parser("manifest")
    manifest_parser.add_argument("--cell-arc-csv", required=True)
    manifest_parser.add_argument("--dir-name", required=True)
    manifest_parser.add_argument("--command", required=True, dest="command_path")
    manifest_parser.add_argument("--spice", required=True)

    manifest_dir_parser = subparsers.add_parser("manifest-dir")
    manifest_dir_parser.add_argument("--root-dir", required=True)
    manifest_dir_parser.add_argument("--cell-arc-csv")
    manifest_dir_parser.add_argument("--command", required=True, dest="command_path")
    manifest_dir_parser.add_argument("--output", required=True)
    manifest_dir_parser.add_argument("--deck-name", default="mc_sim.sp")

    args = parser.parse_args(argv)

    if args.command == "parse-log":
        payload = asdict(parse_fmc_log(Path(args.log_path)))
    elif args.command == "manifest":
        cell_arc = _find_cell_arc(Path(args.cell_arc_csv), args.dir_name)
        payload = asdict(
            build_manifest_row(
                cell_arc=cell_arc,
                command=parse_fmc_command_file(Path(args.command_path)),
                spice=parse_spice_deck(Path(args.spice)),
            )
        )
    elif args.command == "manifest-dir":
        command = parse_fmc_command_file(Path(args.command_path))
        if args.cell_arc_csv:
            rows, missing = build_manifest_rows_from_directory(
                root_dir=Path(args.root_dir),
                cell_arc_points=parse_cell_arc_points(Path(args.cell_arc_csv)),
                command=command,
                deck_name=args.deck_name,
            )
            mode = "cell_arc_csv"
        else:
            rows, missing = build_manifest_rows_from_subfolders(
                root_dir=Path(args.root_dir),
                command=command,
                deck_name=args.deck_name,
            )
            mode = "scan_subfolders"
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as handle:
            for row in rows:
                handle.write(json.dumps(asdict(row), sort_keys=True) + "\n")
        payload = {
            "mode": mode,
            "rows_written": len(rows),
            "missing_decks": len(missing),
            "missing_dir_names": missing[:20],
            "output": str(output_path),
        }
    else:
        raise AssertionError(f"Unhandled command: {args.command}")

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _find_cell_arc(csv_path: Path, dir_name: str):
    for row in parse_cell_arc_points(csv_path):
        if row.dir_name == dir_name:
            return row
    raise SystemExit(f"No cell_arc_pt row found for dir_name: {dir_name}")


if __name__ == "__main__":
    raise SystemExit(main())
