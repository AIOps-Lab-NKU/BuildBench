(() => {
  const legacyHost = "aiops-lab-nku.github.io";
  const legacyBasePath = "/BuildBench";
  const currentPath = window.location.pathname;
  const normalizedPath = currentPath.toLowerCase();
  const normalizedBasePath = legacyBasePath.toLowerCase();

  if (window.location.hostname.toLowerCase() !== legacyHost) return;
  if (
    normalizedPath !== normalizedBasePath &&
    !normalizedPath.startsWith(`${normalizedBasePath}/`)
  ) {
    return;
  }

  const relativePath = currentPath.slice(legacyBasePath.length) || "/";
  const destination = new URL(
    `https://matrix.cstcloud.cn/build-bench${relativePath}`,
  );
  destination.search = window.location.search;
  destination.hash = window.location.hash;
  window.location.replace(destination.href);
})();

const menuButton = document.querySelector("[data-menu-button]");
const nav = document.querySelector("[data-nav]");
const siteHeader = document.querySelector(".site-header");
const navMore = document.querySelector("[data-nav-more]");
const navMoreButton = document.querySelector("[data-nav-more-toggle]");
const localNavLinks = Array.from(document.querySelectorAll('.page-rail nav a[href^="#"]'));

function translate(value) {
  return window.BuildBenchI18n?.t(value) || value;
}

function renderIcons() {
  window.lucide?.createIcons({ attrs: { "stroke-width": 1.8 } });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderAccountState(account, session) {
  const teamName = session?.team?.name ? String(session.team.name) : "";
  const stateKey = teamName ? `team:${teamName}` : "anonymous";
  if (account.dataset.accountState === stateKey) return;

  if (teamName) {
    account.innerHTML = `
      <a href="team.html" class="account-action account-action--team account-team-link">
        <i data-lucide="users" aria-hidden="true"></i>
        <span>${escapeHtml(teamName)}</span>
      </a>
      <a class="account-action account-action--primary" href="my-submissions.html">${translate("My Submissions")}</a>
      <button class="account-action account-action--danger" type="button" data-account-signout>${translate("Sign out")}</button>
    `;
    account.querySelector("[data-account-signout]")?.addEventListener("click", async () => {
      try {
        await window.BuildBenchAuth.logout();
      } finally {
        window.location.assign("index.html");
      }
    });
  } else {
    account.innerHTML = `
      <a class="account-action account-action--secondary" href="login.html">${translate("Sign in")}</a>
      <a class="account-action account-action--primary account-register-link" href="register.html">${translate("Register team")}</a>
    `;
  }
  account.dataset.accountState = stateKey;
  account.hidden = false;
  renderIcons();
}

async function renderAccountNavigation() {
  const actions = document.querySelector(".header-actions");
  if (!actions) return;
  let account = actions.querySelector("[data-account-navigation]");
  if (!account) {
    account = document.createElement("div");
    account.className = "account-navigation";
    account.dataset.accountNavigation = "";
    actions.append(account);
  }
  if (account.dataset.accountHydrating === "true") return;
  account.dataset.accountHydrating = "true";

  const hint = window.BuildBenchAuth?.getSessionHint?.();
  const hintedSession = hint?.authenticated
    ? { team: { name: hint.team_name } }
    : null;
  renderAccountState(account, hintedSession);

  const session = await window.BuildBenchAuth?.getSession?.();
  renderAccountState(account, session);
  delete account.dataset.accountHydrating;
}

function setMoreMenu(open) {
  if (!navMore || !navMoreButton) return;
  navMore.classList.toggle("open", open);
  navMoreButton.setAttribute("aria-expanded", String(open));
}

function setMenu(open) {
  if (!menuButton || !nav) return;

  updateMobileNavGeometry();
  menuButton.setAttribute("aria-expanded", String(open));
  menuButton.setAttribute(
    "aria-label",
    translate(open ? "Close navigation" : "Open navigation"),
  );
  menuButton.setAttribute("title", translate(open ? "Close navigation" : "Open navigation"));
  nav.classList.toggle("open", open);
  document.body.classList.toggle("menu-open", open);
  if (!open) setMoreMenu(false);
  menuButton.innerHTML = `<i data-lucide="${open ? "x" : "menu"}" aria-hidden="true"></i>`;
  renderIcons();
}

function updateMobileNavGeometry() {
  if (!siteHeader) return;
  const headerRect = siteHeader.getBoundingClientRect();
  const top = Math.max(0, Math.round(headerRect.height));
  const height = Math.max(0, Math.round(window.innerHeight - Math.max(0, headerRect.bottom)));
  document.documentElement.style.setProperty("--mobile-nav-top", `${top}px`);
  document.documentElement.style.setProperty("--mobile-nav-height", `${height}px`);
}

menuButton?.addEventListener("click", () => {
  setMenu(menuButton.getAttribute("aria-expanded") !== "true");
});

navMoreButton?.addEventListener("click", (event) => {
  event.stopPropagation();
  setMoreMenu(navMoreButton.getAttribute("aria-expanded") !== "true");
});

navMore?.addEventListener("focusout", (event) => {
  if (!navMore.contains(event.relatedTarget)) setMoreMenu(false);
});

document.querySelectorAll(".site-nav a").forEach((link) => {
  link.addEventListener("click", () => setMenu(false));
});

document.addEventListener("click", (event) => {
  if (!navMore?.contains(event.target)) setMoreMenu(false);
});

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  const moreWasOpen = navMoreButton?.getAttribute("aria-expanded") === "true";
  setMoreMenu(false);
  setMenu(false);
  if (moreWasOpen && window.innerWidth > 1080) navMoreButton?.focus();
});

window.addEventListener("resize", () => {
  updateMobileNavGeometry();
  if (window.innerWidth > 1080) setMenu(false);
});

window.addEventListener("buildbench:languagechange", () => {
  updateMobileNavGeometry();
  setMenu(menuButton?.getAttribute("aria-expanded") === "true");
  document.querySelector("[data-account-navigation]")?.remove();
  renderAccountNavigation();
});

if ("IntersectionObserver" in window && localNavLinks.length) {
  const sections = localNavLinks
    .map((link) => document.getElementById(decodeURIComponent(link.getAttribute("href").slice(1))))
    .filter((section, index, items) => section && items.indexOf(section) === index);

  const setActiveLocalSection = (sectionId) => {
    localNavLinks.forEach((link) => {
      const isActive = link.getAttribute("href") === `#${sectionId}`;
      link.classList.toggle("active", isActive);
      if (isActive) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  };

  const initialSectionId = window.location.hash.slice(1);
  setActiveLocalSection(
    sections.some((section) => section.id === initialSectionId) ? initialSectionId : sections[0]?.id,
  );

  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (!visible) return;
      setActiveLocalSection(visible.target.id);
    },
    { rootMargin: "-24% 0px -64%", threshold: [0, 0.1, 0.3] },
  );

  sections.forEach((section) => observer.observe(section));
}

renderAccountNavigation();

window.addEventListener("DOMContentLoaded", () => {
  updateMobileNavGeometry();
  renderIcons();
});
