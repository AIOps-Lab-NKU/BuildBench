from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class FrontendContractTests(unittest.TestCase):
    def test_my_submissions_has_api_hooks(self) -> None:
        html = (ROOT / "my-submissions.html").read_text(encoding="utf-8")
        for hook in (
            "data-agent-upload",
            "data-upload-button",
            "data-submission-notice",
            "data-agent-versions-list",
            "data-agent-version-count",
            "data-log-modal",
            "data-log-content",
            "data-log-download",
            "submissions.js",
        ):
            self.assertIn(hook, html)

    def test_agent_versions_table_and_full_evaluation_empty_state(self) -> None:
        html = (ROOT / "my-submissions.html").read_text(encoding="utf-8")
        script = (ROOT / "submissions.js").read_text(encoding="utf-8")
        self.assertIn("Agent submission versions", html)
        self.assertIn("Submission ID", script)
        self.assertIn("data-smoke-action", script)
        self.assertIn("data-full-evaluations-list", html)
        self.assertIn(
            "You currently have no full evaluation submissions for this competition.",
            html,
        )
        self.assertIn("Smoke Test", script)
        self.assertIn("Actions", script)
        self.assertIn("Start Full Evaluation", script)
        self.assertIn("data-log-action", script)
        self.assertIn("View log", script)
        self.assertIn("showModal", script)
        self.assertNotIn("submission-log.html?id=", script)
        self.assertNotIn(
            "Hosted Smoke Test queued. This page will update automatically.",
            script,
        )

    def test_public_status_contract_and_log_modal(self) -> None:
        html = (ROOT / "my-submissions.html").read_text(encoding="utf-8")
        script = (ROOT / "submissions.js").read_text(encoding="utf-8")
        translations = (ROOT / "i18n" / "my-submissions.js").read_text(
            encoding="utf-8"
        )
        for label in (
            "Checking",
            "Testing",
            "Qualified",
            "Failed",
            "Evaluating",
            "Completed",
        ):
            self.assertIn(f'"{label}"', script)
            self.assertIn(f'"{label}"', translations)
        self.assertIn("<dialog", html)
        self.assertIn("aria-labelledby", html)
        self.assertIn("/log", script)
        self.assertIn("download=1", script)

    def test_quick_start_uses_real_vertical_workflow(self) -> None:
        html = (ROOT / "submission.html").read_text(encoding="utf-8")
        for command in (
            "./bb doctor",
            "./bb demo",
            "./bb init my-agent",
            "./bb test --agent ./agents/my-agent",
            "./bb check --agent ./agents/my-agent",
            "./bb package --agent ./agents/my-agent",
            "dist/agent-submission.zip",
        ):
            self.assertIn(command, html)
        self.assertEqual(html.count('class="quick-start-number"'), 6)
        self.assertEqual(html.count('class="quick-start-result"'), 6)

    def test_submission_script_uses_only_milestone_c_routes(self) -> None:
        script = (ROOT / "submissions.js").read_text(encoding="utf-8")
        self.assertIn('api("/api/submissions"', script)
        self.assertIn("/smoke-test", script)
        self.assertNotIn("/api/full-evaluation", script)
        self.assertNotIn("Content-Length", script)

    def test_runtime_state_is_git_ignored(self) -> None:
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("runtime-data/", ignored)


if __name__ == "__main__":
    unittest.main()
