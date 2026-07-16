"""Fail when tracked reviewer reports are stale relative to regenerated output.

The report generators intentionally record the wall-clock generation time. A raw
``git diff --exit-code`` would therefore fail on every run even when all metrics,
guardrails, scenarios, decisions, and reviewer copy are unchanged. This checker
compares the working-tree reports produced by ``run_full_verification.py`` with
the versions committed at ``HEAD`` after normalizing only volatile generation
timestamps.

Usage:
    python scripts/run_full_verification.py
    python scripts/check_report_freshness.py
"""

from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORT_PATHS = [
    Path("reports/quality_report.json"),
    Path("reports/experiment_result.json"),
    Path("reports/decision_memo.md"),
    Path("reports/review_report.html"),
    Path("reports/scenario_matrix.json"),
    Path("reports/scenario_matrix.md"),
]

ISO_TIMESTAMP_PATTERN = re.compile(
    r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})\b"
)
VOLATILE_JSON_KEYS = {"generated_at"}
TIMESTAMP_PLACEHOLDER = "<normalized-generated-at>"


def read_committed(path: Path) -> str:
    """Read a tracked file from the current commit rather than the working tree."""

    result = subprocess.run(
        ["git", "show", f"HEAD:{path.as_posix()}"],
        cwd=ROOT_DIR,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "file is not tracked at HEAD"
        raise RuntimeError(f"Unable to read committed {path}: {detail}")
    return result.stdout


def normalize_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: TIMESTAMP_PLACEHOLDER if key in VOLATILE_JSON_KEYS else normalize_json_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [normalize_json_value(item) for item in value]
    return value


def normalize_json(text: str) -> str:
    value = json.loads(text)
    normalized = normalize_json_value(value)
    return json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def normalize_text(text: str) -> str:
    normalized = ISO_TIMESTAMP_PATTERN.sub(TIMESTAMP_PLACEHOLDER, text)
    return normalized.replace("\r\n", "\n").rstrip() + "\n"


def normalize(path: Path, text: str) -> str:
    if path.suffix == ".json":
        return normalize_json(text)
    return normalize_text(text)


def compare_report(path: Path) -> tuple[bool, str]:
    working_path = ROOT_DIR / path
    if not working_path.exists():
        return False, f"Missing regenerated report: {path}"

    committed = normalize(path, read_committed(path))
    regenerated = normalize(path, working_path.read_text(encoding="utf-8"))
    if committed == regenerated:
        return True, ""

    diff = "".join(
        difflib.unified_diff(
            committed.splitlines(keepends=True),
            regenerated.splitlines(keepends=True),
            fromfile=f"HEAD/{path.as_posix()}",
            tofile=f"regenerated/{path.as_posix()}",
            n=3,
        )
    )
    return False, diff


def main() -> int:
    failures: list[tuple[Path, str]] = []

    for path in REPORT_PATHS:
        try:
            is_fresh, detail = compare_report(path)
        except (json.JSONDecodeError, RuntimeError) as error:
            failures.append((path, str(error)))
            continue

        if is_fresh:
            print(f"PASS {path.as_posix()}")
        else:
            failures.append((path, detail))

    if not failures:
        print("\nAll tracked DecisionOps reports are semantically fresh.")
        print("Volatile generated_at timestamps were normalized before comparison.")
        return 0

    print("\nStale generated reports detected:", file=sys.stderr)
    for path, detail in failures:
        print(f"\n--- {path.as_posix()} ---", file=sys.stderr)
        print(detail.rstrip(), file=sys.stderr)

    print(
        "\nRegenerate reports with `python scripts/run_full_verification.py`, "
        "review the changes, and commit the updated artifacts.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
