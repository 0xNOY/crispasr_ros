#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path

import numpy as np


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from crispasr_ros.audio_resample import candidate_capture_rates, resample_int16_mono


class AudioResampleTest(unittest.TestCase):
    def test_candidate_capture_rates_prioritize_request_then_target_then_default(self):
        self.assertEqual(
            [44100, 16000, 48000, 32000],
            candidate_capture_rates(
                target_rate=16000,
                requested_capture_rate=44100,
                default_capture_rate=48000,
            ),
        )

    def test_candidate_capture_rates_drop_empty_and_duplicate_rates(self):
        self.assertEqual(
            [16000, 48000, 44100, 32000],
            candidate_capture_rates(
                target_rate=16000,
                requested_capture_rate=0,
                default_capture_rate=16000,
            ),
        )

    def test_resamples_48khz_chunk_to_16khz_chunk(self):
        samples = np.arange(4800, dtype=np.int16)

        resampled = resample_int16_mono(samples, input_rate=48000, output_rate=16000)

        self.assertEqual(np.int16, resampled.dtype)
        self.assertEqual(1600, resampled.size)
        np.testing.assert_array_equal(np.array([0, 3, 6, 9, 12], dtype=np.int16), resampled[:5])

    def test_accepts_sounddevice_mono_shape(self):
        samples = np.arange(4800, dtype=np.int16).reshape(-1, 1)

        resampled = resample_int16_mono(samples, input_rate=48000, output_rate=16000)

        self.assertEqual(1600, resampled.size)

    def test_rejects_multichannel_audio(self):
        samples = np.zeros((10, 2), dtype=np.int16)

        with self.assertRaises(ValueError):
            resample_int16_mono(samples, input_rate=48000, output_rate=16000)


if __name__ == "__main__":
    unittest.main()
