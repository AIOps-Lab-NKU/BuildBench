window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.submission = Object.freeze({
  "Agent Submission Guide | Build-Bench Challenge": "Agent 提交指南 | Build-Bench Challenge",
  "Agent submission guide for the Build-Bench Challenge, including package contents, runtime directories, build feedback, testing, and submission requirements.":
    "Build-Bench Challenge 的 Agent 提交指南，包括提交内容、运行目录、构建反馈、测试和提交要求。",
  "Agent submission": "Agent 提交",
  "Agent Submission Guide": "Agent 提交指南",
  "Submit a runnable Agent source bundle, not Case-specific answers or pre-generated patches. The platform starts one isolated instance for each Case. The Agent modifies its worktree and may request a limited number of build-feedback runs. When the run ends, the platform creates the canonical":
    "提交一个可运行的 Agent 源码包，而不是针对特定 Case 的答案或预先生成的补丁。平台为每个 Case 启动一个独立实例。Agent 修改工作区，并可请求有限次数的构建反馈。运行结束后，平台生成 canonical",
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
  "Before using a full-evaluation attempt, run the Starter Kit checks locally, confirm the Agent can process an Example Case through the published workspace interface, package that exact version, and pass its hosted Smoke Test. Start full evaluation only after selecting the qualified version in My Submissions; uploading a new version alone does not place it in the evaluation queue.":
    "在使用完整评测机会前，请先在本地运行 Starter Kit 检查，确认 Agent 能通过已发布的工作区接口处理一个 Example Case，打包该确切版本，并通过平台 Hosted Smoke Test。只有在“我的提交”中选择已通过的版本后才启动完整评测；仅上传新版本不会使其进入评测队列。",
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
  "Before you begin": "开始前准备",
  "The Starter Kit is designed for a Linux shell. The commands below have been verified on Ubuntu and WSL2; use Docker Desktop with Linux containers when working through WSL2.":
    "Starter Kit 面向 Linux Shell 设计。以下命令已在 Ubuntu 和 WSL2 中验证；通过 WSL2 使用时，请启用 Docker Desktop 的 Linux 容器。",
  "Local prerequisites": "本地运行前提",
  "Item": "项目",
  "What you need": "需要准备",
  "Host tools": "宿主机工具",
  "Git and Docker Engine 24+, or Docker Desktop with Linux containers enabled.":
    "Git 和 Docker Engine 24+，或已启用 Linux 容器的 Docker Desktop。",
  "Host packages": "宿主机软件包",
  "Python, RPM tooling,": "Python、RPM 工具和",
  ", compilers, and Case dependencies are not installed on the host; versioned containers provide them.":
    "、编译器及 Case 依赖无需安装到宿主机；这些内容由固定版本容器提供。",
  "Network": "网络",
  "Initial setup needs access to the GitHub release and the published container registry or organizer mirror. Agent runtime network policy is":
    "首次准备需要访问 GitHub Release，以及已发布的容器镜像仓库或组织方镜像源。Agent 运行时网络策略为",
  "TBA": "待公布",
  "CPU, memory, and disk": "CPU、内存与磁盘",
  "Minimum and recommended local resources are": "本地最低和推荐资源配置为",
  ". Formal evaluation quotas are published separately and may differ from your local machine.":
    "。正式评测资源配额将另行发布，可能与本地机器配置不同。",
  "Credentials": "凭据",
  "Do not place model API keys in the Agent directory or ZIP. The platform credential-injection policy is":
    "不要把模型 API Key 放入 Agent 目录或 ZIP。平台凭据注入策略为",
  "Check": "检查",
  "verifies required commands, Docker access, host architecture, and runtime-image availability. It does not certify that your machine meets the final competition resource limits.":
    "会检查必要命令、Docker 访问、宿主机架构和运行镜像可用性，但不会判定机器是否满足最终竞赛资源限制。",
  "Download the current ZIP from": "从",
  ", extract it in a Linux or WSL2 shell, and enter the versioned directory.":
    "下载当前 ZIP，在 Linux 或 WSL2 Shell 中解压，并进入带版本号的目录。",
  "Configure": "配置",
  "No project configuration is required at this step. Keep the entire extracted directory together.":
    "此步骤不需要项目配置，请保持解压后的整个目录结构完整。",
  "Verify": "确认",
  "Run": "运行",
  "; all later": "；后续所有",
  "commands must be executed from this directory.": "命令都必须在该目录中执行。",
  ", and": "和",
  "Use the image references pinned by the release. If the organizer provides a registry mirror, set":
    "默认使用该版本固定的镜像引用。如果组织方提供镜像源，请先设置",
  "before running": "，再运行",
  "What it runs": "执行内容",
  "performs environment checks only.": "只执行环境检查。",
  "uses the official Example Agent and the self-contained": "使用官方 Example Agent 和自包含的",
  "Case; it does not use your Agent code.": "Case，不会使用你编写的 Agent 代码。",
  "Argument": "参数",
  "becomes both the directory name and default": "既是目录名，也是默认的",
  ". Use 2–64 lowercase letters, digits, or hyphens.": "。请使用 2–64 个小写字母、数字或连字符。",
  "Edit repair logic under": "在",
  ", pin Python dependencies with": "中编写修复逻辑；在",
  ", and change name, version, or entrypoint in": "中使用固定版本依赖；名称、版本或入口命令在",
  "Input": "输入",
  "must point to the Agent directory that contains": "必须指向包含",
  ". The command runs each ID listed in": "的 Agent 目录。该命令会运行",
  "; release": "中列出的每个 ID；版本",
  "contains one local Example Case,": "包含 1 个本地 Example Case：",
  "Agent behavior": "Agent 行为",
  "The entrypoint declared in": "在",
  "runs once per Case. It reads": "中声明的入口会为每个 Case 运行一次。它读取",
  ", edits": "，修改",
  ", and writes": "，并写入",
  "Rejects missing required files, unsupported manifest fields, invalid entrypoints, unpinned dependencies, generated outputs, caches, symbolic links, and likely credentials.":
    "检查并拒绝缺失必需文件、不支持的清单字段、无效入口、未固定依赖、生成产物、缓存、符号链接和疑似凭据。",
  "Package": "打包",
  "Writes": "默认生成",
  "by default. Use": "。仅在需要不同本地文件名时使用",
  "only when you need a different local filename.": "。",
  "Make new submission": "创建新提交",
  "Upload": "上传",
  "Select the ZIP produced by": "请选择由",
  ", not the whole Starter Kit directory and not a ZIP you assembled manually.":
    "生成的 ZIP，不要上传整个 Starter Kit 目录，也不要手工重新组装 ZIP。",
  "After upload": "上传后",
  "The platform stores an immutable Agent version, performs static checks, and then runs the hosted Smoke Test. Full evaluation starts only after you explicitly select a qualified version.":
    "平台保存不可变的 Agent 版本，执行静态检查，然后运行平台 Smoke Test。只有显式选择已通过的版本后，才会开始完整评测。",
  "Cases used during development and evaluation": "开发与评测使用的 Case",
  "Case sets are versioned separately from the Agent submission format. Counts that have not yet been frozen remain placeholders and will be published with the corresponding dataset release.":
    "Case 集与 Agent 提交格式分别进行版本管理。尚未冻结的数量保留为占位符，并随对应数据集版本发布。",
  "Case set": "Case 集",
  "Purpose": "用途",
  "Current scope": "当前范围",
  "Local Example Cases": "本地 Example Case",
  "Verify the Starter Kit, Agent entrypoint, workspace protocol, patch generation, and local Validator path.":
    "验证 Starter Kit、Agent 入口、工作区协议、补丁生成和本地 Validator 链路。",
  "1 public Case:": "1 个公开 Case：",
  "Development Cases": "开发 Case",
  "Public Cases for Agent development and broader local experiments.":
    "用于 Agent 开发和更广泛本地实验的公开 Case。",
  "Count TBA": "数量待公布",
  "Hosted Smoke Cases": "平台 Smoke Case",
  "A lightweight hosted subset used to qualify an uploaded Agent version.":
    "用于验证上传 Agent 版本的轻量级平台子集。",
  "Full Evaluation Cases": "完整评测 Case",
  "Organizer-controlled Cases used for formal scoring.": "由组织方控制、用于正式计分的 Case。",
  "Scope": "范围",
  "The original Build-Bench benchmark is the source of competition candidates; its historical total must not be read as the final competition Case count. Final set sizes and versions will be announced on":
    "原始 Build-Bench benchmark 是竞赛候选 Case 的来源；其历史总数不等于最终竞赛 Case 数量。最终集合规模和版本将在",
  "agent-submission.zip": "agent-submission.zip",
  "Declares Agent identity, managed runtime, entrypoint, and protocol version.":
    "声明 Agent 身份、托管运行环境、入口命令和协议版本。",
  "Contains the Agent implementation and the declared Python module or script.":
    "包含 Agent 实现以及已声明的 Python 模块或脚本。",
  "Declare every third-party Python dependency with an exact": "每个第三方 Python 依赖都必须使用精确的",
  "version.": "版本。",
  "Required in v0.1.": "v0.1 中必需。",
  "Describes how the Agent works and any participant-facing notes.":
    "说明 Agent 的工作方式及参赛者需要了解的事项。",
  "The manifest declares how the platform builds and starts the Agent. Version":
    "该清单声明平台如何构建并启动 Agent。版本",
  "supports the managed Python 3.11 profile; the Starter Kit validates this exact contract before packaging.":
    "支持托管 Python 3.11 配置；Starter Kit 会在打包前验证这一准确协议。",
  "agent.yaml": "agent.yaml",
  "Execution contract": "执行协议",
  "Agent execution contract": "Agent 执行协议",
  "Invocation": "调用方式",
  "The platform starts the": "平台按照",
  "list from": "中的",
  "once for each Case, with the Agent bundle as the process working directory.":
    "列表为每个 Case 启动一次进程，并将 Agent 包目录作为进程工作目录。",
  "Workspace variable": "工作区变量",
  ". Resolve all Case input, worktree, and structured output paths from this root.":
    "。所有 Case 输入、工作树和结构化输出路径都应从该根目录解析。",
  "Completion": "完成条件",
  "For the current v0.1 local protocol, exit with code": "在当前 v0.1 本地协议中，应以退出码",
  "and write": "结束，并写入",
  "with": "，其中",
  ". A non-zero exit is an Agent error.": "。非零退出码会被判定为 Agent 错误。",
  "Diagnostics": "诊断信息",
  "Write human-readable progress to stdout or stderr. Do not place secrets in logs; both streams are retained by the platform.":
    "将便于阅读的进度写入 stdout 或 stderr。不要在日志中输出密钥；平台会保留这两个输出流。",
  "Repair result": "修复结果",
  "Do not submit a pre-generated patch. Modify only the writable worktree; the platform creates the canonical":
    "不要提交预先生成的补丁。只能修改可写工作树；Agent 退出后，平台会生成 canonical",
  "after the Agent exits.": "。",
  "/workspace": "/workspace",
  "Write": "写入",
  "Place machine-readable completion status and diagnostics in": "将机器可读的完成状态和诊断信息写入",
  "output/agent-result.json": "output/agent-result.json",
  "minimal successful result": "最小成功结果",
  "The hosted evaluation design lets an Agent request bounded build feedback through the platform-provided":
    "平台评测设计允许 Agent 通过平台提供的",
  "command. This command is not included in Starter Kit": "命令请求有限次数的构建反馈。Starter Kit",
  "; its request/response schema, limits, and release version remain":
    "尚未包含该命令；其请求/响应 Schema、限制和发布版本均为",
  "Agent": "Agent",
  "bb-build": "bb-build",
  "Download the Starter Kit from": "从",
  ". Add versioned Development Cases when their public release becomes available.":
    "下载 Starter Kit；Development Case 公开发布后，再加入对应的版本化数据。",
  "Run at least one Example Case, edit only": "至少运行一个 Example Case，只修改",
  ", and verify the required": "，并验证必需的",
  "The manifest passes": "清单通过",
  "and declares one valid managed-Python entrypoint.": "，并声明一个有效的托管 Python 入口。",
  "The entrypoint starts without interactive input, writes the required structured result, and exits with code":
    "入口命令无需交互输入即可启动，写出必需的结构化结果，并在正常完成时以退出码",
  "when it completes normally.": "退出。",
  "contains": "包含",
  "and a supported status.": "以及受支持的状态。",
  "The Agent completes at least one released local Example Case.":
    "Agent 至少能够完成一个已发布的本地 Example Case。",
  "Released": "已发布",
  "Starter Kit": "Starter Kit",
  "provides the local Runner, managed-Python template, one": "提供本地 Runner、托管 Python 模板、1 个",
  "Example Case, conformance checks, and deterministic packaging. Development Cases and standalone protocol schemas remain on the release roadmap.":
    "Example Case、合规检查和确定性打包。Development Case 和独立协议 Schema 仍在后续发布计划中。",
  "Version": "版本",
  "accepts the managed Python 3.11 runtime only. Custom Docker runtimes are not accepted in this release.":
    "仅接受托管 Python 3.11 运行环境。本版本不接受自定义 Docker 运行环境。",
  "Write the required machine-readable completion result to":
    "将必需的机器可读完成结果写入",
  "When the hosted build-feedback protocol is released, requests will go through":
    "平台构建反馈协议发布后，请求将通过",
  "and the Build Gateway. The Docker Validator remains organizer-controlled.":
    "和 Build Gateway 处理。Docker Validator 始终由组织方控制。",
  "Dependencies and managed runtime": "依赖与托管运行环境",
  "Declare every third-party Python dependency in": "在",
  "with an exact": "中为每个第三方 Python 依赖声明精确的",
  "version. Direct URLs, Git references, editable installs, local paths, and unpinned requirements are rejected by":
    "版本。直接 URL、Git 引用、可编辑安装、本地路径和未固定版本的依赖都会被",
  ". Undeclared host packages must not be assumed.": "拒绝。不得假设宿主机提供未声明的软件包。",
  "Custom": "自定义",
  "submissions are deferred beyond protocol": "提交延后到协议",
  ". If introduced later, their supported base images and image-build policy will be released as a new submission-protocol version rather than silently changing the current contract.":
    "之后。如果后续引入，将通过新的提交协议版本发布受支持的基础镜像和镜像构建策略，而不会静默修改当前协议。",
  "Agent runtime network access, model credential injection, maximum ZIP size, submission frequency, and formal CPU, memory, storage, wall-time, and build-request limits are":
    "Agent 运行时网络访问、模型凭据注入、ZIP 大小上限、提交频率，以及正式评测的 CPU、内存、存储、运行时长和构建请求限制均为",
  "You need a Linux or WSL2 shell, Git, and Docker Engine 24+ or Docker Desktop with Linux containers. Run":
    "你需要 Linux 或 WSL2 Shell、Git，以及 Docker Engine 24+ 或使用 Linux 容器的 Docker Desktop。下载 Starter Kit 后运行",
  "after downloading the Starter Kit to verify the local setup.":
    "，以检查本地环境。",
  "Different versioned Case sets are used for local examples, development, hosted Smoke Tests, and Full Evaluation. See":
    "本地示例、开发、平台 Smoke Test 和完整评测使用不同的版本化 Case 集。请查看",
  "for their scope and release status.": "，了解各 Case 集的范围和发布状态。",
  "Planned feature.": "计划功能。",
  "Bounded hosted build feedback will be introduced in a later protocol release. Its CLI, limits, and response schema are not part of Starter Kit":
    "受限的平台构建反馈将在后续协议版本中引入。其 CLI、限制和响应 Schema 不属于 Starter Kit",
  "Canonical patch": "Canonical 补丁",
  "The platform derives the canonical patch from the modified worktree. How that patch is checked and rebuilt is defined in the":
    "平台根据修改后的工作树生成 canonical 补丁。该补丁的检查和重新构建方式由",
  "Evaluation Protocol": "评测协议",
  "Before spending a Full Evaluation attempt, run": "在使用一次完整评测机会前，请运行",
  ", test the Agent on all released Example Cases, package that exact version, upload it, and pass the Hosted Smoke Test. Full Evaluation begins only after you explicitly select the qualified immutable version.":
    "，在所有已发布的 Example Case 上测试 Agent，打包并上传这个确切版本，再通过平台 Smoke Test。只有显式选择已通过的不可变版本后，完整评测才会开始。",
  "Use this checklist on the exact immutable Agent version that you intend to upload and evaluate.":
    "请对准备上传和评测的确切不可变 Agent 版本逐项检查。",
  "Final submission checklist": "最终提交清单",
  "Required files exist at the ZIP root.": "必需文件位于 ZIP 根目录。",
  "passes.": "检查通过。",
  "The entrypoint is deterministic and non-interactive.": "入口命令是确定性的，且不需要交互输入。",
  "All dependencies are exactly pinned.": "所有依赖均已精确锁定版本。",
  "No secrets, caches, generated patches, or run artifacts are included.":
    "提交中不包含密钥、缓存、预生成补丁或运行产物。",
  "Only": "仅修改",
  "is modified.": "。",
  "follows protocol": "遵循协议",
  "The uploaded version passes the Hosted Smoke Test.": "上传的版本通过平台 Smoke Test。",
  "The intended immutable version is selected for Full Evaluation.": "已选择预期的不可变版本用于完整评测。",
  "Runtime and policy": "运行环境与政策",
  "The Agent runs as a non-root user in an isolated runtime,": "Agent 以非 root 用户身份在隔离环境中运行，",
  "is read-only, and the Docker Socket is not provided. Remaining network, resource, quota, and submission policies will be published before submissions open.":
    "为只读目录，且不提供 Docker Socket。其余网络、资源、配额和提交政策将在提交开放前公布。",
  "Next page": "下一页",
  "Next": "下一页",
  "See the competition resources and release status": "查看竞赛资源及其发布状态",
  "Build-Bench Challenge": "Build-Bench Challenge",
});
