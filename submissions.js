(function () {
  "use strict";

  const uploadInput = document.querySelector("[data-agent-upload]");
  const uploadButton = document.querySelector("[data-upload-button]");
  const notice = document.querySelector("[data-submission-notice]");
  const versionList = document.querySelector("[data-agent-versions-list]");
  const fullList = document.querySelector("[data-full-evaluations-list]");
  const versionCount = document.querySelector("[data-agent-version-count]");
  const fullCount = document.querySelector("[data-full-count]");
  const fullUsed = document.querySelector("[data-full-used]");
  const bestScore = document.querySelector("[data-best-score]");
  const bestScoreNote = document.querySelector("[data-best-score-note]");
  const logModal = document.querySelector("[data-log-modal]");
  const logStatus = document.querySelector("[data-log-status]");
  const logAgent = document.querySelector("[data-log-agent]");
  const logId = document.querySelector("[data-log-id]");
  const logContent = document.querySelector("[data-log-content]");
  const logError = document.querySelector("[data-log-error]");
  const logDownload = document.querySelector("[data-log-download]");
  const evaluationModal = document.querySelector("[data-evaluation-confirm]");
  const evaluationConfirmAgent = document.querySelector("[data-evaluation-confirm-agent]");
  const evaluationConfirmId = document.querySelector("[data-evaluation-confirm-id]");
  const evaluationConfirmError = document.querySelector("[data-evaluation-confirm-error]");
  const evaluationConfirmButton = document.querySelector("[data-evaluation-confirm-action]");

  const ACTIVE_SUBMISSION = new Set(["checking", "smoke_queued", "smoke_running"]);
  const ACTIVE_EVALUATION = new Set(["queued", "preparing", "evaluating", "finalizing"]);
  const RETRYABLE = new Set(["qualified", "smoke_failed", "infrastructure_error"]);
  const PAGE_SIZE = 6;
  let currentPage = 1;
  let submissions = [];
  let evaluations = [];
  let evaluationReadiness = {
    enabled: false,
    ready: false,
    message: "Full Evaluation is not available yet.",
  };
  let pendingEvaluationSubmissionId = null;
  let pollTimer = null;

  function t(value) {
    return window.BuildBenchI18n?.t(value) || value;
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function publicStatus(item) {
    if (item.status === "checking") return "Checking";
    if (["smoke_queued", "smoke_running"].includes(item.status)) return "Testing";
    if (["qualified", "smoke_passed"].includes(item.status)) return "Qualified";
    return "Failed";
  }

  function statusToneFromLabel(status) {
    if (["Qualified", "Completed"].includes(status)) return "success";
    if (["Checking", "Testing", "Queued", "Preparing", "Evaluating", "Finalizing"].includes(status)) {
      return "running";
    }
    if (status === "Cancelled") return "warning";
    return "error";
  }

  function evaluationStatusLabel(status) {
    const labels = {
      queued: "Queued",
      preparing: "Preparing",
      evaluating: "Evaluating",
      finalizing: "Finalizing",
      completed: "Completed",
      cancelled: "Cancelled",
      system_error: "System Error",
    };
    return labels[status] || "System Error";
  }

  function formatDate(value) {
    if (!value) return "—";
    const language = window.BuildBenchI18n?.getLanguage() === "zh" ? "zh-CN" : "en";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return new Intl.DateTimeFormat(language, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
  }

  function formatDuration(seconds) {
    if (seconds === null || seconds === undefined) return "—";
    const value = Math.max(Number(seconds) || 0, 0);
    const hours = Math.floor(value / 3600);
    const minutes = Math.floor((value % 3600) / 60);
    const secs = Math.floor(value % 60);
    if (hours) return `${hours}h ${minutes}m`;
    if (minutes) return `${minutes}m ${secs}s`;
    return `${secs}s`;
  }

  function countLabel(value, singular, plural, chineseUnit) {
    if (window.BuildBenchI18n?.getLanguage() === "zh") return `${value} ${chineseUnit}`;
    return value === 1 ? `1 ${singular}` : `${value} ${plural}`;
  }

  function pageLabel(page, totalPages) {
    if (window.BuildBenchI18n?.getLanguage() === "zh") return `第 ${page} 页，共 ${totalPages} 页`;
    return `Page ${page} of ${totalPages}`;
  }

  function setNotice(message, tone = "info") {
    if (!notice) return;
    notice.hidden = !message;
    notice.className = `submission-notice ${tone}`;
    notice.textContent = message ? t(message) : "";
  }

  function evaluationBySubmission(submissionId) {
    return evaluations.find((item) => item.submission_id === submissionId);
  }

  function evaluationAction(evaluation) {
    const label =
      evaluation.status === "completed"
        ? "View results"
        : evaluation.status === "system_error"
          ? "View diagnostics"
          : "View details";
    return `<a class="submission-row-action secondary" href="evaluation-detail.html?id=${encodeURIComponent(evaluation.evaluation_id)}">
      <i data-lucide="arrow-up-right" aria-hidden="true"></i>${escapeHtml(t(label))}
    </a>`;
  }

  function renderAccountSummary() {
    if (fullUsed) fullUsed.textContent = String(evaluations.length);
    const completed = evaluations.filter(
      (item) => item.status === "completed" && typeof item.score === "number",
    );
    if (!completed.length) {
      if (bestScore) bestScore.textContent = "—";
      if (bestScoreNote) bestScoreNote.textContent = t("No evaluated submission");
      return;
    }
    const best = Math.max(...completed.map((item) => item.score));
    if (bestScore) bestScore.textContent = `${(best * 100).toFixed(1)}%`;
    if (bestScoreNote) bestScoreNote.textContent = t("Build success rate");
  }

  function renderFullEvaluations() {
    if (!fullList) return;
    if (fullCount) {
      fullCount.textContent = countLabel(evaluations.length, "run", "runs", "次运行");
    }
    renderAccountSummary();
    if (!evaluations.length) {
      fullList.innerHTML = `
        <div class="competition-empty-state competition-empty-state-inline">
          <i data-lucide="info" aria-hidden="true"></i>
          <p>${escapeHtml(t("You currently have no full evaluation submissions for this competition."))}</p>
        </div>`;
      return;
    }

    fullList.innerHTML = `
      <div class="full-evaluation-table-wrap">
        <table class="full-evaluation-table">
          <thead>
            <tr>
              <th scope="col">${escapeHtml(t("Status"))}</th>
              <th scope="col">${escapeHtml(t("Evaluation ID"))}</th>
              <th scope="col">${escapeHtml(t("Agent version"))}</th>
              <th scope="col">${escapeHtml(t("Started"))}</th>
              <th scope="col">${escapeHtml(t("Progress"))}</th>
              <th scope="col">${escapeHtml(t("Duration"))}</th>
              <th scope="col">${escapeHtml(t("Score"))}</th>
              <th scope="col">${escapeHtml(t("Actions"))}</th>
            </tr>
          </thead>
          <tbody>
            ${evaluations
              .map((evaluation) => {
                const status = evaluationStatusLabel(evaluation.status);
                const progress = evaluation.progress || {};
                const score =
                  evaluation.status === "completed" && typeof evaluation.score === "number"
                    ? `${(evaluation.score * 100).toFixed(1)}%`
                    : "—";
                return `
                  <tr>
                    <td data-label="${escapeHtml(t("Status"))}">
                      <span class="submission-status ${statusToneFromLabel(status)}">${escapeHtml(t(status))}</span>
                    </td>
                    <td data-label="${escapeHtml(t("Evaluation ID"))}"><code>${escapeHtml(evaluation.evaluation_id)}</code></td>
                    <td data-label="${escapeHtml(t("Agent version"))}">
                      <strong>${escapeHtml(evaluation.agent?.name || "Agent")}</strong>
                      <small>v${escapeHtml(evaluation.agent?.version || "—")}</small>
                    </td>
                    <td data-label="${escapeHtml(t("Started"))}"><time>${escapeHtml(formatDate(evaluation.started_at || evaluation.queued_at))}</time></td>
                    <td data-label="${escapeHtml(t("Progress"))}">
                      <strong>${escapeHtml(progress.completed ?? 0)} / ${escapeHtml(progress.total ?? 0)}</strong>
                      <small>${escapeHtml(progress.percent ?? 0)}%</small>
                    </td>
                    <td data-label="${escapeHtml(t("Duration"))}">${escapeHtml(formatDuration(evaluation.duration_seconds))}</td>
                    <td data-label="${escapeHtml(t("Score"))}"><strong>${escapeHtml(score)}</strong></td>
                    <td data-label="${escapeHtml(t("Actions"))}">${evaluationAction(evaluation)}</td>
                  </tr>`;
              })
              .join("")}
          </tbody>
        </table>
      </div>`;
  }

  function smokeSummary(item) {
    const smokeStatus = item.smoke?.status || "not_started";
    const summary = item.smoke?.summary;
    const passed = summary?.succeeded ?? 0;
    const total = summary?.case_count ?? 0;
    let label = "Not run";
    let tone = "idle";
    if (["queued", "running"].includes(smokeStatus)) {
      label = "Running";
      tone = "running";
    } else if (smokeStatus === "passed") {
      label = "Passed";
      tone = "success";
    } else if (["failed", "infrastructure_error"].includes(smokeStatus)) {
      label = "Failed";
      tone = "error";
    }
    const score = total > 0 ? `<small>${escapeHtml(passed)}/${escapeHtml(total)}</small>` : "";
    return `<span class="smoke-test-state ${tone}"><strong>${escapeHtml(t(label))}</strong>${score}</span>`;
  }

  function logButton(item) {
    return `<button type="button" class="submission-view-log" data-log-action="${escapeHtml(item.id)}">
      <i data-lucide="file-terminal" aria-hidden="true"></i>${escapeHtml(t("View log"))}
    </button>`;
  }

  function fullEvaluationButton(item) {
    const evaluation = evaluationBySubmission(item.id);
    if (evaluation) return evaluationAction(evaluation);
    if (item.status !== "smoke_passed") return "";
    const disabled = !evaluationReadiness.ready;
    const title = disabled ? evaluationReadiness.message : "Start Full Evaluation";
    return `<button type="button" class="submission-row-action full-evaluation-trigger" data-evaluation-action="${escapeHtml(item.id)}" ${disabled ? "disabled" : ""} title="${escapeHtml(t(title))}">
      <i data-lucide="play" aria-hidden="true"></i>${escapeHtml(t("Start Full Evaluation"))}
    </button>`;
  }

  function renderAgentVersions() {
    if (!versionList) return;
    if (versionCount) {
      versionCount.textContent = countLabel(submissions.length, "version", "versions", "个版本");
    }
    if (!submissions.length) {
      currentPage = 1;
      versionList.innerHTML = `
        <div class="competition-empty-state">
          <i data-lucide="package-open" aria-hidden="true"></i>
          <div><strong>${escapeHtml(t("No Agent versions yet"))}</strong><p>${escapeHtml(t("Upload an Agent ZIP to create your first immutable submission version."))}</p></div>
        </div>`;
      return;
    }

    const totalPages = Math.max(1, Math.ceil(submissions.length / PAGE_SIZE));
    currentPage = Math.min(Math.max(currentPage, 1), totalPages);
    const startIndex = (currentPage - 1) * PAGE_SIZE;
    const visibleSubmissions = submissions.slice(startIndex, startIndex + PAGE_SIZE);

    versionList.innerHTML = `
      <div class="agent-version-table-wrap">
        <table class="agent-version-table">
          <thead><tr>
            <th scope="col">${escapeHtml(t("Status"))}</th>
            <th scope="col">${escapeHtml(t("Submission ID"))}</th>
            <th scope="col">${escapeHtml(t("Agent version"))}</th>
            <th scope="col">${escapeHtml(t("Submitted"))}</th>
            <th scope="col">${escapeHtml(t("Smoke Test"))}</th>
            <th scope="col">${escapeHtml(t("Actions"))}</th>
          </tr></thead>
          <tbody>
            ${visibleSubmissions
              .map((item) => {
                const canRun = RETRYABLE.has(item.status);
                const actionLabel = item.status === "qualified" ? "Run Smoke Test" : "Retry Smoke Test";
                const agentName = item.agent?.name || item.filename;
                const agentVersion = item.agent?.version || "—";
                const status = publicStatus(item);
                return `<tr data-submission-id="${escapeHtml(item.id)}">
                  <td data-label="${escapeHtml(t("Status"))}"><span class="submission-status ${statusToneFromLabel(status)}">${escapeHtml(t(status))}</span></td>
                  <td data-label="${escapeHtml(t("Submission ID"))}"><code class="agent-version-id">${escapeHtml(item.id)}</code></td>
                  <td data-label="${escapeHtml(t("Agent version"))}"><strong class="agent-version-name">${escapeHtml(agentName)}</strong><span class="agent-version-number">v${escapeHtml(agentVersion)}</span></td>
                  <td data-label="${escapeHtml(t("Submitted"))}"><time>${escapeHtml(formatDate(item.created_at))}</time><code class="agent-version-sha">SHA ${escapeHtml(String(item.sha256 || "").slice(0, 12))}…</code></td>
                  <td data-label="${escapeHtml(t("Smoke Test"))}">${smokeSummary(item)}</td>
                  <td data-label="${escapeHtml(t("Actions"))}"><div class="agent-version-actions">
                    ${canRun ? `<button type="button" class="submission-row-action" data-smoke-action="${escapeHtml(item.id)}"><i data-lucide="flask-conical" aria-hidden="true"></i>${escapeHtml(t(actionLabel))}</button>` : ""}
                    ${fullEvaluationButton(item)}
                    ${logButton(item)}
                  </div></td>
                </tr>`;
              })
              .join("")}
          </tbody>
        </table>
      </div>
      ${
        totalPages > 1
          ? `<nav class="agent-version-pagination" aria-label="${escapeHtml(t("Agent version pages"))}">
              <button type="button" data-page-action="previous" ${currentPage === 1 ? "disabled" : ""}><i data-lucide="chevron-left" aria-hidden="true"></i>${escapeHtml(t("Previous"))}</button>
              <span aria-live="polite">${escapeHtml(pageLabel(currentPage, totalPages))}</span>
              <button type="button" data-page-action="next" ${currentPage === totalPages ? "disabled" : ""}>${escapeHtml(t("Next"))}<i data-lucide="chevron-right" aria-hidden="true"></i></button>
            </nav>`
          : ""
      }`;
  }

  function render() {
    renderFullEvaluations();
    renderAgentVersions();
    window.lucide?.createIcons({ attrs: { "stroke-width": 1.8 } });
    schedulePolling();
  }

  async function api(path, options = {}) {
    if (window.BuildBenchAuth?.request) {
      return window.BuildBenchAuth.request(path, options);
    }
    const response = await fetch(path, { cache: "no-store", ...options });
    let payload = {};
    try {
      payload = await response.json();
    } catch {
      // The structured HTTP error below is more useful than a JSON parser error.
    }
    if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
    return payload;
  }

  async function loadDashboard({ quiet = false } = {}) {
    try {
      const [submissionPayload, evaluationPayload, health] = await Promise.all([
        api("/api/submissions"),
        api("/api/full-evaluations"),
        api("/api/health"),
      ]);
      submissions = submissionPayload.submissions || [];
      evaluations = evaluationPayload.evaluations || [];
      evaluationReadiness = {
        enabled: Boolean(health.full_evaluation_enabled),
        ready: Boolean(health.full_evaluation_ready),
        message: health.full_evaluation_message || "Full Evaluation is not available yet.",
      };
      if (!quiet) setNotice("");
      render();
    } catch (error) {
      if (error.status === 401 && window.BuildBenchAuth) {
        await window.BuildBenchAuth.requireSession();
        return;
      }
      setNotice("Submission service is unavailable. Start the Build-Bench website backend and try again.", "error");
      if (!quiet) console.error(error);
    }
  }

  async function upload(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".zip")) {
      setNotice("Choose the agent-submission.zip created by ./bb package.", "error");
      return;
    }
    uploadButton.disabled = true;
    setNotice("Uploading and checking the Agent bundle…", "running");
    try {
      const record = await api("/api/submissions", {
        method: "POST",
        headers: { "Content-Type": "application/zip", "X-Agent-Filename": file.name },
        body: file,
      });
      submissions = [record, ...submissions.filter((item) => item.id !== record.id)];
      currentPage = 1;
      setNotice(
        record.status === "qualified"
          ? "Agent bundle passed static checks. You may now run a Hosted Smoke Test."
          : record.message,
        record.status === "qualified" ? "success" : "error",
      );
      render();
    } catch (error) {
      setNotice(error.message, "error");
    } finally {
      uploadButton.disabled = false;
      uploadInput.value = "";
    }
  }

  async function runSmokeTest(submissionId) {
    const button = document.querySelector(`[data-smoke-action="${CSS.escape(submissionId)}"]`);
    if (button) button.disabled = true;
    setNotice("");
    try {
      const record = await api(`/api/submissions/${encodeURIComponent(submissionId)}/smoke-test`, {
        method: "POST",
      });
      submissions = submissions.map((item) => (item.id === record.id ? record : item));
      render();
    } catch (error) {
      setNotice(error.message, "error");
      if (button) button.disabled = false;
    }
  }

  function openEvaluationConfirmation(submissionId) {
    const record = submissions.find((item) => item.id === submissionId);
    if (!record || !evaluationModal || !evaluationReadiness.ready) return;
    pendingEvaluationSubmissionId = submissionId;
    const name = record.agent?.name || record.filename || "Agent";
    const version = record.agent?.version || "—";
    evaluationConfirmAgent.textContent = `${name} · v${version}`;
    evaluationConfirmId.textContent = record.id;
    evaluationConfirmError.hidden = true;
    evaluationConfirmError.textContent = "";
    evaluationConfirmButton.disabled = false;
    evaluationModal.showModal();
    window.lucide?.createIcons({ attrs: { "stroke-width": 1.8 } });
  }

  async function createFullEvaluation() {
    if (!pendingEvaluationSubmissionId) return;
    evaluationConfirmButton.disabled = true;
    evaluationConfirmError.hidden = true;
    const idempotencyKey =
      globalThis.crypto?.randomUUID?.() || `web-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    try {
      const evaluation = await api(
        `/api/submissions/${encodeURIComponent(pendingEvaluationSubmissionId)}/full-evaluations`,
        { method: "POST", headers: { "Idempotency-Key": idempotencyKey } },
      );
      evaluations = [
        evaluation,
        ...evaluations.filter((item) => item.evaluation_id !== evaluation.evaluation_id),
      ];
      evaluationModal.close();
      pendingEvaluationSubmissionId = null;
      render();
      window.location.href = `evaluation-detail.html?id=${encodeURIComponent(evaluation.evaluation_id)}`;
    } catch (error) {
      evaluationConfirmError.hidden = false;
      evaluationConfirmError.textContent = error.message;
      evaluationConfirmButton.disabled = false;
    }
  }

  async function openLog(submissionId) {
    const record = submissions.find((item) => item.id === submissionId);
    if (!record || !logModal) return;
    const status = publicStatus(record);
    logStatus.textContent = t(status);
    logStatus.className = `submission-status ${statusToneFromLabel(status)}`;
    logAgent.textContent = `${record.agent?.name || record.filename || "Agent"} · v${record.agent?.version || "—"}`;
    logId.textContent = record.id;
    logContent.textContent = t("Loading log…");
    logError.hidden = true;
    logDownload.hidden = true;
    logModal.showModal();
    window.lucide?.createIcons({ attrs: { "stroke-width": 1.8 } });
    const logPath = `/api/submissions/${encodeURIComponent(record.id)}/log`;
    try {
      const response = await fetch(logPath, { cache: "no-store" });
      if (!response.ok) throw new Error(t("The requested log could not be loaded."));
      logContent.textContent = await response.text();
      logDownload.href = `${logPath}?download=1`;
      logDownload.hidden = false;
    } catch (error) {
      logError.hidden = false;
      logError.textContent = error.message || t("The requested log could not be loaded.");
      logContent.textContent = t("No log is available for this submission.");
    }
  }

  function schedulePolling() {
    if (pollTimer) window.clearTimeout(pollTimer);
    pollTimer = null;
    const hasActiveSubmission = submissions.some((item) => ACTIVE_SUBMISSION.has(item.status));
    const hasActiveEvaluation = evaluations.some((item) => ACTIVE_EVALUATION.has(item.status));
    if (!hasActiveSubmission && !hasActiveEvaluation) return;
    pollTimer = window.setTimeout(() => loadDashboard({ quiet: true }), 3000);
  }

  uploadButton?.addEventListener("click", () => uploadInput?.click());
  uploadInput?.addEventListener("change", () => upload(uploadInput.files?.[0]));
  versionList?.addEventListener("click", (event) => {
    const pageButton = event.target.closest("[data-page-action]");
    if (pageButton && !pageButton.disabled) {
      currentPage += pageButton.dataset.pageAction === "next" ? 1 : -1;
      renderAgentVersions();
      window.lucide?.createIcons({ attrs: { "stroke-width": 1.8 } });
      document.getElementById("agent-versions-title")?.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    const log = event.target.closest("[data-log-action]");
    if (log) return openLog(log.dataset.logAction);
    const smoke = event.target.closest("[data-smoke-action]");
    if (smoke) return runSmokeTest(smoke.dataset.smokeAction);
    const evaluation = event.target.closest("[data-evaluation-action]");
    if (evaluation) openEvaluationConfirmation(evaluation.dataset.evaluationAction);
  });
  logModal?.querySelectorAll("[data-log-close]").forEach((button) => {
    button.addEventListener("click", () => logModal.close());
  });
  logModal?.addEventListener("click", (event) => {
    if (event.target === logModal) logModal.close();
  });
  evaluationModal?.querySelector("[data-evaluation-cancel]")?.addEventListener("click", () => {
    pendingEvaluationSubmissionId = null;
    evaluationModal.close();
  });
  evaluationConfirmButton?.addEventListener("click", createFullEvaluation);
  evaluationModal?.addEventListener("click", (event) => {
    if (event.target === evaluationModal) {
      pendingEvaluationSubmissionId = null;
      evaluationModal.close();
    }
  });
  window.addEventListener("buildbench:languagechange", render);
  window.addEventListener("DOMContentLoaded", () => loadDashboard());
})();
