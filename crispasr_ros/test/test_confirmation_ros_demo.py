#!/usr/bin/env python3

import ast
import subprocess
import sys
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PACKAGE_ROOT / "scripts" / "confirmation_ros_demo"


class ConfirmationRosDemoTest(unittest.TestCase):
    def parse_script(self):
        return ast.parse(SCRIPT_PATH.read_text())

    def test_demo_script_exists(self):
        self.assertTrue(SCRIPT_PATH.exists())

    def test_demo_uses_ros_confirmation_and_speech_topics(self):
        source = SCRIPT_PATH.read_text()

        self.assertIn("ConfirmationResult", source)
        self.assertIn("SpeechResult", source)
        self.assertIn("/confirmation_result", source)
        self.assertIn("/speech_result", source)

    def test_demo_does_not_use_standalone_microphone_or_asr_engine(self):
        source = SCRIPT_PATH.read_text()

        self.assertNotIn("sounddevice", source)
        self.assertNotIn("ASREngine", source)
        self.assertNotIn("ConfirmationGate", source)

    def test_demo_defines_main_entrypoint(self):
        tree = self.parse_script()
        functions = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        }

        self.assertIn("main", functions)

    def test_help_works_without_ros_environment(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertIn("--confirmation-topic", proc.stdout)
        self.assertIn("--speech-topic", proc.stdout)


if __name__ == "__main__":
    unittest.main()
