window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.task = Object.freeze({
  "Task & Dataset | Build-Bench Challenge": "任务与数据集 | Build-Bench Challenge",
  "Build-Bench Challenge task definition, case format, dataset, and planned competition splits.":
    "Build-Bench Challenge 的任务定义、Case 格式、数据发布和拟定竞赛划分。",
  "Dataset splits and the final case schema will be frozen before launch.":
    "数据划分和最终 Case 结构将在竞赛启动前冻结。",
  "Challenge specification": "竞赛任务说明",
  "Task & Dataset": "任务与数据集",
  "Each case asks an Agent to repair a package that fails on the target architecture and to make the official build validator succeed.":
    "每个 Case 要求 Agent 修复一个在目标架构上构建失败的软件包，并让官方构建验证器通过。",
  "Case unit": "Case 单元",
  "One package build failure": "一个软件包构建失败",
  "Input": "输入",
  "Source, metadata, and logs": "源码、元数据和日志",
  "Success oracle": "成功判据",
  "Executable build": "实际构建",
  "On this page": "本页内容",
  "Objective": "任务目标",
  "Case anatomy": "Case 构成",
  "Repair workflow": "修复流程",
  "Dataset release": "数据发布",
  "Competition splits": "竞赛数据划分",
  "Provenance": "数据来源",
  "Source basis": "内容依据",
  "Build-Bench paper and accepted ICSE competition proposal": "Build-Bench 论文和已接收的 ICSE 竞赛提案",
  "Repair portability failures at system scale": "面向系统规模修复移植失败",
  "Each task starts from a package that builds on a source architecture but fails when rebuilt on a target architecture. The Agent must inspect the supplied evidence and produce a focused repair.":
    "每项任务都从一个能在源架构上构建、但在目标架构上重新构建时失败的软件包开始。Agent 必须检查提供的证据，并给出针对性的修复。",
  "Given": "输入",
  "A reproducible failed package case": "一个可复现的失败软件包 Case",
  "Produce": "输出",
  "A valid repair artifact": "有效的修复制品",
  "Pass": "通过",
  "The official target build": "官方目标架构构建",
  "The evaluator does not require a repair to match an organizer-authored reference patch. A repair succeeds only when it applies cleanly, respects the modification policy, and completes the configured build validator.":
    "评测器不要求修复与主办方编写的参考补丁一致。只有当修复能够顺利应用、符合修改规则，并通过指定的构建验证器时，才算成功。",
  "What an Agent receives": "Agent 获得的内容",
  "Released cases will use a stable directory layout. The exact manifest schema and immutable paths will be versioned with the starter kit.":
    "发布的 Case 将使用稳定的目录结构。准确的 manifest 结构和不可修改路径会随 Starter Kit 一同进行版本管理。",
  "Package specifications": "软件包规范文件",
  "files or equivalent package metadata": "文件或等价的软件包元数据",
  "Package artifacts": "软件包制品",
  "Source archives, existing patches, service files, and auxiliary build-service files":
    "源码归档、已有补丁、服务文件及构建服务辅助文件",
  "Failure evidence": "失败证据",
  "The original failed build log from the target architecture": "目标架构上的原始失败构建日志",
  "Architecture labels": "架构信息",
  "Source architecture, target architecture, and validator backend metadata": "源架构、目标架构及验证器后端元数据",
  "Integrity metadata": "完整性元数据",
  "Case identifier, checksums, constraints, and paths that must remain immutable":
    "Case 标识、校验和、约束条件及必须保持不变的路径",
  "Inspect, diagnose, repair, verify": "检查、诊断、修复、验证",
  "The research workflow is being adapted into an organizer-run competition harness.":
    "研究工作流正在改造成由主办方运行的竞赛评测框架。",
  "Inspect the package context": "检查软件包上下文",
  "Read manifests, specifications, source files, build scripts, existing patches, and the failed log.":
    "阅读 manifest、规范文件、源文件、构建脚本、已有补丁和失败日志。",
  "Diagnose the cross-architecture fault": "诊断跨架构故障",
  "Identify architecture assumptions, unavailable dependencies, compiler differences, packaging errors, or target-sensitive tests.":
    "识别架构假设、不可用依赖、编译器差异、打包错误或对目标架构敏感的测试。",
  "Generate a repair": "生成修复",
  "Modify only permitted package files and emit the required repair artifact through the Agent interface.":
    "只修改允许变更的软件包文件，并通过 Agent 接口输出规定格式的修复制品。",
  "Validate by building": "通过构建进行验证",
  "The official evaluator applies the repair to a clean copy and rebuilds on the target architecture.":
    "官方评测器将修复应用到干净副本，并在目标架构上重新构建。",
  "Competition cases are frozen by release version": "竞赛 Case 以发布版本为准",
  "The research corpus informs the competition, but the official case set is defined only by a versioned release manifest.":
    "研究数据集为竞赛提供来源依据，但正式 Case 集只由版本化发布清单定义。",
  "The final release will publish case identifiers, checksums, split membership, allowed paths, validator version, and reconstruction instructions where redistribution is constrained.":
    "最终发布会包含 Case 标识、校验和、数据划分、允许修改路径、验证器版本，以及在再分发受限时使用的重建说明。",
  "Release status:": "发布状态：",
  "candidate packages are accepted only after both the original failure and the repaired success can be reproduced under a frozen environment.":
    "候选软件包只有在冻结环境中同时复现原始失败和修复后成功构建后，才会被接收为正式 Case。",
  "Failure categories": "失败类别",
  "Cases cover build failures where architecture portability affects compilation, preparation, testing, packaging, or the build environment.":
    "Case 覆盖架构移植性影响编译、准备、测试、打包或构建环境的失败。",
  "Compilation error": "编译错误",
  "Source or compiler behavior differs on the target architecture.": "源码或编译器行为在目标架构上出现差异。",
  "Build preparation error": "构建准备错误",
  "Configuration, dependency discovery, or generated build files fail before compilation.":
    "配置、依赖发现或生成的构建文件在编译前失败。",
  "Test failure": "测试失败",
  "Architecture-sensitive tests block package completion.": "架构敏感测试阻止软件包完成构建。",
  "Packaging error": "打包错误",
  "Spec files, macros, installed paths, or package manifests need repair.":
    "spec 文件、宏、安装路径或软件包 manifest 需要修复。",
  "Environment and infrastructure": "环境与基础设施",
  "Build-service assumptions or platform dependencies must be handled carefully.":
    "需要谨慎处理构建服务假设或平台依赖。",
  "Planned competition splits": "拟定竞赛划分",
  "Development, validation, and hidden test": "开发集、验证集与隐藏测试集",
  "Split": "数据集",
  "Visibility": "可见性",
  "Purpose": "用途",
  "Development": "开发集",
  "Local debugging, tutorials, and method development": "用于本地调试、教程和方法开发",
  "Validation": "验证集",
  "Public inputs and scores": "输入和分数公开",
  "Leaderboard feedback during the public phase": "在公开阶段提供排行榜反馈",
  "Test": "测试集",
  "Held out": "不公开",
  "Organizer-run final ranking": "由主办方运行并生成最终排名",
  "Cases will be grouped by package so that near-duplicate packages do not appear across splits. Final counts and package assignments are not yet published.":
    "Case 将按软件包分组，避免高度相似的软件包被分到不同数据集中。最终规模和软件包分配尚未公布。",
  "Provenance and licensing": "数据来源与许可",
  "Release only what can be shared responsibly": "只发布能够合规共享的内容",
  "The paper corpus originates from public openSUSE build scenarios. Dataset expansion is also investigating other distributions, package ecosystems, and ISA directions that can be reproduced in a containerized build environment.":
    "论文数据集来自公开的 openSUSE 构建场景。数据扩充也在调研能够在容器化构建环境中复现的其他发行版、软件包生态和 ISA 方向。",
  "Before release, organizers will audit license metadata, remove local credentials and personal paths, document redistribution constraints, and group semantic duplicates.":
    "发布前，主办方将审核许可证元数据，移除本地凭据和个人路径，记录再分发限制，并按语义对重复项分组。",
  "When redistribution is unclear, the starter kit may provide reconstruction scripts that retrieve artifacts from public package sources instead of distributing original archives.":
    "如果再分发条件不明确，Starter Kit 可能提供重建脚本，从公开软件包源获取制品，而不直接分发原始归档。",
  "Hugging Face dataset:": "Hugging Face 数据集：",
  "the public repository link will be added after the first dataset version passes validation, licensing, and deduplication review.":
    "首个数据集版本通过验证、许可证和去重审核后，再添加公开仓库链接。",
  "Next": "下一页",
  "Agent Submission": "Agent 提交",
  "Understand the single submission model": "了解统一提交模式",
  "Build-Bench workflow from failed package context through agent repair to Open Build Service validation":
    "Build-Bench 工作流：从失败软件包上下文，经 Agent 修复，到 Open Build Service 验证",
  "Build-Bench failure categories": "Build-Bench 失败类别",
  "Scrollable competition split table": "可横向滚动的竞赛划分表",
});
