window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.submission = Object.freeze({
  "Agent Submission Guide | Build-Bench Challenge": "Agent 提交指南 | Build-Bench Challenge",
  "Agent submission guide for the Build-Bench Challenge, including package contents, runtime directories, build feedback, testing, and submission requirements.":
    "Build-Bench Challenge 的 Agent 提交指南，包括提交内容、运行目录、构建反馈、测试和提交要求。",
  "Agent submission": "Agent 提交",
  "Agent Submission Guide": "Agent 提交指南",
  "Submit a runnable Agent source bundle. The platform starts one isolated instance for each Case. The Agent modifies its worktree and may request a limited number of build-feedback runs. When the run ends, the platform creates the canonical":
    "提交一个可运行的 Agent 源码包。平台为每个 Case 启动一个独立实例。Agent 修改工作区，并可请求有限次数的构建反馈。运行结束后，平台生成 canonical",
  ", and the Docker Validator verifies it on a clean Case.": "，再由 Docker Validator 在干净的 Case 上完成验证。",
  "Submission guide navigation": "提交指南导航",
  "Competition": "竞赛",
  "Competition pages": "竞赛页面",
  "Data & Downloads": "数据与下载",
  "My Submissions": "我的提交",
  "Upload Agent": "上传 Agent",
  "On this page": "本页目录",
  "Quick start": "快速开始",
  "Submission contents": "提交内容",
  "Runtime interface": "运行接口",
  "Test your submission": "测试你的提交",
  "Submission requirements": "提交要求",
  "01 / Start": "01 / 开始",
  "Prepare and qualify one Agent version before requesting a full evaluation.":
    "在申请完整评测前，先准备并验证一个 Agent 版本。",
  "Run the official example first, then create, test, package, and upload your own Agent.":
    "先运行官方示例，再创建、测试、打包并上传你自己的 Agent。",
  "Submission preparation steps": "提交准备步骤",
  "Get the Starter Kit": "获取 Starter Kit",
  "Download the archive from": "从",
  ", extract it, and enter the project directory.": "下载安装包，解压后进入项目目录。",
  "Expected: the current directory contains": "预期结果：当前目录包含",
  ",": "、",
  "and": "以及",
  ".": "。",
  "Run the official demo": "运行官方示例",
  "Check Git, Docker, and the versioned images, then run the complete failure-to-success example.":
    "检查 Git、Docker 和固定版本镜像，然后运行完整的“失败到成功”示例。",
  "Expected:": "预期结果：",
  "; evidence is saved under": "；运行证据保存在",
  "Create your Agent": "创建你的 Agent",
  "Copy the managed Python template into a new editable Agent directory.":
    "将托管 Python 模板复制为一个新的可编辑 Agent 目录。",
  "Expected: a new Agent is created at": "预期结果：新的 Agent 创建在",
  "; existing directories are never overwritten.": "；已有目录不会被覆盖。",
  "Edit": "修改",
  "and test locally": "并在本地测试",
  "Implement the repair logic in": "在",
  ", then run every bundled Example Case.": "中实现修复逻辑，然后运行所有随附的 Example Case。",
  "Expected: per-Case patches, logs, and validation results are written under":
    "预期结果：每个 Case 的补丁、日志和验证结果写入",
  "Check and package": "检查并打包",
  "Validate the manifest, entrypoint, dependencies, and files before creating a deterministic upload bundle.":
    "创建确定性的上传包之前，检查清单、入口命令、依赖和文件。",
  "Expected: both checks pass and the command prints the ZIP path, size, and SHA-256.":
    "预期结果：两项检查均通过，命令输出 ZIP 路径、大小和 SHA-256。",
  "Upload the Agent bundle": "上传 Agent 包",
  "Open": "打开",
  ", choose": "，选择",
  ", and upload the generated ZIP.": "，然后上传生成的 ZIP。",
  "Expected: a new immutable Agent version appears in the submission table and enters the Checking state.":
    "预期结果：提交表格中出现一个新的不可变 Agent 版本，并进入“检查中”状态。",
  "Download the Starter Kit": "下载 Starter Kit",
  "Get the schemas, local Runner, example Case, and validation tools when released.":
    "发布后获取 Schema、本地 Runner、示例 Case 和验证工具。",
  "Implement your Agent": "实现 Agent",
  "Add the source code and declare one entrypoint in": "加入源码，并在",
  ".": "。",
  "Run local checks": "本地检查",
  "Check the ZIP structure, manifest, entrypoint, and directory permissions.":
    "检查 ZIP 结构、清单、入口命令和目录权限。",
  "Test an example Case": "测试示例 Case",
  "Run the Agent against a released development Case.": "在已发布的开发 Case 上运行 Agent。",
  "Run a Smoke Test": "进行 Smoke Test",
  "Use the hosted lightweight check before formal evaluation.": "在正式评测前使用平台提供的轻量检查。",
  "Start full evaluation": "开始完整评测",
  "Select a qualified version and place it in the evaluation queue.": "选择通过检查的版本并加入评测队列。",
  "02 / Package": "02 / 提交包",
  "Upload one ZIP archive with a shallow, inspectable root. The platform reads the manifest before building the Agent runtime.":
    "上传一个根目录简洁、便于检查的 ZIP 压缩包。平台在构建 Agent 运行环境前读取清单。",
  "archive root": "压缩包根目录",
  "and": "和",
  "Required.": "必需。",
  "Declare the runtime and include the Agent implementation.": "声明运行环境并包含 Agent 实现。",
  "Required when using the managed Python runtime.": "使用托管 Python 环境时必需。",
  "Include only when using a custom runtime.": "仅在使用自定义运行环境时包含。",
  "Optional local tests and method documentation.": "可选的本地测试和方法说明。",
  "Do not include secrets or evaluation answers.": "不得包含密钥或评测答案。",
  "Exclude": "请勿包含",
  "files, API keys, pre-generated patches, hidden Case information, caches, and runtime artifacts.":
    "文件、API Key、预生成补丁、隐藏 Case 信息、缓存和运行产物。",
  "Minimum": "最小",
  "The manifest declares how the platform builds and starts the Agent. The complete schema will be provided in the Starter Kit.":
    "清单声明平台如何构建和启动 Agent。完整 Schema 将在 Starter Kit 中提供。",
  "minimum managed-runtime example": "最小托管运行环境示例",
  "03 / Runtime": "03 / 运行环境",
  "Each Case starts in a fresh workspace. The original input remains unchanged while the Agent works on a writable copy.":
    "每个 Case 都从全新的工作区开始。原始输入保持不变，Agent 仅操作可写副本。",
  "Workspace": "工作区",
  "one Case run": "单次 Case 运行",
  "Read": "读取",
  "It contains the task metadata, initial failure evidence, and original package tree.":
    "其中包含任务元数据、初始失败证据和原始软件包目录。",
  "Modify only": "只修改",
  "This is the candidate package tree used for build requests.": "构建请求使用这里的候选软件包目录。",
  "Use stdout and stderr for logs.": "使用 stdout 和 stderr 输出日志。",
  "The platform captures both streams for diagnostics.": "平台采集两种输出用于诊断。",
  "Optionally write": "可选写入",
  "Place machine-readable completion details in": "将机器可读的完成信息写入",
  "Build feedback": "构建反馈",
  "When build feedback is enabled, the Agent requests a build through the platform-provided":
    "启用构建反馈后，Agent 通过平台提供的",
  "command. This planned CLI will be included in the Starter Kit.":
    "命令请求构建。该 CLI 计划随 Starter Kit 提供。",
  "Planned CLI example": "计划中的 CLI 示例",
  "not yet released": "尚未发布",
  "Build feedback flow": "构建反馈流程",
  "Build Gateway": "构建网关",
  "Docker Validator": "Docker Validator",
  "Status and log excerpt": "构建状态和日志片段",
  "The Agent does not receive the Docker Socket.": "Agent 不会获得 Docker Socket。",
  "The Agent does not start the Validator directly.": "Agent 不会直接启动 Validator。",
  "Build requests and per-build time are limited.": "构建次数和单次构建时间均受限制。",
  "The platform retains the complete build logs.": "完整构建日志由平台保存。",
  "Final patch": "最终补丁",
  "Canonical patch validation flow": "Canonical 补丁验证流程",
  "Original Case": "原始 Case",
  "Modified worktree": "修改后的工作区",
  "Canonical repair.diff": "Canonical repair.diff",
  "allowed_paths check": "allowed_paths 检查",
  "Official evaluation uses only the canonical diff generated by the platform.":
    "正式评测只使用平台生成的 canonical diff。",
  "The patch is reapplied to a clean Case before the final target build.":
    "最终目标架构构建前，平台会将补丁重新应用到干净的 Case。",
  "04 / Test": "04 / 测试",
  "Test the exact Agent version you intend to evaluate. Local checks catch packaging errors; the hosted Smoke Test checks that the same bundle can run under the competition protocol.":
    "请测试计划用于评测的同一个 Agent 版本。本地检查用于发现打包错误；平台 Smoke Test 用于确认同一提交包能够按照竞赛协议运行。",
  "Before full evaluation": "完整评测前",
  "Complete these checks in order before using a full-evaluation attempt:":
    "在使用一次完整评测机会前，请按顺序完成以下检查：",
  "Prepare the released tools.": "准备已发布的工具。",
  "Download the Starter Kit, schemas, and development Cases from":
    "从",
  "when they become available.": "下载发布后的 Starter Kit、Schema 和开发 Case。",
  "Run local conformance checks.": "运行本地合规检查。",
  "Validate the ZIP layout and": "检查 ZIP 结构与",
  ", then start the declared entrypoint in the local Runner.": "，然后在本地 Runner 中启动声明的入口命令。",
  "Exercise the runtime interface.": "验证运行接口。",
  "Run at least one example Case, edit only": "至少运行一个示例 Case，仅修改",
  ", and verify any": "，并检查",
  "output.": "输出（如有）。",
  "Pass a hosted Smoke Test.": "通过平台 Smoke Test。",
  "Upload the same Agent bundle from": "从",
  "and review the returned logs and diagnostics.": "上传同一 Agent 提交包，并检查返回的日志和诊断信息。",
  "Select the qualified version.": "选择合格版本。",
  "Start full evaluation explicitly; uploading a new version alone does not place it in the evaluation queue.":
    "需要显式启动完整评测；仅上传新版本不会自动进入评测队列。",
  "Testing locally": "本地测试",
  "Local testing should confirm that the submission contract works before organizer resources are used. Check all of the following:":
    "本地测试应在占用组织方资源前确认提交协议可以正常工作。请检查以下各项：",
  "The ZIP opens with": "ZIP 解压后应在根目录包含",
  "at its root.": "。",
  "The manifest matches the published Agent Schema and declares one valid entrypoint.":
    "清单符合已发布的 Agent Schema，并声明一个有效的入口命令。",
  "The entrypoint starts without interactive input and exits with a meaningful status.":
    "入口命令无需交互输入即可启动，并以有意义的状态退出。",
  "remains unchanged; repository edits are confined to":
    "保持不变；软件包修改仅发生在",
  "Optional": "可选的",
  "output matches the published result schema.": "输出符合已发布的结果 Schema。",
  "The Agent completes at least one released example or local Smoke Case.":
    "Agent 至少能够完成一个已发布的示例 Case 或本地 Smoke Case。",
  "The Starter Kit will provide the local Runner, conformance CLI, schemas, example Cases, and exact commands. These downloads are not yet published.":
    "Starter Kit 将提供本地 Runner、合规检查 CLI、Schema、示例 Case 和准确命令。这些下载资源尚未发布。",
  "Smoke tests": "Smoke Test",
  "A hosted Smoke Test uses the same Agent Runner, workspace layout, build-feedback protocol, and status schema as formal evaluation, but runs only a small set of lightweight public Cases. It is intended to expose missing dependencies, invalid entrypoints, permission errors, and malformed output before a full evaluation.":
    "平台 Smoke Test 使用与正式评测相同的 Agent Runner、工作区布局、构建反馈协议和状态 Schema，但只运行少量轻量级公开 Case，用于在完整评测前发现依赖缺失、入口命令无效、权限错误和输出格式错误。",
  "Smoke Test results include more detailed logs and diagnostics than the leaderboard. They do not contribute to the official score, and passing a Smoke Test does not guarantee success on the full Case set.":
    "Smoke Test 会提供比排行榜更详细的日志和诊断信息，其结果不计入正式成绩；通过 Smoke Test 也不代表能够在完整 Case 集上成功。",
  "Full evaluation": "完整评测",
  "Uploading an Agent creates a versioned submission but does not automatically start full evaluation. After that version passes format checks and the required Smoke Test, select it in":
    "上传 Agent 会创建一个带版本的提交，但不会自动启动完整评测。该版本通过格式检查和必要的 Smoke Test 后，请在",
  "and choose": "中选择该版本并点击",
  ". The platform then creates one isolated Agent job per Case and schedules jobs subject to the published resource policy.":
    "。平台随后为每个 Case 创建一个隔离的 Agent 任务，并按照已发布的资源策略进行调度。",
  "For each Case, the platform records the Agent outcome separately from the final Docker Validator outcome. Only the canonical patch generated from the Agent's worktree is reapplied to a clean Case for the official target-architecture build.":
    "对于每个 Case，平台分别记录 Agent 运行结果和最终 Docker Validator 结果。正式目标架构构建只会将 Agent 工作区生成的 canonical patch 重新应用到干净 Case。",
  "Start evaluation": "开始评测",
  "05 / Requirements": "05 / 要求",
  "A submission must be reproducible, non-interactive, and safe to run against organizer-controlled Cases. Requirements that are still under infrastructure review are marked":
    "提交必须可复现、无需交互，并能安全地在组织方管理的 Case 上运行。仍在进行基础设施评审的要求标记为",
  "Key requirements checklist": "关键要求清单",
  "Submit one source ZIP containing the required": "提交一个源码 ZIP，其中必须包含",
  "entries.": "。",
  "Declare one runtime: managed Python 3.11 with":
    "声明一种运行环境：使用",
  ", or a custom runtime with a platform-reviewed": "的托管 Python 3.11，或使用由平台审核的",
  "Provide a deterministic, non-interactive entrypoint that can process one Case per invocation.":
    "提供确定性、无需交互的入口命令，每次调用处理一个 Case。",
  "Do not include": "不得包含",
  "files, credentials, API keys, pre-generated repair patches, hidden Case information, dependency caches, or previous run artifacts.":
    "文件、凭据、API Key、预生成修复补丁、隐藏 Case 信息、依赖缓存或以往运行产物。",
  "Read task metadata and the original package only from":
    "任务元数据和原始软件包只能从",
  "; make all proposed repairs in": "读取；所有拟议修复都应在",
  "Do not modify evaluator files or paths outside the Case's published":
    "不得修改评测器文件或 Case 已发布",
  "Only optional machine-readable status and diagnostics may be written to":
    "仅可向",
  ". The official": "写入可选的机器可读状态和诊断信息。正式",
  "is generated by the platform, not the Agent.": "由平台生成，而不是由 Agent 生成。",
  "Runtime and security": "运行环境与安全",
  "The Agent runs as a non-root user in an isolated runtime created for one Case.":
    "Agent 以非 root 用户身份，在为单个 Case 创建的隔离运行环境中执行。",
  "is mounted read-only; only the work and output directories are writable.":
    "以只读方式挂载；只有工作目录和输出目录可写。",
  "The Docker Socket and Docker daemon are never exposed to the Agent.":
    "Agent 无法访问 Docker Socket 或 Docker daemon。",
  "Build feedback is requested through the platform-provided":
    "构建反馈通过平台提供的",
  "command and Build Gateway. The Docker Validator remains organizer-controlled.":
    "命令和 Build Gateway 请求，Docker Validator 始终由组织方控制。",
  "The platform captures stdout, stderr, exit status, wall time, and build requests for diagnosis and audit.":
    "平台采集 stdout、stderr、退出状态、运行时长和构建请求，用于诊断与审计。",
  "Network policy, per-Case wall-time limit, maximum build requests, CPU, memory, and storage limits are":
    "网络策略、单 Case 运行时长、最大构建请求次数、CPU、内存和存储限制均为",
  "Dependencies and custom runtime": "依赖与自定义运行环境",
  "For the managed runtime, declare Python dependencies in":
    "使用托管运行环境时，请在",
  ". The competition will publish the exact Python 3.11 base environment and supported installation process with the Starter Kit. Undeclared host packages must not be assumed.":
    "中声明 Python 依赖。竞赛将随 Starter Kit 发布准确的 Python 3.11 基础环境和支持的安装流程；不得假设宿主机提供未声明的软件包。",
  "A custom": "自定义",
  "is optional for Agents that cannot use the managed runtime. The platform will inspect it, build an immutable image, record its digest, and run it under the same non-root, filesystem, network, and resource policies as managed submissions.":
    "适用于无法使用托管运行环境的 Agent，可选提供。平台会对其进行检查，构建不可变镜像并记录摘要，然后按照与托管提交相同的非 root、文件系统、网络和资源策略运行。",
  "Supported base images, package-installation rules, network access during image construction and execution, maximum ZIP size, and submission frequency are":
    "支持的基础镜像、软件包安装规则、镜像构建与运行期间的网络访问、ZIP 大小上限和提交频率均为",
  ". Final values will be published before submissions open.":
    "。最终数值将在提交入口开放前发布。",
  "Next page": "下一页",
  "Next": "下一页",
  "See the competition resources and release status": "查看竞赛资源及其发布状态",
  "Build-Bench Challenge": "Build-Bench Challenge",
});
