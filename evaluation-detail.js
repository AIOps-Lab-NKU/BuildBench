(function () {
  "use strict";

  const query = new URLSearchParams(window.location.search);
  const evaluationId = query.get("id");
  const heading = document.querySelector("[data-evaluation-heading]");
  const errorBox = document.querySelector("[data-evaluation-error]");
  const statusNode = document.querySelector("[data-evaluation-status]");
  const idNode = document.querySelector("[data-evaluation-id]");
  const agentNode = document.querySelector("[data-evaluation-agent]");
  const startedNode = document.querySelector("[data-evaluation-started]");
  const progressNode = document.querySelector("[data-evaluation-progress]");
  const progressBar = document.querySelector("[data-evaluation-progress-bar]");
  const progressLabel = document.querySelector("[data-evaluation-progress-label]");
  const progressNote = document.querySelector("[data-evaluation-progress-note]");
  const stages = document.querySelector("[data-evaluation-stages]");
  const resultPanel = document.querySelector("[data-evaluation-result]");
  const scoreNode = document.querySelector("[data-evaluation-score]");
  const resultNote = document.querySelector("[data-evaluation-result-note]");
  const timeline = document.querySelector("[data-evaluation-timeline]");

  const TERMINAL = new Set(["completed", "cancelled", "system_error"]);
  const ORDER = ["queued", "preparing", "evaluating", "finalizing", "completed"];
  const EVENT_TYPES = ["snapshot", "phase", "progress", "completed", "system_error"];
  const seenEvents = new Set();
  let eventSource = null;
  let pollTimer = null;
  let currentRecord = null;

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

  function formatDate(value) {
    if (!value) return "—";
    const language = window.BuildBenchI18n?.getLanguage() === "zh" ? "zh-CN" : "en";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return new Intl.DateTimeFormat(language, {
      dateStyle: "medium",
      timeStyle: "medium",
    }).format(date);
  }

  function statusLabel(status) {
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

  function statusTone(status) {
    if (status === "completed") return "success";
    if (["cancelled"].includes(status)) return "warning";
    if (status === "system_error") return "error";
    return "running";
  }

  async function api(path) {
    const response = await fetch(path, { cache: "no-store" });
    let payload = {};
    try {
      payload = await response.json();
    } catch {
      // Fall through to the structured status error.
    }
    if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
    return payload;
  }

  function setError(message) {
    errorBox.hidden = !message;
    errorBox.textContent = message || "";
  }

  function renderStages(status) {
    if (!stages) return;
    const effectiveStatus = ["cancelled", "system_error"].includes(status)
      ? currentRecord?.progress?.completed
        ? "evaluating"
        : "queued"
      : status;
    const activeIndex = Math.max(ORDER.indexOf(effectiveStatus), 0);
    stages.querySelectorAll("[data-stage]").forEach((item, index) => {
      item.classList.toggle("complete", index < activeIndex || status === "completed");
      item.classList.toggle("active", index === activeIndex && status !== "completed");
      item.classList.toggle("stopped", TERMINAL.has(status) && status !== "completed" && index === activeIndex);
    });
  }

  function render(record) {
    currentRecord = record;
    const status = statusLabel(record.status);
    const progress = record.progress || {};
    const percent = Math.min(Math.max(Number(progress.percent) || 0, 0), 100);
    document.title = `${record.evaluation_id} | Build-Bench Challenge`;
    heading.textContent = `${record.agent?.name || "Agent"} · v${record.agent?.version || "—"}`;
    statusNode.textContent = t(status);
    statusNode.className = `submission-status ${statusTone(record.status)}`;
    idNode.textContent = record.evaluation_id;
    agentNode.textContent = `${record.agent?.name || "Agent"} · v${record.agent?.version || "—"}`;
    startedNode.textContent = formatDate(record.started_at || record.queued_at);
    progressLabel.textContent = `${progress.completed ?? 0} / ${progress.total ?? 0} · ${percent}%`;
    progressNode.setAttribute("aria-valuenow", String(percent));
    progressBar.style.width = `${percent}%`;
    renderStages(record.status);

    if (record.status === "system_error") {
      progressNote.textContent = t("The organizer-controlled evaluation service stopped this run. No partial score is published.");
    } else if (record.status === "cancelled") {
      progressNote.textContent = t("This evaluation was cancelled by an organizer. No score is published.");
    } else if (record.status === "completed") {
      progressNote.textContent = t("All Cases completed and the official result is frozen.");
    } else {
      progressNote.textContent = t("The official score is published only after all Cases finish and the run is finalized.");
    }

    if (record.status === "completed" && typeof record.score === "number") {
      resultPanel.hidden = false;
      scoreNode.textContent = `${(record.score * 100).toFixed(1)}%`;
      resultNote.textContent = t("This score is based on the frozen Case set and evaluation protocol shown in the run snapshot.");
    } else {
      resultPanel.hidden = true;
    }
    window.lucide?.createIcons({ attrs: { "stroke-width": 1.8 } });
  }

  function eventDescription(event) {
    const payload = event.payload || {};
    if (event.type === "snapshot") {
      return t("Evaluation created and the immutable run snapshot was recorded.");
    }
    if (event.type === "progress") {
      return `${t("Evaluation progress updated")}: ${payload.completed_cases ?? 0} / ${payload.total_cases ?? 0}.`;
    }
    if (event.type === "completed") return t("Evaluation completed and the official result was frozen.");
    if (event.type === "system_error") return t("The evaluation stopped because an organizer-controlled service failed.");
    if (event.type === "phase") {
      return `${t("Evaluation entered phase")} ${t(statusLabel(payload.status))}.`;
    }
    return t("Evaluation state updated.");
  }

  function appendEvent(event) {
    if (!timeline || seenEvents.has(event.id)) return;
    if (timeline.dataset.initial !== "ready") {
      timeline.innerHTML = "";
      timeline.dataset.initial = "ready";
    }
    seenEvents.add(event.id);
    const item = document.createElement("li");
    item.innerHTML = `<time>${escapeHtml(formatDate(event.created_at))}</time><p>${escapeHtml(eventDescription(event))}</p>`;
    timeline.append(item);
  }

  async function loadRecord() {
    if (!evaluationId) {
      setError(t("Evaluation ID is missing from the URL."));
      return null;
    }
    try {
      const record = await api(`/api/full-evaluations/${encodeURIComponent(evaluationId)}`);
      setError("");
      render(record);
      if (TERMINAL.has(record.status)) stopLiveUpdates();
      return record;
    } catch (error) {
      setError(error.message);
      return null;
    }
  }

  function schedulePolling() {
    if (pollTimer) window.clearTimeout(pollTimer);
    if (currentRecord && TERMINAL.has(currentRecord.status)) return;
    pollTimer = window.setTimeout(async () => {
      await loadRecord();
      schedulePolling();
    }, 5000);
  }

  function stopLiveUpdates() {
    eventSource?.close();
    eventSource = null;
    if (pollTimer) window.clearTimeout(pollTimer);
    pollTimer = null;
  }

  function startEventStream() {
    if (!evaluationId || !("EventSource" in window)) {
      schedulePolling();
      return;
    }
    eventSource = new EventSource(`/api/full-evaluations/${encodeURIComponent(evaluationId)}/events`);
    EVENT_TYPES.forEach((type) => {
      eventSource.addEventListener(type, async (message) => {
        try {
          appendEvent(JSON.parse(message.data));
        } catch {
          // A malformed optional timeline event must not break status updates.
        }
        const record = await loadRecord();
        if (record && TERMINAL.has(record.status)) stopLiveUpdates();
      });
    });
    eventSource.onerror = () => {
      eventSource?.close();
      eventSource = null;
      schedulePolling();
    };
  }

  async function initialize() {
    const record = await loadRecord();
    if (record && !TERMINAL.has(record.status)) startEventStream();
  }

  window.addEventListener("buildbench:languagechange", () => {
    if (currentRecord) render(currentRecord);
  });
  window.addEventListener("beforeunload", stopLiveUpdates);
  window.addEventListener("DOMContentLoaded", initialize);
})();
