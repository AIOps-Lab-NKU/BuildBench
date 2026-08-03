window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.task = Object.freeze({
  "Task & Dataset | Build-Bench Challenge": "任务与数据集 | Build-Bench Challenge",
  "Build-Bench Challenge task definition, case format, dataset, and planned competition splits.":
    "Build-Bench Challenge 的任务定义、Case 内容、数据集及竞赛数据划分。",
  "Dataset splits and the final case schema will be frozen before launch.":
    "数据集划分和最终 Case 结构将在竞赛启动前冻结。",
  "Challenge specification": "竞赛任务说明",
  "Task & Dataset": "任务与数据集",
  "Build-Bench evaluates whether an Agent can repair a software package that builds successfully on one architecture but fails on another. The platform converts the Agent's final changes into a canonical patch and validates the repair in the official target-architecture build environment.":
    "Build-Bench 评测 Agent 能否修复一个在某种架构上构建成功、但在另一种架构上构建失败的软件包。平台将 Agent 的最终修改转换为规范补丁，并在官方目标架构构建环境中验证修复。",
  "Task flow": "任务流程",
  "Cross-architecture failure": "跨架构构建失败",
  "Agent diagnosis and repair": "Agent 诊断与修复",
  "Clean target build": "干净环境中的目标架构构建",
  "On this page": "本页内容",
  "In this article": "本文内容",
  "Task definition": "任务定义",
  "Case contents": "Case 内容",
  "Repair and evaluation": "修复与评测",
  "Dataset": "数据集",
  "Splits and data integrity": "数据划分与完整性",
  "Each Case begins with a software package that builds on a source instruction set architecture but fails when rebuilt on a target architecture. The Agent receives the package materials, architecture metadata, and initial failure evidence needed to diagnose that portability failure.":
    "每个 Case 都从一个能在源指令集架构上构建、但在目标架构上重新构建时失败的软件包开始。Agent 会获得诊断该移植失败所需的软件包材料、架构元数据和初始失败证据。",
  "The Agent may modify only the permitted package files. When the run ends, the platform derives a canonical":
    "Agent 只能修改允许变更的软件包文件。运行结束后，平台会生成规范的",
  "from the final workspace. The repair does not need to match an organizer-authored patch; it succeeds only when it passes the modification policy and completes the official target build on a clean Case.":
    "。修复不需要与主办方编写的补丁一致；只有通过修改规则检查，并在干净 Case 上完成官方目标架构构建时，才算成功。",
  "The downloadable Case schema is still being finalized. At the protocol level, every Case provides the following information:":
    "可下载 Case 的结构仍在最终确定中。在协议层面，每个 Case 都会提供以下信息：",
  "Package sources and packaging metadata.": "软件包源码与打包元数据。",
  "Source archives, package specifications, existing patches, and auxiliary build files required by the task.":
    "任务所需的源码归档、软件包规范、已有补丁和辅助构建文件。",
  "Architecture information.": "架构信息。",
  "The source architecture, target architecture, and build constraints used for validation.":
    "用于验证的源架构、目标架构和构建约束。",
  "Initial failure evidence.": "初始失败证据。",
  "The failed target-architecture build log and related task metadata.":
    "目标架构上的失败构建日志及相关任务元数据。",
  "Build configuration.": "构建配置。",
  "The configuration and dependency constraints required to reproduce the build environment.":
    "复现构建环境所需的配置和依赖约束。",
  "Integrity and modification policy.": "完整性与修改规则。",
  "Case identifiers, checksums, immutable inputs, and the paths the Agent may change.":
    "Case 标识、校验和、不可变输入以及 Agent 可以修改的路径。",
  "A downloaded Case bundle, the Agent's runtime": "下载的 Case 包、Agent 运行时的",
  ", and the Validator's internal dependency storage are separate interfaces. The final Case schema will be versioned with the Starter Kit; see the":
    "和 Validator 的内部依赖存储属于不同接口。最终 Case 结构将随 Starter Kit 进行版本管理；请参阅",
  "runtime interface": "运行时接口",
  "for the directories visible to an Agent.": "了解 Agent 可见的目录。",
  "The platform prepares an isolated Case workspace.": "平台准备隔离的 Case 工作区。",
  "Immutable inputs and a writable package worktree are created for one Case run.":
    "平台为一次 Case 运行创建不可变输入和可写的软件包工作树。",
  "The Agent inspects the inputs and modifies the writable repository.":
    "Agent 检查输入并修改可写仓库。",
  "It can analyze the failure evidence, edit permitted files, and request build feedback within the published limits.":
    "Agent 可以分析失败证据、编辑允许修改的文件，并在公布的限制内请求构建反馈。",
  "The platform generates the canonical patch.": "平台生成规范补丁。",
  "The final workspace is compared with the clean Case to produce the official":
    "平台将最终工作区与干净 Case 进行比较，生成官方",
  "The official Validator performs the target build.": "官方 Validator 执行目标架构构建。",
  "The patch is applied to a clean Case and verified in the target-architecture build environment.":
    "补丁会应用到干净 Case，并在目标架构构建环境中完成验证。",
  "See the": "请参阅",
  "Evaluation Protocol": "评测协议",
  "for build feedback, status transitions, scoring, logs, and infrastructure-error handling.":
    "了解构建反馈、状态转换、评分、日志和基础设施错误处理。",
  "The published Build-Bench benchmark contains 268 reproducible failures collected from real open-source package builds. It covers system configuration issues, missing dependencies, architecture-specific source problems, and build-script incompatibilities.":
    "已发布的 Build-Bench benchmark 包含 268 个从真实开源软件包构建中收集的可复现失败，覆盖系统配置问题、依赖缺失、架构特定源码问题和构建脚本不兼容。",
  "Published benchmark by migration direction": "按迁移方向划分的已发布 benchmark",
  "Published benchmark": "已发布 benchmark",
  "Migration direction": "迁移方向",
  "Cases": "Case 数量",
  "Total": "总计",
  "The competition dataset is being prepared from a larger, independently audited candidate pool. Candidate counts describe preparation progress, not the final number of accepted evaluation Cases.":
    "竞赛数据集正在从一个规模更大、独立审核的候选池中准备。候选数量反映的是准备进度，并不等于最终通过验收的评测 Case 数量。",
  "Competition candidate pool status": "竞赛候选池状态",
  "Competition candidate pool": "竞赛候选池",
  "Dataset status": "数据状态",
  "Publication state": "发布状态",
  "Public": "公开",
  "Structurally complete candidates": "结构完整的候选 Case",
  "Under audit": "审核中",
  "Build or validation attempted": "已发起构建或验证尝试",
  "Deduplicated candidates": "已去重候选",
  "Target hidden-set size": "隐藏测试集目标规模",
  "Not yet frozen": "尚未冻结",
  "Based on the current pool and audit progress, the organizers aim to retain approximately 1,000 Cases for the final hidden evaluation. The exact number remains subject to integrity, licensing, deduplication, and reproducibility checks.":
    "根据当前候选池和审核进度，主办方计划为最终隐藏评测保留约 1,000 个 Case。准确数量仍取决于完整性、许可证、去重和可复现性检查。",
  "Competition dataset splits": "竞赛数据划分",
  "Competition splits": "竞赛数据划分",
  "Split": "数据集",
  "Participant access": "参赛者访问方式",
  "Purpose": "用途",
  "Development": "开发集",
  "Downloadable public Cases": "可下载的公开 Case",
  "Local development and testing": "本地开发与测试",
  "Validation": "验证集",
  "Hosted evaluation with controlled feedback": "提供受控反馈的托管评测",
  "Public competition phase": "公开竞赛阶段",
  "Hidden test": "隐藏测试集",
  "Organizer-only": "仅主办方可见",
  "Final ranking": "最终排名",
  "Cases will be grouped by package family and checked for semantic similarity so that near-duplicate packages do not leak across splits. The hidden set will be frozen from the competition-specific candidate pool rather than mixed with the published benchmark.":
    "Case 将按软件包家族分组并检查语义相似性，避免近似重复的软件包跨数据集泄漏。隐藏测试集将从竞赛专用候选池中冻结，不会与已发布 benchmark 混用。",
  "Before a Case is accepted, organizers review its provenance, license and redistribution conditions, reproducibility, and integrity metadata. When direct redistribution is not permitted, the release may provide reconstruction instructions instead of the original artifact.":
    "在接收 Case 前，主办方会审核其来源、许可证与再分发条件、可复现性和完整性元数据。若不允许直接再分发，发布内容可能提供重建说明，而不提供原始制品。",
  "Data status": "数据状态",
  "Final split sizes, per-Case timeouts, submission limits, and the validation protocol will be frozen and published before the public competition phase.":
    "最终数据集规模、单 Case 超时、提交限制和验证协议将在公开竞赛阶段前冻结并发布。",
  "Next steps": "后续步骤",
  "Data & Downloads": "数据与下载",
  "Get the Starter Kit and released competition resources.": "获取 Starter Kit 和已发布的竞赛资源。",
  "Agent Submission Guide": "Agent 提交指南",
  "Prepare, test, and package a runnable Agent.": "准备、测试并打包可运行的 Agent。",
  "Review build feedback, status handling, and scoring.": "查看构建反馈、状态处理和评分规则。",
});
