"""Parse completed FMC log/OCR text into training labels and metadata."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from .schema import (
    FmcClientEvent,
    FmcLogParse,
    FmcRunConfig,
    FmcSampleEvent,
    FmcSampleResult,
    FmcTimingLabel,
)


LOG_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+-\s+"
    r"(?P<logger>.+?)\s+-\s+(?P<level>[A-Z]+)\s+-\s+(?P<message>.*)$"
)
OPTION_RE = re.compile(r"^(?P<key>[A-Z][A-Z0-9_]+)\s+::\s+(?P<value>.*)$")
JOB_ID_RE = re.compile(r"Associated Job ID is (?P<job_id>\d+)")
SPAWN_CLIENT_RE = re.compile(r"Spawn client (?P<client_id>\d+)")
CLIENT_AVAILABLE_RE = re.compile(r"Client (?P<client_id>\d+) is available\.")
SAMPLE_FIRST_RE = re.compile(r"sample_id (?P<sample_id>.+?) is simulated for first time\.")
SAMPLE_DISPATCH_RE = re.compile(r"Simulating sample (?P<sample_id>.+?) on client (?P<client_id>\d+)")
SIM_RESULT_RE = re.compile(r"Received SIM_RESULTS:::(?P<body>.*?) contents")
PARAM_RESULT_RE = re.compile(r"Parameter and simulated value (?P<body>\(.+\))")
METRIC_RE = re.compile(r"(?P<name>[A-Za-z][A-Za-z /\-\[\]%]+?)\s*=\s*(?P<value>[^\s]+)")


def parse_fmc_log(path: str | Path) -> FmcLogParse:
    log_path = Path(path)
    text = log_path.read_text()

    config: dict[str, Any] = {}
    client_events: list[FmcClientEvent] = []
    sample_events: list[FmcSampleEvent] = []
    sample_results: list[FmcSampleResult] = []
    metrics: dict[str, Any] = {}
    current_spawn_client: int | None = None

    for raw_line in text.splitlines():
        message, timestamp = _extract_message(raw_line)
        if not message:
            continue

        if option_match := OPTION_RE.match(message):
            config[option_match.group("key")] = _coerce_scalar(option_match.group("value").strip())

        if spawn_match := SPAWN_CLIENT_RE.search(message):
            current_spawn_client = int(spawn_match.group("client_id"))
            client_events.append(
                FmcClientEvent(timestamp=timestamp, event_type="client_spawn", client_id=current_spawn_client, message=message)
            )

        if job_match := JOB_ID_RE.search(message):
            client_events.append(
                FmcClientEvent(
                    timestamp=timestamp,
                    event_type="client_job_id",
                    client_id=current_spawn_client,
                    job_id=job_match.group("job_id"),
                    message=message,
                )
            )

        if available_match := CLIENT_AVAILABLE_RE.search(message):
            client_events.append(
                FmcClientEvent(
                    timestamp=timestamp,
                    event_type="client_available",
                    client_id=int(available_match.group("client_id")),
                    message=message,
                )
            )

        if sample_first_match := SAMPLE_FIRST_RE.search(message):
            sample_events.append(
                FmcSampleEvent(
                    timestamp=timestamp,
                    event_type="sample_first_simulated",
                    sample_id=sample_first_match.group("sample_id"),
                    message=message,
                )
            )

        if dispatch_match := SAMPLE_DISPATCH_RE.search(message):
            sample_events.append(
                FmcSampleEvent(
                    timestamp=timestamp,
                    event_type="sample_dispatched",
                    sample_id=dispatch_match.group("sample_id"),
                    client_id=int(dispatch_match.group("client_id")),
                    message=message,
                )
            )

        if sim_match := SIM_RESULT_RE.search(message):
            sample_results.append(
                FmcSampleResult(sample_id=None, values=_parse_sim_result_values(sim_match.group("body")), timestamp=timestamp)
            )

        if param_match := PARAM_RESULT_RE.search(message):
            parsed_result = _parse_parameter_result(param_match.group("body"))
            if parsed_result is not None:
                sample_id, values = parsed_result
                sample_results.append(FmcSampleResult(sample_id=sample_id, values=values, timestamp=timestamp))

        if metric_match := METRIC_RE.search(message):
            metrics[_normalize_metric_name(metric_match.group("name"))] = _coerce_scalar(metric_match.group("value"))

    return FmcLogParse(
        run_config=FmcRunConfig(values=config, source=log_path.name, feature_kind="post_run_metadata"),
        client_events=client_events,
        sample_events=sample_events,
        sample_results=sample_results,
        timing_label=_build_timing_label(metrics, text),
    )


def _extract_message(raw_line: str) -> tuple[str, str | None]:
    line = raw_line.strip()
    if not line or line.startswith("```") or line.startswith("#"):
        return "", None

    if match := LOG_RE.match(line):
        return match.group("message").strip(), match.group("timestamp")
    return line, None


def _coerce_scalar(value: str) -> Any:
    clean = value.strip()
    if clean in {"True", "False"}:
        return clean == "True"
    if clean in {"None", "[blank / not visible]", ""}:
        return None
    try:
        if re.fullmatch(r"[-+]?\d+", clean):
            return int(clean)
        if re.fullmatch(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:e[-+]?\d+)?", clean, flags=re.IGNORECASE):
            return float(clean)
    except ValueError:
        return clean
    return clean


def _parse_sim_result_values(body: str) -> tuple[float, ...]:
    return tuple(float(part) for part in body.split(":::") if part)


def _parse_parameter_result(body: str) -> tuple[str, tuple[float, ...]] | None:
    if "<" in body or ">" in body:
        return None
    parsed = ast.literal_eval(body)
    return parsed[0], tuple(float(value) for value in parsed[1:])


def _normalize_metric_name(name: str) -> str:
    return (
        name.strip()
        .replace("[%]", "percent")
        .replace("[CPU-hrs]", "cpu_hrs")
        .replace("[hrs/retraining]", "hrs_per_retraining")
        .replace("[hrs/ordering]", "hrs_per_ordering")
        .replace("[hrs]", "hrs")
        .replace("/", " ")
        .replace("-", " ")
        .lower()
        .replace(" ", "_")
    )


def _build_timing_label(metrics: dict[str, Any], text: str) -> FmcTimingLabel:
    status = "complete" if "THANOS complete." in text else "unknown"
    return FmcTimingLabel(
        total_effort_cpu_hrs=metrics.get("total_effort_cpu_hrs"),
        sensitivity_effort_cpu_hrs=metrics.get("sensitivity_effort_cpu_hrs"),
        convergence_effort_cpu_hrs=metrics.get("convergence_effort_cpu_hrs"),
        total_wall_time_hrs=metrics.get("total_wall_time_hrs"),
        sensitivity_wall_time_hrs=metrics.get("sensitivity_wall_time_hrs"),
        convergence_wall_time_hrs=metrics.get("convergence_wall_time_hrs"),
        num_sensitivity_samples=metrics.get("num_sensitivity_samples"),
        num_convergence_samples=metrics.get("num_convergence_samples"),
        num_total_samples=metrics.get("num_total_samples"),
        initial_num_clients_used=metrics.get("initial_num_clients_used"),
        num_clients_used_for_convergence=metrics.get("num_clients_used_for_convergence"),
        status=status,
    )
