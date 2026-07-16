const menuButton = document.querySelector("[data-menu-button]");
const nav = document.querySelector("[data-nav]");
const siteHeader = document.querySelector(".site-header");
const localNavLinks = Array.from(document.querySelectorAll('.page-rail nav a[href^="#"]'));

function translate(value) {
  return window.BuildBenchI18n?.t(value) || value;
}

function renderIcons() {
  window.lucide?.createIcons({ attrs: { "stroke-width": 1.8 } });
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

document.querySelectorAll(".site-nav a").forEach((link) => {
  link.addEventListener("click", () => setMenu(false));
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") setMenu(false);
});

window.addEventListener("resize", () => {
  updateMobileNavGeometry();
  if (window.innerWidth > 1080) setMenu(false);
});

window.addEventListener("buildbench:languagechange", () => {
  updateMobileNavGeometry();
  setMenu(menuButton?.getAttribute("aria-expanded") === "true");
});

if ("IntersectionObserver" in window && localNavLinks.length) {
  const sections = Array.from(document.querySelectorAll(".page-document section[id]"));
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (!visible) return;
      localNavLinks.forEach((link) => {
        link.classList.toggle("active", link.getAttribute("href") === `#${visible.target.id}`);
      });
    },
    { rootMargin: "-24% 0px -64%", threshold: [0, 0.1, 0.3] },
  );

  sections.forEach((section) => observer.observe(section));
}

const boardRows = Array.from(document.querySelectorAll(".leaderboard-table tbody tr"));
const boardFilters = Array.from(document.querySelectorAll("[data-board-filter]"));

function applyBoardFilter(direction) {
  if (!boardRows.length) return;

  const tbody = boardRows[0].parentElement;
  const sortedRows = [...boardRows].sort(
    (a, b) => Number(b.dataset.rate) - Number(a.dataset.rate),
  );

  let rank = 0;
  sortedRows.forEach((row) => {
    const visible = direction === "all" || row.dataset.direction === direction;
    row.hidden = !visible;
    if (visible) {
      rank += 1;
      row.querySelector("[data-rank]").textContent = String(rank);
    }
    tbody.appendChild(row);
  });

  boardFilters.forEach((button) => {
    const active = button.dataset.boardFilter === direction;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });

  const visibleRows = sortedRows.filter((row) => !row.hidden);
  const packageCount = direction === "forward" ? 163 : direction === "reverse" ? 105 : 268;
  const modelCount = new Set(visibleRows.map((row) => row.querySelector('th[scope="row"]').textContent)).size;
  const bestRate = Math.max(...visibleRows.map((row) => Number(row.dataset.rate)));

  const packageStat = document.querySelector("[data-board-packages]");
  const modelStat = document.querySelector("[data-board-models]");
  const bestStat = document.querySelector("[data-board-best]");
  if (packageStat) packageStat.textContent = String(packageCount);
  if (modelStat) modelStat.textContent = String(modelCount);
  if (bestStat) bestStat.textContent = `${bestRate.toFixed(2)}%`;
}

boardFilters.forEach((button) => {
  button.addEventListener("click", () => applyBoardFilter(button.dataset.boardFilter));
});

if (boardRows.length) applyBoardFilter("all");

window.addEventListener("DOMContentLoaded", () => {
  updateMobileNavGeometry();
  renderIcons();
});
