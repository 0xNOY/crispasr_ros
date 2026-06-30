#!/usr/bin/env python3

import os
import sys
import tempfile
import unittest
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from crispasr_ros.runtime_paths import ensure_crispasr_runtime_paths


class RuntimePathsTest(unittest.TestCase):
    def setUp(self):
        self.original_sys_path = list(sys.path)
        self.original_lib_path = os.environ.get("CRISPASR_LIB_PATH")

    def tearDown(self):
        sys.path[:] = self.original_sys_path
        if self.original_lib_path is None:
            os.environ.pop("CRISPASR_LIB_PATH", None)
        else:
            os.environ["CRISPASR_LIB_PATH"] = self.original_lib_path

    def make_workspace(self, root: Path) -> None:
        (root / "pixi.toml").write_text("[workspace]\nname = \"crispasr_ros\"\n")
        (root / "crispasr_src" / "python").mkdir(parents=True)
        (root / "build" / "native" / "src").mkdir(parents=True)
        (root / "build" / "native" / "src" / "libcrispasr.so").touch()

    def test_sets_default_crispasr_lib_path_when_workspace_library_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_workspace(root)
            os.environ.pop("CRISPASR_LIB_PATH", None)

            ensure_crispasr_runtime_paths(root / "install" / "ros2" / "lib" / "crispasr_ros")

            self.assertEqual(
                str(root / "build" / "native" / "src" / "libcrispasr.so"),
                os.environ["CRISPASR_LIB_PATH"],
            )

    def test_preserves_existing_crispasr_lib_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_workspace(root)
            os.environ["CRISPASR_LIB_PATH"] = "/custom/libcrispasr.so"

            ensure_crispasr_runtime_paths(root / "install" / "ros2" / "lib" / "crispasr_ros")

            self.assertEqual("/custom/libcrispasr.so", os.environ["CRISPASR_LIB_PATH"])

    def test_prepends_local_python_binding_path_when_it_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_workspace(root)
            binding_path = str(root / "crispasr_src" / "python")
            sys.path = [path for path in sys.path if path != binding_path]

            ensure_crispasr_runtime_paths(root / "crispasr_ros" / "scripts" / "crispasr_node")

            self.assertEqual(binding_path, sys.path[0])


if __name__ == "__main__":
    unittest.main()
