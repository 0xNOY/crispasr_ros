"""Runtime path setup for the in-tree CrispASR development layout."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def find_workspace_root(start_path: str | os.PathLike[str]) -> Path | None:
    """Find the nearest parent directory containing this package's pixi.toml."""
    current = Path(start_path).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if (candidate / "pixi.toml").exists():
            return candidate
    return None


def ensure_crispasr_runtime_paths(start_path: str | os.PathLike[str]) -> None:
    """Expose local CrispASR bindings and native library when running from pixi."""
    workspace_root = find_workspace_root(start_path)
    if workspace_root is None:
        return

    binding_path = workspace_root / "crispasr_src" / "python"
    binding_path_str = str(binding_path)
    if binding_path.exists() and binding_path_str not in sys.path:
        sys.path.insert(0, binding_path_str)

    lib_path = workspace_root / "build" / "native" / "src" / "libcrispasr.so"
    if "CRISPASR_LIB_PATH" not in os.environ and lib_path.exists():
        os.environ["CRISPASR_LIB_PATH"] = str(lib_path)
