from __future__ import annotations

import hashlib
import html as html_lib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class FrontendContractTests(unittest.TestCase):
    def test_all_pages_share_versioned_local_frontend_assets(self) -> None:
        release = "20260813-3"
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

    def test_primary_navigation_uses_ordered_more_dropdown_sitewide(self) -> None:
        expected_routes = [
            "index.html",
            "task.html",
            "submission.html",
            "leaderboard.html",
            "rules.html",
            "timeline.html",
            "faq.html",
            "contact.html",
        ]
        active_routes = {
            "index.html": "index.html",
            "task.html": "task.html",
            "submission.html": "submission.html",
            "data-downloads.html": "submission.html",
            "my-submissions.html": "submission.html",
            "evaluation-detail.html": "submission.html",
            "leaderboard.html": "leaderboard.html",
            "rules.html": "rules.html",
            "timeline.html": "timeline.html",
            "faq.html": "faq.html",
            "contact.html": "contact.html",
        }

        for page_path in sorted(ROOT.glob("*.html")):
            page = page_path.read_text(encoding="utf-8")
            nav_start = page.index('<nav class="site-nav"')
            nav_end = page.index("</nav>", nav_start) + len("</nav>")
            nav = page[nav_start:nav_end]

            with self.subTest(page=page_path.name):
                self.assertEqual(re.findall(r'href="([^"]+)"', nav), expected_routes)
                self.assertEqual(nav.count("data-nav-more>"), 1)
                self.assertEqual(nav.count("data-nav-more-toggle"), 1)
                self.assertEqual(nav.count("data-nav-more-menu"), 1)
                self.assertLess(nav.index("data-nav-more>"), nav.index('href="timeline.html"'))
                self.assertIn("Competition dates and milestones", nav)
                self.assertIn("Common questions and participant support", nav)
                self.assertIn("Competition contact and organizing team", nav)
                self.assertLess(nav.index('href="faq.html"'), nav.index('href="contact.html"'))

                active_route = active_routes.get(page_path.name)
                if active_route is None:
                    self.assertNotIn('aria-current="page"', nav)
                else:
                    self.assertEqual(nav.count('aria-current="page"'), 1)
                    self.assertIn(f'href="{active_route}"', nav)

                if page_path.name in {"timeline.html", "faq.html", "contact.html"}:
                    self.assertIn('class="nav-more active"', nav)
                else:
                    self.assertNotIn('class="nav-more active"', nav)

        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        translations = (ROOT / "i18n.js").read_text(encoding="utf-8")
        for contract in (
            ".nav-more-toggle",
            ".nav-more-menu",
            ".nav-more:hover .nav-more-menu",
            ".nav-more.open .nav-more-menu",
            ".nav-more.active .nav-more-toggle",
        ):
            self.assertIn(contract, css)
        for contract in (
            'document.querySelector("[data-nav-more]")',
            'document.querySelector("[data-nav-more-toggle]")',
            'navMoreButton.setAttribute("aria-expanded", String(open))',
            'navMore?.addEventListener("focusout"',
        ):
            self.assertIn(contract, app)
        for contract in (
            'More: "更多"',
            '"Competition dates and milestones": "比赛日期与里程碑"',
            '"Common questions and participant support": "常见问题与参赛支持"',
            'Contact: "联系我们"',
            '"Competition contact and organizing team": "竞赛联系信息与组织团队"',
        ):
            self.assertIn(contract, translations)

    def test_leaderboard_navigation_uses_text_emphasis(self) -> None:
        for page_path in sorted(ROOT.glob("*.html")):
            page = page_path.read_text(encoding="utf-8")
            nav_start = page.index('<nav class="site-nav"')
            nav_end = page.index("</nav>", nav_start) + len("</nav>")
            nav = page[nav_start:nav_end]
            with self.subTest(page=page_path.name):
                self.assertEqual(nav.count('class="nav-emphasis'), 1)
                self.assertIn('href="leaderboard.html"', nav)
                self.assertIn('data-lucide="trophy"', nav)

        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        emphasis_rules = re.findall(
            r"\.site-nav \.nav-emphasis \{(?P<body>.*?)\}", css, re.DOTALL
        )
        self.assertEqual(len(emphasis_rules), 2)

        desktop_rule, mobile_rule = emphasis_rules
        for contract in (
            "color: var(--blue-dark);",
            "font-weight: 800;",
            "background: transparent;",
            "border-radius: 0;",
        ):
            self.assertIn(contract, desktop_rule)
        for obsolete in (
            "color: #fff;",
            "background: var(--dark);",
            "border-radius: 5px;",
        ):
            self.assertNotIn(obsolete, desktop_rule)

        emphasis_section = css[css.index(".site-nav .nav-emphasis"):css.index(".site-nav svg")]
        self.assertIn(".site-nav .nav-emphasis svg", emphasis_section)
        self.assertIn("color: var(--amber);", emphasis_section)
        self.assertIn(".site-nav .nav-emphasis:hover", emphasis_section)
        self.assertIn(".site-nav .nav-emphasis.active", emphasis_section)
        self.assertNotIn("background: var(--blue-dark);", emphasis_section)

        for contract in (
            "justify-content: flex-start;",
            "margin: 0;",
            "padding: 0 4px;",
        ):
            self.assertIn(contract, mobile_rule)

    def test_overview_uses_a_poster_style_competition_hero(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for contract in (
            'class="overview-shell overview-hero-shell"',
            'class="overview-hero-copy"',
            'class="overview-hero-art"',
            'class="overview-hero-illustration"',
            'src="assets/buildbench-repair-agent.png"',
            'class="overview-hero-partners"',
            'src="assets/overview-icons/medal.png"',
            'src="assets/affiliations/nankai-university.jpg"',
            'src="assets/affiliations/microsoft.svg"',
            'src="assets/overview-icons/challenge.png"',
            'src="assets/overview-icons/process.png"',
            'src="assets/overview-icons/evaluated.png"',
            'src="assets/overview-icons/calendar.png"',
            'src="assets/overview-icons/reference.png"',
            "Repair real cross-architecture package build failures with autonomous LLM Agents.",
            "Build-Bench Challenge turns these failures into an executable, benchmark-driven competition",
            "A Case is counted",
            "patch complies with competition policy",
            "Accepted to the ICSE 2027 Competition Track",
            "Nankai University · Microsoft",
            "Supporters",
            'src="assets/affiliations/meituan-new.png?v=20260816-1"',
            'src="assets/affiliations/cnic.png?v=20260817-1"',
            "Model API support",
            "Compute infrastructure support",
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
            "calendar.png",
            "reference.png",
        ):
            self.assertTrue((ROOT / "assets" / "overview-icons" / icon).is_file())
        self.assertNotIn('class="status-strip"', html)
        self.assertNotIn('class="overview-art-placeholder"', html)
        self.assertNotIn('<dl class="overview-hero-credits"', html)
        self.assertNotIn("Sponsored by", html)
        self.assertNotIn("Industry collaboration", html)
        self.assertNotIn("Build-Bench Team · Microsoft", html)
        self.assertNotIn('src="assets/overview-icons/handshake.png"', html)
        self.assertNotIn('overview-credit-icon::before', (ROOT / "styles.css").read_text(encoding="utf-8"))

    def test_contact_replaces_overview_organizers(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn('class="overview-section overview-last-section overview-references-section"', html)
        self.assertIn('<a href="contact.html">Contact</a>', html)
        self.assertNotIn("overview-organizers-section", html)
        self.assertNotIn("overview-organizer-list", html)
        self.assertNotIn('src="assets/overview-icons/organizers.png"', html)
        self.assertNotIn(".overview-page .overview-organizer", css)

    def test_contact_page_uses_plain_responsive_team_roster(self) -> None:
        html = (ROOT / "contact.html").read_text(encoding="utf-8")
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        translations = (ROOT / "i18n" / "contact.js").read_text(encoding="utf-8")
        left_start = html.index('class="contact-roster-column" aria-label="Primary organizers"')
        right_start = html.index('class="contact-roster-column" aria-label="Organizing team members"')
        roster_end = html.index("</section>", right_start)
        left_column = html[left_start:right_start]
        right_column = html[right_start:roster_end]

        self.assertIn("Contact Information", html)
        self.assertIn("For any inquiries, please email us at", html)
        self.assertIn("buildbench-challenge@googlegroups.com", html)
        self.assertEqual(left_column.count('class="contact-member"'), 3)
        self.assertEqual(right_column.count('class="contact-member"'), 4)
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
            "https://minghuama233.github.io/",
            "https://terriyyy.github.io/",
            "https://worstwoof.github.io/",
        ):
            self.assertIn(homepage, html)
        self.assertEqual(html.count('class="contact-member-homepage"'), 5)
        self.assertNotIn("contact-member-homepage--placeholder", html)
        self.assertNotIn("Competition Organizer", html + translations)
        self.assertNotIn("Organizing Team Member", html + translations)
        self.assertIn("Her research focuses on AI Agents", html + translations)
        self.assertNotIn("His research focuses on AI Agents", html + translations)

        image_names = (
            "chenyu-zhao.jpg",
            "shenglin-zhang.png",
            "minghua-ma.png",
            "yihang-lin.png",
            "zihao-huang.jpg",
            "an-xu.jpg",
            "chengtai-li.jpg",
        )
        for image_name in image_names:
            self.assertIn(f'src="assets/contact/{image_name}"', html)
            self.assertTrue((ROOT / "assets" / "contact" / image_name).is_file())

        for article in re.findall(r'<article class="contact-member">(.*?)</article>', html, re.S):
            self.assertLess(article.index("contact-member-avatar"), article.index("<h3>"))
            self.assertLess(article.index("<h3>"), article.index("contact-member-affiliation"))
            if "contact-member-homepage" in article:
                self.assertLess(article.index("contact-member-affiliation"), article.index("contact-member-homepage"))
                self.assertLess(article.index("contact-member-homepage"), article.index("contact-member-bio"))
            else:
                self.assertTrue("An Xu" in article or "Chengtai Li" in article)
                self.assertLess(article.index("contact-member-affiliation"), article.index("contact-member-bio"))
        for contract in (
            ".contact-roster",
            "grid-template-columns: repeat(3, minmax(0, 1fr));",
            "grid-template-columns: repeat(4, minmax(0, 1fr));",
            "grid-template-columns: repeat(2, minmax(0, 1fr));",
            ".contact-member",
            "flex-direction: column;",
            "width: min(1220px, calc(100% - 64px));",
            ".organizer-photo-wrap",
            "width: 104px;",
            "height: 116px;",
            "overflow: visible;",
            ".organizer-photo",
            "max-width: 104px;",
            "max-height: 116px;",
            "width: auto;",
            "height: auto;",
            "object-fit: contain;",
            "object-position: center center;",
            ".organizer-photo--chengtai",
            "width: 90px;",
            "@media (max-width: 1180px)",
            "@media (max-width: 720px)",
            "grid-template-columns: 1fr;",
        ):
            self.assertIn(contract, css)
        contact_css = css[css.index("/* Contact */"):css.index("@media (max-width: 680px)", css.index("/* Contact */"))]
        self.assertNotIn("box-shadow", contact_css)
        self.assertNotIn("height: 100vh", contact_css)
        self.assertNotIn("overflow: hidden", contact_css)
        self.assertEqual(contact_css.count("object-fit: cover"), 1)
        self.assertNotIn("object-position: bottom", contact_css)
        self.assertNotIn("scale(", contact_css)
        self.assertNotIn("translate(", contact_css)
        self.assertNotIn("contact-card", html + css)
        self.assertEqual(html.count('class="organizer-photo-wrap"'), 7)
        self.assertEqual(html.count('contact-member-avatar organizer-photo'), 7)
        self.assertEqual(html.count("organizer-photo--chengtai"), 1)
        for contract in (
            '"Contact Information": "联系方式"',
            '"Nankai University": "南开大学"',
            '"Microsoft M365 Research": "微软 M365 研究院"',
            '"Chenyu Zhao": "赵晨宇"',
            '"Shenglin Zhang": "张圣林"',
            '"Minghua Ma": "马明华"',
            '"Yihang Lin": "林亦航"',
            '"Zihao Huang": "黄子豪"',
            '"An Xu": "徐安"',
            '"Chengtai Li": "李铖泰"',
            '"An Xu is an undergraduate student in Software Engineering at Nankai University.',
            '"徐安是南开大学软件工程专业本科生。',
        ):
            self.assertIn(contract, translations)

        bios = re.findall(r'<p class="contact-member-bio">(.*?)</p>', html, re.S)
        self.assertEqual(len(bios), 7)
        for bio in bios:
            self.assertIn(html_lib.unescape(re.sub(r"\s+", " ", bio).strip()), translations)

    def test_overview_places_competition_and_support_roles_in_hero(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "overview.css").read_text(encoding="utf-8")
        translations = (ROOT / "i18n" / "overview.js").read_text(encoding="utf-8")
        hero_art = html.index('class="overview-hero-art"')
        partners = html.index('class="overview-hero-partners"')
        affiliations = html.index('class="overview-hero-affiliations"', partners)
        challenge = html.index('class="overview-section"', partners)
        self.assertLess(hero_art, partners)
        self.assertLess(partners, affiliations)
        self.assertLess(affiliations, challenge)
        self.assertNotIn('class="overview-affiliations-section"', html)

        partner_positions = [
            html.index('class="overview-credit-item overview-credit-track"', partners, challenge),
            html.index('class="overview-credit-item overview-credit-organizer"', partners, challenge),
            affiliations,
        ]
        self.assertEqual(partner_positions, sorted(partner_positions))
        self.assertLess(html.index("Official competition", partners, challenge), html.index("assets/overview-icons/medal.png", partners, challenge))
        self.assertLess(html.index("Organized by", partners, challenge), html.index("assets/affiliations/nankai-university.jpg", partners, challenge))
        self.assertLess(html.index("Supporters", affiliations, challenge), html.index("assets/affiliations/meituan-new.png", affiliations, challenge))

        organizer_assets = (
            "assets/affiliations/nankai-university.jpg",
            "assets/affiliations/microsoft.svg",
        )
        positions = [html.index(asset, partners, affiliations) for asset in organizer_assets]
        self.assertEqual(positions, sorted(positions))
        for asset in organizer_assets:
            self.assertTrue((ROOT / asset).is_file())

        supporter_assets = (
            "assets/affiliations/meituan-new.png",
            "assets/affiliations/cnic.png",
        )
        for asset in supporter_assets:
            self.assertIn(asset, html[affiliations:challenge])
            self.assertTrue((ROOT / asset).is_file())
        self.assertNotIn("assets/affiliations/chinese-academy-of-sciences.jpg", html)

        for contract in (
            ".overview-page .overview-hero-partners",
            ".overview-page .overview-hero-partners .overview-credit-body",
            "grid-area: partners;",
            "align-items: start;",
            "flex-direction: column;",
            "grid-template-columns: minmax(240px, 0.9fr) minmax(270px, 0.95fr) minmax(460px, 1.45fr);",
            '"partners partners"',
            "min-height: calc(100svh - var(--header-height));",
            ".overview-page .overview-hero-partners .overview-organizer-logos",
            ".overview-page .overview-hero-partners .overview-hero-affiliation-list",
            ".overview-page .overview-hero-partners .overview-supporter-logo--cnic",
        ):
            self.assertIn(contract, css)
        for contract in (
            '"Official competition": "官方竞赛"',
            'Supporters: "支持单位"',
            '"Meituan": "美团"',
            '"Computer Network Information Center, Chinese Academy of Sciences": "中科院计算机网络信息中心"',
            '"Model API support": "模型 API 支持"',
            '"Compute infrastructure support": "算力设备支持"',
        ):
            self.assertIn(contract, translations)
        self.assertNotIn('"Chinese Academy of Sciences":', translations)

    def test_overview_uses_revised_challenge_copy(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for expected in (
            "Build-Bench Challenge asks teams to develop an LLM-based repair Agent",
            "source and target architecture metadata",
            "Build and test your Agent with the Starter Kit and public development Cases.",
            "Submit an Agent version and pass the Hosted Smoke Test.",
            "official ranking is based on verified executable outcomes",
            "more than 200 public development packages and over 1,000 hidden evaluation packages",
        ):
            self.assertIn(expected, html)
        self.assertNotIn("Repairs may involve dependency declarations", html)

    def test_overview_uses_revised_workflow_and_omits_unconfirmed_recognition(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "overview.css").read_text(encoding="utf-8")
        translations = (ROOT / "i18n" / "overview.js").read_text(encoding="utf-8")
        self.assertLess(html.index('id="evaluation-title"'), html.index('id="dates-title"'))
        self.assertLess(html.index('id="dates-title"'), html.index('id="references-title"'))

        for expected in (
            'class="overview-workflow-scroll"',
            'src="assets/overview-evaluation-workflow.png"',
            "Build-Bench Challenge evaluation workflow",
            'href="#reference-1"',
            'aria-label="See reference 1"',
            '>[1]</a>',
            '<li id="reference-1">',
            "Can Language Models Go Beyond Coding?",
            "EvidenT: An Evidence-Preserving Framework",
            "https://arxiv.org/abs/2511.00780",
            "https://conf.researchr.org/details/issta-2026/",
        ):
            self.assertIn(expected, html)

        self.assertLess(html.index('href="#reference-1"'), html.index('<li id="reference-1">'))
        self.assertLess(html.index('class="overview-challenge-figure"'), html.index('class="overview-section-link"'))
        for unconfirmed in (
            "overview-highlights-section",
            'id="highlights-title"',
            'class="overview-prize-list"',
            "Prizes and recognition",
            "Recognition and opportunities",
            "1st Prize",
            "$1,000",
            "Best Open Source / Best Repair Award",
        ):
            self.assertNotIn(unconfirmed, html)

        self.assertIn(".overview-page .overview-workflow-scroll", css)
        self.assertIn("width: min(94%, 840px)", css)
        self.assertTrue((ROOT / "assets" / "overview-evaluation-workflow.png").is_file())
        self.assertNotIn("overview-prize", css)
        self.assertIn('"See reference 1": "查看参考文献 1"', translations)
        for unconfirmed_translation in (
            '"Prizes and recognition":',
            '"1st Prize":',
            '"Best Open Source / Best Repair Award":',
        ):
            self.assertNotIn(unconfirmed_translation, translations)
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
            'href="submission.html#runtime-interface"',
        ):
            self.assertIn(expected, html)

        section_ids = (
            "why-this-challenge",
            "your-mission",
            "agent-inputs",
            "agent-actions",
            "repair-lifecycle",
            "solved",
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
            'class="challenge-meta',
            "Challenge summary",
            "268 reproducible failures",
            "x86_64 ↔ aarch64",
            "Executable verification",
            'id="benchmark-scope"',
            'href="#benchmark-scope"',
            'class="challenge-benchmark-directions"',
            "Benchmark scope",
            "Benchmark migration directions",
            "<dt>163</dt><dd>x86_64 → aarch64</dd>",
            "<dt>105</dt><dd>aarch64 → x86_64</dd>",
            "View the Build-Bench Benchmark",
            "Docker Validator",
            "repair.diff",
        ):
            self.assertNotIn(removed, html)

        for selector in (
            ".challenge-headline",
            ".challenge-lifecycle",
            ".challenge-start-links",
        ):
            self.assertIn(selector, css)
        self.assertNotIn(".challenge-meta", css)
        self.assertNotIn(".challenge-benchmark-directions", css)
        for removed_translation in (
            '"Challenge summary":',
            '"268 reproducible failures":',
            '"x86_64 ↔ aarch64":',
            '"Executable verification":',
            '"Benchmark scope":',
            '"The published Build-Bench benchmark contains 268 reproducible cross-architecture package build failures across two migration directions:":',
            '"Benchmark migration directions":',
            '"x86_64 → aarch64":',
            '"aarch64 → x86_64":',
            '"The published benchmark provides the research foundation and public development resources for the competition.',
            '"View the Build-Bench Benchmark":',
        ):
            self.assertNotIn(removed_translation, translations)
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
            "Manual Quick Start",
            "https://github.com/AIOps-Lab-NKU/BuildBench-Agent-Baseline.git",
            "cd BuildBench-Agent-Baseline/starter-kit",
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
        self.assertIn('id="manual-quick-start"', html)

        for expected in (
            "Build, test, and submit your Agent",
            "Get Started",
            'id="agent-package"',
            'id="runtime-interface"',
            'id="test-and-qualify"',
            'id="final-checklist"',
            "04 / Qualify",
            "05 / Final",
        ):
            self.assertIn(expected, html)
        self.assertNotIn("build-feedback protocol, and status schema", html)

    def test_submission_guide_keeps_participant_contract_in_scope(self) -> None:
        html = (ROOT / "submission.html").read_text(encoding="utf-8")
        rules = (ROOT / "rules.html").read_text(encoding="utf-8")

        for expected in (
            "You need a Linux or WSL2 shell",
            "Different versioned Case sets are used",
            "Planned feature.",
            "The official repair is the final file state of",
            "modified_paths</code>, if included, is advisory only",
            "automatically derives a canonical <code>repair.diff</code>",
            "Git extended unified-diff format",
            "disables rename detection for deterministic canonicalization",
            "replays this diff on a fresh Case",
            "per-Case evaluation artifacts, logs, and validation results",
            "precomputed Case-specific repair patches",
            "lightweight qualification Cases",
            "For the current v0.1 protocol",
            "The Hosted Smoke Test uses the same Agent Runner",
            "Before Full Evaluation",
            "The entrypoint starts non-interactively and follows the declared runtime contract.",
            "No secrets, caches, precomputed Case-specific repair patches, or run artifacts are included.",
            "No intended repair is left only as an unapplied patch",
            "Final submission checklist",
            "Runtime and policy",
        ):
            self.assertIn(expected, html)

        for removed in (
            "Planned CLI example",
            "Build feedback flow",
            "Canonical patch validation flow",
            "pre-generated patches",
            "lightweight public Cases",
            "deterministic and non-interactive",
            "For the current v0.1 local protocol",
            "hosted Smoke Test",
            "Smoke tests",
            "full evaluation",
            "127.0.0.1",
            "localhost",
            'class="compact-flow',
            'class="boundary-list',
        ):
            self.assertNotIn(removed, html)

        self.assertIn("official Docker Validator", rules)
        self.assertIn("rules.html#evaluation-scoring", html)

    def test_evaluation_protocol_is_consolidated_into_rules(self) -> None:
        html = (ROOT / "rules.html").read_text(encoding="utf-8")
        translations = (ROOT / "i18n" / "rules.js").read_text(encoding="utf-8")

        for expected in (
            "5.1 Successful repair and Per-Case validation",
            "5.2 Terminal outcomes",
            "5.3 Ranking and diagnostics",
            "5.4 Evaluation stages and feedback",
            "5.5 Versioned parameters",
            "official Docker Validator",
            "Verified Build Success Rate",
            "Execution Time",
            "Token Usage",
            "Hosted Smoke Test",
            "Full Evaluation during the public phase",
            "Hidden final evaluation",
            "infrastructure_error",
            "No partial official score is published",
            "Current pilot settings do not define these competition limits",
        ):
            self.assertIn(expected, html)

        for expected in (
            "5.1 Successful repair and Per-Case validation",
            "5.2 Terminal outcomes",
            "5.3 Ranking and diagnostics",
            "5.4 Evaluation stages and feedback",
            "5.5 Versioned parameters",
            "Verified Build Success Rate",
            "Execution Time",
            "Token Usage",
            "Hosted Smoke Test.",
            "Full Evaluation during the public phase.",
            "Hidden final evaluation.",
            "No partial official score is published",
            "Current pilot settings do not define these competition limits",
        ):
            self.assertIn(f'"{expected}', translations)

        self.assertFalse((ROOT / "evaluation.html").exists())
        self.assertFalse((ROOT / "i18n" / "evaluation.js").exists())
        for page_path in ROOT.glob("*.html"):
            self.assertNotIn("evaluation.html", page_path.read_text(encoding="utf-8"))

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
            "Verified Build Success Rate",
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
            "releases/download/v0.1.0-rc.2/"
            "buildbench-starter-kit-0.1.0-rc.2.zip",
            html,
        )
        self.assertIn(
            "releases/download/v0.1.0-rc.2/SHA256SUMS",
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
        for removed in (
            "Research reference",
            "Paper-reported model success rates",
            "research-baselines",
            "research-baseline-table",
            "data-board-filter",
            "63.19%",
            "29.52%",
        ):
            self.assertNotIn(removed, html)
        self.assertNotIn("boardRows", (ROOT / "app.js").read_text(encoding="utf-8"))
        self.assertNotIn("research-baseline", (ROOT / "styles.css").read_text(encoding="utf-8"))
        self.assertNotIn("Research reference", (ROOT / "i18n" / "leaderboard.js").read_text(encoding="utf-8"))
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
        self.assertIn('name="captain_institutional_email"', register)
        self.assertIn('data-member-field="institutional_email"', register)
        self.assertIn("institutional_email", registration_script)
        self.assertIn("data-login-form", login)
        self.assertIn("auth-login-card", login)
        self.assertNotIn("login-brand-panel", login)
        self.assertIn("auth-register-card", register)
        self.assertIn("auth-form-section", register)
        self.assertIn("data-team-page", team)
        self.assertIn('name="institutional_email"', team)
        self.assertIn("/api/team/members", team_script)
        self.assertIn("institutional_email", team_script)
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

    def test_submission_uses_right_hand_document_navigation(self) -> None:
        styles = (ROOT / "styles.css").read_text(encoding="utf-8")
        submission = (ROOT / "submission.html").read_text(encoding="utf-8")
        self.assertIn("page-layout right-doc-layout", submission)
        self.assertIn('class="page-rail', submission)
        self.assertIn('class="page-document', submission)
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
