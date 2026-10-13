"""Collect a small, redacted source bundle for CodeAid analysis."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


ALLOWED_SUFFIXES = {
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "venv",
}
SENSITIVE_PATH_PARTS = {
    ".aws",
    ".ssh",
    "credentials",
    "secrets",
}
SENSITIVE_FILE_NAME = re.compile(
    r"(?:secret|credential|password|private[_-]?key|id_rsa|id_ed25519|keystore|\.pem$|\.key$)",
    re.IGNORECASE,
)

MAX_FILE_BYTES = 48_000
MAX_BUNDLE_CHARS = 24_000

_PRIVATE_KEY = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.DOTALL,
)
_BEARER_TOKEN = re.compile(r"(?i)(\bBearer\s+)[A-Za-z0-9._~+/-]+=*")
_KNOWN_TOKEN = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{16,}|"
    r"github_pat_[A-Za-z0-9_]{16,})\b"
)
_QUOTED_SECRET_ASSIGNMENT = re.compile(
    r"(?i)([\"']?[A-Za-z0-9_.-]*"
    r"(?:API[_-]?KEY|ACCESS[_-]?TOKEN|TOKEN|SECRET|PASSWORD|PRIVATE[_-]?KEY)"
    r"[A-Za-z0-9_.-]*[\"']?\s*[:=]\s*)(?P<quote>[\"'])"
    r"(?P<value>.*?)(?P=quote)"
)
_UNQUOTED_SECRET_ASSIGNMENT = re.compile(
    r"(?i)([\"']?[A-Za-z0-9_.-]*"
    r"(?:API[_-]?KEY|ACCESS[_-]?TOKEN|TOKEN|SECRET|PASSWORD|PRIVATE[_-]?KEY)"
    r"[A-Za-z0-9_.-]*[\"']?\s*[:=]\s*)"
    r"(?P<value>[A-Za-z0-9_./+=-]{20,})(?=\s*(?:[,};#]|$))"
)


@dataclass(frozen=True)
class SourceFile:
    path: str
    content: str


@dataclass(frozen=True)
class ContextBundle:
    files: tuple[SourceFile, ...]
    skipped_files: int
    total_characters: int


def redact_secrets(text: str) -> str:
    """Redact common credentials before source or logs leave the machine."""
    text = _PRIVATE_KEY.sub("[REDACTED PRIVATE KEY]", text)
    text = _BEARER_TOKEN.sub(r"\1[REDACTED]", text)
    text = _KNOWN_TOKEN.sub("[REDACTED TOKEN]", text)

    def replace_assignment(match: re.Match[str]) -> str:
        quote = match.group("quote")
        return f"{match.group(1)}{quote}[REDACTED]{quote}"

    text = _QUOTED_SECRET_ASSIGNMENT.sub(replace_assignment, text)
    return _UNQUOTED_SECRET_ASSIGNMENT.sub(r"\1[REDACTED]", text)


def collect_context(
    root: str | Path,
    *,
    max_file_bytes: int = MAX_FILE_BYTES,
    max_bundle_chars: int = MAX_BUNDLE_CHARS,
) -> ContextBundle:
    """Collect bounded text files while skipping likely secrets and generated data."""
    project_root = Path(root).expanduser().resolve()
    if not project_root.is_dir():
        raise ValueError("The selected project folder does not exist or is not a directory.")

    collected: list[SourceFile] = []
    skipped = 0
    total_chars = 0

    for current, dirnames, filenames in os.walk(project_root, followlinks=False):
        current_path = Path(current)
        relative_parts = current_path.relative_to(project_root).parts
        if any(part.lower() in SENSITIVE_PATH_PARTS for part in relative_parts):
            dirnames[:] = []
            continue

        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in IGNORED_DIRECTORIES
            and not name.startswith(".")
            and not (current_path / name).is_symlink()
        )

        for filename in sorted(filenames):
            path = current_path / filename
            relative_path = path.relative_to(project_root)

            if path.is_symlink():
                skipped += 1
                continue
            if filename.lower().startswith(".env"):
                skipped += 1
                continue
            if SENSITIVE_FILE_NAME.search(filename):
                skipped += 1
                continue
            if path.suffix.lower() not in ALLOWED_SUFFIXES:
                skipped += 1
                continue

            try:
                if path.stat().st_size > max_file_bytes:
                    skipped += 1
                    continue
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                skipped += 1
                continue

            if "\x00" in text:
                skipped += 1
                continue

            text = redact_secrets(text)
            remaining = max_bundle_chars - total_chars
            if remaining <= 0:
                skipped += 1
                continue
            if len(text) > remaining:
                marker = "\n[context truncated]"
                text = (
                    text[: remaining - len(marker)] + marker
                    if remaining > len(marker)
                    else text[:remaining]
                )

            collected.append(SourceFile(path=relative_path.as_posix(), content=text))
            total_chars += len(text)

    return ContextBundle(
        files=tuple(collected),
        skipped_files=skipped,
        total_characters=total_chars,
    )


def format_context(bundle: ContextBundle) -> str:
    """Format collected files with clear, stable path boundaries."""
    sections = [f"### {source.path}\n```\n{source.content}\n```" for source in bundle.files]
    return "\n\n".join(sections)
