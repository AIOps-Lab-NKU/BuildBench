window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.task = Object.freeze({
  "Challenge | Build-Bench": "竞赛任务 | Build-Bench",
  "Build a runnable Agent that diagnoses and repairs real cross-architecture package build failures under executable verification.":
    "构建可运行的 Agent，诊断并修复经过可执行验证的真实跨架构软件包构建失败。",
  "Build-Bench Challenge": "Build-Bench 竞赛",
  "Build autonomous LLM Agents that repair real package build failures across x86_64, Arm64, and RISC-V.":
    "构建自主 LLM Agent，修复 x86_64、Arm64 和 RISC-V 之间真实软件包的跨架构构建失败。",
  "Build-Bench Challenge evaluates whether runnable repair Agents can diagnose and fix real cross-architecture package build failures under controlled, executable evaluation.":
    "Build-Bench 竞赛评估可运行的修复 Agent 能否在受控的可执行评测环境中诊断并修复真实的跨架构软件包构建失败。",
  "On this page": "本页内容",
  "Motivation and task": "动机与任务",
  "Evaluation scope": "评测范围",
  "Case inputs": "Case 输入",
  "Agent behavior and constraints": "Agent 行为与约束",
  "Evaluation and scoring": "评测与计分",
  "Getting started": "开始上手",
  "Cloud, edge, and emerging computing platforms increasingly rely on heterogeneous instruction set architectures. However, architecture-specific code, dependencies, compiler behavior, build options, and packaging logic can cause software packages to fail when migrated to a new architecture. Diagnosing these failures often requires expertise across source code, toolchains, packaging systems, and hardware architectures, making large-scale migration costly and time-consuming. Such platform migration needs are common across organizations, and with the growing adoption of cost-effective AI workloads, more teams are considering cross-architecture migration to optimize their infrastructure.":
    "云、边缘和新兴计算平台越来越依赖异构指令集架构。然而，架构特定的代码、依赖、编译器行为、构建选项和打包逻辑可能导致软件包在迁移到新架构时构建失败。诊断这些失败通常需要跨源码、工具链、打包系统和硬件架构的专业知识，使得大规模迁移成本高昂且耗时。这类平台迁移需求在各组织中非常普遍，随着成本效益更高的 AI 工作负载的广泛采用，更多团队正在考虑跨架构迁移以优化基础设施。",
  "Build-Bench Challenge asks whether LLM-based repair Agents can automate this process reliably and generalize across packages, failure types, architectures, and migration directions. Each Case begins with a real software package that builds successfully on a source architecture but fails when rebuilt for a target architecture. The Agent must investigate the failure and modify the permitted package files so that the package can be rebuilt successfully for the target architecture.":
    "Build-Bench 竞赛探究基于 LLM 的修复 Agent 能否可靠地自动化这一过程，并在不同软件包、失败类型、架构和迁移方向上泛化。每个 Case 从一个真实软件包开始，该软件包在源架构上构建成功，但在为目标架构重新构建时失败。Agent 必须调查失败原因并修改允许范围内的软件包文件，使软件包能够成功为目标架构重建。",
  "Participants may design their Agent prompts, tools, and repair procedures freely. During each Case, the Agent must apply all intended changes directly to the permitted package worktree. It may edit individual files, rewrite complete files, create or delete files, or generate and apply patches internally.":
    "参赛者可以自由设计 Agent 的提示词、工具和修复流程。在每个 Case 中，Agent 必须将所有预期修改直接应用到允许的软件包工作树。它可以编辑单个文件、重写完整文件、创建或删除文件，或在内部生成并应用补丁。",
  "After the Agent exits, the organizers compare the final worktree with the original Case and automatically derive a canonical diff that captures all worktree changes. This diff is then replayed on a clean copy of the Case for verification in the official target-architecture environment.":
    "Agent 退出后，组织者比较最终工作树与原始 Case，自动生成捕获所有工作树更改的规范差异。该差异随后在干净的 Case 副本上重放，在官方目标架构环境中进行验证。",
  "Goal": "目标",
  "Input": "输入",
  "Agent output": "Agent 输出",
  "Verification": "验证",
  "Repair a package that builds on the source ISA but fails on the target ISA.":
    "修复在源 ISA 上构建成功但在目标 ISA 上构建失败的软件包。",
  "A prepared package workspace, source and target ISA metadata, failed-build evidence, and package build context.":
    "准备好的软件包工作区、源和目标 ISA 元数据、构建失败证据以及软件包构建上下文。",
  "The final state of files within the permitted worktree, together with the required structured completion result.":
    "允许工作树内文件的最终状态，以及所需的结构化完成结果。",
  "A canonical patch replayed on a clean Case and evaluated by the official target-architecture build.":
    "在干净的 Case 上重放并通过官方目标架构构建进行评估的规范补丁。",
  "The challenge is designed to measure whether an Agent generalizes across software packages, failure types, instruction set architectures, and migration directions. It therefore evaluates all bidirectional migration pairs among the three supported ISAs:":
    "竞赛旨在衡量 Agent 能否跨软件包、失败类型、指令集架构和迁移方向泛化。因此，它评估三个支持的 ISA 之间的所有双向迁移组合：",
  "x86_64 \u2194 aarch64 \u00a0\u00b7\u00a0 x86_64 \u2194 riscv64 \u00a0\u00b7\u00a0 aarch64 \u2194 riscv64":
    "x86_64 \u2194 aarch64 \u00a0\u00b7\u00a0 x86_64 \u2194 riscv64 \u00a0\u00b7\u00a0 aarch64 \u2194 riscv64",
  "Participants receive more than 200 public development packages for understanding the task and testing their systems. Final evaluation uses over 1,000 hidden packages drawn from broader software ecosystems and sources. Hidden evaluation is intended to discourage Case-specific rules and measure performance beyond packages seen during development.":
    "参赛者将获得超过 200 个公开开发软件包用于理解任务和测试系统。最终评测使用超过 1,000 个来自更广泛软件生态的隐藏软件包。隐藏评测旨在防止针对特定 Case 的规则，衡量在开发阶段未见过的软件包上的表现。",
  "At the beginning of each Case, the Agent receives the information needed to diagnose the initial target-architecture failure. Depending on the package, the workspace may contain source code, packaging specifications, metadata, build scripts, existing package-side patches, and other build-related files.":
    "在每个 Case 开始时，Agent 会收到诊断初始目标架构失败所需的信息。根据软件包情况，工作区可能包含源代码、打包规范、元数据、构建脚本、现有软件包补丁和其他构建相关文件。",
  "The standard Case input includes:": "标准 Case 输入包括：",
  "a prepared package workspace;": "准备好的软件包工作区；",
  "source and target architecture metadata;": "源和目标架构元数据；",
  "the initial failed target-build log; and": "初始目标架构构建失败日志；以及",
  "the packaging and build context included with that Case.": "该 Case 附带的打包和构建上下文。",
  "The exact directory layout and runtime interface are defined in the versioned":
    "确切的目录布局和运行时接口在版本化的",
  ".": "。",
  "The Agent may inspect the available package and build context, use relevant tools, analyze the failure, and modify files within the permitted package paths. It must complete the task autonomously during organizer-run evaluation.":
    "Agent 可以检查可用的软件包和构建上下文、使用相关工具、分析失败原因，并在允许的软件包路径内修改文件。在组织者运行的评测中，Agent 必须自主完成任务。",
  "All participating systems are evaluated under the same versioned execution contract. The":
    "所有参赛系统在相同的版本化执行合约下接受评估。",
  "defines the Agent package, workspace, entrypoint, permitted paths, and required outputs.":
    "定义了 Agent 软件包、工作区、入口点、允许路径和所需输出。",
  "Repair output contract": "修复输出合约",
  "The Agent must apply every intended repair directly to":
    "Agent 必须将所有预期修复直接应用到",
  ". Within the permitted paths, it may edit existing files, create new files, or delete files. An Agent that generates a patch internally must apply that patch to the worktree before it exits. A candidate patch written only to the output directory is not treated as the official repair.":
    "。在允许路径内，它可以编辑现有文件、创建新文件或删除文件。在内部生成补丁的 Agent 必须在退出前将该补丁应用到工作树。仅写入输出目录的候选补丁不被视为官方修复。",
  "After completing its repair attempt, the Agent must write":
    "完成修复尝试后，Agent 必须写入",
  ". The result reports completion status and diagnostics, but it does not define the repair itself. Any declared":
    "。结果报告完成状态和诊断信息，但不定义修复本身。任何声明的",
  "field is advisory; the evaluator independently determines the actual changes from the worktree.":
    "字段仅供参考；评估器独立从工作树确定实际更改。",
  "Canonical patch": "规范补丁",
  "After the Agent exits, the evaluator compares the original and final worktrees and derives":
    "Agent 退出后，评估器比较原始和最终工作树，并以 Git 扩展统一差异格式生成",
  "in Git extended unified-diff format. This format records text changes, new and deleted files, and supported file-mode changes using paths relative to the package root. Rename detection is disabled during canonicalization so that renames are represented deterministically as a deletion and an addition.":
    "。该格式记录文本更改、新增和删除的文件，以及使用相对于软件包根目录的路径的文件模式更改。在规范化过程中禁用重命名检测，因此重命名被确定性地表示为删除和添加。",
  "The public development environment is intended to match the official interface, but only results produced by the organizer-run evaluator count toward the leaderboard.":
    "公共开发环境旨在与官方接口保持一致，但只有组织者运行的评估器产生的结果才计入排行榜。",
  "During official evaluation, organizers execute each qualified Agent on hidden Cases under fixed runtime and resource constraints. After each run, the evaluator captures the Agent's final changes and derives a canonical patch. The patch is then applied to a fresh copy of the Case.":
    "在正式评测期间，组织者在固定的运行时和资源约束下对隐藏 Case 执行每个通过资格检查的 Agent。每次运行后，评估器捕获 Agent 的最终更改并生成规范补丁。该补丁随后被应用到新的 Case 副本。",
  "The patched package is rebuilt in the official target-architecture environment. A Case is counted as successfully repaired only when all of the following conditions hold:":
    "打补丁后的软件包在官方目标架构环境中重新构建。仅当以下所有条件成立时，Case 才被视为成功修复：",
  "the canonical patch is generated successfully and applies cleanly to the fresh Case;":
    "规范补丁生成成功并能干净地应用到新的 Case；",
  "the official target-architecture build completes successfully; and":
    "官方目标架构构建成功完成；并且",
  "the expected package artifacts are produced and verified.":
    "预期的软件包产物已生成并验证通过。",
  "Repairs are judged by these verified executable outcomes, not by similarity to a reference patch. If the evaluator cannot derive or cleanly apply the canonical patch, the Case is recorded as":
    "修复结果由这些经过验证的可执行结果判定，而不是通过与参考补丁的相似度。如果评估器无法生成或干净地应用规范补丁，该 Case 将被记录为",
  "and does not count as a successful repair.":
    "，不计入成功修复。",
  "Primary metric: Verified Build Success Rate": "主要指标：验证构建成功率",
  "The percentage of evaluated Cases whose canonical patches apply cleanly, complete the target-architecture build, and produce the expected package artifacts. Execution time and officially recorded token usage are reported separately as secondary efficiency metrics.":
    "规范补丁干净应用、完成目标架构构建并生成预期软件包产物的已评估 Case 的百分比。执行时间和官方记录的 token 使用量作为次要效率指标单独报告。",
  "Read the complete Evaluation and Scoring rules \u2192": "阅读完整的评测与计分规则 \u2192",
  "Use the Starter Kit and public development Cases to understand the workspace, test your Agent locally, and prepare a qualified submission. Before submitting, review the runtime interface, challenge rules, and evaluation protocol.":
    "使用 Starter Kit 和公开开发 Case 了解工作区、本地测试 Agent，并准备通过资格检查的正式提交。提交前，请查看运行时接口、竞赛规则和评测协议。",
  "Get the Starter Kit \u2192": "获取 Starter Kit \u2192",
  "Read the Submission Guide \u2192": "阅读 Submission Guide \u2192",
  "Read Evaluation and Scoring \u2192": "阅读评测与计分规则 \u2192",
});