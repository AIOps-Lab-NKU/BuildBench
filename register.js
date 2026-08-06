(function () {
  "use strict";

  const form = document.querySelector("[data-registration-form]");
  const members = document.querySelector("[data-member-list]");
  const addMember = document.querySelector("[data-add-member]");
  const count = document.querySelector("[data-team-count]");
  const errorBox = document.querySelector("[data-form-error]");
  const submitButton = document.querySelector("[data-register-submit]");
  const template = document.querySelector("[data-member-template]");
  const MAX_ADDITIONAL_MEMBERS = 4;
  const t = (value) => window.BuildBenchI18n?.t(value) || value;

  function setError(message) {
    errorBox.hidden = !message;
    errorBox.textContent = message || "";
    if (message) errorBox.focus();
  }

  function rows() {
    return Array.from(members.querySelectorAll("[data-member-row]"));
  }

  function updateCount() {
    const total = 1 + rows().length;
    count.textContent = `${total} / 5`;
    addMember.disabled = rows().length >= MAX_ADDITIONAL_MEMBERS;
    rows().forEach((row, index) => {
      row.querySelector("[data-member-number]").textContent = String(index + 2);
      row.querySelectorAll("input").forEach((input) => {
        const field = input.dataset.memberField;
        input.name = `member-${index + 2}-${field}`;
      });
    });
  }

  function addMemberRow() {
    if (rows().length >= MAX_ADDITIONAL_MEMBERS) return;
    members.append(template.content.cloneNode(true));
    const row = rows().at(-1);
    const nameInput = row?.querySelector('[data-member-field="name"]');
    const emailInput = row?.querySelector('[data-member-field="email"]');
    const institutionInput = row?.querySelector('[data-member-field="institution"]');
    if (nameInput) nameInput.placeholder = t("Enter the member's full name");
    if (emailInput) emailInput.placeholder = t("Enter the member email");
    if (institutionInput) institutionInput.placeholder = t("University, company, or organization");
    updateCount();
    window.lucide?.createIcons({ attrs: { "stroke-width": 1.8 } });
    row?.querySelector("input")?.focus();
  }

  addMember?.addEventListener("click", addMemberRow);
  members?.addEventListener("click", (event) => {
    const remove = event.target.closest("[data-remove-member]");
    if (!remove) return;
    remove.closest("[data-member-row]")?.remove();
    updateCount();
  });

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    setError("");
    const data = new FormData(form);
    if (data.get("password") !== data.get("confirm_password")) {
      setError("Passwords do not match.");
      return;
    }
    const teamMembers = rows().map((row) => ({
      name: row.querySelector('[data-member-field="name"]').value,
      email: row.querySelector('[data-member-field="email"]').value,
      institution: row.querySelector('[data-member-field="institution"]').value,
    }));
    const payload = {
      captain: {
        name: data.get("captain_name"),
        email: data.get("captain_email"),
        institution: data.get("captain_institution"),
        password: data.get("password"),
      },
      team: {
        name: data.get("team_name"),
        members: teamMembers,
      },
      accept_rules: data.get("accept_rules") === "on",
    };
    submitButton.disabled = true;
    submitButton.textContent = t("Creating team…");
    try {
      await window.BuildBenchAuth.request("/api/auth/register", {
        method: "POST",
        json: payload,
      });
      window.BuildBenchAuth.clearSession();
      await window.BuildBenchAuth.getSession(true);
      window.location.assign("team.html?registered=1");
    } catch (error) {
      setError(error.message || "Registration could not be completed.");
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = t("Create team account");
    }
  });

  updateCount();
})();
