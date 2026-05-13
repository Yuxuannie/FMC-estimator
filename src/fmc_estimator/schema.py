"""Shared parser schemas for FMC estimator phase 1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FmcRunConfig:
    """Configuration parsed from pre-run scripts or post-run FMC logs."""

    values: dict[str, Any]
    source: str
    feature_kind: str = "pre_run_feature"


@dataclass(frozen=True)
class FmcClientEvent:
    timestamp: str | None
    event_type: str
    client_id: int | None = None
    job_id: str | None = None
    message: str = ""
    feature_kind: str = "post_run_metadata"


@dataclass(frozen=True)
class FmcSampleEvent:
    timestamp: str | None
    event_type: str
    sample_id: str | None = None
    client_id: int | None = None
    message: str = ""
    feature_kind: str = "post_run_metadata"


@dataclass(frozen=True)
class FmcSampleResult:
    sample_id: str | None
    values: tuple[float, ...]
    timestamp: str | None = None
    feature_kind: str = "post_run_metadata"


@dataclass(frozen=True)
class FmcTimingLabel:
    total_effort_cpu_hrs: float | None = None
    sensitivity_effort_cpu_hrs: float | None = None
    convergence_effort_cpu_hrs: float | None = None
    total_wall_time_hrs: float | None = None
    sensitivity_wall_time_hrs: float | None = None
    convergence_wall_time_hrs: float | None = None
    num_sensitivity_samples: int | None = None
    num_convergence_samples: int | None = None
    num_total_samples: int | None = None
    initial_num_clients_used: int | None = None
    num_clients_used_for_convergence: int | None = None
    status: str = "unknown"
    feature_kind: str = "post_run_label"


@dataclass(frozen=True)
class SpiceDeckFeatures:
    deck_path: str
    includes: list[str] = field(default_factory=list)
    libs: list[str] = field(default_factory=list)
    params: dict[str, str] = field(default_factory=dict)
    measurements: list[str] = field(default_factory=list)
    analyses: list[str] = field(default_factory=list)
    instances: list[str] = field(default_factory=list)
    header_metadata: dict[str, str] = field(default_factory=dict)
    options: list[str] = field(default_factory=list)
    temps: list[str] = field(default_factory=list)
    feature_kind: str = "pre_run_feature"


@dataclass(frozen=True)
class CellArcPoint:
    cell: str
    drive: str
    arc: str
    constr_pin: str
    constr_dir: str
    rel_pin: str
    rel_dir: str
    when_pins: str
    rel_slew_idx: int | None
    constr_slew_idx: int | None
    timestamp: str | None
    dir_name: str
    out_pin: str | None = None
    when_condition: str | None = None
    table_row_idx: int | None = None
    table_col_idx: int | None = None
    format_variant: str | None = None
    feature_kind: str = "pre_run_feature"


@dataclass(frozen=True)
class ManifestRow:
    task_id: str
    cell_arc: CellArcPoint
    command: FmcRunConfig
    spice: SpiceDeckFeatures
    feature_kind: str = "pre_run_feature"


@dataclass(frozen=True)
class FmcLogParse:
    run_config: FmcRunConfig
    client_events: list[FmcClientEvent]
    sample_events: list[FmcSampleEvent]
    sample_results: list[FmcSampleResult]
    timing_label: FmcTimingLabel
