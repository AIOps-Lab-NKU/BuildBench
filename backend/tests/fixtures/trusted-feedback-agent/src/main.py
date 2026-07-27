"""Trusted Agent fixture that exercises the real bb-build command."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


BROKEN = """# BUILD-BENCH-DEMO-BROKEN
echo "intentional Build-Bench demo failure" >&2
exit 1
"""
FIXED = """# BUILD-BENCH-DEMO-REPAIRED
echo "Build-Bench trusted feedback fixture repaired the package"
"""


def main() -> int:
    workspace = Path(os.environ.get("BB_WORKSPACE", "/workspace"))
    spec = workspace / "work" / "repo" / "input" / "buildbench-hello.spec"
    content = spec.read_text(encoding="utf-8")
    if content.count(BROKEN) != 1:
        raise RuntimeError("trusted fixture could not locate the demo failure")
    spec.write_text(content.replace(BROKEN, FIXED), encoding="utf-8")

    feedback = subprocess.run(
        ["bb-build"],
        text=True,
        capture_output=True,
        check=False,
        timeout=600,
    )
    print(feedback.stdout)
    if feedback.returncode != 0:
        print(feedback.stderr)
        raise RuntimeError("bb-build feedback request failed")
    payload = json.loads(feedback.stdout)
    if payload.get("status") != "succeeded":
        raise RuntimeError(
            f"candidate did not pass build feedback: {payload.get('status')}"
        )

    result = {
        "schema_version": "0.1",
        "status": "completed",
        "message": "Candidate passed one bounded build-feedback request.",
    }
    (workspace / "output" / "agent-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
