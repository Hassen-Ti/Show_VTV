"""Parsing de réponses LLM structurées (labels, tactiques)."""

from __future__ import annotations

import re


def parse_labeled_lines(text: str, labels: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for label in labels:
        match = re.search(rf"^{label}:\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
        if match:
            result[label.lower()] = match.group(1).strip()
    return result


def first_allowed_tactic(raw: str, allowed: list[str], fallback: str) -> str:
    """Parse `TACTIC: <id>` (or bare id) and return an exact allowed tactic."""
    text = (raw or "").strip()
    match = re.search(r"(?im)^\s*TACTIC:\s*(\S+)", text)
    candidate = (match.group(1) if match else text.split()[0] if text else "").strip().lower()
    # Strip trailing punctuation from loose model output.
    candidate = candidate.rstrip(".,;:)")
    allowed_set = {t.lower(): t for t in allowed}
    if candidate in allowed_set:
        return allowed_set[candidate]
    return fallback
