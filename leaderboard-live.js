(() => {
  "use strict";

  const state = document.querySelector("[data-live-board-state]");
  const table = document.querySelector("[data-live-board-table]");
  const body = document.querySelector("[data-live-board-body]");
  const version = document.querySelector("[data-live-board-version]");
  if (!state || !table || !body || !version) return;

  let payload = null;
  let loadError = false;

  const translate = (value) => window.BuildBenchI18n?.t(value) || value;

  function setState(title, detail) {
    state.replaceChildren();
    const heading = document.createElement("strong");
    const message = document.createElement("span");
    heading.textContent = translate(title);
    message.textContent = translate(detail);
    state.append(heading, message);
    state.hidden = false;
    table.hidden = true;
    version.hidden = true;
  }

  function renderTeam(entry) {
    const cell = document.createElement("th");
    cell.scope = "row";
    const name = document.createElement("strong");
    const members = document.createElement("span");
    name.className = "leaderboard-team-name";
    members.className = "leaderboard-team-members";
    name.textContent = String(entry.team_name || "—");
    const memberNames = Array.isArray(entry.members)
      ? entry.members.filter((value) => typeof value === "string" && value.trim())
      : [];
    members.textContent = memberNames.length
      ? memberNames.join(" · ")
      : translate("Members not published");
    cell.append(name, members);
    return cell;
  }

  function textCell(value, className = "") {
    const cell = document.createElement("td");
    cell.textContent = String(value);
    if (className) cell.className = className;
    return cell;
  }

  function render() {
    if (loadError) {
      setState(
        "Leaderboard unavailable",
        "The results service could not be reached. Please try again later.",
      );
      return;
    }
    if (!payload) return;

    const entries = Array.isArray(payload.entries) ? payload.entries : [];
    if (!entries.length) {
      setState(
        "No official results yet",
        "Completed Full Evaluations will appear here after organizer review and publication.",
      );
      return;
    }

    body.replaceChildren();
    entries.forEach((entry) => {
      const row = document.createElement("tr");
      row.append(textCell(entry.rank, "leaderboard-rank"));
      row.append(renderTeam(entry));
      row.append(
        textCell(`${(Number(entry.score || 0) * 100).toFixed(2)}%`, "leaderboard-score"),
      );
      row.append(
        textCell(
          `${Number(entry.successful_cases || 0)} / ${Number(entry.total_cases || 0)}`,
          "leaderboard-success-count",
        ),
      );
      body.append(row);
    });

    state.hidden = true;
    table.hidden = false;
    const caseSet = payload.case_set_version || "—";
    const protocol = payload.protocol_version || "—";
    version.textContent = `${translate("Case set")} ${caseSet} · ${translate("Protocol")} ${protocol}`;
    version.hidden = false;
  }

  fetch("/api/leaderboard", { headers: { Accept: "application/json" } })
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then((value) => {
      payload = value;
      render();
    })
    .catch(() => {
      loadError = true;
      render();
    });

  window.addEventListener("buildbench:languagechange", render);
})();
