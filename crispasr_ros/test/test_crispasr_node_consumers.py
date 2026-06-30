#!/usr/bin/env python3

import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PACKAGE_ROOT / "scripts" / "crispasr_node"


class CrispASRNodeConsumersTest(unittest.TestCase):
    def test_asr_node_skips_audio_when_results_have_no_consumers(self):
        source = SCRIPT_PATH.read_text()

        self.assertIn("def _has_result_consumers(self)", source)
        self.assertIn("self.pub.get_subscription_count() > 0", source)
        self.assertIn("self.confirmation_pub.get_subscription_count() > 0", source)
        self.assertIn("if self.is_sleeping or not self._has_result_consumers():", source)
        self.assertIn("if not self._has_result_consumers():", source)
        self.assertIn("self._drain_audio_queue()", source)

    def test_partial_transcription_requires_speech_result_subscriber(self):
        source = SCRIPT_PATH.read_text()

        self.assertIn("def _has_speech_result_subscribers(self)", source)
        self.assertIn("and self._has_speech_result_subscribers()", source)


if __name__ == "__main__":
    unittest.main()
