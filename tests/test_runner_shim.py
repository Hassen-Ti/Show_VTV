"""Regression: ``python -m show.runner`` must delegate to runtime CLI."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def test_runner_module_help():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(SRC), env["PYTHONPATH"]] if env.get("PYTHONPATH") else [str(SRC)]
    )
    proc = subprocess.run(
        [sys.executable, "-m", "show.runner", "--help"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert proc.returncode == 0, proc.stderr
    assert "--topic" in proc.stdout
