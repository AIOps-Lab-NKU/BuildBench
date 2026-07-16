window.BuildBenchI18nData = window.BuildBenchI18nData || { pages: {} };
window.BuildBenchI18nData.pages.rules = Object.freeze({
    "Participation, integrity, disclosure, and reproducibility rules for the Build-Bench Challenge.":
      "Build-Bench Challenge 的参赛、诚信、披露与可复现性规则。",
    "Rules | Build-Bench Challenge": "规则 | Build-Bench Challenge",
    "Rules preview": "规则预览",
    "Integrity principles come from the accepted proposal; operational thresholds remain TBA.":
      "诚信原则沿用获批提案，具体执行阈值仍待确定。",
    "Competition policy": "竞赛政策",
    "Build real repairs, disclose the system that produced them, preserve the evaluator, and make final results reproducible under organizer control.":
      "实现真实有效的修复，披露生成修复的系统，确保评测器完整，并使最终结果能在主办方控制的环境中复现。",
    "Primary focus": "主要关注",
    "LLM-based repair Agents": "基于 LLM 的修复 Agent",
    "Final validation": "最终验证",
    "Organizer audit and rerun": "主办方审核并重新运行",
    "Thresholds": "阈值",
    "Published before launch": "将在启动前公布",
    "On this page": "本页内容",
    "Eligibility": "参赛资格",
    "Disclosure": "信息披露",
    "Allowed work": "允许的操作",
    "Prohibited conduct": "禁止行为",
    "Resources": "资源",
    "Hidden evaluation": "隐藏评测",
    "Enforcement": "规则执行",
    "Notice": "注意",
    "The versioned rulebook released with the starter kit will supersede this preview.":
      "随入门套件发布的版本化规则手册将取代本预览内容。",
    "This page preserves the accepted proposal's integrity principles while avoiding unconfirmed limits. Team size, submission frequency, API allowlists, and exact resource budgets will be added after organizer approval.":
      "本页保留获批提案中的诚信原则，但不列出尚未确认的限制。团队规模、提交频率、API 允许列表和具体资源预算将在主办方批准后补充。",
    "Eligibility and entry": "参赛资格与报名",
    "Who the competition is designed for": "本竞赛面向哪些参赛者",
    "The primary leaderboard is intended for LLM-based and agentic repair systems from academic, industry, and independent teams. Registration rules, team-size limits, affiliation restrictions, and conflict-of-interest procedures will follow the official ICSE Competition Track requirements and the released rulebook.":
      "主排行榜面向来自学术界、工业界和独立团队的 LLM 及 Agent 修复系统。报名规则、团队人数限制、单位限制和利益冲突处理流程将遵循 ICSE Competition Track 官方要求及发布的规则手册。",
    "One team, one declared entry": "每支团队仅可申报一个参赛项目",
    "Final registration and team-composition rules are TBA.": "最终报名和团队组成规则待定。",
    "Agent-focused ranking": "以 Agent 为核心的排名",
    "Non-LLM systems may appear as clearly labeled comparison baselines, subject to final policy.":
      "非 LLM 系统可作为明确标注的对比基线展示，具体以最终政策为准。",
    "Valid final run required": "必须完成有效的最终运行",
    "A team must submit a conforming Agent and complete organizer-run evaluation to receive a final result.":
      "团队必须提交符合要求的 Agent，并完成由主办方运行的评测，才能获得最终成绩。",
    "Method disclosure": "方法披露",
    "Describe what the Agent actually uses": "说明 Agent 实际使用的内容",
    "Each final entry must disclose enough information for organizers to understand and rerun the method without revealing hidden evaluator data.":
      "每个最终参赛项目必须披露足够的信息，使主办方能在不泄露隐藏评测数据的前提下理解并重新运行该方法。",
    "Base model names and exact versions when available": "基础模型名称，以及可获取时的准确版本",
    "Major prompts, retrieval sources, external tools, static analyzers, and repair-loop design":
      "主要提示词、检索来源、外部工具、静态分析器和修复循环设计",
    "Training, fine-tuning, external knowledge bases, or private data used for the entry":
      "参赛项目使用的训练、微调、外部知识库或私有数据",
    "Third-party APIs and services contacted during Agent execution": "Agent 运行期间调用的第三方 API 和服务",
    "Known nondeterminism, caching, preprocessing, and reproducibility constraints":
      "已知的非确定性、缓存、预处理和可复现性限制",
    "Repair package content through the official interface": "通过官方接口修复软件包内容",
    "Reason over all released case evidence": "综合分析所有已发布 Case 的证据",
    "Specifications, sources, patches, logs, scripts, metadata, and architecture labels.":
      "spec 文件、源代码、补丁、日志、脚本、元数据和架构标签。",
    "Use an internal toolchain": "使用内部工具链",
    "Prompting, retrieval, code search, static analysis, log parsing, and iterative Agent loops.":
      "提示、检索、代码搜索、静态分析、日志解析和迭代式 Agent 循环。",
    "Modify permitted package paths": "修改允许变更的软件包路径",
    "Specifications, build scripts, source code, tests, packaging macros, and related package files.":
      "spec 文件、构建脚本、源代码、测试、打包宏及相关软件包文件。",
    "Return a different valid repair": "返回不同但有效的修复",
    "Repairs need not match an organizer reference patch when they pass policy and executable validation.":
      "只要修复符合规则并通过实际构建验证，就不必与主办方的参考补丁一致。",
    "Do not bypass the task or evaluator": "不得绕过任务或评测器",
    "Hard-code hidden solutions": "硬编码隐藏解法",
    "No embedded hidden patches, case-specific answers, leaked labels, or lookup tables.":
      "不得嵌入隐藏补丁、特定 Case 答案、泄露的标签或查找表。",
    "Exploit evaluator bugs": "利用评测器漏洞",
    "No attempts to escape isolation, alter evaluator metadata, spoof results, or rely on unintended validator behavior.":
      "不得尝试逃逸隔离环境、修改评测器元数据、伪造结果或依赖验证器的非预期行为。",
    "Disable meaningful validation": "破坏有效验证",
    "No deleting essential tests, bypassing the build, or suppressing failures without a legitimate repair.":
      "不得删除必要测试、绕过构建，或在没有合理修复的情况下掩盖失败。",
    "Replace the package with a dummy artifact": "用无效产物替换软件包",
    "The repaired output must remain the intended package and preserve its meaningful functionality.":
      "修复后的输出必须仍是目标软件包，并保留其实际功能。",
    "Modify forbidden paths": "修改禁止变更的路径",
    "Case manifests, checksums, hidden metadata, evaluator files, and other immutable inputs must remain unchanged.":
      "Case 清单、校验和、隐藏元数据、评测器文件及其他不可变输入必须保持不变。",
    "Use undeclared manual intervention": "使用未披露的人工干预",
    "Organizer-run cases must be processed by the submitted Agent under the announced interface and policy.":
      "由主办方运行的 Case 必须由提交的 Agent 按照公布的接口和政策处理。",
    "Models, network, and secrets": "模型、网络与密钥",
    "Do not assume unrestricted external access": "不要假定可以不受限制地访问外部资源",
    "The unified Agent model requires an explicit policy for model APIs and network access. That policy is not final. The release will state whether calls are disabled, allowlisted, or brokered through organizer-managed APIs.":
      "统一 Agent 模式需要明确规定模型 API 和网络访问政策。该政策尚未最终确定。正式发布时将说明外部调用是被禁用、仅限允许列表，还是通过主办方管理的 API 代理。",
    "Participants must never embed production API keys or personal credentials in submitted artifacts. Secret injection, logging, accounting, and redaction will be defined by the official platform.":
      "参赛者不得在提交产物中嵌入生产环境 API 密钥或个人凭据。密钥注入、日志记录、用量统计和脱敏方式将由官方平台规定。",
    "Held-out cases stay under organizer control": "保留 Case 由主办方管理",
    "The hidden test set will not be distributed before final evaluation.": "隐藏测试集不会在最终评测前发布。",
    "Final Agents run with a frozen interface, evaluator version, and resource policy.":
      "最终 Agent 将在接口、评测器版本和资源政策均冻结的条件下运行。",
    "Only aggregate results and limited diagnostic categories will be released after the deadline.":
      "截止日期后仅发布汇总结果和有限的诊断类别。",
    "Organizers may inspect successful, unusually small, suspicious, or policy-sensitive repairs.":
      "主办方可检查成功的、异常小的、可疑的或涉及政策边界的修复。",
    "Entries affected by an evaluator defect may be rerun under a documented correction policy.":
      "受评测器缺陷影响的参赛项目，可依据有记录的修正政策重新运行。",
    "Audit and enforcement": "审核与规则执行",
    "Results must survive review and rerun": "结果必须通过审查与重新运行",
    "Organizers may request source, logs, configuration, method documentation, or a reproducible artifact for finalist verification. A result may be corrected, removed, or disqualified when it cannot be reproduced or violates the released rules.":
      "为核验决赛入围者，主办方可要求提供源代码、日志、配置、方法文档或可复现产物。如果结果无法复现或违反已发布规则，主办方可更正或移除该结果，也可取消参赛资格。",
    "Scrollable enforcement action table": "可滚动的规则处置表",
    "Situation": "情形",
    "Potential action": "可能采取的措施",
    "Malformed or nonconforming Agent output": "Agent 输出格式错误或不符合要求",
    "Case failure or invalid submission under the final scoring policy":
      "根据最终评分政策判定该 Case 失败或提交无效",
    "Accidental evaluator defect": "非故意的评测器缺陷",
    "Announced fix and affected-entry rerun where feasible": "公布修复，并在可行时重新运行受影响的参赛项目",
    "Undeclared dependency or unreproducible finalist": "存在未披露依赖，或决赛入围结果无法复现",
    "Request clarification, corrected artifact, or result removal": "要求说明情况、提交修正产物或移除结果",
    "Build bypass, hidden-answer leakage, or sandbox abuse": "绕过构建、泄露隐藏答案或滥用沙箱",
    "Disqualification and removal from the leaderboard": "取消参赛资格并从排行榜中移除",
    "Next": "下一页",
    "Review the proposed competition schedule": "查看拟定的竞赛时间安排",
});
