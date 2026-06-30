"""Small audio conversion helpers for ROS microphone publishing."""

from __future__ import annotations

import numpy as np


def resample_int16_mono(samples: np.ndarray, input_rate: int, output_rate: int) -> np.ndarray:
    """Resample mono int16 PCM with linear interpolation."""
    if input_rate <= 0 or output_rate <= 0:
        raise ValueError("sample rates must be positive")

    samples = np.asarray(samples)
    if samples.ndim == 2:
        if samples.shape[1] != 1:
            raise ValueError("expected mono audio")
        samples = samples[:, 0]
    elif samples.ndim != 1:
        raise ValueError("expected mono audio")

    samples = samples.astype(np.int16, copy=False)
    if input_rate == output_rate or samples.size == 0:
        return samples.copy()

    output_count = max(1, int(round(samples.size * output_rate / input_rate)))
    input_positions = np.arange(output_count, dtype=np.float64) * input_rate / output_rate
    source_positions = np.arange(samples.size, dtype=np.float64)
    resampled = np.interp(input_positions, source_positions, samples.astype(np.float32))
    return np.clip(np.rint(resampled), -32768, 32767).astype(np.int16)


def candidate_capture_rates(
    target_rate: int,
    requested_capture_rate: int = 0,
    default_capture_rate: int = 0,
) -> list[int]:
    """Return capture rates to probe, preserving order and removing duplicates."""
    rates = [
        requested_capture_rate,
        target_rate,
        default_capture_rate,
        48000,
        44100,
        32000,
        16000,
    ]
    candidates: list[int] = []
    for rate in rates:
        rate = int(round(float(rate or 0)))
        if rate > 0 and rate not in candidates:
            candidates.append(rate)
    return candidates
