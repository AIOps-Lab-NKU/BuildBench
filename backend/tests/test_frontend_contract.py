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
        self.assertIn("data-evaluation-action", script)
        self.assertIn("data-evaluation-confirm", html)
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

    def test_agent_version_pagination_is_six_per_page(self) -> None:
        script = (ROOT / "submissions.js").read_text(encoding="utf-8")
        self.assertIn("const PAGE_SIZE = 6", script)
        self.assertIn("visibleSubmissions", script)
        self.assertIn('data-page-action="previous"', script)
        self.assertIn('data-page-action="next"', script)

    def test_resource_index_has_no_duplicate_bundled_downloads(self) -> None:
        html = (ROOT / "data-downloads.html").read_text(encoding="utf-8")
        self.assertIn("Starter Kit", html)
        self.assertIn("Development Cases", html)
        self.assertIn("Protocol Schemas", html)
        self.assertIn("Runtime Images", html)
        self.assertIn(
            "releases/download/v0.1.0-rc.1/"
            "buildbench-starter-kit-0.1.0-rc.1.zip",
            html,
        )
        self.assertIn(
            "releases/download/v0.1.0-rc.1/SHA256SUMS",
            html,
        )
        self.assertIn("Published pre-release", html)
        self.assertNotIn('data-lucide="download"', html)
        self.assertNotIn('data-lucide="shield-check"', html)
        self.assertNotIn('<th scope="row">Example Agent</th>', html)
        self.assertNotIn('<th scope="row">Local Smoke Cases</th>', html)
        self.assertNotIn('<th scope="row">Case Schema</th>', html)
        self.assertNotIn('<th scope="row">Agent Schema</th>', html)

    def test_submission_script_uses_full_evaluation_routes(self) -> None:
        script = (ROOT / "submissions.js").read_text(encoding="utf-8")
        self.assertIn('api("/api/submissions"', script)
        self.assertIn("/smoke-test", script)
        self.assertIn('api("/api/full-evaluations"', script)
        self.assertIn("/full-evaluations", script)
        self.assertIn("Idempotency-Key", script)
        self.assertNotIn("Start another evaluation", script)
        self.assertNotIn("Content-Length", script)

    def test_full_evaluation_detail_contract(self) -> None:
        html = (ROOT / "evaluation-detail.html").read_text(encoding="utf-8")
        script = (ROOT / "evaluation-detail.js").read_text(encoding="utf-8")
        for hook in (
            "data-evaluation-status",
            "data-evaluation-progress",
            "data-evaluation-stages",
            "data-evaluation-result",
            "data-evaluation-timeline",
        ):
            self.assertIn(hook, html)
        self.assertIn("/api/full-evaluations/", script)
        self.assertIn("EventSource", script)
        self.assertIn("loadEventHistory", script)
        self.assertIn("events?once=1", script)
        self.assertIn("schedulePolling", script)
        self.assertIn("TIMELINE_PHASES", script)
        self.assertIn("!isTimelineEvent(event)", script)
        self.assertNotIn('t("Evaluation progress updated")', script)
        self.assertNotIn("case_id", script)
        self.assertNotIn("successful_cases", script)

    def test_public_evaluation_schema_is_present(self) -> None:
        schema = ROOT / "backend" / "schema" / "evaluation-public-v0.1.schema.json"
        self.assertTrue(schema.is_file())
        text = schema.read_text(encoding="utf-8")
        self.assertIn('"status"', text)
        self.assertIn('"progress"', text)
        self.assertNotIn('"case_id"', text)

    def test_runtime_state_is_git_ignored(self) -> None:
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("runtime-data/", ignored)

    def test_leaderboard_has_versioned_live_results_contract(self) -> None:
        html = (ROOT / "leaderboard.html").read_text(encoding="utf-8")
        script = (ROOT / "leaderboard-live.js").read_text(encoding="utf-8")
        schema = (
            ROOT / "backend" / "schema" / "leaderboard-public-v0.1.schema.json"
        )
        self.assertIn("Published Full Evaluations", html)
        self.assertIn("data-live-board-body", html)
        self.assertIn("leaderboard-live.js", html)
        self.assertIn('fetch("/api/leaderboard"', script)
        self.assertIn("case_set_version", script)
        self.assertIn("protocol_version", script)
        self.assertTrue(schema.is_file())


if __name__ == "__main__":
    unittest.main()
