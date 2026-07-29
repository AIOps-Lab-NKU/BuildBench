(function () {
  "use strict";

  const page = document.querySelector("[data-team-page]");
  const loading = document.querySelector("[data-team-loading]");
  const teamNameForm = document.querySelector("[data-team-name-form]");
  const teamNameInput = document.querySelector("[data-team-name]");
  const memberList = document.querySelector("[data-team-members]");
  const memberCount = document.querySelector("[data-team-member-count]");
  const addButton = document.querySelector("[data-open-member-form]");
  const dialog = document.querySelector("[data-member-dialog]");
  const memberForm = document.querySelector("[data-member-form]");
  const memberDialogTitle = document.querySelector("[data-member-dialog-title]");
  const errorBox = document.querySelector("[data-team-error]");
  const notice = document.querySelector("[data-team-notice]");
  let context = null;
  let editingId = null;

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function message(target, value) {
    target.hidden = !value;
    target.textContent = value || "";
  }

  function render() {
    const team = context.team;
    teamNameInput.value = team.name;
    memberCount.textContent = `${team.members.length} / 5`;
    addButton.disabled = team.members_locked || team.members.length >= 5;
    document.querySelector("[data-team-id]").textContent = team.team_id;
    document.querySelector("[data-team-status]").textContent = team.members_locked
      ? "Roster locked"
      : "Registration active";
    memberList.innerHTML = team.members
      .map(
        (member) => `
          <tr>
            <td><span class="team-member-order">${member.display_order}</span></td>
            <td><strong>${escapeHtml(member.name)}</strong>${member.is_captain ? '<span class="team-captain-label">Captain</span>' : ""}</td>
            <td><a href="mailto:${escapeHtml(member.email)}">${escapeHtml(member.email)}</a></td>
            <td>${escapeHtml(member.institution)}</td>
            <td>
              ${
                member.is_captain || team.members_locked
                  ? '<span class="team-readonly-label">Account owner</span>'
                  : `<div class="team-row-actions">
                      <button type="button" data-edit-member="${escapeHtml(member.member_id)}">Edit</button>
                      <button type="button" class="danger" data-delete-member="${escapeHtml(member.member_id)}">Remove</button>
                    </div>`
              }
            </td>
          </tr>`,
      )
      .join("");
    page.hidden = false;
    loading.hidden = true;
    window.lucide?.createIcons({ attrs: { "stroke-width": 1.8 } });
  }

  async function refresh() {
    const session = await window.BuildBenchAuth.requireSession();
    if (!session) return;
    context = session;
    render();
  }

  function openMember(member = null) {
    editingId = member?.member_id || null;
    memberForm.reset();
    memberDialogTitle.textContent = member ? "Edit team member" : "Add team member";
    if (member) {
      memberForm.elements.name.value = member.name;
      memberForm.elements.email.value = member.email;
      memberForm.elements.institution.value = member.institution;
    }
    message(errorBox, "");
    dialog.showModal();
  }

  teamNameForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    message(notice, "");
    try {
      context.team = await window.BuildBenchAuth.request("/api/team", {
        method: "PATCH",
        json: { name: teamNameInput.value },
      });
      window.BuildBenchAuth.clearSession();
      message(notice, "Team name updated.");
      render();
    } catch (error) {
      message(notice, error.message);
    }
  });

  addButton?.addEventListener("click", () => openMember());
  document.querySelectorAll("[data-member-cancel]").forEach((button) => {
    button.addEventListener("click", () => dialog.close());
  });

  memberForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = new FormData(memberForm);
    const path = editingId
      ? `/api/team/members/${encodeURIComponent(editingId)}`
      : "/api/team/members";
    try {
      context.team = await window.BuildBenchAuth.request(path, {
        method: editingId ? "PATCH" : "POST",
        json: {
          name: data.get("name"),
          email: data.get("email"),
          institution: data.get("institution"),
        },
      });
      window.BuildBenchAuth.clearSession();
      dialog.close();
      message(notice, editingId ? "Team member updated." : "Team member added.");
      render();
    } catch (error) {
      message(errorBox, error.message);
    }
  });

  memberList?.addEventListener("click", async (event) => {
    const edit = event.target.closest("[data-edit-member]");
    if (edit) {
      openMember(context.team.members.find((member) => member.member_id === edit.dataset.editMember));
      return;
    }
    const remove = event.target.closest("[data-delete-member]");
    if (!remove || !window.confirm("Remove this member from the team?")) return;
    try {
      context.team = await window.BuildBenchAuth.request(
        `/api/team/members/${encodeURIComponent(remove.dataset.deleteMember)}`,
        { method: "DELETE" },
      );
    } catch (error) {
      // DELETE returns a small acknowledgement, then reload the canonical roster.
      if (error.status) {
        message(notice, error.message);
        return;
      }
    }
    window.BuildBenchAuth.clearSession();
    context = await window.BuildBenchAuth.getSession(true);
    message(notice, "Team member removed.");
    render();
  });

  refresh().catch((error) => {
    loading.textContent = error.message || "Team details could not be loaded.";
  });
})();
