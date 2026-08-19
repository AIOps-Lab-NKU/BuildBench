window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.overview = Object.freeze({
  "Build-Bench Challenge | ICSE 2027": "Build-Bench Challenge | ICSE 2027",
  "Repair real cross-architecture package build failures with autonomous LLM Agents.":
    "让自主 LLM Agent 修复真实的跨架构软件包构建失败。",
  "A competition for LLM-based repair Agents that address real package build failures across x86_64, aarch64, and riscv64.":
    "面向 LLM 修复 Agent 的真实软件包构建失败修复竞赛，覆盖 x86_64、aarch64 与 riscv64 架构。",
  "ICSE 2027 Competition Track": "ICSE 2027 Competition Track",
  "Cloud, edge, and emerging platforms increasingly span heterogeneous instruction set architectures, making software portability a growing engineering challenge.":
    "云计算、边缘计算和新兴平台正越来越多地采用异构指令集架构，软件要在这些平台之间保持可移植，正成为日益突出的工程挑战。",
  "Architecture-specific code, dependencies, compilers, build options, and packaging logic can cause a package that builds on one architecture to fail on another.":
    "特定架构的代码、依赖、编译器、构建选项和打包逻辑，都可能导致一个在某种架构上能够构建的软件包在另一种架构上构建失败。",
  "Build-Bench Challenge turns these failures into an executable, benchmark-driven competition for LLM-based repair Agents that generalize across packages, failure types, architectures, and migration directions.":
    "Build-Bench Challenge 将这些故障转化为一项可执行、由基准驱动的竞赛，用于评测 LLM 修复 Agent 能否跨软件包、故障类型、架构和迁移方向实现泛化。",
  "Cloud, edge, and emerging platforms increasingly span heterogeneous instruction set architectures, making software portability a growing engineering challenge. Architecture-specific code, dependencies, compilers, build options, and packaging logic can cause a package that builds on one architecture to fail on another. Build-Bench Challenge turns these failures into an executable, benchmark-driven competition for LLM-based repair Agents that generalize across packages, failure types, architectures, and migration directions.":
    "云计算、边缘计算和新兴平台正越来越多地采用异构指令集架构，软件要在这些平台之间保持可移植，正成为日益突出的工程挑战。特定架构的代码、依赖、编译器、构建选项和打包逻辑，都可能导致一个在某种架构上能够构建的软件包在另一种架构上构建失败。Build-Bench Challenge 将这些故障转化为一项可执行、由基准驱动的竞赛，用于评测 LLM 修复 Agent 能否跨软件包、故障类型、架构和迁移方向实现泛化。",
  "Teams submit a runnable repair Agent rather than Case-specific patches. Organizers execute each qualified Agent on controlled source-to-target migration Cases, derive a canonical patch from its modifications, and reapply the patch to a clean copy of the package. A Case is counted as successfully repaired only when the patch complies with competition policy and the official target-architecture build completes with the expected package artifacts.":
    "团队提交的是可运行的修复 Agent，而不是针对特定 Case 的补丁。组织方在受控的源架构到目标架构迁移 Case 上运行每个通过资格检查的 Agent，根据其修改生成 canonical patch，并将补丁重新应用到软件包的干净副本。只有当补丁符合竞赛政策，且官方目标架构构建成功并产出预期的软件包制品时，该 Case 才算修复成功。",
  "Evaluation scope:": "评测范围：",
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
  "Official competition": "官方竞赛",
  "Accepted to the ICSE 2027 Competition Track": "已获 ICSE 2027 竞赛赛道接收",
  "View official track page": "查看官方赛道页面",
  "Organized by": "组织方",
  "Nankai University · Microsoft": "南开大学 · 微软",
  "Industry collaboration": "产业合作",
  "Microsoft": "微软",
  Supporters: "支持单位",
  "Model API support": "模型 API 支持",
  "Compute infrastructure support": "算力设备支持",
  "Nankai University": "南开大学",
  "Meituan": "美团",
  "Computer Network Information Center, Chinese Academy of Sciences": "中科院计算机网络信息中心",
  "Nankai University logo": "南开大学校徽",
  "Microsoft logo": "微软标志",
  "Meituan logo": "美团标志",
  "Computer Network Information Center, Chinese Academy of Sciences logo": "中科院计算机网络信息中心标志",
  "Official competition and organizing partners": "官方竞赛与组织方",
  "Build-Bench Challenge evaluation workflow, from Case input and Agent execution to patch canonicalization, clean rebuilding, and scoring":
    "Build-Bench Challenge 评测流程：从 Case 输入和 Agent 执行，到补丁规范化、干净环境重构建与计分",
  "Scrollable evaluation workflow diagram": "可横向滚动查看的评测流程图",
  "What is the challenge?": "竞赛任务是什么？",
  "Build-Bench Challenge asks teams to develop an LLM-based repair Agent for real software packages that build on one instruction set architecture (ISA) but fail after migration to another. The competition covers migrations among x86_64, aarch64, and riscv64, and evaluates whether an Agent can generalize across packages, failure types, architectures, and migration directions.":
    "Build-Bench Challenge 要求团队为真实软件包开发基于 LLM 的修复 Agent。这些软件包能够在一种指令集架构（ISA）上成功构建，却在迁移到另一种架构后构建失败。竞赛覆盖 x86_64、aarch64 和 riscv64 之间的迁移，并评测 Agent 能否跨软件包、故障类型、架构和迁移方向实现泛化。",
  "For each Case, the Agent receives a package workspace, source and target architecture metadata, and the failed target-build log. It may inspect and modify only permitted files. Organizers derive a canonical patch from these changes, apply it to a clean package copy, and rebuild the package in a controlled target-architecture environment. A repair succeeds only when the patch passes policy checks, the build completes, and the expected package artifacts are produced.":
    "对于每个 Case，Agent 会获得软件包工作区、源架构与目标架构元数据，以及目标架构构建失败日志。Agent 只能检查和修改允许范围内的文件。组织方根据这些修改生成 canonical patch，将其应用到软件包的干净副本，并在受控的目标架构环境中重新构建。只有当补丁通过政策检查、构建完成且产生预期的软件包制品时，修复才算成功。",
  "The workflow below summarizes how submitted Agents are executed, converted into canonical patches, and validated through clean target-architecture builds.":
    "下方流程概括了提交的 Agent 如何被执行、转换为 canonical patch，并通过干净的目标架构构建完成验证。",
  "This challenge builds on Build-Bench, our study accepted for publication in ACM Transactions on Software Engineering and Methodology (TOSEM)":
    "本竞赛建立在 Build-Bench 研究基础之上，该研究已被 ACM Transactions on Software Engineering and Methodology（TOSEM）接收发表",
  ", which established the original cross-architecture repair task and executable evaluation workflow. The competition substantially expands this foundation by covering bidirectional migrations among x86_64, aarch64, and riscv64, incorporating packages from more diverse software ecosystems and sources, and providing more than 200 public development packages and over 1,000 hidden evaluation packages. It also introduces a standardized Agent interface and organizer-run executable validation to evaluate generalization at competition scale.":
    "。该研究建立了最初的跨架构修复任务和可执行评测流程。本竞赛在此基础上大幅扩展，覆盖 x86_64、aarch64 与 riscv64 之间的双向迁移，纳入来自更多软件生态和来源的软件包，提供 200 多个公开开发软件包和 1,000 多个隐藏评测软件包，并引入标准化 Agent 接口以及由组织方运行的可执行验证，以竞赛规模评测泛化能力。",
  "See reference 1": "查看参考文献 1",
  "Existing results show substantial room for improvement, motivating the development of more capable autonomous repair Agents.":
    "现有结果表明，该问题仍有很大的提升空间，因此需要开发能力更强的自主修复 Agent。",
  "Build-Bench Challenge evaluation workflow, from Case input and Agent execution to patch canonicalization, clean rebuilding, and scoring.":
    "Build-Bench Challenge 评测流程：从 Case 输入和 Agent 执行，到补丁规范化、干净环境重构建与计分。",
  "How the competition works": "如何参加竞赛",
  "Develop": "开发",
  "— Build and test your Agent with the Starter Kit and public development Cases.":
    "— 使用 Starter Kit 和公开开发 Case 构建并测试你的 Agent。",
  "Qualify": "资格验证",
  "— Submit an Agent version and pass the Hosted Smoke Test.":
    "— 提交一个 Agent 版本并通过 Hosted Smoke Test。",
  "Compete": "正式竞赛",
  "— Freeze a qualified version for organizer-run evaluation on hidden Cases and leaderboard ranking.":
    "— 冻结一个通过资格检查的版本，由组织方在隐藏 Case 上运行评测并生成排行榜名次。",
  "How is performance scored?": "如何计算性能得分？",
  "Using the workflow above, official ranking is based on verified executable outcomes, not similarity to a reference patch.":
    "按照上述流程，官方排名依据经过验证的可执行结果，而不是与参考补丁的相似度。",
  "The primary metric is": "主要指标是",
  "Verified Build Success Rate": "经验证的构建成功率",
  ": the percentage of evaluated Cases that pass all policy, clean-build, and artifact checks.":
    "：在所有受评测 Case 中，通过全部政策、干净构建和制品检查的 Case 比例。",
  "Execution Time": "执行时间",
  "and officially recorded": "以及官方记录的",
  "Token Usage": "Token 使用量",
  "are reported separately as secondary efficiency metrics.": "将分别作为次要效率指标报告。",
  "Read Evaluation and scoring": "阅读评测与计分规则",
  Timeline: "时间安排",
  "19 August 2026": "2026 年 8 月 19 日",
  "— Website beta and initial documentation": "— 网站 Beta 版与初始文档发布",
  "20–28 August 2026": "2026 年 8 月 20–28 日",
  "— Invited pilot": "— 邀请试点",
  "31 August 2026": "2026 年 8 月 31 日",
  "— Rules and resource limits frozen": "— 规则与资源限制冻结",
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
