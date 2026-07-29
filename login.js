(function () {
  "use strict";

  const form = document.querySelector("[data-login-form]");
  const errorBox = document.querySelector("[data-form-error]");
  const submitButton = document.querySelector("[data-login-submit]");

  function setError(message) {
    errorBox.hidden = !message;
    errorBox.textContent = message || "";
    if (message) errorBox.focus();
  }

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    setError("");
    const data = new FormData(form);
    submitButton.disabled = true;
    submitButton.textContent = "Signing in…";
    try {
      await window.BuildBenchAuth.request("/api/auth/login", {
        method: "POST",
        json: {
          email: data.get("email"),
          password: data.get("password"),
        },
      });
      window.BuildBenchAuth.clearSession();
      await window.BuildBenchAuth.getSession(true);
      window.location.replace(window.BuildBenchAuth.safeReturnUrl("my-submissions.html"));
    } catch (error) {
      setError(error.message || "Sign in failed.");
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Sign in";
    }
  });
})();
