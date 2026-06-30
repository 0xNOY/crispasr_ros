#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from crispasr_ros.confirmation import ConfirmationGate


class ConfirmationGateTest(unittest.TestCase):
    def setUp(self):
        self.gate = ConfirmationGate(
            wake_words=["eraser", "hey eraser"],
            positive_words=["yes", "ready", "release"],
            negative_words=["no", "wrong"],
            wake_window_sec=3.0,
        )

    def test_ignores_confirmation_without_wake_word(self):
        self.assertIsNone(self.gate.consume("yes", now=10.0))

    def test_accepts_wake_word_and_confirmation_in_same_utterance(self):
        result = self.gate.consume("Eraser release", now=10.0)

        self.assertIsNotNone(result)
        self.assertEqual("positive", result.intent)
        self.assertEqual("release", result.command)
        self.assertTrue(result.has_wake_word)

    def test_accepts_confirmation_inside_wake_window(self):
        self.assertIsNone(self.gate.consume("hey eraser", now=10.0))

        result = self.gate.consume("ready", now=12.0)

        self.assertIsNotNone(result)
        self.assertEqual("positive", result.intent)
        self.assertEqual("ready", result.command)
        self.assertFalse(result.has_wake_word)
        self.assertTrue(result.is_within_wake_window)

    def test_rejects_confirmation_after_wake_window(self):
        self.assertIsNone(self.gate.consume("hey eraser", now=10.0))

        self.assertIsNone(self.gate.consume("ready", now=14.1))

    def test_negative_words_override_positive_words(self):
        result = self.gate.consume("Eraser no not ready", now=10.0)

        self.assertIsNotNone(result)
        self.assertEqual("negative", result.intent)
        self.assertEqual("no", result.command)


if __name__ == "__main__":
    unittest.main()
