(() => {
  const state = document.querySelector("[data-live-board-state]");
  const table = document.querySelector("[data-live-board-table]");
  const body = document.querySelector("[data-live-board-body]");
  const version = document.querySelector("[data-live-board-version]");
  if (!state || !table || !body || !version) return;

  const text = (value) => document.createTextNode(String(value ?? ""));
  const cell = (value, header = false) => {
    const element = document.createElement(header ? "th" : "td");
    if (header) element.scope = "row";
    element.append(text(value));
    return element;
  };
  const duration = (seconds) => {
    const value = Number(seconds || 0);
    if (value < 60) return `${value}s`;
    const minutes = Math.floor(value / 60);
    const remainder = value % 60;
    return remainder ? `${minutes}m ${remainder}s` : `${minutes}m`;
  };

  fetch("/api/leaderboard", { headers: { Accept: "application/json" } })
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then((payload) => {
      const entries = Array.isArray(payload.entries) ? payload.entries : [];
      if (!entries.length) {
        state.textContent = "No official competition results have been published yet.";
        return;
      }
      entries.forEach((entry) => {
        const row = document.createElement("tr");
        row.append(cell(entry.rank));
        row.append(cell(entry.team_name, true));
        row.append(cell(`${entry.agent_name} ${entry.agent_version}`));
        row.append(cell(`${entry.successful_cases} / ${entry.total_cases}`));
        row.append(cell(`${(Number(entry.score) * 100).toFixed(2)}%`));
        row.append(cell(duration(entry.duration_seconds)));
        row.append(cell(new Date(entry.published_at).toLocaleString()));
        body.append(row);
      });
      state.hidden = true;
      table.hidden = false;
      const first = entries[0];
      version.textContent = `Case set ${first.case_set_version} · Protocol ${first.protocol_version}`;
      version.hidden = false;
    })
    .catch(() => {
      state.textContent =
        "The live competition leaderboard is unavailable. Research baselines remain available below.";
    });
})();
