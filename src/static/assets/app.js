// --- Localization Dictionary ---------------------------------------------
const I18N = {
  en: {
    docTitle: "Futures Trading Assistant",
    headerTitle: "Futures Trading Assistant",
    headerSubtitle: "Multi-Domain Intelligence",
    newChat: "New chat",
    conversationsLabel: "Recent conversations",
    noConversations: "No conversations yet",
    deleteTitle: "Delete conversation",
    renameTitle: "Rename conversation",
    renamePrompt: "Rename this conversation:",
    pinTitle: "Pin conversation (keep it from being auto-deleted)",
    unpinTitle: "Unpin conversation",
    welcomeTitle: "👋 How can I help you today?",
    welcomeText: "Ask a question about your futures trading documents. Try one of these:",
    placeholder: "Type your question...",
    hint: "Press Enter to send · Shift+Enter for a new line",
    settingsTitle: "Settings",
    themeDark: "Dark Mode",
    themeLight: "Light Mode",
    suggestions: [
      "What is the difference between initial and maintenance margin?",
      "How does a futures contract differ from a forward contract?",
      "What happens during a margin call?",
      "Explain daily mark-to-market settlement.",
    ],
    errorAuth: "Authentication error: the server has no valid API key.",
    errorHttp: (s) => "Something went wrong (HTTP " + s + ").",
    errorNetwork: "⚠️ Could not reach the server. Is it running?",
    statusRouting: "Routing…",
    statusPreparing: "Preparing search…",
    statusExpanding: "Expanding queries…",
    statusRetrieving: "Searching documents…",
    statusGrading: "Checking relevance…",
    statusRewriting: "Refining search…",
    statusAnswering: "Writing answer…",
    setupTitle: "Welcome — one quick step",
    setupText: "To use the hosted Gemini model, paste your Google AI Studio API key.",
    setupPlaceholder: "Paste your Gemini API key",
    setupSubmit: "Save & continue",
    setupSaving: "Verifying…",
    setupInvalid: "That key was rejected. Please check it and try again.",
    setupError: "Could not save the key. Please try again.",
  },
  hu: {
    docTitle: "Futures Kereskedési Tudástár",
    headerTitle: "Futures Kereskedési Tudástár",
    headerSubtitle: "Többdomaines Intelligencia",
    newChat: "Új beszélgetés",
    conversationsLabel: "Legutóbbi beszélgetések",
    noConversations: "Még nincsenek beszélgetések",
    deleteTitle: "Beszélgetés törlése",
    renameTitle: "Beszélgetés átnevezése",
    renamePrompt: "Nevezze át ezt a beszélgetést:",
    pinTitle: "Beszélgetés rögzítése (nem törlődik automatikusan)",
    unpinTitle: "Rögzítés feloldása",
    welcomeTitle: "👋 Miben segíthetek ma?",
    welcomeText: "Tegyen fel kérdést a határidős kereskedési dokumentumaival kapcsolatban. Próbálja ki ezeket:",
    placeholder: "Írja be a kérdését...",
    hint: "Küldés: Enter · Új sor: Shift+Enter",
    settingsTitle: "Beállítások",
    themeDark: "Sötét Mód",
    themeLight: "Világos Mód",
    suggestions: [
      "Mi a különbség a kezdeti és a fenntartási letét között?",
      "Miben különbözik a futures ügylet a forward ügylettől?",
      "Mi történik egy letétfeltöltési felszólítás (margin call) során?",
      "Magyarázza el a napi piaci elszámolás (mark-to-market) folyamatát.",
    ],
    errorAuth: "Hitelesítési hiba: a szervernek nincs érvényes API-kulcsa.",
    errorHttp: (s) => "Hiba történt (HTTP " + s + ").",
    errorNetwork: "⚠️ A szerver nem érhető el. Fut egyáltalán?",
    statusRouting: "Irányítás…",
    statusPreparing: "Keresés előkészítése…",
    statusExpanding: "Lekérdezések bővítése…",
    statusRetrieving: "Dokumentumok keresése…",
    statusGrading: "Relevancia ellenőrzése…",
    statusRewriting: "Keresés finomítása…",
    statusAnswering: "Válasz írása…",
    setupTitle: "Üdvözöljük — egy gyors lépés",
    setupText: "A hosztolt Gemini modell használatához illessze be a Google AI Studio API-kulcsát.",
    setupPlaceholder: "Illessze be a Gemini API-kulcsot",
    setupSubmit: "Mentés és folytatás",
    setupSaving: "Ellenőrzés…",
    setupInvalid: "A kulcsot elutasította a szolgáltató. Ellenőrizze és próbálja újra.",
    setupError: "A kulcs mentése nem sikerült. Próbálja újra.",
  },
};

let LANG = "en";
let T = I18N.en;
let currentAppName = "Futures Trading Assistant";

// --- DOM Elements --------------------------------------------------------
const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("send");
const newChatBtn = document.getElementById("new-chat");
const convEl = document.getElementById("conversations");
const activeConvTitleEl = document.getElementById("active-conv-title");
const appBrandNameEl = document.getElementById("app-brand-name");
const appBrandSubtitleEl = document.getElementById("app-brand-subtitle");
const sidebarEl = document.getElementById("sidebar");
const btnSidebarToggle = document.getElementById("btn-sidebar-toggle");

// Theme
const btnThemeToggle = document.getElementById("btn-theme-toggle");
const themeIconEl = document.getElementById("theme-icon");
const themeLabelEl = document.getElementById("theme-label");

// Settings Modal
const btnSettings = document.getElementById("btn-settings");
const modalSettings = document.getElementById("modal-settings");
const settingsClose = document.getElementById("settings-close");
const settingAppName = document.getElementById("setting-app-name");
const settingBtnSaveName = document.getElementById("setting-btn-save-name");
const settingNameStatus = document.getElementById("setting-name-status");
const settingTheme = document.getElementById("setting-theme");
const settingLanguage = document.getElementById("setting-language");
const stProvider = document.getElementById("st-provider");
const stModel = document.getElementById("st-model");
const stStorage = document.getElementById("st-storage");
const stReady = document.getElementById("st-ready");
const btnRelaunchWizard = document.getElementById("btn-relaunch-wizard");

// Onboarding Modal
const modalOnboarding = document.getElementById("modal-onboarding");
const onboardingClose = document.getElementById("onboarding-close");
const onboardingStepPill = document.getElementById("onboarding-step-pill");
const obBtnPrev = document.getElementById("ob-btn-prev");
const obBtnNext = document.getElementById("ob-btn-next");
const obBtnFinish = document.getElementById("ob-btn-finish");
const obModelName = document.getElementById("ob-model-name");
const obGeminiKeyGroup = document.getElementById("ob-gemini-key-group");
const obApiKey = document.getElementById("ob-api-key");
const obS3CredsContainer = document.getElementById("ob-s3-creds-container");
const obLocalCredsContainer = document.getElementById("ob-local-creds-container");
const obAwsAccessKey = document.getElementById("ob-aws-access-key");
const obAwsSecretKey = document.getElementById("ob-aws-secret-key");
const obAwsRegion = document.getElementById("ob-aws-region");
const obAwsBucket = document.getElementById("ob-aws-bucket");
const obStatus = document.getElementById("ob-status");

// Profiles & Multi-Tenant
let profiles = [];
let currentProfileId = "default";
const profileSelectEl = document.getElementById("profile-select");
const btnProfileConfig = document.getElementById("btn-profile-config");
const btnKbManager = document.getElementById("btn-kb-manager");
const btnBenchmarks = document.getElementById("btn-benchmarks");

// Modals: Profile, KB, Benchmarks
const modalProfile = document.getElementById("modal-profile");
const profClose = document.getElementById("prof-close");
const profIdEl = document.getElementById("prof-id");
const profNameEl = document.getElementById("prof-name");
const profDescEl = document.getElementById("prof-desc");
const profPromptEl = document.getElementById("prof-prompt");
const profGuardCitationsEl = document.getElementById("prof-guard-citations");
const profGuardPhiEl = document.getElementById("prof-guard-phi");
const profCreateNewBtn = document.getElementById("prof-create-new");
const profSaveBtn = document.getElementById("prof-save");
const profStatusEl = document.getElementById("prof-status");

const modalKb = document.getElementById("modal-kb");
const kbClose = document.getElementById("kb-close");
const kbActiveProfileEl = document.getElementById("kb-active-profile");
const kbFileInput = document.getElementById("kb-file-input");
const kbUploadBtn = document.getElementById("kb-upload-btn");
const kbUploadStatus = document.getElementById("kb-upload-status");
const kbDocsList = document.getElementById("kb-docs-list");

const modalBenchmarks = document.getElementById("modal-benchmarks");
const bmClose = document.getElementById("bm-close");
const bmSummaryChips = document.getElementById("bm-summary-chips");
const bmReportContent = document.getElementById("bm-report-content");

const setupOverlay = document.getElementById("setup-overlay");
const setupKeyEl = document.getElementById("setup-key");
const setupSubmitEl = document.getElementById("setup-submit");
const setupErrorEl = document.getElementById("setup-error");

// State
let currentId = null;
let busy = false;
let currentStep = 1;

// --- Theme Management ----------------------------------------------------
function getSavedTheme() {
  return localStorage.getItem("rag_theme") || "dark";
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("rag_theme", theme);
  if (theme === "dark") {
    themeIconEl.textContent = "🌙";
    themeLabelEl.textContent = T.themeDark;
    if (settingTheme) settingTheme.value = "dark";
  } else {
    themeIconEl.textContent = "☀️";
    themeLabelEl.textContent = T.themeLight;
    if (settingTheme) settingTheme.value = "light";
  }
}

btnThemeToggle.addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  applyTheme(current === "dark" ? "light" : "dark");
});

if (settingTheme) {
  settingTheme.addEventListener("change", (e) => applyTheme(e.target.value));
}

// Mobile sidebar toggle
if (btnSidebarToggle) {
  btnSidebarToggle.addEventListener("click", () => {
    sidebarEl.classList.toggle("open");
  });
}

// --- App Name & Brand Management -----------------------------------------
function updateAppNameUI(name) {
  currentAppName = name || "Futures Trading Assistant";
  if (appBrandNameEl) appBrandNameEl.textContent = currentAppName;
  if (activeConvTitleEl && !activeConvTitleEl.dataset.isCustom) {
    activeConvTitleEl.textContent = currentAppName;
  }
  document.title = currentAppName;
  if (settingAppName) settingAppName.value = currentAppName;
}

// --- Language & Suggestions ----------------------------------------------
function renderSuggestions() {
  const box = document.getElementById("suggestions");
  if (!box) return;
  box.innerHTML = "";
  for (const text of T.suggestions) {
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.textContent = text;
    box.appendChild(chip);
  }
}

function applyLanguage() {
  document.documentElement.lang = LANG;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (typeof T[key] === "string") el.textContent = T[key];
  });
  if (inputEl) inputEl.placeholder = T.placeholder;
  if (setupKeyEl) setupKeyEl.placeholder = T.setupPlaceholder;
  if (settingLanguage) settingLanguage.value = LANG;
  applyTheme(getSavedTheme());
  renderSuggestions();
}

if (settingLanguage) {
  settingLanguage.addEventListener("change", (e) => {
    LANG = e.target.value;
    T = I18N[LANG] || I18N.en;
    applyLanguage();
  });
}

// --- Utilities -----------------------------------------------------------
function newId() {
  const rnd = window.crypto && crypto.randomUUID
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2, 11);
  return "web-" + rnd;
}

function autoGrow() {
  inputEl.style.height = "auto";
  inputEl.style.height = Math.min(inputEl.scrollHeight, 160) + "px";
}
inputEl.addEventListener("input", autoGrow);

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setBusy(state) {
  busy = state;
  sendBtn.disabled = state;
  inputEl.disabled = state;
}

function stageLabel(stage) {
  const key = "status" + stage.charAt(0).toUpperCase() + stage.slice(1);
  return T[key] || null;
}

// --- Safe Markdown Renderer ----------------------------------------------
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderInline(s) {
  const codes = [];
  s = s.replace(/`([^`]+)`/g, (_, c) => {
    codes.push(c);
    return "\u0000" + (codes.length - 1) + "\u0000";
  });
  s = s.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    (_, t, u) => '<a href="' + u + '" target="_blank" rel="noopener noreferrer">' + t + "</a>"
  );
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/__([^_]+)__/g, "<strong>$1</strong>");
  s = s.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, "$1<em>$2</em>");
  s = s.replace(/(^|[^_\w])_([^_\n]+)_(?!_)/g, "$1<em>$2</em>");
  s = s.replace(/\u0000(\d+)\u0000/g, (_, i) => "<code>" + codes[+i] + "</code>");
  return s;
}

function renderMarkdown(src) {
  const lines = escapeHtml(src).replace(/\r\n/g, "\n").split("\n");
  const out = [];
  const stack = [];
  let i = 0;

  const closeTo = (depth) => {
    while (stack.length > depth) out.push("</" + stack.pop() + ">");
  };

  while (i < lines.length) {
    const line = lines[i];

    if (/^\s*```/.test(line)) {
      closeTo(0);
      const langMatch = line.match(/^\s*```([a-zA-Z0-9_-]*)/);
      const lang = langMatch && langMatch[1] ? langMatch[1] : "code";
      const buf = [];
      i++;
      while (i < lines.length && !/^\s*```/.test(lines[i])) buf.push(lines[i++]);
      i++;
      out.push(
        `<div class="code-block-wrapper">` +
        `<div class="code-block-header"><span class="code-lang">${lang}</span>` +
        `<button class="code-copy-btn" onclick="copyCode(this)">Copy</button></div>` +
        `<pre><code>${buf.join("\n")}</code></pre></div>`
      );
      continue;
    }

    if (/^\s*$/.test(line)) {
      closeTo(0);
      i++;
      continue;
    }

    const h = line.match(/^\s*(#{1,6})\s+(.*)$/);
    if (h) {
      closeTo(0);
      const lvl = Math.min(h[1].length, 3);
      out.push("<h" + lvl + ">" + renderInline(h[2]) + "</h" + lvl + ">");
      i++;
      continue;
    }

    const li = line.match(/^(\s*)([-*+]|\d+[.)])\s+(.*)$/);
    if (li) {
      const depth = Math.floor(li[1].replace(/\t/g, "  ").length / 2) + 1;
      const type = /\d/.test(li[2]) ? "ol" : "ul";
      while (stack.length > depth) out.push("</" + stack.pop() + ">");
      if (stack.length === depth && stack[depth - 1] !== type) {
        out.push("</" + stack.pop() + ">");
      }
      while (stack.length < depth) {
        out.push("<" + type + ">");
        stack.push(type);
      }
      out.push("<li>" + renderInline(li[3]) + "</li>");
      i++;
      continue;
    }

    const bq = line.match(/^\s*>\s?(.*)$/);
    if (bq) {
      closeTo(0);
      out.push("<blockquote>" + renderInline(bq[1]) + "</blockquote>");
      i++;
      continue;
    }

    closeTo(0);
    const para = [line];
    i++;
    while (
      i < lines.length &&
      !/^\s*$/.test(lines[i]) &&
      !/^\s*#{1,6}\s+/.test(lines[i]) &&
      !/^\s*([-*+]|\d+[.)])\s+/.test(lines[i]) &&
      !/^\s*```/.test(lines[i]) &&
      !/^\s*>\s?/.test(lines[i])
    ) {
      para.push(lines[i++]);
    }
    out.push("<p>" + para.map(renderInline).join("<br>") + "</p>");
  }
  closeTo(0);
  return out.join("\n");
}

window.copyCode = function (btn) {
  const wrapper = btn.closest(".code-block-wrapper");
  if (!wrapper) return;
  const codeEl = wrapper.querySelector("pre code");
  if (!codeEl) return;
  navigator.clipboard.writeText(codeEl.textContent || "").then(() => {
    btn.textContent = "Copied!";
    setTimeout(() => { btn.textContent = "Copy"; }, 2000);
  });
};

// --- Message Rendering & Welcome -----------------------------------------
function renderWelcome() {
  messagesEl.innerHTML = "";
  const welcome = document.createElement("div");
  welcome.className = "welcome";
  welcome.id = "welcome";

  const badge = document.createElement("div");
  badge.className = "welcome-badge";
  badge.textContent = "✦ AI Knowledge Platform";

  const h2 = document.createElement("h2");
  h2.textContent = T.welcomeTitle;

  const p = document.createElement("p");
  p.textContent = T.welcomeText;

  const sug = document.createElement("div");
  sug.className = "suggestions-grid";
  sug.id = "suggestions";

  welcome.append(badge, h2, p, sug);
  messagesEl.appendChild(welcome);
  renderSuggestions();
  if (activeConvTitleEl) {
    activeConvTitleEl.textContent = currentAppName;
    delete activeConvTitleEl.dataset.isCustom;
  }
}

function addMessage(role, text, opts) {
  opts = opts || {};
  const existing = messagesEl.querySelector(".welcome");
  if (existing) existing.remove();

  const row = document.createElement("div");
  row.className = "msg-row " + role;

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";

  if (opts.markdown) {
    bubble.innerHTML = renderMarkdown(text);
  } else {
    bubble.textContent = text;
  }

  row.appendChild(bubble);
  messagesEl.appendChild(row);
  scrollToBottom();
  return { row, bubble };
}

function renderSources(container, sources) {
  if (!sources || sources.length === 0) return;
  const card = document.createElement("div");
  card.className = "sources-card";

  const title = document.createElement("div");
  title.className = "sources-title";
  title.textContent = "Referenced Sources";
  card.appendChild(title);

  const list = document.createElement("div");
  list.className = "sources-list";
  for (const s of sources) {
    const pill = document.createElement("span");
    pill.className = "source-chip";
    pill.textContent = "📄 " + s.name + (s.page != null ? " (p. " + s.page + ")" : "");
    list.appendChild(pill);
  }
  card.appendChild(list);
  container.appendChild(card);
}

// --- Chat Streaming ------------------------------------------------------
async function send(question) {
  if (busy || !question.trim()) return;
  const q = question.trim();

  addMessage("user", q);
  inputEl.value = "";
  autoGrow();
  setBusy(true);

  if (activeConvTitleEl && !activeConvTitleEl.dataset.isCustom) {
    activeConvTitleEl.textContent = q.length > 32 ? q.slice(0, 32) + "…" : q;
  }

  const { bubble } = addMessage("bot", "");
  const statusPill = document.createElement("div");
  statusPill.className = "streaming-status-pill";
  statusPill.textContent = stageLabel("preparing") || "Preparing search…";

  const answer = document.createElement("div");
  answer.className = "answer-body";
  bubble.appendChild(statusPill);
  bubble.appendChild(answer);

  let raw = "";
  let done = null;

  try {
    const res = await fetch("/chat/events", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: q,
        session_id: currentId,
        profile_id: currentProfileId,
      }),
    });

    if (!res.ok || !res.body) {
      statusPill.remove();
      const detail = res.status === 401 ? T.errorAuth : T.errorHttp(res.status);
      bubble.textContent = "⚠️ " + detail;
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done: streamDone } = await reader.read();
      if (streamDone) break;
      buffer += decoder.decode(value, { stream: true });
      let nl;
      while ((nl = buffer.indexOf("\n")) >= 0) {
        const line = buffer.slice(0, nl).trim();
        buffer = buffer.slice(nl + 1);
        if (!line) continue;
        const event = JSON.parse(line);

        if (event.type === "status") {
          const label = stageLabel(event.stage);
          if (label) statusPill.textContent = label;
        } else if (event.type === "token") {
          if (raw === "") {
            const answering = stageLabel("answering");
            if (answering) statusPill.textContent = answering;
          }
          raw += event.text;
          answer.textContent = raw;
          scrollToBottom();
        } else if (event.type === "done") {
          done = event;
        } else if (event.type === "error") {
          statusPill.remove();
          const detail = event.code === "auth" ? T.errorAuth : (event.detail || T.errorHttp(500));
          bubble.textContent = "⚠️ " + detail;
          return;
        }
      }
    }

    statusPill.remove();
    let finalText = raw;
    if (done && done.note) finalText = done.note + "\n\n" + raw;
    answer.innerHTML = renderMarkdown(finalText);
    if (done) renderSources(bubble, done.sources);
    scrollToBottom();
    loadConversations();
  } catch (err) {
    statusPill.remove();
    if (!raw) bubble.textContent = T.errorNetwork;
  } finally {
    setBusy(false);
    inputEl.focus();
  }
}

sendBtn.addEventListener("click", () => send(inputEl.value));
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send(inputEl.value);
  }
});

messagesEl.addEventListener("click", (e) => {
  if (e.target.classList.contains("chip")) {
    send(e.target.textContent);
  }
});

newChatBtn.addEventListener("click", startNewChat);

function startNewChat() {
  currentId = newId();
  renderWelcome();
  highlightActive();
  inputEl.focus();
}

// --- Conversations & Sidebar ---------------------------------------------
function highlightActive() {
  convEl.querySelectorAll(".conv-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.id === currentId);
  });
}

function renderConversations(convs) {
  convEl.innerHTML = "";
  if (!convs || convs.length === 0) {
    const empty = document.createElement("div");
    empty.className = "conv-section-label";
    empty.textContent = T.noConversations;
    convEl.appendChild(empty);
    return;
  }

  for (const conv of convs) {
    const item = document.createElement("div");
    item.className = "conv-item";
    item.dataset.id = conv.id;

    if (conv.pinned) {
      const pinIcon = document.createElement("span");
      pinIcon.className = "conv-pin-icon";
      pinIcon.textContent = "📌";
      item.appendChild(pinIcon);
    }

    const title = document.createElement("span");
    title.className = "conv-title";
    title.textContent = conv.title || "Untitled";

    const pinBtn = document.createElement("button");
    pinBtn.className = "conv-btn";
    pinBtn.textContent = conv.pinned ? "📍" : "📌";
    pinBtn.title = conv.pinned ? T.unpinTitle : T.pinTitle;
    pinBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      togglePin(conv.id, !conv.pinned);
    });

    const renameBtn = document.createElement("button");
    renameBtn.className = "conv-btn";
    renameBtn.textContent = "✏️";
    renameBtn.title = T.renameTitle;
    renameBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      renameConversation(conv.id, conv.title);
    });

    const delBtn = document.createElement("button");
    delBtn.className = "conv-btn delete";
    delBtn.textContent = "🗑";
    delBtn.title = T.deleteTitle;
    delBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteConversation(conv.id);
    });

    item.append(title, pinBtn, renameBtn, delBtn);
    item.addEventListener("click", () => openConversation(conv.id, conv.title));
    convEl.appendChild(item);
  }
  highlightActive();
}

async function loadConversations() {
  try {
    const res = await fetch("/conversations");
    if (res.ok) renderConversations(await res.json());
  } catch (_) { /* ignore */ }
}

async function openConversation(id, title) {
  if (busy) return;
  currentId = id;
  if (activeConvTitleEl) {
    activeConvTitleEl.textContent = title || "Conversation";
    activeConvTitleEl.dataset.isCustom = "true";
  }
  try {
    const res = await fetch("/conversations/" + encodeURIComponent(id));
    if (!res.ok) return;
    const msgs = await res.json();
    messagesEl.innerHTML = "";
    if (msgs.length === 0) {
      renderWelcome();
    } else {
      for (const m of msgs) {
        const isUser = m.role === "human";
        addMessage(isUser ? "user" : "bot", m.content, { markdown: !isUser });
      }
    }
    highlightActive();
    scrollToBottom();
    inputEl.focus();
  } catch (_) { /* ignore */ }
}

async function deleteConversation(id) {
  try {
    await fetch("/conversations/" + encodeURIComponent(id), { method: "DELETE" });
  } catch (_) { /* ignore */ }
  if (id === currentId) startNewChat();
  loadConversations();
}

async function renameConversation(id, currentTitle) {
  const next = window.prompt(T.renamePrompt, currentTitle || "");
  if (next === null) return;
  const title = next.trim();
  if (!title || title === currentTitle) return;
  try {
    await fetch("/conversations/" + encodeURIComponent(id), {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
  } catch (_) { /* ignore */ }
  loadConversations();
}

async function togglePin(id, pinned) {
  try {
    await fetch("/conversations/" + encodeURIComponent(id) + "/pin", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pinned }),
    });
  } catch (_) { /* ignore */ }
  loadConversations();
}

// --- Onboarding Wizard Controller ----------------------------------------
function showOnboarding(step = 1) {
  currentStep = step;
  updateOnboardingStep();
  modalOnboarding.classList.add("show");
}

function updateOnboardingStep() {
  document.querySelectorAll(".wizard-step").forEach((el, idx) => {
    el.classList.toggle("active", idx + 1 === currentStep);
  });
  onboardingStepPill.textContent = `Step ${currentStep} of 4`;
  obBtnPrev.style.display = currentStep > 1 ? "block" : "none";
  obBtnNext.style.display = currentStep < 4 ? "block" : "none";
  obBtnFinish.style.display = currentStep === 4 ? "block" : "none";

  if (currentStep === 2) {
    const provider = document.querySelector('input[name="ob-provider"]:checked')?.value || "gemini";
    if (obGeminiKeyGroup) obGeminiKeyGroup.style.display = provider === "gemini" ? "block" : "none";
  }

  if (currentStep === 4) {
    const isS3 = document.querySelector('input[name="ob-storage"]:checked')?.value === "s3";
    if (obS3CredsContainer) obS3CredsContainer.style.display = isS3 ? "block" : "none";
    if (obLocalCredsContainer) obLocalCredsContainer.style.display = isS3 ? "none" : "block";
  }
}

// Language toggle inside wizard immediately switches UI dictionary
document.querySelectorAll('input[name="ob-lang"]').forEach((radio) => {
  radio.addEventListener("change", (e) => {
    LANG = e.target.value;
    T = I18N[LANG] || I18N.en;
    applyLanguage();
  });
});

// Provider toggle inside wizard
document.querySelectorAll('input[name="ob-provider"]').forEach((radio) => {
  radio.addEventListener("change", (e) => {
    const isGemini = e.target.value === "gemini";
    if (obGeminiKeyGroup) obGeminiKeyGroup.style.display = isGemini ? "block" : "none";
    if (obModelName) {
      obModelName.value = isGemini ? "gemini-3.5-flash-lite" : "qwen2.5:7b";
    }
  });
});

obBtnNext.addEventListener("click", () => {
  if (currentStep < 4) {
    currentStep++;
    updateOnboardingStep();
  }
});

obBtnPrev.addEventListener("click", () => {
  if (currentStep > 1) {
    currentStep--;
    updateOnboardingStep();
  }
});

onboardingClose.addEventListener("click", () => modalOnboarding.classList.remove("show"));

obBtnFinish.addEventListener("click", async () => {
  const lang = document.querySelector('input[name="ob-lang"]:checked')?.value || "en";
  const provider = document.querySelector('input[name="ob-provider"]:checked')?.value || "gemini";
  const model = obModelName ? obModelName.value.trim() : (provider === "gemini" ? "gemini-3.5-flash-lite" : "qwen2.5:7b");
  const storage = document.querySelector('input[name="ob-storage"]:checked')?.value || "local";
  const isS3 = storage === "s3";
  const apiKey = obApiKey ? obApiKey.value.trim() : "";
  const awsAccessKey = obAwsAccessKey ? obAwsAccessKey.value.trim() : "";
  const awsSecretKey = obAwsSecretKey ? obAwsSecretKey.value.trim() : "";
  const awsRegion = obAwsRegion ? obAwsRegion.value.trim() : "eu-central-1";
  const awsBucket = obAwsBucket ? obAwsBucket.value.trim() : "futures-rag-lab-docs";

  if (provider === "gemini" && !apiKey) {
    obStatus.textContent = "Google AI Studio API key is required for Gemini.";
    obStatus.className = "status-msg error";
    return;
  }

  if (isS3 && (!awsAccessKey || !awsSecretKey)) {
    obStatus.textContent = "AWS Access Key ID and Secret Access Key are required for S3.";
    obStatus.className = "status-msg error";
    return;
  }

  obStatus.textContent = "Configuring backend and validating connection…";
  obStatus.className = "status-msg";
  obBtnFinish.disabled = true;

  try {
    const payload = {
      language: lang,
      llm_provider: provider,
      model: model,
      api_key: apiKey || null,
      use_s3_storage: isS3,
      aws_access_key_id: isS3 ? awsAccessKey : null,
      aws_secret_access_key: isS3 ? awsSecretKey : null,
      aws_region: isS3 ? awsRegion : null,
      aws_s3_bucket_name: isS3 ? awsBucket : null,
      app_name: currentAppName,
    };

    const res = await fetch("/config/setup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      obStatus.textContent = "Setup complete! Launching assistant…";
      obStatus.className = "status-msg success";
      setTimeout(async () => {
        modalOnboarding.classList.remove("show");
        LANG = lang;
        T = I18N[LANG] || I18N.en;
        applyLanguage();
        await loadBackendStatus();
        await loadProfiles();
        inputEl.focus();
      }, 700);
    } else {
      const err = await res.json().catch(() => ({}));
      obStatus.textContent = err.detail || "Configuration failed. Please check credentials.";
      obStatus.className = "status-msg error";
    }
  } catch (_) {
    obStatus.textContent = "Network error connecting to configuration service.";
    obStatus.className = "status-msg error";
  } finally {
    obBtnFinish.disabled = false;
  }
});

// --- Settings Modal Controller -------------------------------------------
btnSettings.addEventListener("click", async () => {
  modalSettings.classList.add("show");
  settingNameStatus.textContent = "";
  await loadBackendStatus();
});

settingsClose.addEventListener("click", () => modalSettings.classList.remove("show"));

settingBtnSaveName.addEventListener("click", async () => {
  const newName = settingAppName.value.trim();
  if (!newName) return;
  settingNameStatus.textContent = "Saving…";
  settingNameStatus.className = "status-msg";
  try {
    const res = await fetch("/config/app-name", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ app_name: newName }),
    });
    if (res.ok) {
      updateAppNameUI(newName);
      settingNameStatus.textContent = "Brand name updated successfully!";
      settingNameStatus.className = "status-msg success";
    } else {
      settingNameStatus.textContent = "Failed to update name.";
      settingNameStatus.className = "status-msg error";
    }
  } catch (_) {
    settingNameStatus.textContent = "Network error updating name.";
    settingNameStatus.className = "status-msg error";
  }
});

btnRelaunchWizard.addEventListener("click", () => {
  modalSettings.classList.remove("show");
  showOnboarding(1);
});

async function loadBackendStatus() {
  try {
    const res = await fetch("/config");
    if (res.ok) {
      const cfg = await res.json();
      if (cfg.app_name) updateAppNameUI(cfg.app_name);
      if (stProvider) stProvider.textContent = cfg.provider || "gemini";
      if (stModel) stModel.textContent = cfg.model || "gemini-2.5-flash";
      if (stStorage) stStorage.textContent = cfg.use_s3_storage ? "Amazon S3 Bucket" : "Local Filesystem";
      if (stReady) {
        stReady.textContent = cfg.ready ? "Active & Ready" : (cfg.needs_api_key ? "Needs API Key" : "Initializing");
        stReady.className = "status-badge " + (cfg.ready ? "ready" : "not-ready");
      }
    }
  } catch (_) { /* ignore */ }
}

// --- Profiles Controller -------------------------------------------------
async function loadProfiles() {
  try {
    const res = await fetch("/profiles");
    if (res.ok) {
      const data = await res.json();
      profiles = data.profiles || [];
      profileSelectEl.innerHTML = "";
      for (const p of profiles) {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = p.name || p.id;
        profileSelectEl.appendChild(opt);
      }
      if (profiles.some((p) => p.id === currentProfileId)) {
        profileSelectEl.value = currentProfileId;
      } else if (profiles.length > 0) {
        currentProfileId = profiles[0].id;
        profileSelectEl.value = currentProfileId;
      }
      updateActiveProfileLabel();
    }
  } catch (_) { /* ignore */ }
}

function updateActiveProfileLabel() {
  const p = profiles.find((x) => x.id === currentProfileId);
  if (kbActiveProfileEl) {
    kbActiveProfileEl.textContent = p ? p.name : currentProfileId;
  }
}

profileSelectEl.addEventListener("change", (e) => {
  currentProfileId = e.target.value;
  updateActiveProfileLabel();
});

btnProfileConfig.addEventListener("click", () => {
  const p = profiles.find((x) => x.id === currentProfileId);
  if (p) {
    profIdEl.value = p.id;
    profIdEl.disabled = true;
    profNameEl.value = p.name || "";
    profDescEl.value = p.description || "";
    profPromptEl.value = p.system_prompt || "";
    const guards = p.guardrails || {};
    profGuardCitationsEl.checked = Boolean(guards.enforce_citations);
    profGuardPhiEl.checked = Boolean(guards.anonymize_phi);
  } else {
    resetProfileForm();
  }
  profStatusEl.textContent = "";
  profStatusEl.className = "status-msg";
  modalProfile.classList.add("show");
});

function resetProfileForm() {
  profIdEl.value = "";
  profIdEl.disabled = false;
  profNameEl.value = "";
  profDescEl.value = "";
  profPromptEl.value = "";
  profGuardCitationsEl.checked = false;
  profGuardPhiEl.checked = false;
}

profCreateNewBtn.addEventListener("click", () => {
  resetProfileForm();
  profIdEl.focus();
});

profClose.addEventListener("click", () => modalProfile.classList.remove("show"));

profSaveBtn.addEventListener("click", async () => {
  const id = profIdEl.value.trim();
  const name = profNameEl.value.trim();
  if (!id || !name) {
    profStatusEl.textContent = "Profile ID and Display Name are required.";
    profStatusEl.className = "status-msg error";
    return;
  }
  const payload = {
    id,
    name,
    description: profDescEl.value.trim(),
    system_prompt: profPromptEl.value.trim(),
    guardrails: {
      enforce_citations: profGuardCitationsEl.checked,
      anonymize_phi: profGuardPhiEl.checked,
    },
  };
  profStatusEl.textContent = "Saving profile…";
  profStatusEl.className = "status-msg";
  try {
    const isExisting = profiles.some((p) => p.id === id);
    const method = isExisting ? "PUT" : "POST";
    const url = isExisting ? `/profiles/${encodeURIComponent(id)}` : "/profiles";
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      profStatusEl.textContent = "Profile saved successfully!";
      profStatusEl.className = "status-msg success";
      currentProfileId = id;
      await loadProfiles();
    } else {
      const err = await res.json().catch(() => ({}));
      profStatusEl.textContent = err.detail || "Failed to save profile.";
      profStatusEl.className = "status-msg error";
    }
  } catch (_) {
    profStatusEl.textContent = "Network error saving profile.";
    profStatusEl.className = "status-msg error";
  }
});

// --- Knowledge Base Manager ----------------------------------------------
btnKbManager.addEventListener("click", async () => {
  updateActiveProfileLabel();
  modalKb.classList.add("show");
  await loadKbDocuments();
});

kbClose.addEventListener("click", () => modalKb.classList.remove("show"));

async function loadKbDocuments() {
  kbDocsList.innerHTML = '<tr><td colspan="4" class="text-muted">Loading documents…</td></tr>';
  try {
    const res = await fetch(`/documents?profile_id=${encodeURIComponent(currentProfileId)}`);
    if (res.ok) {
      const data = await res.json();
      renderKbDocs(data.documents || []);
    } else {
      kbDocsList.innerHTML = '<tr><td colspan="4" class="text-muted">Failed to load documents.</td></tr>';
    }
  } catch (_) {
    kbDocsList.innerHTML = '<tr><td colspan="4" class="text-muted">Network error loading documents.</td></tr>';
  }
}

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

function renderKbDocs(docs) {
  kbDocsList.innerHTML = "";
  if (docs.length === 0) {
    kbDocsList.innerHTML = '<tr><td colspan="4" class="text-muted">No documents found for this profile.</td></tr>';
    return;
  }
  for (const doc of docs) {
    const tr = document.createElement("tr");
    const tdName = document.createElement("td");
    tdName.textContent = doc.filename;
    const tdSize = document.createElement("td");
    tdSize.textContent = formatBytes(doc.size);
    const tdTime = document.createElement("td");
    tdTime.textContent = doc.last_modified ? new Date(doc.last_modified).toLocaleDateString() : "-";
    const tdActions = document.createElement("td");
    const delBtn = document.createElement("button");
    delBtn.className = "kb-btn-delete";
    delBtn.textContent = "Delete";
    delBtn.addEventListener("click", async () => {
      if (!confirm(`Delete ${doc.filename}?`)) return;
      try {
        const res = await fetch(`/documents/${encodeURIComponent(doc.filename)}?profile_id=${encodeURIComponent(currentProfileId)}`, {
          method: "DELETE",
        });
        if (res.ok) loadKbDocuments();
      } catch (_) { /* ignore */ }
    });
    tdActions.appendChild(delBtn);
    tr.append(tdName, tdSize, tdTime, tdActions);
    kbDocsList.appendChild(tr);
  }
}

kbUploadBtn.addEventListener("click", async () => {
  const file = kbFileInput.files[0];
  if (!file) {
    kbUploadStatus.textContent = "Please select a file first.";
    kbUploadStatus.className = "status-msg error";
    return;
  }
  const formData = new FormData();
  formData.append("file", file);
  kbUploadStatus.textContent = "Uploading & indexing…";
  kbUploadStatus.className = "status-msg";
  kbUploadBtn.disabled = true;
  try {
    const res = await fetch(`/documents/upload?profile_id=${encodeURIComponent(currentProfileId)}`, {
      method: "POST",
      body: formData,
    });
    if (res.ok) {
      kbUploadStatus.textContent = "Document uploaded and indexed successfully!";
      kbUploadStatus.className = "status-msg success";
      kbFileInput.value = "";
      await loadKbDocuments();
    } else {
      const err = await res.json().catch(() => ({}));
      kbUploadStatus.textContent = err.detail || "Upload failed.";
      kbUploadStatus.className = "status-msg error";
    }
  } catch (_) {
    kbUploadStatus.textContent = "Network error uploading document.";
    kbUploadStatus.className = "status-msg error";
  } finally {
    kbUploadBtn.disabled = false;
  }
});

// --- Benchmarks Viewer ---------------------------------------------------
btnBenchmarks.addEventListener("click", async () => {
  modalBenchmarks.classList.add("show");
  bmSummaryChips.innerHTML = "";
  bmReportContent.textContent = "Fetching latest benchmark analytics…";
  try {
    const res = await fetch("/benchmarks/report");
    if (res.ok) {
      const data = await res.json();
      if (data.available && data.report_markdown) {
        bmReportContent.textContent = data.report_markdown;
        const winner = data.overall_winner;
        if (winner && winner.model_name) {
          const chip = document.createElement("div");
          chip.className = "bm-chip";
          chip.innerHTML = `🏆 Top Winner: <strong>${winner.model_name}</strong> (Score: ${(winner.score || 0).toFixed(3)})`;
          bmSummaryChips.appendChild(chip);
        }
        if (data.top_3_models && data.top_3_models.length > 0) {
          const chip = document.createElement("div");
          chip.className = "bm-chip";
          chip.innerHTML = `🥇 Top 3: ${data.top_3_models.map((m) => m.model_name).join(", ")}`;
          bmSummaryChips.appendChild(chip);
        }
      } else {
        bmReportContent.textContent = "No benchmark report found. Run `uv run python -m src.benchmarks.cli` to generate reports.";
      }
    } else {
      bmReportContent.textContent = "Failed to fetch benchmark report.";
    }
  } catch (_) {
    bmReportContent.textContent = "Network error loading benchmark report.";
  }
});

bmClose.addEventListener("click", () => modalBenchmarks.classList.remove("show"));

// Overlay click to close
window.addEventListener("click", (e) => {
  if (e.target === modalProfile) modalProfile.classList.remove("show");
  if (e.target === modalKb) modalKb.classList.remove("show");
  if (e.target === modalBenchmarks) modalBenchmarks.classList.remove("show");
  if (e.target === modalSettings) modalSettings.classList.remove("show");
});

// --- Initialization ------------------------------------------------------
(async () => {
  let needsOnboarding = false;
  try {
    const res = await fetch("/config");
    if (res.ok) {
      const cfg = await res.json();
      if (cfg.language && I18N[cfg.language]) {
        LANG = cfg.language;
        T = I18N[LANG];
      }
      if (cfg.app_name) updateAppNameUI(cfg.app_name);
      if (cfg.setup_required || !cfg.ready || cfg.needs_api_key) {
        needsOnboarding = true;
      }
    }
  } catch (_) { /* fall back to defaults */ }

  applyTheme(getSavedTheme());
  applyLanguage();
  currentId = newId();
  await loadProfiles();
  await loadConversations();

  if (needsOnboarding) {
    showOnboarding(1);
  } else {
    inputEl.focus();
  }
})();
