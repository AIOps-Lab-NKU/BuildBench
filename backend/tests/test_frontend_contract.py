from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class FrontendContractTests(unittest.TestCase):
    def test_all_pages_share_versioned_local_frontend_assets(self) -> None:
        release = "20260809-2"
        html_paths = sorted(ROOT.glob("*.html"))
        self.assertEqual(len(html_paths), 14)

        shared_assets = (
            "styles.css",
            "assets/vendor/lucide.min.js",
            "i18n.js",
            "auth-client.js",
            "app.js",
        )
        for page_path in html_paths:
            page = page_path.read_text(encoding="utf-8")
            with self.subTest(page=page_path.name):
                for asset in shared_assets:
                    reference = f"{asset}?v={release}"
                    self.assertIn(reference, page)
                    self.assertEqual(page.count(reference), 1)
                self.assertNotIn("unpkg.com/lucide", page)

        lucide = ROOT / "assets" / "vendor" / "lucide.min.js"
        self.assertTrue(lucide.is_file())
        self.assertGreater(lucide.stat().st_size, 300_000)
        self.assertEqual(
            hashlib.sha256(lucide.read_bytes()).hexdigest(),
            "3411692820cb8d47543f69496aa25fd603a358f4498046f41c508a5a3342210e",
        )

    def test_overview_uses_a_poster_style_competition_hero(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for contract in (
            'class="overview-shell overview-hero-shell"',
            'class="overview-hero-copy"',
            'class="overview-hero-art"',
            'class="overview-hero-illustration"',
            'src="assets/buildbench-repair-agent.png"',
            'class="overview-hero-credits"',
            'class="overview-credit-list"',
            'src="assets/overview-icons/medal.png"',
            'src="assets/overview-icons/graduation-hat.png"',
            'src="assets/overview-icons/challenge.png"',
            'src="assets/overview-icons/process.png"',
            'src="assets/overview-icons/evaluated.png"',
            'src="assets/overview-icons/trophy.png"',
            'src="assets/overview-icons/calendar.png"',
            'src="assets/overview-icons/reference.png"',
            "Competition partners",
            "ICSE 2027 Competition Track",
            "Build-Bench Team · Microsoft",
            "Get the Starter Kit",
            "Explore the Challenge",
        ):
            self.assertIn(contract, html)
        self.assertTrue((ROOT / "assets" / "buildbench-repair-agent.png").is_file())
        for icon in (
            "medal.png",
            "graduation-hat.png",
            "challenge.png",
            "process.png",
            "evaluated.png",
            "trophy.png",
            "calendar.png",
            "reference.png",
        ):
            self.assertTrue((ROOT / "assets" / "overview-icons" / icon).is_file())
        self.assertNotIn('class="status-strip"', html)
        self.assertNotIn('class="overview-art-placeholder"', html)
        self.assertNotIn('<dl class="overview-hero-credits"', html)
        self.assertNotIn("Sponsored by", html)
        self.assertNotIn("Industry collaboration", html)
        self.assertNotIn('src="assets/overview-icons/handshake.png"', html)
        self.assertNotIn('overview-credit-icon::before', (ROOT / "styles.css").read_text(encoding="utf-8"))

    def test_overview_places_requested_organizers_after_hero(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertLess(html.index('class="overview-section overview-organizers-section"'), html.index('class="overview-framework-band"'))
        for name in (
            "Chenyu Zhao",
            "Shenglin Zhang",
            "Minghua Ma",
            "Yihang Lin",
            "Zihao Huang",
            "An Xu",
            "Chengtai Li",
        ):
            self.assertIn(name, html)
        for homepage in (
            "https://zcyyc.github.io/",
            "https://nkcs.iops.ai/zhangshenglin/",
            "https://marvin233.github.io/",
            "https://worstwoof.github.io/",
        ):
            self.assertIn(homepage, html)
        self.assertEqual(html.count('aria-label="Homepage link to be announced"'), 3)
        self.assertIn('src="assets/overview-icons/organizers.png"', html)
        self.assertTrue((ROOT / "assets" / "overview-icons" / "organizers.png").is_file())
        self.assertNotIn(".overview-page .overview-organizer-list li + li", css)

    def test_overview_uses_concise_challenge_copy(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for expected in (
            "Build-Bench challenges teams to build an Agent",
            "For each Case, the Agent receives a package workspace",
            "Build and test your Agent with the Starter Kit and public Cases.",
            "Upload an Agent version and pass the Hosted Smoke Test.",
            "Solutions are judged by verified build results",
        ):
            self.assertIn(expected, html)
        self.assertNotIn("Repairs may involve dependency declarations", html)

    def test_overview_includes_prizes_and_references_in_order(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertLess(html.index('id="evaluation-title"'), html.index('id="prizes-title"'))
        self.assertLess(html.index('id="prizes-title"'), html.index('id="dates-title"'))
        self.assertLess(html.index('id="dates-title"'), html.index('id="references-title"'))
        for expected in (
            "$1,000 USD (approx. ¥6,800 RMB)",
            "$500 USD (approx. ¥3,400 RMB)",
            "$250 USD (approx. ¥1,700 RMB)",
            "$2,750 USD (approx. ¥18,600 RMB)",
            "ICSE 2027 Attendance Support",
            "Prize &amp; Attendance Details",
            "Can Language Models Go Beyond Coding?",
            "EvidenT: An Evidence-Preserving Framework",
            "https://arxiv.org/abs/2511.00780",
            "https://conf.researchr.org/details/issta-2026/",
        ):
            self.assertIn(expected, html)
        self.assertEqual(html.count(">[paper]</a>"), 2)

    def test_challenge_page_uses_agent_competition_narrative(self) -> None:
        html = (ROOT / "task.html").read_text(encoding="utf-8")
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        translations = (ROOT / "i18n" / "task.js").read_text(encoding="utf-8")

        for expected in (
            "<title>Challenge | Build-Bench</title>",
            'content="Build a runnable Agent that diagnoses and repairs real cross-architecture package build failures under executable verification."',
            '<h1 id="challenge-page-title">Challenge</h1>',
            "Build an Agent that repairs real cross-architecture build failures",
            "You submit a runnable Agent — not precomputed Case-by-Case patches.",
            'class="challenge-lifecycle"',
            "Case workspace",
            "Agent diagnosis &amp; repair",
            "Final workspace",
            "Clean target rebuild",
            'class="challenge-benchmark-directions"',
            "<dt>163</dt><dd>x86_64 → aarch64</dd>",
            "<dt>105</dt><dd>aarch64 → x86_64</dd>",
            'href="submission.html#runtime-interface"',
            'href="https://github.com/AIOps-Lab-NKU/BuildBench"',
        ):
            self.assertIn(expected, html)

        section_ids = (
            "why-this-challenge",
            "your-mission",
            "agent-inputs",
            "agent-actions",
            "repair-lifecycle",
            "solved",
            "benchmark-scope",
            "start-building",
        )
        positions = [html.index(f'id="{section_id}"') for section_id in section_ids]
        self.assertEqual(positions, sorted(positions))

        for removed in (
            "Task &amp; Dataset",
            "1,687",
            "1,074",
            "candidate pool",
            "Splits and data integrity",
            'class="task-table',
            'class="status-strip',
            "Docker Validator",
            "repair.diff",
        ):
            self.assertNotIn(removed, html)

        for selector in (
            ".challenge-headline",
            ".challenge-meta",
            ".challenge-lifecycle",
            ".challenge-benchmark-directions",
            ".challenge-start-links",
        ):
            self.assertIn(selector, css)
        for translated in (
            'Challenge: "竞赛任务"',
            '"Your mission": "你的任务"',
            '"What counts as solved?": "怎样才算解决一个 Case？"',
            '"Get the Starter Kit": "获取 Starter Kit"',
        ):
            self.assertIn(translated, translations)
        self.assertNotIn("Task & Dataset", translations)

    def test_challenge_label_and_cross_links_are_consistent_sitewide(self) -> None:
        for page_path in ROOT.glob("*.html"):
            page = page_path.read_text(encoding="utf-8")
            if '<nav class="site-nav"' not in page or 'href="task.html"' not in page:
                continue
            with self.subTest(page=page_path.name):
                self.assertIn(">Challenge</a>", page)
                self.assertNotIn("Task &amp; Data", page)

        overview = (ROOT / "index.html").read_text(encoding="utf-8")
        faq = (ROOT / "faq.html").read_text(encoding="utf-8")
        rules = (ROOT / "rules.html").read_text(encoding="utf-8")
        self.assertIn('<a href="task.html">Challenge</a>', overview)
        self.assertIn('href="task.html#your-mission">Read the Challenge</a>', faq)
        self.assertIn("The Challenge page defines the competition task", rules)

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
            "Coding Agent Quick Start",
            "Human Quick Start",
            "Read AGENTS.md before changing files.",
            "./bb bootstrap my-agent --json",
            "./bb ready --agent ./agents/my-agent --json",
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
        self.assertEqual(html.count('class="quick-start-result"'), 7)
        self.assertIn('id="coding-agent-quick-start"', html)
        self.assertIn('id="human-quick-start"', html)

    def test_submission_guide_keeps_participant_contract_in_scope(self) -> None:
        html = (ROOT / "submission.html").read_text(encoding="utf-8")
        evaluation = (ROOT / "evaluation.html").read_text(encoding="utf-8")

        for expected in (
            "You need a Linux or WSL2 shell",
            "Different versioned Case sets are used",
            "Planned feature.",
            "The platform derives the canonical patch from the modified worktree.",
            "Final submission checklist",
            "Runtime and policy",
        ):
            self.assertIn(expected, html)

        for removed in (
            "Planned CLI example",
            "Build feedback flow",
            "Canonical patch validation flow",
            'class="compact-flow',
            'class="boundary-list',
        ):
            self.assertNotIn(removed, html)

        self.assertIn("How each Case is evaluated", evaluation)
        self.assertIn("official Docker Validator", evaluation)
        self.assertIn("evaluation.html#case-evaluation", html)

    def test_evaluation_protocol_is_participant_facing(self) -> None:
        html = (ROOT / "evaluation.html").read_text(encoding="utf-8")

        for expected in (
            "What counts as a successful repair?",
            "How each Case is evaluated",
            "How outcomes are handled",
            "How scoring works",
            "Evaluation stages and feedback",
            "Rules to be published before evaluation opens",
            "infrastructure_error",
            "No partial score is published",
        ):
            self.assertIn(expected, html)

        for organizer_only in (
            "Working evaluation",
            "Working decision",
            "Open decisions",
            "Team review",
            "Seven observable stages",
            'class="metric-panel',
        ):
            self.assertNotIn(organizer_only, html)

        self.assertNotIn('class="status-strip', html)
        self.assertEqual(html.count('class="protocol-table'), 2)

    def test_rules_page_is_a_plain_numbered_participant_rulebook(self) -> None:
        html = (ROOT / "rules.html").read_text(encoding="utf-8")
        translations = (ROOT / "i18n" / "rules.js").read_text(
            encoding="utf-8"
        )

        for expected in (
            "REGISTERING A TEAM OR SUBMITTING AN AGENT",
            "1. Competition scope",
            "2. Team registration and eligibility",
            "3. Agent submission and version control",
            "4. Competition data, models, and tools",
            "5. Evaluation and scoring",
            "6. Prohibited conduct",
            "7. Hidden evaluation and confidentiality",
            "8. Method disclosure and reproducibility",
            "9. Review, correction, and enforcement",
            "10. Versioned rules and pending parameters",
            "A Team may contain no more than five members",
            "Build Success Rate is the primary ranking metric",
        ):
            self.assertIn(expected, html)
            self.assertIn(f'"{expected}', translations)

        for removed in (
            'class="status-strip',
            'class="masthead-facts',
            'class="rule-points',
            'class="allowed-grid',
            'class="prohibited-list',
            'class="numbered-rules',
            'class="decision-table',
            "Rules preview",
            "Working Decision",
            "Team Review",
        ):
            self.assertNotIn(removed, html)

        self.assertNotIn("<table", html)
        self.assertEqual(html.count('class="rules-section'), 10)
        self.assertIn('class="page-rail rules-outline"', html)

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
        self.assertIn("Each Team may run one Full Evaluation", html)
        self.assertIn("data-live-board-body", html)
        self.assertIn("leaderboard-live.js", html)
        self.assertIn("Successful Cases", html)
        self.assertNotIn("Agent version", html)
        self.assertIn("Paper-reported model success rates", html)
        self.assertEqual(html.count('data-direction="forward"'), 7)
        self.assertEqual(html.count('data-direction="reverse"'), 7)
        self.assertIn("data-board-filter", html)
        self.assertIn("63.19%", html)
        self.assertIn("29.52%", html)
        self.assertIn('fetch("/api/leaderboard"', script)
        self.assertIn("case_set_version", script)
        self.assertIn("protocol_version", script)
        self.assertIn("entry.members", script)
        self.assertTrue(schema.is_file())

    def test_team_registration_and_session_frontend_contract(self) -> None:
        register = (ROOT / "register.html").read_text(encoding="utf-8")
        login = (ROOT / "login.html").read_text(encoding="utf-8")
        team = (ROOT / "team.html").read_text(encoding="utf-8")
        auth_client = (ROOT / "auth-client.js").read_text(encoding="utf-8")
        registration_script = (ROOT / "register.js").read_text(
            encoding="utf-8"
        )
        team_script = (ROOT / "team.js").read_text(encoding="utf-8")
        for hook in (
            "data-registration-form",
            "data-member-list",
            "data-add-member",
            "data-team-count",
        ):
            self.assertIn(hook, register)
        self.assertIn("/api/auth/register", registration_script)
        self.assertIn("MAX_ADDITIONAL_MEMBERS = 4", registration_script)
        self.assertIn("data-login-form", login)
        self.assertIn("auth-login-card", login)
        self.assertNotIn("login-brand-panel", login)
        self.assertIn("auth-register-card", register)
        self.assertIn("auth-form-section", register)
        self.assertIn("data-team-page", team)
        self.assertIn("/api/team/members", team_script)
        self.assertIn("X-CSRF-Token", auth_client)
        self.assertIn('credentials: "same-origin"', auth_client)

    def test_every_page_loads_shared_session_client(self) -> None:
        for path in ROOT.glob("*.html"):
            if path.name.startswith("404"):
                continue
            html = path.read_text(encoding="utf-8")
            self.assertIn(
                "auth-client.js",
                html,
                msg=f"{path.name} does not load the shared session client",
            )

    def test_timeline_is_a_participant_facing_date_list(self) -> None:
        html = (ROOT / "timeline.html").read_text(encoding="utf-8")
        translations = (ROOT / "i18n" / "timeline.js").read_text(
            encoding="utf-8"
        )

        for expected in (
            "Website beta and initial documentation",
            "Invited pilot",
            "Rules and resource limits frozen",
            "Public development and validation open",
            "Final Agent version freeze",
            "Final results published",
        ):
            self.assertIn(expected, html)
            self.assertIn(f'"{expected}"', translations)

        for date in (
            'datetime="2026-08-14"',
            'datetime="2026-08-17"',
            'datetime="2026-08-31"',
            'datetime="2026-09-07"',
            'datetime="2026-11-13"',
            'datetime="2026-11-20"',
        ):
            self.assertIn(date, html)

        for removed in (
            'class="status-strip',
            'class="masthead-facts',
            'class="page-rail',
            'class="source-callout',
            'class="gate-list',
            'class="phase-sequence',
            'class="notification-row',
            "July 31, 2026",
            "Proposal milestones",
        ):
            self.assertNotIn(removed, html)

        self.assertIn('class="roadmap"', html)
        self.assertEqual(html.count('class="roadmap-status '), 6)
        self.assertEqual(html.count("<time "), 6)
        self.assertNotIn("<table", html)

    def test_faq_follows_the_participant_journey_and_current_protocol(self) -> None:
        html = (ROOT / "faq.html").read_text(encoding="utf-8")
        translations = (ROOT / "i18n" / "faq.js").read_text(
            encoding="utf-8"
        )

        for expected in (
            "1. Start and register",
            "2. Develop locally",
            "3. Upload and qualify a version",
            "4. Evaluation and scoring",
            "5. Data, dates, and results",
            "How does Team registration work?",
            "Can I submit a custom Docker runtime?",
            "Can the Agent request build feedback while it runs?",
            "What does the Hosted Smoke Test check?",
            "How are failures, timeouts, and infrastructure errors handled?",
            "Which Case sets are used, and how large is the benchmark?",
            "What are the key participant dates?",
        ):
            self.assertIn(expected, html)
            self.assertIn(f'"{expected}"', translations)

        for current_fact in (
            "up to five people",
            "managed Python 3.11",
            "Do not assume that bb-build is currently available",
            "Every accepted upload is stored as an immutable Agent version",
            "Build Success Rate is the primary metric",
            "approximately 1,000 Cases",
            "August 17\u201328",
            "November 13",
        ):
            self.assertIn(current_fact, html)

        for obsolete in (
            'class="status-strip',
            'class="masthead-facts',
            'class="page-rail',
            'class="section-label',
            "Agent Submission Contract",
            "Are patch output and Agent container separate submission modes?",
            "Yes, when protocol.build_feedback",
            "Open Build Service is a platform",
            "Another 200 public package candidates",
            "July 31, 2026",
            "Research Leaderboard",
            "Team-size, affiliation, registration, and conflict-of-interest rules have not yet been announced",
        ):
            self.assertNotIn(obsolete, html)

        self.assertEqual(html.count('class="faq-section"'), 5)
        self.assertEqual(html.count("<details"), 19)
        self.assertNotIn("<table", html)

    def test_submission_and_evaluation_use_right_hand_document_navigation(self) -> None:
        styles = (ROOT / "styles.css").read_text(encoding="utf-8")

        for filename in ("submission.html", "evaluation.html"):
            html = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn("page-layout right-doc-layout", html)
            self.assertIn('class="page-rail', html)
            self.assertIn('class="page-document', html)

        submission = (ROOT / "submission.html").read_text(encoding="utf-8")
        self.assertIn("Competition", submission)
        self.assertIn("On this page", submission)
        self.assertIn(".right-doc-layout > .page-rail", styles)
        self.assertIn("grid-column: 2", styles)

    def test_account_navigation_is_stable_across_page_loads(self) -> None:
        auth_client = (ROOT / "auth-client.js").read_text(encoding="utf-8")
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        i18n = (ROOT / "i18n.js").read_text(encoding="utf-8")
        styles = (ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertIn("buildbench.session-hint.v1", auth_client)
        self.assertIn("getSessionHint", auth_client)
        self.assertIn("renderAccountState(account, hintedSession)", app)
        self.assertLess(
            app.index("renderAccountState(account, hintedSession)"),
            app.index("await window.BuildBenchAuth?.getSession?.()"),
        )
        self.assertIn("renderAccountNavigation();", app)
        self.assertIn('account.setAttribute("data-account-navigation", "")', i18n)
        self.assertIn('href="login.html">Sign in</a>', i18n)
        self.assertLess(
            i18n.index('className = "language-control"'),
            i18n.index('className = "account-navigation"'),
        )
        self.assertIn("min-width: 176px", styles)


if __name__ == "__main__":
    unittest.main()
