window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.submission = Object.freeze({
  "Agent Submission | Build-Bench Challenge": "Agent 提交 | Build-Bench Challenge",
  "Draft contract": "合约草案",
  "The single-Agent model is confirmed; packaging, API fields, budgets, and network policy are not final.":
    "单一 Agent 模式已经确认；打包方式、API 字段、预算和网络策略尚未最终确定。",
  "Draft interface": "接口草案",
  "Agent Submission": "Agent 提交",
  "Teams will provide one repair Agent that satisfies a standardized input and output contract. Organizers will run the Agent on competition cases and score its resulting repairs.":
    "参赛团队将提交一个满足标准化输入输出合约的修复 Agent。主办方会用该 Agent 处理竞赛 Case，并对修复结果评分。",
  "Submission model": "提交模式",
  "One Agent": "单一 Agent",
  "Execution": "运行方式",
  "Organizer controlled": "由主办方控制",
  "Contract version": "合约版本",
  "To be announced": "待公布",
  "On this page": "本页内容",
  "Lifecycle": "运行流程",
  "Agent input": "Agent 输入",
  "Agent output": "Agent 输出",
  "Packaging": "打包方式",
  "Resources & APIs": "资源与 API",
  "Checklist": "发布清单",
  "Do not build against field names on this page until the versioned starter kit is released.":
    "在带版本的 starter kit 发布前，请勿依赖本页所示字段名进行开发。",
  "Interface under design": "接口仍在设计中",
  "The organizing team has confirmed a single Agent submission model. The delivery artifact, invocation method, schemas, resource limits, model access, and failure semantics still require team approval.":
    "主办团队已确认采用单一 Agent 提交模式。交付制品、调用方式、schema、资源限制、模型访问和失败语义仍需团队确认。",
  "Submit an Agent, not precomputed answers": "提交 Agent，而不是预先计算的答案",
  "A team supplies a reproducible Agent that can consume the prescribed case input and emit the prescribed repair output. The competition harness invokes that Agent on organizer-controlled validation and hidden test cases.":
    "团队需提供一个可复现的 Agent，能够接收规定的 Case 输入并输出规定格式的修复结果。竞赛评测框架会在主办方控制的验证集和隐藏测试集上调用该 Agent。",
  "One competition entry": "一种竞赛提交形式",
  "The Agent may internally use prompting, retrieval, static analysis, build-log parsing, tool calls, or iterative repair loops. These are implementation choices inside the same submission model, not separate submission modes.":
    "Agent 内部可以使用提示、检索、静态分析、构建日志解析、工具调用或迭代修复循环。这些都是同一提交模式下的实现选择，不是独立的提交方式。",
  "The repair patch remains the common artifact that the evaluator applies and builds. It is an Agent output, not a second way to enter the competition.":
    "修复补丁仍是评测器应用并构建的统一制品。它是 Agent 的输出，而不是另一种参赛方式。",
  "Organizer-run lifecycle": "主办方运行流程",
  "From Agent artifact to leaderboard score": "从 Agent 制品到排行榜得分",
  "Team submits Agent": "团队提交 Agent",
  "The platform validates metadata and stores an immutable, versioned entry.":
    "平台验证元数据，并保存不可变且带版本的参赛制品。",
  "Harness starts runtime": "评测框架启动运行环境",
  "The organizer launches the Agent in an isolated environment with the announced limits.":
    "主办方在隔离环境中按公布的限制启动 Agent。",
  "Harness provides a case": "评测框架提供 Case",
  "The Agent receives a case directory and metadata through the versioned interface.":
    "Agent 通过带版本的接口接收 Case 目录和元数据。",
  "Agent emits a repair": "Agent 输出修复",
  "The Agent writes a unified diff and structured completion status to the output location.":
    "Agent 将 unified diff 和结构化完成状态写入指定输出位置。",
  "Evaluator builds package": "评测器构建软件包",
  "The repair is applied to a clean copy and verified with the official target build.":
    "修复会应用到干净副本，并通过官方目标架构构建进行验证。",
  "Results are aggregated": "汇总结果",
  "Valid case outcomes contribute to the submission score and leaderboard statistics.":
    "有效的 Case 结果会计入提交得分和排行榜统计。",
  "Draft input contract": "输入合约草案",
  "What the harness provides": "评测框架提供的内容",
  "The final starter kit will define an exact directory tree and machine-readable schema. The following capabilities are intended, but field names are not final.":
    "最终 starter kit 将定义准确的目录树和机器可读 schema。以下能力是拟定方案，但字段名尚未最终确定。",
  "Read-only case directory": "只读 Case 目录",
  "Package specifications, source archives, existing patches, auxiliary build-service files, and the failed log.":
    "软件包规范文件、源码归档、已有补丁、构建服务辅助文件和失败日志。",
  "Case manifest": "Case manifest",
  "Case ID, package name, source architecture, target architecture, validator backend, and checksums.":
    "Case ID、软件包名称、源架构、目标架构、验证器后端和校验和。",
  "Invocation transport": "调用方式",
  "Fixed CLI command, local HTTP API, or equivalent harness adapter.":
    "固定 CLI 命令、本地 HTTP API 或等价的评测框架适配器。",
  "Iteration feedback": "迭代反馈",
  "Whether an Agent can request build attempts during one case, and which logs are returned after each attempt.":
    "Agent 能否在处理单个 Case 时请求构建，以及每次尝试后返回哪些日志。",
  "Draft output contract": "输出合约草案",
  "Return a repair and a structured status": "返回修复结果和结构化状态",
  "A unified diff is the planned repair artifact because it is inspectable, auditable, and can be applied to a clean package copy. The harness also needs a machine-readable result describing whether the Agent produced a repair.":
    "计划采用 unified diff 作为修复制品，因为它便于检查和审核，也能应用到干净的软件包副本。评测框架还需要机器可读的结果，用来说明 Agent 是否生成了修复。",
  "Illustrative output only - not the final schema": "仅为输出示例，不是最终 schema",
  "The sample communicates the shape of the contract, not guaranteed names or values. The released JSON Schema and conformance tests will be authoritative.":
    "该示例仅说明合约的大致结构，不保证字段名或取值。最终以发布的 JSON Schema 和一致性测试为准。",
  "Expected result classes": "预期结果类型",
  "Repair produced": "已生成修复",
  "A candidate diff is available for policy checks and executable validation.":
    "候选 diff 可用于规则检查和可执行验证。",
  "No repair": "未生成修复",
  "The Agent completed but intentionally emitted no patch for the case.":
    "Agent 已完成运行，但有意未为该 Case 输出补丁。",
  "Agent failure": "Agent 失败",
  "The Agent crashed, timed out, or returned malformed output; final scoring semantics are TBA.":
    "Agent 崩溃、超时或返回格式错误的输出；最终评分语义待定。",
  "Delivery and entrypoint": "交付方式与入口点",
  "Reproducible packaging is required; the vehicle is TBA": "必须可复现打包；具体形式待定",
  "The Agent must be runnable without manual intervention and must expose one deterministic entrypoint. The team has not yet chosen whether the official artifact will be a container image, a source repository plus lockfile, or another packaged runtime.":
    "Agent 必须能够在无人干预的情况下运行，并提供一个确定的入口点。团队尚未决定官方制品采用容器镜像、源码仓库加 lockfile，还是其他打包运行环境。",
  "Decision": "待定事项",
  "Current status": "当前状态",
  "Submission artifact": "提交制品",
  "Open": "待定",
  "Container image, repository bundle, or platform-managed package":
    "容器镜像、仓库包或平台托管软件包",
  "Entrypoint": "入口点",
  "Fixed CLI or local API": "固定 CLI 或本地 API",
  "Architecture of Agent runtime": "Agent 运行环境架构",
  "Native, emulated, or platform selected": "原生、模拟或由平台选择",
  "Dependency installation": "依赖安装",
  "Prebuilt only or bounded setup phase": "仅允许预构建，或提供受限的初始化阶段",
  "Versioning": "版本管理",
  "Immutable artifact digest per leaderboard entry": "每条排行榜记录对应不可变的制品摘要",
  "Resources and external services": "资源与外部服务",
  "Policies that must be frozen before submissions open": "提交开放前必须冻结的策略",
  "Time and iteration budget": "时间与迭代预算",
  "Per-case wall time, maximum repair attempts, tool calls, and build requests.":
    "每个 Case 的实际运行时间、最大修复次数、工具调用次数和构建请求次数。",
  "Compute budget": "计算资源预算",
  "CPU, memory, disk, accelerator availability, and concurrency.":
    "CPU、内存、磁盘、加速器可用性和并发数。",
  "Network policy": "网络策略",
  "Whether outbound access is disabled, allowlisted, or brokered only through organizer APIs.":
    "是否禁用外部访问、采用白名单，或仅允许通过主办方 API 代理访问。",
  "Model credentials": "模型凭据",
  "Supported model providers, secret injection, accounting, and whether teams may bring their own keys.":
    "支持的模型提供商、密钥注入与计费方式，以及团队能否使用自有密钥。",
  "Retry semantics": "重试语义",
  "Startup retries, transient API failures, malformed output, timeout, and evaluator fault handling.":
    "启动重试、临时 API 故障、格式错误的输出、超时和评测器故障处理。",
  "Submission frequency": "提交频率",
  "Daily limits, artifact replacement, validation queue priority, and final-entry selection.":
    "每日限制、制品替换、验证队列优先级和最终参赛版本选择。",
  "Release checklist": "发布清单",
  "What participants will receive before launch": "参赛者将在启动前获得的内容",
  "Versioned Agent interface specification": "带版本的 Agent 接口规范",
  "JSON Schema or equivalent validation contract": "JSON Schema 或等价的验证合约",
  "Minimal conforming example Agent": "符合规范的最小示例 Agent",
  "Local conformance and smoke-test command": "本地一致性检查和冒烟测试命令",
  "Development cases with expected evaluator outputs": "附带预期评测器输出的开发 Case",
  "Published resource, model API, network, and failure policies":
    "公开的资源、模型 API、网络和失败处理策略",
  "Next": "下一页",
  "See how Agent runs become scores": "了解 Agent 运行结果如何转化为得分",
  "Draft Agent submission model and organizer-run API contract for the Build-Bench Challenge.":
    "Build-Bench Challenge 的 Agent 提交模式草案及主办方运行的 API 合约。",
  "Scrollable Agent packaging decision table": "可横向滚动的 Agent 打包决策表",
});
