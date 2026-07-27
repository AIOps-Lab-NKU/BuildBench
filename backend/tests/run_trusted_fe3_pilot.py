"""Run the FE-3 trusted/public single-Case integration pilot on Linux."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.evaluation_runner import (
    CommandValidatorExecutor,
    DockerAgentConfig,
    DockerAgentExecutor,
    FormalCaseRunner,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--agent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validator", type=Path, required=True)
    parser.add_argument("--agent-image", required=True)
    parser.add_argument(
        "--validator-image",
        default="buildbench-validator-runtime:v0",
    )
    parser.add_argument("--cleanup-image", default="ubuntu:24.04")
    parser.add_argument("--agent-timeout", type=int, default=600)
    parser.add_argument("--build-timeout", type=int, default=900)
    args = parser.parse_args()

    asset = Path(__file__).resolve().parents[1] / "runner_assets" / "bb-build"
    agent = DockerAgentExecutor(
        DockerAgentConfig(
            image=args.agent_image,
            entrypoint=("python", "-m", "src.main"),
            timeout_seconds=args.agent_timeout,
            build_feedback_timeout_seconds=max(
                min(args.build_timeout, args.agent_timeout - 30),
                1,
            ),
        ),
        asset,
    )
    validator = CommandValidatorExecutor(
        (str(args.validator.resolve(strict=True)),),
        timeout_seconds=args.build_timeout,
        environment={
            "BUILD_CASE_RUNTIME_IMAGE": args.validator_image,
            "BUILD_CASE_CLEANUP_IMAGE": args.cleanup_image,
        },
    )
    runner = FormalCaseRunner(
        agent,
        validator,
        build_attempt_limit=1,
    )
    result = runner.run(
        case_run_id="CR-trustedpilot000",
        case_ordinal=1,
        case_dir=args.case,
        agent_dir=args.agent,
        output_dir=args.output,
    )
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0 if result.status == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
