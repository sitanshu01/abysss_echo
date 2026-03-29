"""Pipeline orchestration for Abyssal Echo."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from abyssal_echo.clock_sync import apply_clock_correction, compute_sensor_drift
from abyssal_echo.data_loader import DatasetPaths, load_datasets, maybe_generate_synthetic_data
from abyssal_echo.doppler_velocity import attach_engine_frequency, solve_submarine_velocity, summarize_speed
from abyssal_echo.echo_filter import flag_primary_signals, keep_primary_signals
from abyssal_echo.sound_speed import enrich_with_sound_speed
from abyssal_echo.triangulation import reconstruct_trajectory


@dataclass(frozen=True)
class PipelineOutputs:
    cleaned_pings: pd.DataFrame
    drift_offsets: pd.DataFrame
    trajectory: pd.DataFrame
    speed_summary: pd.DataFrame


def run_pipeline(paths: DatasetPaths, output_dir: Path | str = "outputs") -> PipelineOutputs:
    """Execute the full acoustic reconstruction pipeline."""
    maybe_generate_synthetic_data(paths)
    acoustic_pings, engine_logs = load_datasets(paths)

    enriched = enrich_with_sound_speed(acoustic_pings)
    flagged = flag_primary_signals(enriched)
    primary = keep_primary_signals(flagged)

    drift = compute_sensor_drift(primary)
    corrected = apply_clock_correction(flagged, drift)
    corrected_primary = corrected.loc[corrected["Is_Primary"]].copy()

    doppler_ready = attach_engine_frequency(corrected_primary, engine_logs)
    doppler = solve_submarine_velocity(doppler_ready)
    trajectory = reconstruct_trajectory(doppler.loc[doppler["Source_Label"].eq("nautilus")].copy())
    speed_summary = summarize_speed(doppler.loc[doppler["Source_Label"].eq("nautilus")].copy())

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    corrected.to_csv(out_dir / "cleaned_acoustic_pings.csv", index=False)
    drift.to_csv(out_dir / "sensor_clock_drift.csv", index=False)
    doppler.to_csv(out_dir / "doppler_enriched_pings.csv", index=False)
    speed_summary.to_csv(out_dir / "doppler_speed_summary.csv", index=False)
    trajectory.to_csv(out_dir / "reconstructed_trajectory.csv", index=False)

    return PipelineOutputs(
        cleaned_pings=corrected,
        drift_offsets=drift,
        trajectory=trajectory,
        speed_summary=speed_summary,
    )

