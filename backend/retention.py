"""Conservative retention cleanup for Full Evaluation attempt artifacts."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backend.evaluation_store import EvaluationStore


def prune_evaluation_outputs(
    *,
    store: EvaluationStore,
    output_root: Path,
    retention_days: int,
    dry_run: bool = True,
) -> list[dict[str, object]]:
    if retention_days < 1:
        raise ValueError("retention_days must be positive")
    root = output_root.resolve()
    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=retention_days)
    ).replace(microsecond=0).isoformat()
    actions: list[dict[str, object]] = []
    for evaluation in store.terminal_evaluations_before(cutoff):
        evaluation_id = str(evaluation["evaluation_id"])
        candidate = (root / evaluation_id).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        exists = candidate.is_dir() and not candidate.is_symlink()
        action = {
            "evaluation_id": evaluation_id,
            "finished_at": evaluation["finished_at"],
            "path": str(candidate),
            "exists": exists,
            "deleted": False,
        }
        if exists and not dry_run:
            shutil.rmtree(candidate)
            action["deleted"] = True
            store.audit(
                actor_id="retention-service",
                actor_role="system",
                action="delete_evaluation_artifacts",
                target_type="evaluation",
                target_id=evaluation_id,
                details={"retention_days": retention_days},
            )
        actions.append(action)
    return actions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--retention-days", type=int, default=30)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    actions = prune_evaluation_outputs(
        store=EvaluationStore(args.database),
        output_root=args.output_root,
        retention_days=args.retention_days,
        dry_run=not args.apply,
    )
    print(
        json.dumps(
            {
                "dry_run": not args.apply,
                "actions": actions,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
