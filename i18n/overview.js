window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.overview = Object.freeze({
  "Build-Bench Challenge | ICSE 2027": "Build-Bench Challenge | ICSE 2027",
  "The Build-Bench Challenge at ICSE 2027 evaluates agents for executable cross-architecture package build repair.":
    "ICSE 2027 Build-Bench Challenge 面向跨架构软件包构建修复，评测能够执行修复任务的 Agent。",
  "A competition for agent-driven repair of real package build failures across x86_64 and aarch64.":
    "面向 Agent 的真实软件包构建失败修复竞赛，覆盖 x86_64 与 aarch64 架构。",
  "ICSE 2027 Competition Track": "ICSE 2027 Competition Track",
  "Repair real cross-architecture software package build failures.": "修复真实的跨架构软件包构建失败。",
  "Software increasingly has to run across heterogeneous hardware, yet package portability failures often emerge only when a project is rebuilt for another instruction-set architecture. Diagnosing them requires reasoning across source code, package metadata, dependencies, build scripts, and logs.":
    "软件日益需要运行在异构硬件平台上，但软件包的可移植性问题往往只有在迁移到另一种指令集架构并重新构建时才会暴露。定位这类问题需要综合分析源码、包元数据、依赖、构建脚本和日志。",
  "Teams submit a runnable repair Agent. Organizers run each qualified Agent on competition Cases, generate a canonical repair patch from its work, and verify the repair by rebuilding the clean package in the target environment.":
    "参赛团队提交一个可运行的修复 Agent。组织者在竞赛 Case 上运行每个通过检查的 Agent，根据其工作区生成规范化修复补丁，并在干净的目标环境中重新构建软件包以验证修复。",
  "Get the Starter Kit": "获取 Starter Kit",
  "Explore Task & Dataset": "查看任务与数据集",
  "Primary actions": "主要操作",
  "What is the challenge?": "竞赛任务是什么？",
  "A Case represents a real software package that builds on a source instruction-set architecture but fails when rebuilt for a target architecture. The published Build-Bench benchmark contains 268 reproducible failures across x86_64 and aarch64 migration directions.":
    "每个 Case 都对应一个真实软件包：它能在源指令集架构上完成构建，但迁移到目标架构后构建失败。已发布的 Build-Bench Benchmark 包含 268 个可复现失败，覆盖 x86_64 与 aarch64 迁移方向。",
  "The Agent receives the package sources and packaging files, source and target architecture metadata, and the initial failed target-build log. It can inspect existing patches and auxiliary build files, then modify only the package paths permitted by the Case.":
    "Agent 会获得软件包源码与打包文件、源架构和目标架构元数据，以及目标构建的初始失败日志。它可以检查已有补丁和辅助构建文件，但只能修改 Case 允许的软件包路径。",
  "Repairs may involve dependency declarations, architecture-specific source code, unsupported compiler options, packaging rules, tests, or build scripts. The goal is to correct the portability failure without bypassing the required build or validation steps.":
    "修复可能涉及依赖声明、架构相关源码、不受支持的编译器选项、打包规则、测试或构建脚本。目标是在不绕过必要构建与验证步骤的前提下解决可移植性故障。",
  "Cross-architecture failure example": "跨架构构建失败示例",
  "Example.": "示例。",
  "A compiler option accepted by an x86_64 toolchain may be rejected during an aarch64 build. A valid repair might apply that option only where it is supported while preserving the package's normal build and tests.":
    "某个被 x86_64 工具链接受的编译选项，可能在 aarch64 构建中被拒绝。有效修复可以只在支持该选项的环境中启用它，同时保留软件包的正常构建与测试。",
  "How the competition works": "如何参加竞赛",
  "Read the challenge and rules.": "阅读任务和规则。",
  "Review the Case scope, allowed modifications, evaluation policy, and participation requirements.":
    "了解 Case 范围、允许修改的内容、评测政策和参赛要求。",
  "Develop and test the Agent locally.": "在本地开发并测试 Agent。",
  "Use the Starter Kit and example Cases to implement the repair strategy and check the submission package.":
    "使用 Starter Kit 和示例 Case 实现修复策略，并检查提交包。",
  "Run the Hosted Smoke Test.": "运行平台冒烟测试。",
  "Upload an Agent version and verify its package, entry point, runtime, and protocol on lightweight public Cases.":
    "上传一个 Agent 版本，并通过轻量公开 Case 检查打包结构、入口、运行环境和协议。",
  "Freeze a version for Full Evaluation.": "冻结用于完整评测的版本。",
  "Select a qualified, immutable Agent version for the organizer-run evaluation.":
    "选择一个已通过检查且不可变的 Agent 版本，由组织者运行评测。",
  "Check the official results and leaderboard.": "查看官方结果和排行榜。",
  "Review the completed evaluation and compare the verified score with other teams.":
    "查看已完成的评测，并将经过验证的成绩与其他队伍进行比较。",
  "How are repairs evaluated?": "修复如何评测？",
  "Organizers run the submitted Agent separately on each competition Case. The Agent works on a writable copy of the package, and the platform derives a canonical":
    "组织者会在每个竞赛 Case 上分别运行提交的 Agent。Agent 在软件包的可写副本上工作，平台根据最终工作区生成规范化",
  "from the final workspace.": "。",
  "The platform then applies that patch to a clean copy of the Case and rebuilds the package in the official target-architecture environment. The patch must comply with the allowed-path policy, the build must complete, and the expected package artifacts must pass validation.":
    "随后，平台把该补丁应用到干净的 Case 副本，并在官方目标架构环境中重新构建软件包。补丁必须符合允许路径政策，构建必须完成，且预期的软件包产物必须通过校验。",
  "Repairs are not compared with a reference patch. Different solutions are accepted when they satisfy the policy and produce a genuine successful build.":
    "评测不会把修复与参考补丁进行文本比较。只要不同方案符合政策并真正完成构建，就可以被接受。",
  "Read the Evaluation Protocol": "阅读评测协议",
  "for the full validation stages and result definitions.": "，了解完整验证阶段和结果定义。",
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
  "Task & Dataset": "任务与数据集",
  "Submission Guide": "提交指南",
  "Evaluation Protocol": "评测协议",
  "Rules": "规则",
  "Timeline": "时间安排",
  "FAQ": "常见问题",
  "Organized by Nankai University with industry collaboration from Microsoft.":
    "由南开大学组织，微软提供产业合作支持。",
  "Project links": "项目链接",
  "Paper": "论文",
  "Citation": "引用",
  "GitHub": "GitHub",
  "Contact": "联系",
  "Back to top": "返回顶部",
});
