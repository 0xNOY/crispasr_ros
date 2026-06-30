#!/usr/bin/env python3

import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class MicrophoneArecordBackendTest(unittest.TestCase):
    def test_ros1_microphone_defaults_to_arecord_backend(self):
        params = (PACKAGE_ROOT / "config" / "params_ros1.yaml").read_text()
        launch = (PACKAGE_ROOT / "launch" / "audio_source.launch").read_text()

        self.assertIn('audio_backend: "arecord"', params)
        self.assertIn("arecord_command:", params)
        self.assertIn('<arg name="audio_backend" default="arecord" />', launch)
        self.assertIn('<param name="audio_backend" value="$(arg audio_backend)" />', launch)

    def test_ros2_microphone_defaults_to_arecord_backend(self):
        params = (PACKAGE_ROOT / "config" / "params_ros2.yaml").read_text()
        launch = (PACKAGE_ROOT / "launch" / "audio_source.launch.py").read_text()

        self.assertIn('audio_backend: "arecord"', params)
        self.assertIn("arecord_command:", params)
        self.assertIn("default_value='arecord'", launch)
        self.assertIn("'audio_backend': audio_backend", launch)

    def test_microphone_node_keeps_sounddevice_as_explicit_backend(self):
        source = (PACKAGE_ROOT / "scripts" / "microphone_node").read_text()

        self.assertIn('self.node.get_param("audio_backend", "arecord")', source)
        self.assertIn('if self.audio_backend == "arecord":', source)
        self.assertIn('if self.audio_backend != "sounddevice":', source)


if __name__ == "__main__":
    unittest.main()
