(function () {
  "use strict";

  const uploadInput = document.querySelector("[data-agent-upload]");
  const uploadButton = document.querySelector("[data-upload-button]");
  const notice = document.querySelector("[data-submission-notice]");
  const versionList = document.querySelector("[data-agent-versions-list]");
  const fullList = document.querySelector("[data-full-evaluations-list]");
  const versionCount = document.querySelector("[data-agent-version-count]");
  const fullCount = document.querySelector("[data-full-count]");
  const logModal = document.querySelector("[data-log-modal]");
  const logStatus = document.querySelector("[data-log-status]");
  const logAgent = document.querySelector("[data-log-agent]");
  const logId = document.querySelector("[data-log-id]");
  const logContent = document.querySelector("[data-log-content]");
  const logError = document.querySelector("[data-log-error]");
  const logDownload = document.querySelector("[data-log-download]");
  const ACTIVE = new Set(["checking", "smoke_queued", "smoke_running"]);
  const RETRYABLE = new Set(["qualified", "smoke_failed", "infrastructure_error"]);
  let submissions = [];
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
    const evaluation = item.full_evaluation?.status;
    if (["queued", "running", "evaluating"].includes(evaluation)) return "Evaluating";
    if (["completed", "succeeded"].includes(evaluation)) return "Completed";
    if (item.status === "checking") return "Checking";
    if (["smoke_queued", "smoke_running"].includes(item.status)) return "Testing";
    if (["qualified", "smoke_passed"].includes(item.status)) return "Qualified";
    return "Failed";
  }

  function statusLabel(item) {
    return t(publicStatus(item));
  }

  function statusTone(item) {
    const status = publicStatus(item);
    if (["Qualified", "Completed"].includes(status)) return "success";
    if (["Checking", "Testing", "Evaluating"].includes(status)) return "running";
    return "error";
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

  function countLabel(value, singular, plural, chineseUnit) {
    if (window.BuildBenchI18n?.getLanguage() === "zh") {
      return `${value} ${chineseUnit}`;
    }
    return value === 1 ? `1 ${singular}` : `${value} ${plural}`;
  }

  function setNotice(message, tone = "info") {
    if (!notice) return;
    notice.hidden = !message;
    notice.className = `submission-notice ${tone}`;
    notice.textContent = message ? t(message) : "";
  }

  function renderFullEvaluations() {
    if (!fullList) return;
    const evaluations = submissions.filter(
      (item) => item.full_evaluation?.status !== "not_started",
    );
    if (fullCount) {
      fullCount.textContent = countLabel(evaluations.length, "run", "runs", "次运行");
    }
    if (!evaluations.length) {
      fullList.innerHTML = `
        <div class="competition-empty-state competition-empty-state-inline">
          <i data-lucide="info" aria-hidden="true"></i>
          <p>${escapeHtml(t("You currently have no full evaluation submissions for this competition."))}</p>
        </div>
      `;
      return;
    }
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
    return `
      <span class="smoke-test-state ${tone}">
        <strong>${escapeHtml(t(label))}</strong>
        ${score}
      </span>
    `;
  }

  function logButton(item) {
    return `
      <button type="button" class="submission-view-log" data-log-action="${escapeHtml(item.id)}">
        <i data-lucide="file-terminal" aria-hidden="true"></i>
        ${escapeHtml(t("View log"))}
      </button>
    `;
  }

  function renderAgentVersions() {
    if (!versionList) return;
    if (versionCount) {
      versionCount.textContent = countLabel(
        submissions.length,
        "version",
        "versions",
        "个版本",
      );
    }
    if (!submissions.length) {
      versionList.innerHTML = `
        <div class="competition-empty-state">
          <i data-lucide="package-open" aria-hidden="true"></i>
          <div>
            <strong>${escapeHtml(t("No Agent versions yet"))}</strong>
            <p>${escapeHtml(t("Upload an Agent ZIP to create your first immutable submission version."))}</p>
          </div>
        </div>
      `;
      return;
    }

    versionList.innerHTML = `
      <div class="agent-version-table-wrap">
        <table class="agent-version-table">
          <thead>
            <tr>
              <th scope="col">${escapeHtml(t("Status"))}</th>
              <th scope="col">${escapeHtml(t("Submission ID"))}</th>
              <th scope="col">${escapeHtml(t("Agent version"))}</th>
              <th scope="col">${escapeHtml(t("Submitted"))}</th>
              <th scope="col">${escapeHtml(t("Smoke Test"))}</th>
              <th scope="col">${escapeHtml(t("Actions"))}</th>
            </tr>
          </thead>
          <tbody>
          ${submissions
          .map((item) => {
            const canRun = RETRYABLE.has(item.status);
            const canEvaluate =
              item.status === "smoke_passed" &&
              item.full_evaluation?.status === "not_started";
            const actionLabel =
              item.status === "qualified" ? "Run Smoke Test" : "Retry Smoke Test";
            const agentName = item.agent?.name || item.filename;
            const agentVersion = item.agent?.version || "—";
            return `
              <tr data-submission-id="${escapeHtml(item.id)}">
                <td data-label="${escapeHtml(t("Status"))}">
                  <span class="submission-status ${statusTone(item)}">${escapeHtml(statusLabel(item))}</span>
                </td>
                <td data-label="${escapeHtml(t("Submission ID"))}">
                  <code class="agent-version-id">${escapeHtml(item.id)}</code>
                </td>
                <td data-label="${escapeHtml(t("Agent version"))}">
                  <strong class="agent-version-name">${escapeHtml(agentName)}</strong>
                  <span class="agent-version-number">v${escapeHtml(agentVersion)}</span>
                </td>
                <td data-label="${escapeHtml(t("Submitted"))}">
                  <time>${escapeHtml(formatDate(item.created_at))}</time>
                  <code class="agent-version-sha">SHA ${escapeHtml(String(item.sha256 || "").slice(0, 12))}…</code>
                </td>
                <td data-label="${escapeHtml(t("Smoke Test"))}">
                  ${smokeSummary(item)}
                </td>
                <td data-label="${escapeHtml(t("Actions"))}">
                  <div class="agent-version-actions">
                    ${
                      canRun
                        ? `<button type="button" class="submission-row-action" data-smoke-action="${escapeHtml(item.id)}">
                             <i data-lucide="flask-conical" aria-hidden="true"></i>${escapeHtml(t(actionLabel))}
                           </button>`
                        : ""
                    }
                    ${
                      canEvaluate
                        ? `<button type="button" class="submission-row-action secondary" disabled title="${escapeHtml(t("Coming soon"))}">
                             <i data-lucide="play" aria-hidden="true"></i>${escapeHtml(t("Start Full Evaluation"))}
                           </button>`
                        : ""
                    }
                    ${logButton(item)}
                  </div>
                </td>
              </tr>
            `;
          })
          .join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  function render() {
    renderFullEvaluations();
    renderAgentVersions();
    window.lucide?.createIcons({ attrs: { "stroke-width": 1.8 } });
    schedulePolling();
  }

  async function api(path, options = {}) {
    const response = await fetch(path, {
      cache: "no-store",
      ...options,
    });
    let payload = {};
    try {
      payload = await response.json();
    } catch {
      // A structured error below is more useful than a JSON parser exception.
    }
    if (!response.ok) {
      throw new Error(payload.error || `Request failed (${response.status})`);
    }
    return payload;
  }

  async function loadSubmissions({ quiet = false } = {}) {
    try {
      const payload = await api("/api/submissions");
      submissions = payload.submissions || [];
      if (!quiet) setNotice("");
      render();
    } catch (error) {
      setNotice(
        "Submission service is unavailable. Start the Build-Bench website backend and try again.",
        "error",
      );
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
        headers: {
          "Content-Type": "application/zip",
          "X-Agent-Filename": file.name,
        },
        body: file,
      });
      submissions = [record, ...submissions.filter((item) => item.id !== record.id)];
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

  async function openLog(submissionId) {
    const record = submissions.find((item) => item.id === submissionId);
    if (!record || !logModal) return;
    const agentName = record.agent?.name || record.filename || "Agent";
    const agentVersion = record.agent?.version || "—";
    logStatus.textContent = statusLabel(record);
    logStatus.className = `submission-status ${statusTone(record)}`;
    logAgent.textContent = `${agentName} · v${agentVersion}`;
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

  function closeLog() {
    if (logModal?.open) logModal.close();
  }

  function schedulePolling() {
    if (pollTimer) {
      window.clearTimeout(pollTimer);
      pollTimer = null;
    }
    if (!submissions.some((item) => ACTIVE.has(item.status))) return;
    pollTimer = window.setTimeout(() => loadSubmissions({ quiet: true }), 3000);
  }

  uploadButton?.addEventListener("click", () => uploadInput?.click());
  uploadInput?.addEventListener("change", () => upload(uploadInput.files?.[0]));
  versionList?.addEventListener("click", (event) => {
    const log = event.target.closest("[data-log-action]");
    if (log) {
      openLog(log.dataset.logAction);
      return;
    }
    const button = event.target.closest("[data-smoke-action]");
    if (button) runSmokeTest(button.dataset.smokeAction);
  });
  logModal?.querySelectorAll("[data-log-close]").forEach((button) => {
    button.addEventListener("click", closeLog);
  });
  logModal?.addEventListener("click", (event) => {
    if (event.target === logModal) closeLog();
  });
  window.addEventListener("buildbench:languagechange", render);
  window.addEventListener("DOMContentLoaded", () => loadSubmissions());
})();
