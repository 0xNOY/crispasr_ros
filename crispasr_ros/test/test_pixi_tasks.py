#!/usr/bin/env python3

import tomllib
import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
PIXI_TOML = WORKSPACE_ROOT / "pixi.toml"


class PixiTasksTest(unittest.TestCase):
    def load_pixi(self):
        return tomllib.loads(PIXI_TOML.read_text())

    def launch_commands(self):
        pixi = self.load_pixi()
        for feature_name in ("ros1", "ros2"):
            tasks = pixi["feature"][feature_name]["tasks"]
            for task_name in ("launch-server", "launch-audio", "launch-audio-mic"):
                task = tasks[task_name]
                yield feature_name, task_name, task["cmd"] if isinstance(task, dict) else task

    def test_launch_tasks_do_not_inline_runtime_environment_exports(self):
        forbidden_fragments = (
            "export ROS_IP",
            "export ROS_HOSTNAME",
            "export ROS_MASTER_URI",
            "export CRISPASR_LIB_PATH",
            "export PYTHONPATH",
        )

        for feature_name, task_name, command in self.launch_commands():
            with self.subTest(feature=feature_name, task=task_name):
                for fragment in forbidden_fragments:
                    self.assertNotIn(fragment, command)

    def test_launch_tasks_source_install_space_before_launching(self):
        for feature_name, task_name, command in self.launch_commands():
            with self.subTest(feature=feature_name, task=task_name):
                self.assertIn(f". install/{feature_name}/setup.bash", command)

    def test_native_build_enables_cuda_backend_by_default(self):
        pixi = self.load_pixi()
        command = pixi["tasks"]["build-native"]

        self.assertIn("-DGGML_CUDA=ON", command)


if __name__ == "__main__":
    unittest.main()
