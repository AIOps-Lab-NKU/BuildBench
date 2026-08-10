window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.task = Object.freeze({
  "Challenge | Build-Bench": "竞赛任务 | Build-Bench",
  "Build a runnable Agent that diagnoses and repairs real cross-architecture package build failures under executable verification.":
    "构建可运行的 Agent，诊断并修复经过可执行验证的真实跨架构软件包构建失败。",
  "Agent competition": "Agent 竞赛任务",
  Challenge: "竞赛任务",
  "Build an Agent that repairs real cross-architecture build failures":
    "构建能够修复真实跨架构构建失败的 Agent",
  "Build-Bench challenges teams to develop a runnable software-repair Agent for real packages that build successfully on one instruction-set architecture but fail when rebuilt on another.":
    "Build-Bench 要求参赛团队开发一个可运行的软件修复 Agent，用于处理真实软件包在一个指令集架构上能够成功构建、迁移到另一架构后却发生构建失败的问题。",
  "For each Case, the Agent investigates a failed build inside a prepared package workspace, modifies the permitted package files, and produces a repair that can be independently verified by the competition platform.":
    "对于每个 Case，Agent 将进入准备好的软件包工作区，分析目标架构上的构建失败，修改允许范围内的软件包文件，并产生能够由竞赛平台独立验证的修复结果。",
  "You submit a runnable Agent — not precomputed Case-by-Case patches.":
    "参赛者提交的是可运行的 Agent，而不是针对每个 Case 预先生成的补丁。",
  "On this page": "本页内容",
  "Why this challenge?": "为什么设置这个 Challenge？",
  "Your mission": "你的任务",
  "What your Agent works with": "Agent 会获得什么？",
  "What your Agent can do": "Agent 可以做什么？",
  "The repair lifecycle": "修复过程",
  "What counts as solved?": "怎样才算解决一个 Case？",
  "Start building": "开始构建你的 Agent",
  "Modern software increasingly needs to run across heterogeneous architectures, toolchains, dependencies, and packaging environments. A package that works on one architecture may fail on another because of architecture-specific code, build configuration, dependencies, compiler behavior, or packaging rules.":
    "现代软件需要运行在越来越多样的硬件架构、工具链、依赖和软件包环境中。同一个软件包可能因为架构相关代码、构建配置、依赖、编译器行为或打包规则，在一种架构上正常构建，却在另一种架构上失败。",
  "Can an autonomous Agent diagnose a real build failure and repair the package end to end?":
    "自主 Agent 能否诊断真实构建失败，并端到端地完成软件包修复？",
  "The challenge focuses on repairs that work in a real build environment, rather than changes that merely look similar to a reference solution.":
    "Challenge 关注修复结果能否在真实构建环境中成立，而不是修复文本是否与某个参考答案相似。",
  "Each Case starts from a real software package that builds successfully on a source architecture but fails on a target architecture.":
    "每个 Case 都来自一个真实软件包：它能够在源架构上成功构建，但在目标架构上构建失败。",
  "Your Agent receives a prepared package workspace and the initial failure context. It must investigate the cause of the failure and modify the permitted package files so that the package can be rebuilt successfully for the target architecture.":
    "Agent 会获得准备好的软件包工作区和初始失败上下文，需要自主定位失败原因，并修改允许范围内的软件包文件，使软件包最终能够在目标架构上重新成功构建。",
  "During official evaluation, the Agent must complete this task autonomously under the competition runtime and rules.":
    "正式评测期间，Agent 必须在竞赛规定的运行环境和规则下自主完成这一过程。",
  "At the beginning of a Case, the Agent is given the package workspace, source and target architecture information, the initial failed-build evidence, and the packaging and build context included with that Case.":
    "在每个 Case 开始时，Agent 会获得软件包工作区、源架构与目标架构信息、初始构建失败证据，以及 Case 中包含的打包和构建上下文。",
  "The workspace may contain source code, packaging files, build scripts, existing package-side patches, metadata, and other files relevant to diagnosing the failure.":
    "工作区可能包括源码、软件包配置文件、构建脚本、已有的软件包补丁、元数据以及其他与故障诊断相关的文件。",
  "See the detailed, versioned runtime specification": "查看详细的版本化运行时规范",
  "The Agent may inspect the available package and build context, reason about the failure, and modify files within the permitted package paths using the tools available in the official runtime.":
    "Agent 可以检查软件包和构建上下文、分析失败原因，并使用官方运行环境提供的工具，在允许的路径范围内修改文件。",
  "Runtime limits, network policy, resource limits, allowed modification scope, and other execution constraints are defined separately in the competition documentation.":
    "具体的运行时限制、网络策略、资源限制、可修改范围和其他执行约束在竞赛文档中另行说明。",
  "Read the Submission Guide": "查看 Submission Guide",
  "Read the Rules": "查看 Rules",
  "Repair lifecycle": "修复过程",
  "Case workspace": "Case 工作区",
  "Agent diagnosis & repair": "Agent 诊断与修复",
  "Final workspace": "最终工作区",
  "Clean target rebuild": "干净环境中的目标架构重新构建",
  "The organizer runs each qualified Agent in a controlled Case workspace. After the run, the platform captures the Agent's final changes and derives the repair used for verification.":
    "组织方会在受控的 Case 工作区中运行通过资格检查的 Agent。运行结束后，平台获取 Agent 的最终修改，并生成用于正式验证的修复结果。",
  "The repair is then applied to a clean copy of the Case and evaluated in the official target-architecture build environment.":
    "随后，该修复会被重新应用到一个干净的 Case 副本，并在官方目标架构构建环境中执行验证。",
  "A Case is solved only when the Agent's final changes can be applied to a clean Case and the package builds successfully in the official target-architecture environment.":
    "只有当 Agent 的最终修改能够重新应用到干净 Case，并使软件包在官方目标架构环境中成功完成构建时，该 Case 才被视为修复成功。",
  "Repairs are judged by verified build results, not by similarity to a reference patch.":
    "修复结果由真实构建结果判定，而不是通过与参考补丁进行文本相似度比较。",
  "Read the Evaluation Protocol": "查看 Evaluation Protocol",
  "Ready to build your Agent?": "准备开始了吗？",
  "Use the Starter Kit and example Cases to understand the workspace, test your Agent locally, and prepare a qualified submission.":
    "使用 Starter Kit 和 Example Cases 熟悉工作区、本地测试 Agent，并准备通过资格检查的正式提交。",
  "Start building links": "开始构建链接",
  "Get the Starter Kit": "获取 Starter Kit",
});
