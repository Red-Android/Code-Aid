"""Run only CodeAid's bundled demo in a disposable temporary copy."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from codeaid.context import redact_secrets


DEMO_PROJECT = Path(__file__).resolve().parents[1] / "fixtures" / "broken_python"
OUTPUT_LIMIT = 12_000


@dataclass(frozen=True)
class TestRunResult:
    return_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool

    @property
    def passed(self) -> bool:
        return self.return_code == 0 and not self.timed_out


def _decode_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _limit_output(text: str) -> str:
    text = redact_secrets(text)
    if len(text) <= OUTPUT_LIMIT:
        return text
    return text[:OUTPUT_LIMIT] + "\n[output truncated]"


def run_bundled_demo(timeout_seconds: int = 20) -> TestRunResult:
    """Run the known demo fixture, never a user-selected repository."""
    if not DEMO_PROJECT.is_dir():
        raise FileNotFoundError("CodeAid's bundled demo project is missing.")

    with tempfile.TemporaryDirectory(prefix="codeaid-demo-") as temporary_dir:
        temp_root = Path(temporary_dir)
        workspace = temp_root / "project"
        shutil.copytree(DEMO_PROJECT, workspace)

        # Do not pass API keys or the rest of the user's environment to test code.
        child_env = {
            "PATH": os.defpath,
            "HOME": str(temp_root),
            "TMPDIR": str(temp_root),
            "TEMP": str(temp_root),
            "TMP": str(temp_root),
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        }
        command = [sys.executable, "-m", "pytest", "-q", "tests"]
        started = time.monotonic()

        try:
            completed = subprocess.run(
                command,
                cwd=workspace,
                env=child_env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                shell=False,
                check=False,
            )
            elapsed = time.monotonic() - started
            return TestRunResult(
                return_code=completed.returncode,
                stdout=_limit_output(completed.stdout),
                stderr=_limit_output(completed.stderr),
                duration_seconds=elapsed,
                timed_out=False,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed = time.monotonic() - started
            return TestRunResult(
                return_code=None,
                stdout=_limit_output(_decode_output(exc.stdout)),
                stderr=_limit_output(_decode_output(exc.stderr)),
                duration_seconds=elapsed,
                timed_out=True,
            )
