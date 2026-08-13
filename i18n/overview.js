window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.overview = Object.freeze({
  "Build-Bench Challenge | ICSE 2027": "Build-Bench Challenge | ICSE 2027",
  "The Build-Bench Challenge at ICSE 2027 evaluates agents for executable cross-architecture package build repair.":
    "ICSE 2027 Build-Bench Challenge 面向跨架构软件包构建修复，评测能够执行修复任务的 Agent。",
  "A competition for agent-driven repair of real package build failures across x86_64 and aarch64.":
    "面向 Agent 的真实软件包构建失败修复竞赛，覆盖 x86_64 与 aarch64 架构。",
  "ICSE 2027 Competition Track": "ICSE 2027 Competition Track",
  "Website beta": "网站 Beta",
  "Repair real cross-architecture package build failures with autonomous Agents.":
    "让自主 Agent 修复真实的跨架构软件包构建失败。",
  "Keeping large-scale software ecosystems portable and buildable across heterogeneous architectures has become an increasingly important challenge for sustainable software evolution. A package that builds on one architecture can still fail on another. Build-Bench turns these real portability failures into an executable benchmark for repair Agents.":
    "让大规模软件生态在异构架构之间持续保持可移植、可构建，正成为软件可持续演进中日益重要的挑战。一个软件包即使能在某种架构上成功构建，在另一种架构上仍可能失败。Build-Bench 将这些真实的可移植性故障转化为可执行验证的 Agent 修复基准。",
  "Teams submit a runnable repair Agent. Organizers run qualified versions, derive a canonical patch, and accept a repair only when the clean target-architecture build succeeds.":
    "参赛团队提交可运行的修复 Agent。组织方运行通过检查的版本，生成规范化补丁，并且只有在干净的目标架构构建成功时才认定修复有效。",
  "Repair real cross-architecture software package build failures.": "修复真实的跨架构软件包构建失败。",
  "Software increasingly has to run across heterogeneous hardware, yet package portability failures often emerge only when a project is rebuilt for another instruction-set architecture. Diagnosing them requires reasoning across source code, package metadata, dependencies, build scripts, and logs.":
    "软件日益需要运行在异构硬件平台上，但软件包的可移植性问题往往只有在迁移到另一种指令集架构并重新构建时才会暴露。定位这类问题需要综合分析源码、包元数据、依赖、构建脚本和日志。",
  "Teams submit a runnable repair Agent. Organizers run each qualified Agent on competition Cases, generate a canonical repair patch from its work, and verify the repair by rebuilding the clean package in the target environment.":
    "参赛团队提交一个可运行的修复 Agent。组织者在竞赛 Case 上运行每个通过检查的 Agent，根据其工作区生成规范化修复补丁，并在干净的目标环境中重新构建软件包以验证修复。",
  "Get the Starter Kit": "获取 Starter Kit",
  "Explore the Challenge": "了解竞赛任务",
  "Primary actions": "主要操作",
  "A repair Agent transforms a broken software package into a validated build artifact":
    "修复 Agent 将构建失败的软件包转化为通过验证的构建产物",
  "Competition hosts and collaborators": "竞赛主办与合作信息",
  "Competition partners": "赛事组织与合作",
  "Official track": "官方赛道",
  "Organized by": "组织方",
  "Nankai University · Microsoft": "南开大学 · 微软",
  "Industry collaboration": "产业合作",
  "Microsoft": "微软",
  "Affiliations": "合作单位",
  "Affiliated institutions and industry partners": "合作高校、科研机构与产业伙伴",
  "Nankai University": "南开大学",
  "Meituan": "美团",
  "Chinese Academy of Sciences": "中国科学院",
  "Nankai University logo": "南开大学校徽",
  "Microsoft logo": "微软标志",
  "Meituan logo": "美团标志",
  "Chinese Academy of Sciences logo": "中国科学院院徽",
  "Build-Bench repair workflow diagram": "Build-Bench 修复工作流图",
  "What is the challenge?": "竞赛任务是什么？",
  "Build-Bench challenges teams to build an Agent that repairs real software packages that succeed on one architecture but fail on another. The published benchmark contains 268 reproducible x86_64 ↔ aarch64 build failures.":
    "Build-Bench 要求参赛团队开发一个 Agent，用于修复在一种架构上构建成功、迁移到另一种架构后构建失败的真实软件包。已发布的 Benchmark 包含 268 个可复现的 x86_64 ↔ aarch64 构建失败。",
  "For each Case, the Agent receives a package workspace and failed-build context, then modifies the permitted files to restore a successful target build.":
    "对于每个 Case，Agent 会获得软件包工作区和构建失败上下文，并通过修改允许的文件来恢复目标架构上的成功构建。",
  "Build-Bench builds on our previously published": "Build-Bench 基于我们此前发布的",
  "CCF-A benchmark": "CCF-A Benchmark",
  "for cross-architecture package build repair.": "开展跨架构软件包构建修复研究。",
  "See reference 1": "查看参考文献 1",
  "Existing results show substantial room for improvement, motivating the development of more capable autonomous repair Agents.":
    "现有结果表明，该问题仍有很大的提升空间，因此需要开发能力更强的自主修复 Agent。",
  "The published Build-Bench workflow for cross-architecture package build repair and verification.":
    "已发布的 Build-Bench 跨架构软件包构建修复与验证工作流。",
  "How the competition works": "如何参加竞赛",
  "Develop": "开发",
  "— Build and test your Agent with the Starter Kit and public Cases.":
    "— 使用 Starter Kit 和公开 Case 开发并测试你的 Agent。",
  "Qualify": "资格验证",
  "— Upload an Agent version and pass the Hosted Smoke Test.":
    "— 上传一个 Agent 版本并通过 Hosted Smoke Test。",
  "Compete": "正式竞赛",
  "— Freeze a qualified version for organizer-run evaluation and leaderboard ranking.":
    "— 冻结一个已通过资格验证的版本，由组织者运行评测并生成排行榜名次。",
  "How are repairs evaluated?": "修复如何评测？",
  "A repair succeeds only if the Agent's final changes can be applied to a clean Case and the package builds successfully in the official target-architecture environment.":
    "只有当 Agent 的最终修改能够应用到干净的 Case，且软件包能够在官方目标架构环境中成功构建时，修复才算成功。",
  "Solutions are judged by verified build results, not by similarity to a reference patch.":
    "解决方案依据经过验证的构建结果进行判定，而不是依据其与参考补丁的相似度。",
  "Repairs are ranked primarily by": "修复结果主要依据",
  "Verified Build Success Rate": "经验证的构建成功率",
  ", with": "排名，同时将",
  "Execution Time": "执行时间",
  "and": "和",
  "Token Usage": "Token 使用量",
  "reported as secondary efficiency metrics.": "作为次要效率指标报告。",
  "Read Evaluation and scoring": "阅读评测与计分规则",
  "Important dates": "重要日期",
  "7 September 2026": "2026 年 9 月 7 日",
  "— Public development and validation open": "— 公开开发与验证阶段开放",
  "13 November 2026": "2026 年 11 月 13 日",
  "— Final Agent versions freeze": "— 最终 Agent 版本冻结",
  "By 20 November 2026": "不晚于 2026 年 11 月 20 日",
  "— Final results published": "— 公布最终结果",
  "ICSE 2027": "ICSE 2027",
  "— Competition session and presentations": "— 竞赛现场环节与方案展示",
  "Competition detail pages": "竞赛详情页面",
  "More information:": "更多信息：",
  Challenge: "竞赛任务",
  "Submission Guide": "提交指南",
  "Evaluation and scoring": "评测与计分",
  "Rules": "规则",
  "Timeline": "时间安排",
  "FAQ": "常见问题",
  "References": "参考文献",
  "Build-Bench publications": "Build-Bench 相关论文",
  "Chenyu Zhao, Shenglin Zhang*, Zeshun Huang, Weilin Jin, Yongqian Sun, Dan Pei, Chaoyun Zhang, Qingwei Lin, Chetan Bansal, Saravan Rajmohan, Minghua Ma. Can Language Models Go Beyond Coding? Assessing the Capability of Language Models to Build Real-World Systems. ACM Transactions on Software Engineering and Methodology (TOSEM), 2026. (CCF A)":
    "Chenyu Zhao, Shenglin Zhang*, Zeshun Huang, Weilin Jin, Yongqian Sun, Dan Pei, Chaoyun Zhang, Qingwei Lin, Chetan Bansal, Saravan Rajmohan, Minghua Ma. Can Language Models Go Beyond Coding? Assessing the Capability of Language Models to Build Real-World Systems. ACM Transactions on Software Engineering and Methodology (TOSEM), 2026. (CCF A)",
  "Chenyu Zhao, Minghua Ma*, Shenglin Zhang, Zeshun Huang, Yongqian Sun, Chetan Bansal, Saravan Rajmohan, Dan Pei. EvidenT: An Evidence-Preserving Framework for Iterative System-Level Package Repair. ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA), 2026. (CCF A)":
    "Chenyu Zhao, Minghua Ma*, Shenglin Zhang, Zeshun Huang, Yongqian Sun, Chetan Bansal, Saravan Rajmohan, Dan Pei. EvidenT: An Evidence-Preserving Framework for Iterative System-Level Package Repair. ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA), 2026. (CCF A)",
  "[paper]": "[论文]",
  "Organized by Nankai University with industry collaboration from Microsoft.":
    "由南开大学组织，微软提供产业合作支持。",
  "Project links": "项目链接",
  "Paper": "论文",
  "Citation": "引用",
  "GitHub": "GitHub",
  "Contact": "联系",
  "Back to top": "返回顶部",
});
