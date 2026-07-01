#!/usr/bin/env python3

import argparse
import importlib.machinery
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PACKAGE_ROOT / "scripts" / "hsr_ssh_asr_demo"


def load_demo_module():
    loader = importlib.machinery.SourceFileLoader("hsr_ssh_asr_demo", str(SCRIPT_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class HsrSshAsrDemoTest(unittest.TestCase):
    def test_help_exposes_vad_tuning_options(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertIn("--vad-threshold", proc.stdout)
        self.assertIn("--silence-duration", proc.stdout)
        self.assertIn("--phrase-time-limit", proc.stdout)
        self.assertIn("--confirmation-topic", proc.stdout)
        self.assertIn("--require-confirmation-wake-word", proc.stdout)

    def test_crispasr_node_receives_noise_robust_vad_defaults(self):
        demo = load_demo_module()
        args = argparse.Namespace(
            language="en",
            audio_topic="/audio",
            vad_threshold=demo.DEFAULT_VAD_THRESHOLD,
            silence_duration=demo.DEFAULT_SILENCE_DURATION,
            phrase_time_limit=demo.DEFAULT_PHRASE_TIME_LIMIT,
            confirmation_topic=demo.DEFAULT_CONFIRMATION_TOPIC,
            require_confirmation_wake_word=False,
        )

        with mock.patch.object(demo, "start_process") as start_process:
            demo.start_crispasr_node(args)

        start_process.assert_called_once()
        cmd = start_process.call_args.args[0]
        self.assertIn("_vad_threshold:=0.7", cmd)
        self.assertIn("_silence_duration:=0.8", cmd)
        self.assertIn("_phrase_time_limit:=10.0", cmd)
        self.assertIn("_confirmation_result_topic:=/confirmation_result", cmd)
        self.assertIn("_confirmation_require_wake_word:=false", cmd)

    def test_demo_subscribes_to_confirmation_result_topic(self):
        source = SCRIPT_PATH.read_text()

        self.assertIn("ConfirmationResult", source)
        self.assertIn("confirmation_result_to_dict", source)
        self.assertIn("rospy.Subscriber(args.confirmation_topic", source)


if __name__ == "__main__":
    unittest.main()
