window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.evaluation = Object.freeze({
  "Evaluation Protocol | Build-Bench Challenge": "评测协议 | Build-Bench Challenge",
  "Participant-facing evaluation protocol, Case outcomes, scoring, and evaluation stages for the Build-Bench Challenge.":
    "Build-Bench Challenge 面向参赛者的评测协议、Case 结果处理、计分方式和评测阶段说明。",
  "Participant protocol": "参赛者评测协议",
  "Evaluation Protocol": "评测协议",
  "This page explains what happens after you select a qualified, immutable Agent version for evaluation: how the platform runs it, validates each repair, records outcomes, and produces a score. For packaging and upload instructions, see the":
    "本页说明选定通过检查且不可变的 Agent 版本后，平台如何运行 Agent、验证每项修复、记录结果并计算分数。有关打包和上传说明，请参阅",
  "Submission Guide": "Agent 提交指南",
  "On this page": "本页内容",
  "Successful repair": "成功修复",
  "Per-Case evaluation": "逐 Case 评测",
  "Outcome handling": "结果处理",
  "Scoring and diagnostics": "计分与诊断",
  "Evaluation stages": "评测阶段",
  "To be announced": "待公布内容",
  "Core principle": "核心原则",
  "What counts as a successful repair?": "什么算成功修复？",
  "A repair succeeds only when the platform can generate a valid canonical patch, apply it to a clean copy of the Case, and build the expected package artifacts on the target architecture under the official Validator.":
    "只有当平台能够生成有效的规范补丁，将其应用到 Case 的干净副本，并在官方 Validator 中于目标架构上构建出预期软件包产物时，该修复才算成功。",
  "The repair does not need to match an organizer reference patch. A different change receives credit when it respects the published policy and produces a genuine successful build.":
    "修复不需要与组织者的参考补丁一致。只要修改符合已公布规则并实现真实、成功的构建，即可获得成功判定。",
  "Primary metric: Build Success Rate": "主要指标：构建成功率",
  "successful Cases ÷ evaluated Cases": "成功 Case 数 ÷ 参与评测的 Case 数",
  "Per-Case protocol": "逐 Case 协议",
  "How each Case is evaluated": "每个 Case 如何评测",
  "Each Case is an independent run. One slow or unsuccessful Case does not stop other scheduled Cases, and the selected Agent archive remains immutable throughout the evaluation.":
    "每个 Case 都是独立运行任务。某个 Case 运行缓慢或修复失败不会阻止其他已调度 Case，且选定的 Agent 压缩包在整个评测期间保持不可变。",
  "Freeze the run inputs.": "冻结本次运行输入。",
  "The platform records the Agent archive and its checksum together with the Case-set, runtime, Validator, and protocol versions.":
    "平台记录 Agent 压缩包及其校验和，同时记录 Case 集、运行时、Validator 和协议版本。",
  "Prepare a clean Case.": "准备干净 Case。",
  "The Case checksum is verified and an isolated writable worktree is created from the original package materials.":
    "平台验证 Case 校验和，并根据原始软件包材料创建隔离的可写工作树。",
  "Run the Agent.": "运行 Agent。",
  "The declared entrypoint receives the standard workspace and runs under the published time, resource, network, and build-feedback policy.":
    "声明的入口命令接收标准工作区，并在已公布的时间、资源、网络和构建反馈策略下运行。",
  "Generate the canonical patch.": "生成规范补丁。",
  "After the Agent exits, the platform validates": "Agent 退出后，平台验证",
  "and derives": "并根据原始工作树和修改后工作树生成",
  "from the original and modified worktrees.": "。",
  "Audit the repair.": "审核修复。",
  "The canonical patch is checked for forbidden paths, policy violations, and build-bypass behavior described in the":
    "平台检查规范补丁是否包含禁止路径、违反策略或",
  "Rules": "规则页面",
  "Rebuild from clean inputs.": "从干净输入重新构建。",
  "The platform reapplies the canonical patch to a fresh Case and invokes the official Docker Validator for the target architecture.":
    "平台将规范补丁重新应用到全新的 Case，并为目标架构调用官方 Docker Validator。",
  "Record the outcome.": "记录结果。",
  "Agent status, Validator status, duration, patch statistics, and permitted logs are stored as structured evidence.":
    "Agent 状态、Validator 状态、耗时、补丁统计和允许展示的日志均以结构化证据保存。",
  "Case results": "Case 结果",
  "How outcomes are handled": "如何处理各类结果",
  "The platform records Agent execution and final build validation separately. An evaluation can complete normally even when many Cases are unsuccessful; an evaluation-level":
    "平台分别记录 Agent 执行结果和最终构建验证结果。即使多个 Case 未成功，整次评测仍可正常完成；评测级别的",
  "System Error": "系统错误",
  "is reserved for organizer-controlled failures.": "仅用于组织者可控基础设施发生故障的情况。",
  "Scrollable Case outcome table": "可横向滚动的 Case 结果表",
  "Outcome": "结果",
  "What it means": "含义",
  "Evaluation treatment": "评测处理",
  "The audited patch produces the expected package artifacts in the clean target build.":
    "通过审核的补丁在干净的目标构建中生成预期软件包产物。",
  "Successful Case.": "记为成功 Case。",
  "The target build fails, dependencies cannot be resolved, or the Agent proposes no allowed change.":
    "目标构建失败、依赖无法解析，或 Agent 未提出允许的修改。",
  "Unsuccessful Case result.": "记为未成功 Case。",
  "The Agent crashes, exits abnormally, or omits a valid": "Agent 崩溃、异常退出，或未提供有效的",
  "The Agent or its permitted build work exceeds the applicable Case-level limit.":
    "Agent 或其允许执行的构建工作超过适用的 Case 级限制。",
  "The canonical repair cannot be applied or violates path, output, or repair policy.":
    "规范修复无法应用，或违反路径、输出或修复策略。",
  "An organizer-controlled Worker, storage service, runtime, or Validator fails independently of the Agent repair.":
    "组织者控制的 Worker、存储服务、运行时或 Validator 发生与 Agent 修复无关的故障。",
  "No partial score is published; the affected evaluation is reviewed or rerun.":
    "不公布不完整分数；受影响的评测将接受复核或重新运行。",
  "Ranking": "排名",
  "How scoring works": "如何计分",
  "Build Success Rate is the primary ranking metric. The platform freezes an aggregate score only after all Cases have terminal outcomes and any organizer infrastructure errors have been resolved. A completed evaluation therefore reports both the number of successful Cases and the total number of evaluated Cases.":
    "构建成功率是主要排名指标。只有当所有 Case 均得到终态结果，且组织者基础设施错误均已解决后，平台才会冻结汇总分数。因此，完成的评测会同时报告成功 Case 数和参与评测的 Case 总数。",
  "Diagnostic information explains where time and failures occurred; it is not combined into a weighted score.":
    "诊断信息用于说明耗时和失败发生的位置，不会组合成加权分数。",
  "Case outcomes grouped by result category": "按结果类别汇总的 Case 结果",
  "Agent runtime and final build duration": "Agent 运行时间和最终构建耗时",
  "Patch size, modified-file count, and policy validation status": "补丁大小、修改文件数量和策略验证状态",
  "Build requests, retries, iterations, and model or tool usage when collected":
    "在平台采集时记录构建请求、重试、迭代以及模型或工具使用情况",
  "Case-set, runtime, Validator, and protocol versions used for the run":
    "本次运行使用的 Case 集、运行时、Validator 和协议版本",
  "Competition phases": "竞赛阶段",
  "Evaluation stages and feedback": "评测阶段与反馈",
  "The same Agent interface is used across stages, but the Case set, purpose, and visible feedback differ.":
    "各阶段使用相同的 Agent 接口，但 Case 集、目的和可见反馈有所不同。",
  "Scrollable evaluation stages table": "可横向滚动的评测阶段表",
  "Stage": "阶段",
  "Purpose": "目的",
  "Version and feedback": "版本与反馈",
  "Hosted Smoke Test": "托管冒烟测试",
  "Check the uploaded bundle, entrypoint, dependencies, workspace behavior, and output contract on a small lightweight set.":
    "在少量轻量 Case 上检查上传包、入口命令、依赖、工作区行为和输出协议。",
  "Runs the uploaded immutable version and returns detailed qualification diagnostics. It does not produce an official score.":
    "运行上传后的不可变版本并返回详细的资格检查诊断信息，不产生正式分数。",
  "Full Evaluation during the public phase": "公开阶段的完整评测",
  "Measure repair performance on the versioned validation set and produce the public evaluation result.":
    "在版本化验证集上衡量修复能力并产生公开评测结果。",
  "Starts only after the team selects a qualified immutable version. Progress and the completed aggregate result appear in My Submissions.":
    "仅在团队选定通过检查的不可变版本后开始。进度和完成后的汇总结果会显示在“我的提交”中。",
  "Hidden final evaluation": "隐藏最终评测",
  "Evaluate the team's frozen final Agent on organizer-controlled held-out Cases.":
    "在组织者控制的保留 Case 上评测团队冻结的最终 Agent。",
  "Uses the frozen Agent, Case set, runtime, Validator, and protocol versions. Aggregate results and permitted diagnostics are released after the deadline.":
    "使用冻结的 Agent、Case 集、运行时、Validator 和协议版本；截止时间后公布汇总结果和允许公开的诊断信息。",
  "Versioned release": "版本化发布",
  "Rules to be published before evaluation opens": "评测开放前将公布的规则",
  "To be announced in the final Evaluation Protocol.": "将在最终版评测协议中公布。",
  "The organizers will publish the exact score-denominator and cancellation semantics; any tie-breaker; Agent and build timeouts; build-feedback, iteration, and tool-call budgets; CPU, memory, storage, concurrency, network, and credential policies; submission frequency and rerun rules; and the feedback visible during public and hidden evaluation. Current pilot settings do not define these competition limits.":
    "组织者将公布准确的计分分母与取消语义、同分判定规则、Agent 和构建超时、构建反馈与迭代及工具调用预算、CPU/内存/存储/并发/网络/凭据策略、提交频率与重跑规则，以及公开和隐藏评测期间可见的反馈。当前试运行设置不代表正式竞赛限制。",
  "See": "参阅",
  "for integrity, disclosure, and enforcement requirements, and": "了解诚信、披露和执行要求，并参阅",
  "Timeline": "时间安排",
  "for the publication and evaluation schedule.": "了解规则发布和评测日程。",
  "Next": "下一页",
  "Review integrity and reproducibility requirements": "查看诚信与可复现性要求"
});
