(function () {
  "use strict";

  const LANGUAGE_KEY = "buildbench.language";
  const SUPPORTED_LANGUAGES = new Set(["en", "zh"]);
  const page = document.body?.dataset.page || "overview";
  const data = window.BuildBenchI18nData || { pages: {} };
  const pageTranslations = data.pages?.[page] || {};
  const originalText = new WeakMap();
  const originalAttributes = new WeakMap();
  const translatableAttributes = ["aria-label", "title", "placeholder", "alt"];

  const commonTranslations = Object.freeze({
    "Skip to main content": "跳转到主要内容",
    "Organizer preview": "主办方预览",
    "Accepted to the ICSE 2027 Competition Track. Rules and infrastructure are being finalized.":
      "已入选 ICSE 2027 竞赛赛道，规则与基础设施正在完善中。",
    "Build-Bench Challenge home": "Build-Bench Challenge 首页",
    "Open navigation": "打开导航",
    "Close navigation": "关闭导航",
    "Primary navigation": "主导航",
    Overview: "概览",
    Challenge: "竞赛任务",
    Submission: "提交",
    Evaluation: "评测",
    Rules: "规则",
    Timeline: "时间安排",
    FAQ: "常见问题",
    Leaderboard: "排行榜",
    "Footer navigation": "页脚导航",
    "Back to top": "返回顶部",
    "ICSE 2027 Competition Track": "ICSE 2027 竞赛赛道",
    "Nankai University": "南开大学",
    Microsoft: "微软",
    Draft: "草案",
    Proposed: "拟定",
    "Under review": "审核中",
    TBA: "待定",
    Intended: "拟定方案",
    Optional: "可选",
    Required: "必需",
    Public: "公开",
    Hidden: "隐藏",
    Current: "当前阶段",
    Planned: "计划中",
    "Next page": "下一页",
    English: "英文",
    Chinese: "中文",
    "Language selection": "语言选择",
    "My Submissions": "我的提交",
    "Sign in": "登录",
    "Sign out": "退出登录",
    "Register team": "注册团队",
  });

  const translations = Object.freeze({
    ...commonTranslations,
    ...pageTranslations,
  });

  function normalize(value) {
    return String(value || "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function readStoredLanguage() {
    try {
      return window.localStorage.getItem(LANGUAGE_KEY);
    } catch {
      return null;
    }
  }

  function writeStoredLanguage(language) {
    try {
      window.localStorage.setItem(LANGUAGE_KEY, language);
    } catch {
      // URL propagation remains available when storage is disabled.
    }
  }

  function requestedLanguage() {
    const queryLanguage = new URL(window.location.href).searchParams.get("lang");
    if (SUPPORTED_LANGUAGES.has(queryLanguage)) return queryLanguage;

    const storedLanguage = readStoredLanguage();
    return SUPPORTED_LANGUAGES.has(storedLanguage) ? storedLanguage : "en";
  }

  let currentLanguage = requestedLanguage();

  function translated(value, language = currentLanguage) {
    const key = normalize(value);
    if (language !== "zh" || !key) return key;
    return translations[key] || key;
  }

  function preserveOuterWhitespace(original, replacement) {
    const leading = original.match(/^\s*/)?.[0] || "";
    const trailing = original.match(/\s*$/)?.[0] || "";
    return `${leading}${replacement}${trailing}`;
  }

  function shouldSkipTextNode(node) {
    const parent = node.parentElement;
    if (!parent) return true;
    if (["SCRIPT", "STYLE", "CODE", "PRE", "NOSCRIPT"].includes(parent.tagName)) {
      return true;
    }
    return Boolean(parent.closest('[translate="no"], .notranslate, [data-i18n-control]'));
  }

  function translateTextNodes() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node = walker.nextNode();
    while (node) {
      if (!shouldSkipTextNode(node)) {
        if (!originalText.has(node)) originalText.set(node, node.nodeValue || "");
        const source = originalText.get(node) || "";
        const key = normalize(source);
        if (key) {
          const value = currentLanguage === "zh" ? translations[key] || key : key;
          node.nodeValue = preserveOuterWhitespace(source, value);
        }
      }
      node = walker.nextNode();
    }
  }

  function attributeSources(element) {
    if (!originalAttributes.has(element)) originalAttributes.set(element, new Map());
    return originalAttributes.get(element);
  }

  function translateAttributes() {
    document.querySelectorAll("[aria-label], [title], [placeholder], [alt]").forEach((element) => {
      if (element.closest("[data-i18n-control]")) return;
      const sources = attributeSources(element);
      translatableAttributes.forEach((attribute) => {
        if (!element.hasAttribute(attribute)) return;
        if (!sources.has(attribute)) sources.set(attribute, element.getAttribute(attribute) || "");
        const source = sources.get(attribute) || "";
        element.setAttribute(attribute, currentLanguage === "zh" ? translated(source) : source);
      });
    });
  }

  const originalTitle = normalize(document.title);
  const translatedMeta = Array.from(
    document.querySelectorAll('meta[name="description"], meta[property="og:title"], meta[property="og:description"]'),
  ).map((element) => ({ element, content: element.getAttribute("content") || "" }));

  function translateMetadata() {
    document.title = currentLanguage === "zh" ? translated(originalTitle) : originalTitle;
    translatedMeta.forEach(({ element, content }) => {
      element.setAttribute("content", currentLanguage === "zh" ? translated(content) : content);
    });
  }

  function isInternalHtmlLink(link) {
    const raw = link.getAttribute("href") || "";
    if (!raw || raw.startsWith("#") || /^(mailto:|tel:|javascript:)/i.test(raw)) return false;
    try {
      const target = new URL(raw, window.location.href);
      const sameSite =
        target.protocol === "file:" ||
        (target.protocol === window.location.protocol && target.host === window.location.host);
      return sameSite && target.pathname.toLowerCase().endsWith(".html");
    } catch {
      return false;
    }
  }

  function updateInternalLinks() {
    document.querySelectorAll("a[href]").forEach((link) => {
      if (!isInternalHtmlLink(link)) return;
      const raw = link.getAttribute("href") || "";
      const absolute = /^(?:[a-z]+:|\/\/)/i.test(raw);
      const target = new URL(raw, window.location.href);
      if (currentLanguage === "zh") target.searchParams.set("lang", "zh");
      else target.searchParams.delete("lang");

      if (absolute) {
        link.setAttribute("href", target.href);
        return;
      }

      const path = raw.split(/[?#]/, 1)[0];
      const query = target.searchParams.toString();
      link.setAttribute("href", `${path}${query ? `?${query}` : ""}${target.hash}`);
    });
  }

  function updateCurrentUrl() {
    try {
      const url = new URL(window.location.href);
      if (currentLanguage === "zh") url.searchParams.set("lang", "zh");
      else url.searchParams.delete("lang");
      window.history.replaceState(window.history.state, "", url.href);
    } catch {
      // file:// previews can restrict history updates; decorated links still preserve language.
    }
  }

  function renderLanguageControl() {
    const control = document.querySelector("[data-language-control]");
    if (!control) return;
    control.setAttribute("aria-label", currentLanguage === "zh" ? "语言选择" : "Language selection");
    control.querySelectorAll("[data-language-option]").forEach((button) => {
      const active = button.dataset.languageOption === currentLanguage;
      button.setAttribute("aria-pressed", String(active));
      button.classList.toggle("active", active);
    });
  }

  function applyLanguage() {
    document.documentElement.lang = currentLanguage === "zh" ? "zh-CN" : "en";
    document.body.dataset.language = currentLanguage;
    translateTextNodes();
    translateAttributes();
    translateMetadata();
    updateInternalLinks();
    renderLanguageControl();
  }

  function setLanguage(language, options = {}) {
    if (!SUPPORTED_LANGUAGES.has(language)) return;
    currentLanguage = language;
    writeStoredLanguage(language);
    if (options.updateUrl !== false) updateCurrentUrl();
    applyLanguage();
    window.dispatchEvent(
      new CustomEvent("buildbench:languagechange", { detail: { language: currentLanguage } }),
    );
  }

  function createLanguageControl() {
    if (document.querySelector("[data-language-control]")) return;
    const menuButton = document.querySelector("[data-menu-button]");
    const nav = document.querySelector("[data-nav]");
    if (!menuButton || !nav) return;

    const actions = document.createElement("div");
    actions.className = "header-actions";
    nav.insertAdjacentElement("afterend", actions);
    actions.appendChild(menuButton);

    const control = document.createElement("div");
    control.className = "language-control";
    control.setAttribute("role", "group");
    control.setAttribute("data-language-control", "");
    control.setAttribute("data-i18n-control", "");
    control.innerHTML = `
      <button type="button" lang="en" data-language-option="en" aria-pressed="false">EN</button>
      <button type="button" lang="zh-CN" data-language-option="zh" aria-pressed="false">中文</button>
    `;
    control.addEventListener("click", (event) => {
      const button = event.target.closest("[data-language-option]");
      if (!button) return;
      setLanguage(button.dataset.languageOption);
    });
    actions.appendChild(control);

    // Create the account controls in the same synchronous pass as the
    // language control. app.js subsequently verifies the server session and
    // hydrates this shell, but the header never renders a language-only state.
    const account = document.createElement("div");
    account.className = "account-navigation";
    account.setAttribute("data-account-navigation", "");
    account.innerHTML = `
      <a class="account-action account-action--secondary" href="login.html">Sign in</a>
      <a class="account-action account-action--primary account-register-link" href="register.html">Register team</a>
    `;
    actions.appendChild(account);
  }

  function audit() {
    const untranslated = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node = walker.nextNode();
    while (node) {
      if (!shouldSkipTextNode(node)) {
        const source = normalize(originalText.get(node) || node.nodeValue || "");
        if (source && /[A-Za-z]{3}/.test(source) && !translations[source]) untranslated.push(source);
      }
      node = walker.nextNode();
    }
    return Array.from(new Set(untranslated));
  }

  window.BuildBenchI18n = Object.freeze({
    audit,
    getLanguage: () => currentLanguage,
    hasTranslation: (value) => Boolean(translations[normalize(value)]),
    setLanguage,
    t: (value) => (currentLanguage === "zh" ? translated(value) : normalize(value)),
  });

  createLanguageControl();
  writeStoredLanguage(currentLanguage);
  updateCurrentUrl();
  applyLanguage();
})();
