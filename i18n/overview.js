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
  "Modern software increasingly needs to run across heterogeneous instruction set architectures (ISAs). A package that builds successfully on one architecture may fail after migration because of architecture-specific dependencies, compiler behavior, build configuration, or packaging logic.":
    "现代软件越来越需要在不同的指令集架构（ISA）上运行。一个软件包可能在某一种架构上能够正常构建，但迁移到另一种架构后，却会因为架构相关的依赖、编译器行为、构建配置或打包逻辑而构建失败。",
  "Build-Bench Challenge asks teams to build and submit a runnable LLM-based repair Agent, rather than Case-specific repair patches. The competition covers bidirectional migrations among x86_64, aarch64, and riscv64 and evaluates whether Agents can generalize across packages, failure types, architectures, and migration directions.":
    "Build-Bench Challenge 要求参赛团队构建并提交一个可运行、以大语言模型（LLM）为基础的修复 Agent，而不是针对每个 Case 单独提交修复补丁。竞赛覆盖 x86_64、aarch64 和 riscv64 三种架构之间的双向迁移，重点考察 Agent 能否适用于不同的软件包、故障类型、架构和迁移方向。",
  "For each Case, the Agent enters a prepared package workspace with source and target architecture metadata and initial target-build failure evidence. During the run, it may inspect the available package and build context, use tools permitted by the competition runtime, and iteratively modify only permitted package files.":
    "对于每个 Case，Agent 会进入一个预先准备好的软件包工作区，并获得源架构、目标架构等元数据，以及目标架构上的初始构建失败信息。运行过程中，Agent 可以查看所提供的软件包内容和构建上下文，使用比赛运行环境允许的工具，并通过多轮分析与修改，仅调整允许范围内的软件包文件。",
  "After the Agent finishes, organizers derive a canonical patch from the Agent's final worktree, apply it to a fresh copy of the Case, and rebuild the package in the official target-architecture environment. A Case is successfully repaired only when the canonical patch applies cleanly, the official build succeeds, and the expected package artifacts are produced and verified. Repairs are judged by verified executable outcomes, not by similarity to a reference patch. The overall workflow is illustrated below.":
    "Agent 运行结束后，组织方会根据其最终工作区中的实际文件状态，统一生成规范化修复补丁（canonical patch）。该补丁会被应用到一份全新的 Case 副本，并在官方目标架构环境中重新构建软件包。只有当补丁能够顺利应用、官方构建成功，并且预期的软件包制品得到生成和验证时，该 Case 才算修复成功。修复结果依据实际可执行的验证结果判定，而不是比较参赛方案与参考补丁是否相似。整体流程如下图所示。",
  "The workflow summarizes how each submitted Agent is executed, converted into a canonical repair, and independently verified through a clean target-architecture build.":
    "该流程展示了每个提交的 Agent 如何被运行、如何根据其最终修改生成规范化修复，以及如何通过一次干净的目标架构构建进行独立验证。",
  "Build-Bench Challenge builds on our prior study accepted for publication in ACM Transactions on Software Engineering and Methodology (TOSEM)":
    "Build-Bench Challenge 建立在我们已被 ACM Transactions on Software Engineering and Methodology（TOSEM）接收发表的前期研究基础上",
  ", which established the original cross-architecture package repair task and executable evaluation workflow. The competition extends this foundation to bidirectional migrations among x86_64, aarch64, and riscv64, with 200 public Development Cases and 1,000+ hidden evaluation Cases. It also introduces a standardized Agent interface and organizer-run evaluation for competition-scale assessment of Agent generalization.":
    "。该研究确立了最初的跨架构软件包修复任务和可执行评测流程。本次竞赛进一步扩展到 x86_64、aarch64 和 riscv64 三种架构之间的双向迁移，并提供 200 个公开开发 Case 和 1,000+ 个隐藏评测 Case。同时，竞赛引入统一的 Agent 接口和由组织方运行的正式评测流程，用于在竞赛规模下考察 Agent 的泛化能力。",
  "See reference 1": "查看参考文献 1",
  "Build your Agent": "构建你的 Agent",
  "How the competition works": "竞赛如何进行？",
  "Develop": "开发（Develop）",
  "— Build and test your Agent with the Starter Kit and public development Cases.":
    "— 使用 Starter Kit 和公开开发 Case 构建并测试你的 Agent。",
  "Qualify": "资格验证（Qualify）",
  "— Submit an Agent version and pass the Hosted Smoke Test.":
    "— 提交一个 Agent 版本，并通过 Hosted Smoke Test（托管冒烟测试）。",
  "Compete": "正式竞赛（Compete）",
  "— Freeze a qualified version for organizer-run evaluation on hidden Cases and leaderboard ranking.":
    "— 从通过资格验证的版本中选定并冻结一个版本，由组织方在隐藏 Case 上运行正式评测，并根据评测结果生成排行榜。",
  "How is performance scored?": "如何计算比赛成绩？",
  "Qualified Agents are evaluated on the official hidden Case set under the same runtime and resource constraints.":
    "通过资格验证的 Agent 将在相同的运行环境和资源限制下，使用官方隐藏 Case 集进行评测。",
  "The primary ranking metric is": "比赛的主要排名指标是",
  "Verified Build Success Rate": "经验证的构建成功率（Verified Build Success Rate）",
  "— the percentage of evaluated Cases for which the canonical repair applies cleanly, the official target-architecture build succeeds, and the expected package artifacts are produced and verified.":
    "——即在全部评测 Case 中，规范化修复能够顺利应用、官方目标架构构建成功，并且预期软件包制品得到生成和验证的 Case 比例。",
  "Execution Time": "执行时间（Execution Time）",
  "and officially recorded": "和由比赛平台正式记录的",
  "Token Usage": "Token 使用量（Token Usage）",
  "are reported separately as secondary efficiency metrics.": "将分别作为次要效率指标进行报告。",
  "Read the Full Competition Rules": "阅读完整竞赛规则",
  "Awards & Recognition": "奖项与荣誉",
  "Winning teams will receive competition certificates and additional recognition associated with the ICSE 2027 Competition Track.":
    "获奖团队将获得竞赛证书，以及与 ICSE 2027 Competition Track 相关的其他荣誉认可。",
  Timeline: "时间安排",
  "19 August 2026": "2026 年 8 月 19 日",
  "— Website beta and initial documentation": "— 网站 Beta 版与初始文档发布",
  "20–28 August 2026": "2026 年 8 月 20–28 日",
  "— Invited pilot": "— 邀请试点",
  "31 August 2026": "2026 年 8 月 31 日",
  "— Rules and resource limits frozen; registration opens": "— 规则与资源限制冻结；开放注册",
  "7 September 2026": "2026 年 9 月 7 日",
  "— Public development and validation open": "— 公开开发与验证阶段开放",
  "13 November 2026": "2026 年 11 月 13 日",
  "— Final Agent versions freeze": "— 最终 Agent 版本冻结",
  "By 20 November 2026": "不晚于 2026 年 11 月 20 日",
  "— Final results published": "— 公布最终结果",
  "Build-Bench competition milestones": "Build-Bench 竞赛里程碑",
  "Participant release": "参赛资源发布",
  "Pre-launch test": "公开前测试",
  "Protocol freeze": "协议冻结",
  "Public phase": "公开阶段",
  "Final selection": "最终版本选择",
  "Official publication": "正式发布",
  "Release": "发布",
  "Pilot": "试点",
  "Policy freeze": "政策冻结",
  "Opening": "开放",
  "Deadline": "截止日期",
  "Results": "结果",
  "Website beta and initial documentation": "网站 Beta 版与初始文档发布",
  "Invited pilot": "邀请试点",
  "Rules and resource limits frozen; registration opens": "规则与资源限制冻结；开放注册",
  "Public development and validation open": "公开开发与验证阶段开放",
  "Final Agent version freeze": "最终 Agent 版本冻结",
  "Final results published": "公布最终结果",
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
