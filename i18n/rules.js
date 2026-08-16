window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.rules = Object.freeze({
  "Official participant rules for team registration, Agent submissions, evaluation integrity, and result verification in the Build-Bench Challenge.":
    "Build-Bench Challenge 关于团队注册、Agent 提交、评测诚信和结果核验的正式参赛规则。",
  "Competition Rules | Build-Bench Challenge": "竞赛规则 | Build-Bench Challenge",
  "Participant rulebook": "参赛规则手册",
  "Competition Rules": "竞赛规则",
  "These rules govern team registration, Agent submissions, evaluation integrity, and result verification for the Build-Bench Challenge.":
    "本规则规定 Build-Bench Challenge 的团队注册、Agent 提交、评测诚信和结果核验要求。",
  "REGISTERING A TEAM OR SUBMITTING AN AGENT CONSTITUTES ACCEPTANCE OF THESE COMPETITION RULES.":
    "注册团队或提交 Agent 即表示接受本竞赛规则。",
  "Build-Bench is a skills-based software engineering competition. Teams develop repair Agents; organizers run qualified Agent versions on competition Cases and validate each proposed repair through an executable target-architecture build.":
    "Build-Bench 是一项以能力为基础的软件工程竞赛。团队开发修复 Agent；主办方在竞赛 Case 上运行通过检查的 Agent 版本，并通过目标架构上的真实可执行构建验证每项修复。",
  "The Rules incorporate the versioned evaluation and scoring protocol and apply together with the Submission Guide, Timeline, and published data notices. Participants should read these materials before registering or starting an official evaluation.":
    "本规则纳入版本化的评测与计分协议，并与《参赛指南》《时间安排》及已发布的数据说明共同适用。参赛者应在注册或启动正式评测前阅读这些材料。",

  "1. Competition scope": "1. 竞赛范围",
  "1.1 Competition title": "1.1 竞赛名称",
  "The competition is the Build-Bench Challenge, organized for the ICSE 2027 Competition Track.":
    "本竞赛名称为 Build-Bench Challenge，面向 ICSE 2027 Competition Track 举办。",
  "1.2 Competition task": "1.2 竞赛任务",
  "A Team submits a runnable LLM-based repair Agent rather than Case-specific patches. The competition covers bidirectional package migrations among the three supported ISAs: x86_64, aarch64, and riscv64. For each Case, the Agent receives a prepared package workspace, source and target architecture metadata, the failed target-build log, and the packaging and build context included with that Case. The Agent diagnoses the failure and modifies the permitted package worktree; the organizer evaluates the resulting change in the official target-architecture environment.":
    "团队提交一个可运行的基于 LLM 的修复 Agent，而非针对具体 Case 的补丁。竞赛覆盖三种受支持指令集架构（x86_64、aarch64 和 riscv64）之间的双向软件包迁移。对于每个 Case，Agent 接收准备好的软件包工作区、源架构与目标架构元数据、目标架构构建失败日志，以及该 Case 附带的打包与构建上下文。Agent 诊断故障并修改允许变更的软件包工作区；主办方在正式的目标架构环境中评测由此产生的修改。",
  "1.3 Participant documentation": "1.3 参赛文档",
  "The Challenge page defines the competition task and released Case sets. The Participate page defines the Agent package and runtime interface. Section 5 of these Rules defines Case execution, validation, outcomes, and scoring. The Timeline gives the official competition dates.":
    "“竞赛任务”页面定义竞赛任务和已发布的 Case 集；“参与比赛”页面定义 Agent 包和运行接口；本规则第 5 节定义 Case 执行、验证、结果与计分；“时间安排”给出正式竞赛日期。",
  "Submission Guide": "提交指南",
  "Evaluation and scoring": "评测与计分",

  "2. Team registration and eligibility": "2. 团队注册与参赛资格",
  "2.1 Team registration": "2.1 团队注册",
  "Each Team is registered by one Team leader, who provides the Team name and member information through the competition website.":
    "每支团队由一名组长注册，组长通过竞赛网站填写团队名称和成员信息。",
  "A Team may contain no more than five members, including the Team leader.":
    "每支团队最多包含五名成员，其中包括组长。",
  "An email address is required for every member and may not appear in more than one Team in this competition.":
    "每位成员均须提供邮箱地址，同一邮箱不得出现在本竞赛的不同团队中。",
  "A person may participate through only one Team. Duplicate, misleading, or false registration information may be rejected or investigated.":
    "每位参赛者只能通过一支团队参赛。重复、误导或虚假的注册信息可能被拒绝或调查。",
  "2.2 Team responsibilities": "2.2 团队责任",
  "The Team leader manages the roster, uploaded Agent versions, and selection of versions for official evaluation.":
    "组长负责管理团队成员、已上传的 Agent 版本以及正式评测版本的选择。",
  "The Team must keep its registration information accurate and complete before the applicable deadline.":
    "团队必须在相应截止日期前确保注册信息准确、完整。",
  "Participants are responsible for confirming that their participation and use of third-party materials are permitted by their institution, employer, and applicable licenses.":
    "参赛者有责任确认其所在机构或雇主以及相关许可证允许其参赛并使用第三方材料。",
  "Any actual or potential conflict of interest involving the organizers must be disclosed through the official support channel.":
    "任何涉及主办方的实际或潜在利益冲突，均须通过官方支持渠道披露。",

  "3. Agent submission and version control": "3. Agent 提交与版本控制",
  "3.1 Conforming Agent bundle": "3.1 符合要求的 Agent 包",
  "The submitted ZIP must contain a runnable Agent source bundle that conforms to the current Submission Guide, manifest schema, and permitted runtime profile.":
    "提交的 ZIP 必须包含可运行的 Agent 源码包，并符合当前《提交指南》、清单 Schema 和允许的运行环境配置。",
  "The entrypoint must be non-interactive and must complete without organizer or participant intervention.":
    "入口命令必须采用非交互方式运行，并在无需主办方或参赛者干预的情况下完成。",
  "The bundle must contain only the Agent code, declared dependencies, configuration, and supporting documentation needed to run it.":
    "提交包只能包含运行 Agent 所需的代码、已声明依赖、配置和说明文档。",
  "Secrets, personal credentials, hidden Case information, pre-generated Case repairs, caches, and previous run artifacts must not be included.":
    "提交包不得包含密钥、个人凭据、隐藏 Case 信息、预生成的 Case 修复、缓存或此前运行产物。",
  "3.2 Immutable versions": "3.2 不可变版本",
  "Every accepted upload creates an immutable Agent version identified by its submission record and content digest.":
    "每次通过接收的上传都会创建一个不可变 Agent 版本，并由提交记录和内容摘要标识。",
  "Any code, dependency, manifest, or configuration change requires a new upload and creates a new version.":
    "代码、依赖、清单或配置发生任何变化，都必须重新上传并创建新版本。",
  "A version must pass the platform checks and Hosted Smoke Test before it can be selected for Full Evaluation.":
    "一个版本必须通过平台检查和 Hosted Smoke Test，才能被选择用于 Full Evaluation。",
  "Uploading a version does not automatically start Full Evaluation. The Team must explicitly select a qualified version.":
    "上传版本不会自动启动 Full Evaluation；团队必须主动选择一个已通过检查的版本。",
  "A later upload does not alter an active or completed evaluation snapshot.":
    "后续上传不会改变正在进行或已完成的评测快照。",
  "3.3 Organizer-run execution": "3.3 由主办方运行",
  "The organizer starts an independent Agent instance for each Case under the published interface and resource policy.":
    "主办方依据已发布的接口和资源政策，为每个 Case 启动独立的 Agent 实例。",
  "The Agent may read the provided inputs and modify only the permitted worktree and output locations.":
    "Agent 可以读取提供的输入，但只能修改允许的工作区和输出位置。",
  "The Agent must apply all intended changes directly to the permitted package worktree. An Agent that generates a patch internally must apply that patch to the worktree before it exits; a candidate patch written only to an output location is not treated as the official repair.":
    "Agent 必须将所有预期修改直接应用到允许变更的软件包工作区。内部生成补丁的 Agent 必须在退出前将该补丁应用到工作区；仅写入输出位置的候选补丁不被视为正式修复。",
  "The completion record (": "完成记录（",
  ") reports status and diagnostics only and does not define the repair. Any declared":
    "）仅报告状态和诊断信息，不定义修复本身。任何声明的",
  "field is advisory; the organizer determines the actual changes from the final worktree.":
    "字段仅供参考；主办方根据最终工作区确定实际修改。",
  "The Agent may not directly access the Docker socket, the final Validator, hidden evaluator files, or organizer infrastructure.":
    "Agent 不得直接访问 Docker Socket、最终 Validator、隐藏评测文件或主办方基础设施。",
  "Stdout, stderr, declared result files, and platform events may be retained for diagnosis, auditing, and reproducibility.":
    "平台可保留标准输出、标准错误、声明的结果文件和平台事件，用于诊断、审计和复现。",

  "4. Competition data, models, and tools": "4. 竞赛数据、模型与工具",
  "4.1 Competition materials": "4.1 竞赛材料",
  "Released Cases, schemas, examples, logs, and Starter Kit materials may be used for participation subject to their published licenses and data notices.":
    "已发布的 Case、Schema、示例、日志和 Starter Kit 材料可用于参赛，但须遵守其已发布许可证和数据说明。",
  "Participants must preserve applicable copyright, attribution, redistribution, and open-source license obligations.":
    "参赛者必须遵守适用的版权、署名、再分发和开源许可证义务。",
  "Unreleased Cases, hidden evaluator assets, and confidential organizer materials may not be obtained, used, shared, or redistributed.":
    "不得获取、使用、共享或再分发未发布的 Case、隐藏评测资产和主办方保密材料。",
  "4.2 Models, external data, and tools": "4.2 模型、外部数据与工具",
  "Teams may develop Agents using language models, prompting, retrieval, code search, static analysis, log processing, and other repair tools that comply with the published runtime and network policy.":
    "团队可以使用符合已发布运行和网络政策的语言模型、提示、检索、代码搜索、静态分析、日志处理及其他修复工具开发 Agent。",
  "External models, datasets, knowledge bases, APIs, and tools must be lawfully accessible to the Team and disclosed as required by Section 8.":
    "团队必须能够合法访问外部模型、数据集、知识库、API 和工具，并按照第 8 节要求进行披露。",
  "Use of a third-party service does not transfer responsibility for compliance, reproducibility, cost, availability, or licensing to the organizers.":
    "使用第三方服务不会将合规、可复现性、成本、可用性或许可责任转移给主办方。",
  "Participants must not embed API keys or personal credentials in an Agent bundle. Any organizer-managed credential mechanism will be described separately if external calls are permitted.":
    "参赛者不得在 Agent 包中嵌入 API Key 或个人凭据。如果允许外部调用，主办方管理的凭据机制将另行说明。",

  "5. Evaluation and scoring": "5. 评测与计分",
  "5.1 Successful repair and Per-Case validation": "5.1 成功修复与逐 Case 验证",
  "Each Case is an independent run. One slow or unsuccessful Case does not stop other scheduled Cases, and the selected Agent archive remains immutable throughout the evaluation.":
    "每个 Case 都是一次独立运行。某个 Case 运行缓慢或未成功不会阻止其他已调度的 Case，且选定的 Agent 归档在整个评测期间保持不可变。",
  "The platform freezes the run inputs by recording the Agent archive and its checksum together with the Case-set, runtime, Validator, and rules versions.":
    "平台通过记录 Agent 归档及其校验和，并同时记录 Case 集、运行环境、Validator 和规则版本来冻结运行输入。",
  "The platform verifies the Case checksum and creates an isolated writable worktree from the original package materials.":
    "平台验证 Case 校验和，并从原始软件包材料创建隔离的可写工作区。",
  "The declared entrypoint receives the standard workspace and runs under the published runtime, time, resource, and network policy.":
    "声明的入口命令接收标准工作区，并依据已发布的运行环境、时间、资源和网络政策执行。",
  "After the Agent exits, the platform validates": "Agent 退出后，平台验证",
  "and derives the canonical": "并根据原始与修改后的工作区生成规范的",
  "from the original and modified worktrees.": "。",
  "The canonical patch is audited for forbidden paths, policy violations, required output structure, and prohibited build-bypass behavior.":
    "平台审核 canonical patch 是否包含禁止路径、违反政策、缺少必要输出结构或存在被禁止的构建绕过行为。",
  "The platform applies the audited patch to a clean copy of the Case and invokes the official Docker Validator in the target-architecture environment.":
    "平台将通过审核的补丁应用到 Case 的干净副本，并在目标架构环境中调用官方 Docker Validator。",
  "Agent status, Validator status, duration, patch statistics, and permitted logs are stored as structured evidence.":
    "Agent 状态、Validator 状态、运行时长、补丁统计信息和允许保留的日志将作为结构化证据存储。",
  "A repair is not compared textually with a reference patch. A Case is counted as successfully repaired only when the required policy checks pass, the canonical patch is derived and applies cleanly to a clean copy of the Case, the official target-architecture build completes successfully, and the expected package artifacts are produced and verified.":
    "修复不会与参考补丁进行文本比对。仅当必需的政策检查通过、canonical patch 成功生成并干净地应用到 Case 的干净副本、正式的目标架构构建成功完成、且生成并验证了预期的软件包产物时，该 Case 才计为修复成功。",
  "5.2 Terminal outcomes": "5.2 终态结果",
  "The platform records Agent execution and final build validation separately. An evaluation can complete normally even when Cases are unsuccessful; an evaluation-level System Error is reserved for organizer-controlled failures.":
    "平台分别记录 Agent 执行和最终构建验证。即使存在未成功的 Case，整次评测仍可正常完成；评测级 System Error 仅用于主办方可控故障。",
  "means the audited patch produces the expected package artifacts in the clean target build and is recorded as a successful Case.":
    "表示通过审核的补丁在干净目标构建中生成预期软件包产物，并记为成功 Case。",
  "mean that the build fails, dependencies cannot be resolved, or the Agent proposes no allowed change; each is an unsuccessful Case.":
    "表示构建失败、依赖无法解析或 Agent 未提出允许的修改；这些结果均记为未成功 Case。",
  "means the Agent crashes, exits abnormally, or omits a valid":
    "表示 Agent 崩溃、异常退出或未提供有效的",
  "; it is an unsuccessful Case.": "；该结果记为未成功 Case。",
  "means the Agent or its permitted build work exceeds the applicable Case-level limit; it is an unsuccessful Case.":
    "表示 Agent 或其允许执行的构建工作超过适用的逐 Case 限制；该结果记为未成功 Case。",
  "means the canonical patch cannot be derived or applied cleanly, or it violates path, output, or repair policy; it is an unsuccessful Case.":
    "表示 canonical patch 无法生成或无法干净地应用，或违反路径、输出或修复政策；该结果记为未成功 Case。",
  "means an organizer-controlled Worker, storage service, runtime, or Validator fails independently of the Agent repair. It is not treated as a participant repair failure; the affected evaluation is reviewed or rerun.":
    "表示主办方控制的 Worker、存储服务、运行环境或 Validator 发生与 Agent 修复无关的故障。该结果不视为参赛者修复失败；受影响的评测将接受复核或重跑。",
  "No partial official score is published while unresolved infrastructure errors prevent the aggregate result from being finalized.":
    "当未解决的基础设施错误导致汇总结果无法最终确定时，不发布不完整的正式分数。",
  "5.3 Ranking and diagnostics": "5.3 排名与诊断",
  "Verified Build Success Rate": "经验证的构建成功率",
  "is the primary ranking metric: the percentage of evaluated Cases that satisfy the verified repair conditions above and are counted as successfully repaired. The platform freezes an aggregate result only after all Cases have terminal outcomes and any organizer-controlled infrastructure errors have been resolved.":
    "是主要排名指标，即满足上述验证修复条件并被计为成功修复的已评测 Case 所占的百分比。只有在所有 Case 均得到终态结果且主办方可控的基础设施错误均已解决后，平台才会冻结汇总结果。",
  "Execution Time": "执行时间",
  "and": "和",
  "officially recorded token usage": "官方记录的 Token 使用量",
  "are reported as secondary efficiency metrics. Diagnostic information explains performance and failures but is not combined into a weighted score.":
    "作为次要效率指标报告。诊断信息用于说明性能和失败原因，但不会合并为加权分数。",
  "Published diagnostics may include:": "公布的诊断信息可包括：",
  "Case outcomes grouped by result category;": "按结果类别汇总的 Case 结果；",
  "Agent execution time and final build duration;": "Agent 执行时间和最终构建时长；",
  "officially recorded token, model, and tool usage when collected;": "官方记录的 Token、模型和工具使用情况；",
  "patch size, modified-file count, and policy-validation status;": "补丁大小、修改文件数量和政策验证状态；",
  "build requests, retries, and repair iterations; and": "构建请求、重试和修复迭代；以及",
  "the Case-set, runtime, Validator, and rules versions used for the run.": "本次运行使用的 Case 集、运行环境、Validator 和规则版本。",
  "The final denominator definition and any tie-breaker will be published before public evaluation opens.":
    "最终分母定义及同分判定规则将在公开评测开放前公布。",
  "5.4 Evaluation stages and feedback": "5.4 评测阶段与反馈",
  "The same Agent interface is used across stages, but the Case set, purpose, and visible feedback differ.":
    "各阶段使用相同的 Agent 接口，但 Case 集、目的和可见反馈有所不同。",
  "Hosted Smoke Test.": "Hosted Smoke Test。",
  "Checks the uploaded bundle, entrypoint, dependencies, workspace behavior, and output contract on a small lightweight set. It runs the uploaded immutable version, returns detailed qualification diagnostics, and does not produce an official score.":
    "在小型轻量 Case 集上检查上传包、入口命令、依赖、工作区行为和输出协议。该测试运行已上传的不可变版本，返回详细的资格诊断信息，但不产生正式分数。",
  "Full Evaluation during the public phase.": "公开阶段的 Full Evaluation。",
  "Measures repair performance on the versioned validation set. It starts only after the Team selects a qualified immutable version; progress and the completed aggregate result appear in My Submissions.":
    "在版本化验证集上衡量修复性能。仅在团队选择通过资格检查的不可变版本后启动；进度和完成后的汇总结果显示在 My Submissions 中。",
  "Hidden final evaluation.": "隐藏最终评测。",
  "Runs the Team's frozen final Agent on organizer-controlled held-out Cases using frozen Agent, Case-set, runtime, Validator, and rules versions. Aggregate results and permitted diagnostics are released after the deadline.":
    "在主办方控制的保留 Case 上运行团队冻结的最终 Agent，并使用冻结的 Agent、Case 集、运行环境、Validator 和规则版本。截止时间后公布汇总结果和允许公开的诊断信息。",
  "5.5 Versioned parameters": "5.5 版本化参数",
  "Before public evaluation opens, the organizers will publish the exact score-denominator and cancellation semantics; any tie-breaker; Agent and build timeouts; build-feedback, iteration, and tool-call budgets; CPU, memory, storage, concurrency, network, and credential policies; submission frequency and rerun rules; and the feedback visible during public and hidden evaluation.":
    "在公开评测开放前，主办方将公布精确的计分分母和取消语义、同分判定规则、Agent 与构建超时、构建反馈/迭代/工具调用预算、CPU/内存/存储/并发/网络/凭据政策、提交频率与重跑规则，以及公开和隐藏评测期间可见的反馈。",
  "Current pilot settings do not define these competition limits. Publication dates appear on the":
    "当前试运行设置不代表正式竞赛限制。发布日期见",

  "6. Prohibited conduct": "6. 禁止行为",
  "Participants must not obtain an advantage by bypassing the repair task, evaluator, resource policy, or Team-registration rules.":
    "参赛者不得通过绕过修复任务、评测器、资源政策或团队注册规则获取优势。",
  "Do not embed hidden solutions, leaked labels, Case-specific lookup tables, pre-generated repair patches, or other undisclosed answers in the Agent or its dependencies.":
    "不得在 Agent 或其依赖中嵌入隐藏解法、泄露标签、特定 Case 查找表、预生成修复补丁或其他未披露答案。",
  "Do not exploit or attempt to escape the Agent runtime, Build Gateway, Validator, sandbox, authentication system, storage, scheduler, or network controls.":
    "不得利用或试图逃逸 Agent 运行环境、Build Gateway、Validator、沙箱、认证系统、存储、调度器或网络控制。",
  "Do not suppress failures, delete essential tests, replace the package with a dummy artifact, or disable meaningful functionality merely to obtain a successful build result.":
    "不得仅为获得构建成功而掩盖失败、删除必要测试、用虚假产物替换软件包或关闭关键功能。",
  "Do not alter immutable Case inputs, manifests, checksums, hidden metadata, evaluator files, result records, or any path outside the permitted worktree.":
    "不得修改不可变 Case 输入、清单、校验和、隐藏元数据、评测器文件、结果记录或允许工作区以外的任何路径。",
  "Do not use undeclared manual, remote, or third-party intervention to make Case-by-Case decisions during organizer-run evaluation.":
    "在主办方运行的评测中，不得使用未披露的人工、远程或第三方干预逐 Case 作出决策。",
  "Do not use multiple Teams, accounts, identities, or automated requests to evade registration, submission, evaluation, or resource limits.":
    "不得使用多个团队、账户、身份或自动化请求规避注册、提交、评测或资源限制。",
  "Do not run unrelated workloads, mine cryptocurrency, interfere with other participants, or attempt to degrade competition services.":
    "不得运行无关工作负载、挖掘加密货币、干扰其他参赛者或试图降低竞赛服务可用性。",

  "7. Hidden evaluation and confidentiality": "7. 隐藏评测与保密",
  "Hidden evaluation Cases remain under organizer control and are not distributed before final evaluation.":
    "隐藏评测 Case 由主办方控制，在最终评测前不会分发。",
  "Official hidden evaluation uses a frozen Agent version, Case-set version, runtime image, Validator image, and protocol version.":
    "正式隐藏评测使用冻结的 Agent 版本、Case 集版本、运行镜像、Validator 镜像和协议版本。",
  "Teams may use only the feedback intentionally released by the platform and must not probe the service to infer hidden Case contents, labels, reference repairs, or evaluator internals.":
    "团队只能使用平台有意发布的反馈，不得探测服务以推断隐藏 Case 内容、标签、参考修复或评测器内部信息。",
  "Organizers may inspect successful, unusually small, suspicious, or policy-sensitive repairs and may rerun an entry to verify its result.":
    "主办方可以检查成功、异常小、可疑或涉及规则边界的修复，并可重新运行参赛项目以核验结果。",
  "Any accidental exposure of hidden or confidential material must be reported promptly and must not be used or shared.":
    "如意外接触隐藏或保密材料，必须立即报告，且不得使用或共享。",

  "8. Method disclosure and reproducibility": "8. 方法披露与可复现性",
  "8.1 Required disclosure": "8.1 必须披露的信息",
  "A final entry must describe the system that produced its result. The disclosure must identify, as applicable:":
    "最终参赛项目必须说明产生其结果的系统。披露内容应根据实际情况包括：",
  "base model names, providers, and versions when available;": "基础模型名称、提供方及可获取时的版本；",
  "major prompt templates or prompting strategy, repair-loop design, retrieval sources, static analyzers, and external tools;":
    "主要提示词模板或提示策略、修复循环设计、检索来源、静态分析器和外部工具；",
  "training, fine-tuning, external datasets, private knowledge bases, and pre-processing used by the entry;":
    "参赛项目使用的训练、微调、外部数据集、私有知识库和预处理；",
  "third-party APIs or services contacted during execution; and": "运行期间调用的第三方 API 或服务；以及",
  "known nondeterminism, caching, dependency, and reproducibility constraints.":
    "已知的非确定性、缓存、依赖和可复现性限制。",
  "8.2 Verification materials": "8.2 核验材料",
  "Teams must retain the submitted source, lockfiles, configuration, and method documentation needed to explain and rerun the evaluated version.":
    "团队必须保留用于说明和重新运行被评测版本的提交源码、锁定文件、配置和方法文档。",
  "Organizers may request logs, configuration details, or a reproducibility demonstration for result review.":
    "主办方可在结果审查时要求提供日志、配置细节或可复现性演示。",
  "Any public solution description or solution paper must correspond to the Agent version that produced the reported official result.":
    "任何公开方案说明或 solution paper 必须与产生所报告正式结果的 Agent 版本相对应。",

  "9. Review, correction, and enforcement": "9. 审查、修正与规则执行",
  "A malformed or nonconforming Agent, output, or patch may be rejected or recorded as unsuccessful under these Rules.":
    "格式错误或不符合要求的 Agent、输出或补丁，可依据本规则被拒绝或记录为未成功。",
  "When an organizer-controlled infrastructure defect affects an evaluation, organizers may correct the defect and rerun the affected work under a documented procedure.":
    "当主办方控制的基础设施缺陷影响评测时，主办方可修正缺陷，并依据有记录的流程重新运行受影响任务。",
  "Organizers may request clarification or verification when an entry is unreproducible, incomplete, anomalous, or potentially noncompliant.":
    "当参赛项目无法复现、不完整、异常或可能不合规时，主办方可要求说明或核验。",
  "A result may be corrected, withheld, or removed when it cannot be verified or when the Team fails to provide required disclosure or reproducibility materials.":
    "如果结果无法核验，或团队未提供要求的披露和复现材料，主办方可更正、暂缓发布或移除结果。",
  "Deliberate hidden-answer use, build bypass, evaluator exploitation, credential abuse, false registration, or other serious misconduct may result in disqualification and removal from the leaderboard.":
    "故意使用隐藏答案、绕过构建、利用评测器、滥用凭据、虚假注册或其他严重不当行为，可能导致取消资格并从排行榜移除。",

  "10. Versioned rules and pending parameters": "10. 版本化规则与待公布参数",
  "Several operational values require pilot measurements and organizer approval. Before public evaluation opens, the organizers will publish and version the following:":
    "部分运行参数需要通过试运行测量并获得主办方批准。在公开评测开放前，主办方将发布并版本化以下内容：",
  "upload, Hosted Smoke Test, and Full Evaluation frequency limits;":
    "上传、Hosted Smoke Test 和 Full Evaluation 的频率限制；",
  "Case-level Agent and build timeouts, CPU, memory, storage, and build-feedback budgets;":
    "逐 Case 的 Agent 与构建超时、CPU、内存、存储和构建反馈预算；",
  "network access, external API, and organizer-managed credential policies;":
    "网络访问、外部 API 和主办方管理凭据的政策；",
  "the official scoring denominator, tie-breaker, feedback visibility, cancellation, rerun, and correction procedures; and":
    "正式评分分母、同分判定、反馈可见性、取消、重试和修正流程；以及",
  "any remaining eligibility, conflict-of-interest, or final-result verification procedures required by the ICSE Competition Track.":
    "ICSE Competition Track 要求的其他参赛资格、利益冲突或最终结果核验流程。",
  "Material updates will carry a version and publication date. The Timeline page governs competition dates, and the frozen version of these Rules governs official scoring.":
    "重要更新将注明版本和发布日期。竞赛日期以“时间安排”页面为准，正式评分以冻结版本规则为准。",

  "Rules contents": "规则目录",
  "Acceptance": "接受规则",
  "2. Teams": "2. 团队",
  "3. Agent submissions": "3. Agent 提交",
  "4. Data, models, and tools": "4. 数据、模型与工具",
  "7. Hidden evaluation": "7. 隐藏评测",
  "8. Disclosure": "8. 信息披露",
  "9. Enforcement": "9. 规则执行",
  "10. Versioned rules": "10. 版本化规则",
  "Next": "下一页",
  "Review the competition schedule": "查看竞赛时间安排",
});
