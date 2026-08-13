window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.faq = Object.freeze({
  "Participant answers for Build-Bench registration, local Agent development, submission, evaluation, data, dates, and results.":
    "关于 Build-Bench 团队注册、Agent 本地开发、提交、评测、数据、日期和结果的参赛者常见问题。",
  "FAQ | Build-Bench Challenge": "常见问题 | Build-Bench Challenge",
  "Participant help": "参赛帮助",
  "Frequently Asked Questions": "常见问题",
  "Short answers to common questions from Team registration and local development through Agent submission, evaluation, and official results.":
    "简要解答从团队注册、本地开发到 Agent 提交、评测和正式结果发布过程中的常见问题。",
  "FAQ categories": "常见问题分类",
  "Browse by stage": "按参赛阶段浏览",
  "Start and register": "开始与注册",
  "Develop locally": "本地开发",
  "Upload and qualify": "上传与资格检查",
  "Evaluation and scoring": "评测与计分",
  "Data, dates, and results": "数据、日期与结果",

  "1. Start and register": "1. 开始与注册",
  "What is Build-Bench, and what does a Team submit?": "Build-Bench 是什么，团队需要提交什么？",
  "Build-Bench evaluates runnable software repair Agents on real package build failures. A Team submits Agent source and a versioned runtime manifest; the organizers run that Agent independently on competition Cases. Teams do not submit pre-generated repair patches or a Docker image as their competition entry.":
    "Build-Bench 使用真实软件包构建失败来评测可运行的软件修复 Agent。团队提交 Agent 源码和版本化运行清单，由组织者在竞赛 Case 上独立运行该 Agent。团队不以预生成修复补丁或 Docker 镜像作为竞赛提交。",
  "Read the Challenge": "查看竞赛任务",
  "How does Team registration work?": "团队如何注册？",
  "One Team leader creates the account and enters the complete roster. A Team may contain up to five people including the leader. Every member email is required, and the same email cannot appear in another Team.":
    "由一名团队负责人创建账号并录入完整成员名单。每支团队最多五人，包括负责人。每位成员必须填写邮箱，同一邮箱不能出现在其他团队中。",
  "Register a Team": "注册团队",
  "Read the Team rules": "阅读团队规则",
  "Where should a first-time participant begin?": "首次参赛应该从哪里开始？",
  "Download the current Starter Kit, run its environment check and official demo, create an Agent from the template, and test that Agent locally before uploading it. The Submission Guide provides the copy-and-run commands.":
    "下载当前 Starter Kit，运行环境检查和官方示例，从模板创建 Agent，并在上传前完成本地测试。《提交指南》提供了可直接复制运行的命令。",
  "Get the Starter Kit": "获取 Starter Kit",
  "Follow the Quick Start": "按照快速开始操作",
  "Must an Agent use a large language model?": "Agent 必须使用大语言模型吗？",
  "Yes. We encourage participants to use an LLM as the Agent's foundation model and combine it with retrieval, static analysis, log processing, search, and other compliant tools to build a more capable repair Agent. The submission must be a runnable Agent; Case-specific answer tables and pre-generated repair patches are prohibited.":
    "是。我们鼓励参赛者以 LLM 作为 Agent 的基础模型，并结合检索、静态分析、日志处理、搜索及其他合规工具构建更强大的修复 Agent。提交必须是可运行的 Agent，禁止使用针对特定 Case 的答案表或预生成修复补丁。",
  "Read the models and tools policy": "阅读模型与工具政策",

  "2. Develop locally": "2. 本地开发",
  "What do I need to run the Starter Kit?": "运行 Starter Kit 需要什么？",
  "You need a Linux or WSL2 shell, Git, and Docker Engine 24 or later, or Docker Desktop using Linux containers. The Starter Kit does not require sudo privileges, but you must have permission to run Docker containers. Docker Desktop typically requires no additional sudo configuration.":
    "你需要 Linux 或 WSL2 Shell、Git、Docker Engine 24+，或使用 Linux 容器的 Docker Desktop。Starter Kit 不强制要求 sudo 权限，但需要具备运行 Docker 容器的权限。使用 Docker Desktop 通常无需额外的 sudo 配置。",
  "Starter Kit v0.1.0-rc.2 includes the bb command, a managed-Python Agent template, an Example Agent, the hello Example Case, local checks, and deterministic packaging.":
    "Starter Kit v0.1.0-rc.2 包含 bb 命令、托管 Python Agent 模板、示例 Agent、hello 示例 Case、本地检查和确定性打包功能。",
  "Check the local setup": "检查本地环境",
  "What can the Agent read, modify, and return?": "Agent 可以读取、修改和返回什么？",
  "The Agent reads task evidence from the read-only input directory, modifies only the writable package worktree, and may write machine-readable status to the output directory. It must follow the workspace paths and agent-result.json schema defined by protocol v0.1.":
    "Agent 从只读输入目录读取任务证据，只修改可写的软件包工作树，并可向输出目录写入机器可读状态。它必须遵守协议 v0.1 定义的工作区路径和 agent-result.json Schema。",
  "Read the runtime interface": "阅读运行接口",
  "Can I submit a custom Docker runtime?": "可以提交自定义 Docker 运行环境吗？",
  "Not in Starter Kit v0.1.0-rc.2. The current submission contract supports the managed Python 3.11 profile. If additional runtime profiles are introduced, they will be published as a versioned protocol update rather than silently enabled.":
    "Starter Kit v0.1.0-rc.2 暂不支持。当前提交合约仅支持托管 Python 3.11 配置。如果以后增加其他运行配置，将通过版本化协议更新正式发布，而不会静默启用。",
  "Read the current package contract": "阅读当前提交包合约",
  "Can the Agent request build feedback while it runs?": "Agent 运行时可以请求构建反馈吗？",
  "Not in the current Starter Kit release. Bounded hosted build feedback is a planned feature; its command, limits, and response schema will be introduced only in a later protocol release. Do not assume that bb-build is currently available.":
    "当前 Starter Kit 版本暂不支持。有限次数的托管构建反馈属于计划功能，其命令、限制和响应 Schema 只会在后续协议版本中引入。请勿假设 bb-build 当前可用。",
  "Check the current runtime contract": "查看当前运行合约",
  "Can an Agent call external model APIs or include API keys?": "Agent 可以调用外部模型 API 或包含 API Key 吗？",
  "Do not include API keys, .env files, or other secrets in the uploaded bundle. The final network-access and organizer-managed credential policy will be published with the frozen rules and resource limits on August 31, 2026.":
    "上传包中不得包含 API Key、.env 文件或其他密钥。最终网络访问政策和组织者托管凭据政策将随冻结后的规则与资源限制于 2026 年 8 月 31 日公布。",
  "Read the pending-policy notice": "阅读待发布政策说明",

  "3. Upload and qualify a version": "3. 上传并通过版本检查",
  "What file should I upload?": "应该上传哪个文件？",
  "Upload the dist/agent-submission.zip archive produced by ./bb package. Do not upload the entire Starter Kit directory or assemble the competition archive manually. Every accepted upload is stored as an immutable Agent version with its own identifier and content digest.":
    "请上传由 ./bb package 生成的 dist/agent-submission.zip。不要上传整个 Starter Kit 目录，也不要手工组装竞赛压缩包。每次通过接收的上传都会保存为不可变 Agent 版本，并具有独立标识符和内容摘要。",
  "Review the submission contents": "查看提交内容要求",
  "What does the Hosted Smoke Test check?": "Hosted Smoke Test 检查什么？",
  "It checks the uploaded bundle, entrypoint, dependencies, workspace permissions, and output contract on a small lightweight Case set. Passing it qualifies that immutable version for Full Evaluation, but produces no official score and does not guarantee success on the full Case set.":
    "它会在一组轻量 Case 上检查上传包、入口命令、依赖、工作区权限和输出合约。通过测试后，该不可变版本具备进行 Full Evaluation 的资格，但不会产生正式分数，也不保证在完整 Case 集上成功。",
  "Read the testing guidance": "阅读测试说明",
  "Can I upload a revised Agent or replace a running evaluation?": "可以上传修订后的 Agent 或替换正在运行的评测吗？",
  "You may upload a revised bundle before the applicable deadline and within the published limits; it becomes a new immutable version. A later upload does not alter an active or completed evaluation. Full Evaluation begins only after the Team explicitly selects a qualified version.":
    "你可以在相应截止日期前、已公布限制范围内上传修订包；它会成为新的不可变版本。后续上传不会更改正在运行或已经完成的评测。只有团队明确选择通过检查的版本后，Full Evaluation 才会开始。",
  "Manage Agent versions": "管理 Agent 版本",
  "Read the version-control rules": "阅读版本控制规则",

  "4. Evaluation and scoring": "4. 评测与计分",
  "How is a proposed repair judged?": "候选修复如何判定？",
  "The platform derives a canonical patch from the Agent's modified worktree, checks the permitted paths and repair policy, reapplies the patch to a clean Case, and invokes the official target-architecture Docker Validator. A repair succeeds because the genuine package build succeeds, not because it resembles a reference patch.":
    "平台根据 Agent 修改后的工作树生成规范补丁，检查允许修改的路径和修复政策，将补丁重新应用到干净 Case，并调用正式的目标架构 Docker Validator。修复成功取决于真实软件包构建成功，而不是与参考补丁相似。",
  "See how each Case is evaluated": "查看单个 Case 的评测方式",
  "How is the competition score calculated?": "竞赛分数如何计算？",
  "Verified Build Success Rate is the primary metric: successful Cases divided by the official evaluation denominator. The exact denominator semantics, any tie-breaker, and remaining resource and rerun rules will be published in the frozen Rules on August 31, 2026.":
    "经验证的构建成功率是主要指标，即成功 Case 数除以正式评测分母。精确的分母语义、同分判定方式以及其余资源和重跑规则，将于 2026 年 8 月 31 日在冻结版规则中公布。",
  "Read the scoring rules": "阅读计分规则",
  "How are failures, timeouts, and infrastructure errors handled?": "构建失败、超时和基础设施错误如何处理？",
  "Build failure, Agent error, timeout, and an invalid patch are unsuccessful Case outcomes. An organizer-controlled infrastructure error is handled separately: no partial score is published, and the affected work is reviewed or rerun under the competition procedure.":
    "构建失败、Agent 错误、超时和无效补丁均属于未成功的 Case 结果。组织者控制范围内的基础设施错误会单独处理：平台不会发布部分分数，并会按照竞赛程序复核或重新运行受影响的任务。",
  "Review all outcome categories": "查看全部结果类别",
  "What is the difference between Smoke Test, Full Evaluation, and hidden evaluation?": "Smoke Test、Full Evaluation 和隐藏评测有什么区别？",
  "Hosted Smoke Test is a small qualification run with detailed diagnostics and no score. Public-phase Full Evaluation measures a selected qualified version on the versioned validation set. Final hidden evaluation runs the Team's frozen final Agent on held-out organizer-controlled Cases and releases only the permitted aggregate results and diagnostics.":
    "Hosted Smoke Test 是提供详细诊断但不计分的小规模资格测试。公开阶段的 Full Evaluation 在版本化验证集上评测团队选定的合格版本。最终隐藏评测在组织者控制的留出 Case 上运行团队冻结的最终 Agent，并仅发布允许公开的汇总结果与诊断信息。",
  "Compare the evaluation stages": "比较不同评测阶段",

  "5. Data, dates, and results": "5. 数据、日期与结果",
  "Which Case sets are used, and how large is the benchmark?": "竞赛使用哪些 Case 集，Benchmark 有多大？",
  "Local examples, public development resources, Hosted Smoke Test, Full Evaluation, and final hidden evaluation use separate versioned Case sets. The published benchmark contains 268 x86_64 and aarch64 migration failures. The organizers aim to retain approximately 1,000 Cases for final hidden evaluation, subject to final integrity, licensing, deduplication, and reproducibility checks.":
    "本地示例、公开开发资源、Hosted Smoke Test、Full Evaluation 和最终隐藏评测使用相互独立的版本化 Case 集。已发布 Benchmark 包含 268 个 x86_64 与 aarch64 迁移失败 Case。组织者计划为最终隐藏评测保留约 1,000 个 Case，具体数量仍取决于最终完整性、许可、去重和可复现性检查。",
  "Read the dataset status": "查看数据集状态",
  "See released resources": "查看已发布资源",
  "Where can I see status, results, and authoritative updates?": "在哪里查看状态、结果和权威更新？",
  "My Submissions shows uploaded Agent versions, qualification logs, Full Evaluation progress, and completed results. The Leaderboard shows published rankings. Versioned changes to dates, resources, rules, and evaluation policy appear on their corresponding competition pages; any official support channel will be identified on this website when available.":
    "“我的提交”展示已上传的 Agent 版本、资格检查日志、Full Evaluation 进度和已完成结果；排行榜展示已发布排名。日期、资源、规则和评测政策的版本化变更会发布在对应竞赛页面；正式支持渠道确定后也将在本网站说明。",
  "Open My Submissions": "打开“我的提交”",
  "Open the Leaderboard": "打开排行榜",

  "Still unsure?": "仍有疑问？",
  "Use the linked detail page as the authoritative source. If an answer and a versioned rule or protocol differ, the latest published rule or protocol controls.":
    "请以回答中链接的详情页为权威来源。如果本页回答与版本化规则或协议不一致，以最新发布的规则或协议为准。",
});
