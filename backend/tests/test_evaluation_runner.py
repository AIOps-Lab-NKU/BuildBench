from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from backend.build_gateway import (
    BuildGateway,
    BuildGatewayError,
    GatewayContext,
    sanitize_log,
)
from backend.canonical_patch import (
    CanonicalPatchError,
    generate_canonical_patch,
)
from backend.evaluation_runner import (
    AgentExecution,
    DockerAgentConfig,
    DockerAgentExecutor,
    FormalCaseRunner,
)


def make_case(root: Path) -> Path:
    case = root / "case"
    (case / "input").mkdir(parents=True)
    (case / "logs").mkdir()
    (case / "input" / "example.spec").write_text(
        "Name: example\nBroken: yes\n",
        encoding="utf-8",
    )
    (case / "manifest.json").write_text(
        '{"case_id":"internal-case"}\n',
        encoding="utf-8",
    )
    (case / "logs" / "original-target-failed.log").write_text(
        "target build failed\n",
        encoding="utf-8",
    )
    return case


class FakeValidator:
    def __init__(self, final_status: str = "succeeded"):
        self.final_status = final_status
        self.calls: list[tuple[Path, Path, Path]] = []

    def validate(
        self, case_dir: Path, patch_path: Path, output_dir: Path
    ) -> dict[str, object]:
        self.calls.append((case_dir, patch_path, output_dir))
        output_dir.mkdir(parents=True)
        status = self.final_status
        payload: dict[str, object] = {
            "status": status,
            "message": f"validator returned {status}",
            "duration_seconds": 2,
            "timed_out": status == "timeout",
        }
        (output_dir / "build-result.json").write_text(
            json.dumps(payload) + "\n",
            encoding="utf-8",
        )
        (output_dir / "build.log").write_text(
            f"build status: {status}\n",
            encoding="utf-8",
        )
        if status == "succeeded":
            artifacts = output_dir / "artifacts"
            artifacts.mkdir()
            (artifacts / "example.rpm").write_bytes(b"rpm")
        return payload


class FakeAgent:
    def __init__(self, mode: str, gateway_holder: dict[str, BuildGateway]):
        self.mode = mode
        self.gateway_holder = gateway_holder
        self.feedback: dict[str, object] | None = None

    def run(
        self,
        *,
        agent_dir: Path,
        workspace: Path,
        log_path: Path,
        gateway_socket: Path,
        gateway_token: str,
    ) -> AgentExecution:
        del agent_dir, gateway_socket
        log_path.write_text(f"mode={self.mode}\n", encoding="utf-8")
        if self.mode == "crash":
            return AgentExecution("agent_error", 9, 1, message="Agent crashed.")
        if self.mode == "timeout":
            return AgentExecution(
                "timeout", None, 3, timed_out=True, message="Agent timed out."
            )

        output = workspace / "output"
        if self.mode == "no_fix":
            (output / "agent-result.json").write_text(
                '{"status":"no_fix","message":"nothing proposed"}\n',
                encoding="utf-8",
            )
            return AgentExecution("completed", 0, 1)
        if self.mode == "invalid_patch":
            (workspace / "work" / "repo" / "manifest.json").write_text(
                '{"tampered":true}\n',
                encoding="utf-8",
            )
        else:
            spec = workspace / "work" / "repo" / "input" / "example.spec"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace("yes", "no"),
                encoding="utf-8",
            )
        if self.mode == "feedback":
            gateway = self.gateway_holder["gateway"]
            self.feedback = gateway.handle(
                {"action": "build"},
                capability_token=gateway_token,
            )
        (output / "agent-result.json").write_text(
            '{"status":"completed","message":"candidate ready"}\n',
            encoding="utf-8",
        )
        return AgentExecution("completed", 0, 1)


def gateway_factory(holder: dict[str, BuildGateway]):
    @contextmanager
    def factory(gateway: BuildGateway, socket_path: Path):
        del socket_path
        holder["gateway"] = gateway
        yield object()

    return factory


class CanonicalPatchTests(unittest.TestCase):
    def test_only_allowed_text_changes_become_platform_patch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = make_case(root)
            modified = root / "modified"
            import shutil

            shutil.copytree(original, modified)
            path = modified / "input" / "example.spec"
            path.write_text("Name: example\nBroken: no\n", encoding="utf-8")
            patch = generate_canonical_patch(original, modified)
            self.assertEqual(patch.changed_paths, ("input/example.spec",))
            self.assertIn("diff --git a/input/example.spec", patch.text)

            (modified / "manifest.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(
                CanonicalPatchError, "outside allowed paths"
            ):
                generate_canonical_patch(original, modified)


class BuildGatewayTests(unittest.TestCase):
    def test_fixed_context_quota_and_sanitized_feedback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = make_case(root)
            modified = root / "modified"
            import shutil

            shutil.copytree(original, modified)
            spec = modified / "input" / "example.spec"
            spec.write_text("Name: example\nBroken: no\n", encoding="utf-8")

            def validator(
                case: Path, patch: Path, output: Path
            ) -> dict[str, object]:
                self.assertEqual(case, original)
                self.assertTrue(patch.is_file())
                output.mkdir(parents=True)
                (output / "build.log").write_text(
                    f"{root}/hidden token=secret-value\n",
                    encoding="utf-8",
                )
                return {"status": "failed", "message": str(root)}

            gateway = BuildGateway(
                GatewayContext(
                    original_case=original,
                    worktree=modified,
                    output_root=root / "attempts",
                    attempt_limit=1,
                ),
                validator,
                capability_token="capability",
            )
            response = gateway.handle(
                {"action": "build"}, capability_token="capability"
            )
            self.assertEqual(response["status"], "failed")
            self.assertNotIn(str(root), repr(response))
            self.assertNotIn("secret-value", repr(response))
            exhausted = gateway.handle(
                {"action": "build"}, capability_token="capability"
            )
            self.assertEqual(exhausted["error"], "attempt_limit_exceeded")
            with self.assertRaises(BuildGatewayError):
                gateway.handle(
                    {"action": "build", "case": "/host/other"},
                    capability_token="capability",
                )
            with self.assertRaises(BuildGatewayError):
                gateway.handle(
                    {"action": "build"}, capability_token="wrong"
                )

    def test_log_sanitizer_bounds_and_redacts(self) -> None:
        value = sanitize_log(
            "api_key=secret\nhttps://user:pass@example.invalid/\n" + "x" * 100,
            limit=40,
        )
        self.assertNotIn("secret", value)
        self.assertNotIn("user:pass", value)
        self.assertLessEqual(len(value), 65)


class FormalCaseRunnerTests(unittest.TestCase):
    def test_case_run_schema_contract_is_machine_readable(self) -> None:
        schema = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "schema"
                / "case-run-result-v0.1.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], "0.1")
        self.assertEqual(
            set(schema["properties"]["status"]["enum"]),
            {
                "succeeded",
                "failed",
                "unresolvable",
                "timeout",
                "no_fix",
                "agent_error",
                "invalid_patch",
                "infrastructure_error",
            },
        )

    def run_mode(
        self, root: Path, mode: str, validator_status: str = "succeeded"
    ):
        holder: dict[str, BuildGateway] = {}
        agent = FakeAgent(mode, holder)
        validator = FakeValidator(validator_status)
        runner = FormalCaseRunner(
            agent,
            validator,
            build_attempt_limit=1,
            gateway_server_factory=gateway_factory(holder),
        )
        agent_dir = root / f"agent-{mode}"
        agent_dir.mkdir()
        result = runner.run(
            case_run_id=f"CR-{mode:0<16}"[:19],
            case_ordinal=1,
            case_dir=make_case(root / mode),
            agent_dir=agent_dir,
            output_dir=root / f"result-{mode}",
        )
        return result, agent, validator

    def test_feedback_patch_and_clean_final_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result, agent, validator = self.run_mode(root, "feedback")
            self.assertEqual(result.status, "succeeded")
            self.assertEqual(result.build_attempts, 1)
            self.assertEqual(len(validator.calls), 2)
            self.assertEqual(agent.feedback["status"], "succeeded")
            output = root / "result-feedback"
            self.assertTrue((output / "repair.diff").is_file())
            self.assertTrue((output / "case-run-result.json").is_file())
            self.assertTrue((output / "artifacts" / "example.rpm").is_file())
            original_spec = (
                validator.calls[-1][0] / "input" / "example.spec"
            ).read_text(encoding="utf-8")
            self.assertIn("Broken: yes", original_spec)

    def test_expected_failures_are_structured_terminal_results(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scenarios = (
                ("no_fix", "succeeded", "no_fix"),
                ("crash", "succeeded", "agent_error"),
                ("timeout", "succeeded", "timeout"),
                ("invalid_patch", "succeeded", "invalid_patch"),
                ("completed", "failed", "failed"),
            )
            for mode, validator_status, expected in scenarios:
                with self.subTest(mode=mode):
                    result, _, _ = self.run_mode(
                        root, mode, validator_status
                    )
                    self.assertEqual(result.status, expected)
                    persisted = json.loads(
                        (
                            root
                            / f"result-{mode}"
                            / "case-run-result.json"
                        ).read_text(encoding="utf-8")
                    )
                    self.assertEqual(persisted["status"], expected)


class DockerAgentBoundaryTests(unittest.TestCase):
    def test_agent_command_has_no_docker_socket_or_free_form_context(self) -> None:
        root = Path(__file__).resolve().parents[1]
        executor = DockerAgentExecutor(
            DockerAgentConfig(
                image="python@sha256:" + "a" * 64,
                entrypoint=("python", "-m", "src.main"),
                timeout_seconds=60,
            ),
            root / "runner_assets" / "bb-build",
        )
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            agent = work / "agent"
            workspace = work / "workspace"
            socket_path = work / "gateway" / "gateway.sock"
            agent.mkdir()
            (workspace / "input").mkdir(parents=True)
            (workspace / "work").mkdir()
            (workspace / "output").mkdir()
            socket_path.parent.mkdir()
            command = executor.command(
                agent_dir=agent,
                workspace=workspace,
                gateway_socket=socket_path,
                gateway_token="secret-token-value",
                container_name="test-container",
            )
        serialized = " ".join(command)
        self.assertNotIn("/var/run/docker.sock", serialized)
        self.assertIn("--network none", serialized)
        self.assertIn("--cap-drop ALL", serialized)
        self.assertIn("python@sha256:", serialized)
        self.assertNotIn("secret-token-value", serialized)
        self.assertIn("BB_BUILD_GATEWAY_TOKEN_FILE", serialized)
        self.assertNotIn("--privileged", command)


if __name__ == "__main__":
    unittest.main()
