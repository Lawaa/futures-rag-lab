// Localization
const I18N = {
  en: {
    docTitle: "Futures Trading Assistant",
    headerTitle: "Futures Trading Assistant",
    headerSubtitle: "Ask about margins, contracts, settlement, risk and more",
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
    hint: "Press Enter to send  Shift+Enter for a new line",
    newConversationTitle: "✨ New conversation",
    newConversationText: "Ask a question about your futures trading documents.",
    suggestions: [
      "What is the difference between initial and maintenance margin?",
      "How does a futures contract differ from a forward contract?",
      "What happens during a margin call?"
    ],
    errorAuth: "Authentication error: the server has no valid API key.",
    errorHttp: (s) => `Something went wrong (HTTP ${s}).`,
    errorNetwork: "⚠️ Could not reach the server. Is it running?",
    statusRouting: "Routing...",
    statusPreparing: "Preparing search...",
    statusExpanding: "Expanding queries...",
    statusRetrieving: "Searching documents...",
    statusGrading: "Checking relevance...",
    statusRewriting: "Refining search...",
    statusAnswering: "Writing answer...",
    setupTitle: "Welcome — one quick step",
    setupText: "To use the hosted Gemini model, paste your Google AI Studio API key. It is stored securely in your operating system's credential manager and never leaves this device except to call the model.",
    setupPlaceholder: "Paste your Gemini API key",
    setupSubmit: "Save & continue",
    setupSaving: "Verifying...",
    setupInvalid: "That key was rejected. Please check it and try again.",
    setupError: "Could not save the key. Please try again."
  },
  hu: {
    docTitle: "Futures Kereskedési Tudástár",
    headerTitle: "Futures Kereskedési Tudástár",
    headerSubtitle: "Kérdezzen letétekről, kontraktusokról, elszámolásról, kockázatról és többsről",
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
    hint: "Küldés: Enter  Új sor: Shift+Enter",
    newConversationTitle: "✨ Új beszélgetés",
    newConversationText: "Tegyen fel kérdést a határidős kereskedési dokumentumaival kapcsolatban.",
    suggestions: [
      "Mi a különbség a kezdeti és a fenntartási letét között?",
      "Miben különbözik a futures ügylet a forward ügylettől?",
      "Mi történik egy letétfeltöltési felszólítás (margin call) során?"
    ],
    errorAuth: "Hitelesítési hiba: a szervernek nincs érvényes API-kulcsa.",
    errorHttp: (s) => `Hiba történt (HTTP ${s}).`,
    errorNetwork: "⚠️ A szerver nem érhető el. Fut egyáltalán?",
    statusRouting: "Irányítás...",
    statusPreparing: "Keresés előkészítése...",
    statusExpanding: "Lekérdezések bővítése...",
    statusRetrieving: "Dokumentumok keresése...",
    statusGrading: "Relevancia ellenőrzése...",
    statusRewriting: "Keresés finomítása...",
    statusAnswering: "Válasz írása...",
    setupTitle: "Üdvözöljük — egy gyors lépés",
    setupText: "A hosztolt Gemini modell használatához illessze be a Google AI Studio API-kulcsát. A kulcs biztonságosan, az operációs rendszer jelszókezelőjében tárolódik, és csak a modell hívásához hagyja el az eszközt.",
    setupPlaceholder: "Illessze be a Gemini API-kulcsot",
    setupSubmit: "Mentés és folytatás",
    setupSaving: "Ellenőrzés...",
    setupInvalid: "A kulcsot elutasította a szolgáltató. Ellenőrizze és próbálja újra.",
    setupError: "A kulcs mentése nem sikerült. Próbálja újra."
  }
};

let LANG = "en";
let T = I18N.en;

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
  document.title = T.docTitle;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (typeof T[key] === "string") el.textContent = T[key];
  });
  inputEl.placeholder = T.placeholder;
  const setupKey = document.getElementById("setup-key");
  if (setupKey) setupKey.placeholder = T.setupPlaceholder;
  renderSuggestions();
}

const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("send");
const newChatBtn = document.getElementById("new-chat");
const convEl = document.getElementById("conversations");

// The active conversation id; a fresh one is generated for each new chat.
let currentId = null;
let busy = false;

function newId() {
  const rnd = (window.crypto && crypto.randomUUID)
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2, 11);
  return "web-" + rnd;
}

function autoGrow() {
  inputEl.style.height = "auto";
  inputEl.style.height = Math.min(inputEl.scrollHeight, 140) + "px";
}
inputEl.addEventListener("input", autoGrow);

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderWelcome() {
  messagesEl.innerHTML = "";
  const welcome = document.createElement("div");
  welcome.className = "welcome";
  const h2 = document.createElement("h2");
  h2.textContent = T.welcomeTitle;
  const p = document.createElement("p");
  p.textContent = T.welcomeText;
  const sug = document.createElement("div");
  sug.className = "suggestions";
  sug.id = "suggestions";
  welcome.append(h2, p, sug);
  messagesEl.appendChild(welcome);
  renderSuggestions();
}

// --- Minimal, safe Markdown renderer ----------------------------------------
// Answers arrive as Markdown; render a useful subset to HTML while escaping
// all content first so nothing can inject markup (XSS-safe).
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderInline(s) {
  // Protect inline code spans from further formatting.
  const codes = [];
  s = s.replace(/`([^`]+)`/g, (_, c) => {
    codes.push(c);
    return "\u0000" + (codes.length - 1) + "\u0000";
  });
  // Links: only http(s) targets are allowed.
  s = s.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s]+)\)/g,
    (_, t, u) => `<a href="${u}" target="_blank" rel="noopener noreferrer">${t}</a>`
  );
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/__([^_]+)__/g, "<strong>$1</strong>");
  s = s.replace(/(^|[^\*])\*([^\*]+)\*(?!\*)/g, "$1<em>$2</em>");
  s = s.replace(/(^|[^_])_([^_]+)_(?!_)/g, "$1<em>$2</em>");
  s = s.replace(/\u0000(\d+)\u0000/g, (_, i) => "<code>" + codes[i] + "</code>");
  return s;
}

function renderMarkdown(src) {
  const lines = escapeHtml(src).replace(/\r\n/g, "\n").split("\n");
  const out = [];
  const stack = []; // open list types, e.g. ["ol", "ul"]
  let i = 0;

  const closeTo = (depth) => {
    while (stack.length > depth) out.push("</" + stack.pop() + ">");
  };

  while (i < lines.length) {
    const line = lines[i];

    // Fenced code block.
    if (/^\s*```/.test(line)) {
      closeTo(0);
      const buf = [];
      i++;
      while (i < lines.length && !/^\s*```/.test(lines[i])) buf.push(lines[i++]);
      i++; // consume closing fence
      out.push("<pre><code>" + buf.join("\n") + "</code></pre>");
      continue;
    }

    // Blank line ends any open block.
    if (/^\s*$/.test(line)) { closeTo(0); i++; continue; }

    // Headings (#, ##, ### capped at h3).
    const h = line.match(/^(\#{1,6})\s+(.*)$/);
    if (h) {
      closeTo(0);
      const lvl = Math.min(h[1].length, 3);
      out.push("<h" + lvl + ">" + renderInline(h[2]) + "</h" + lvl + ">");
      i++; continue;
    }

    // List items (ordered or unordered) with indent-based nesting.
    const li = line.match(/^(\s*)(?:[-*]|\d+\.)\s+(.*)$/);
    if (li) {
      const depth = Math.floor(li[1].replace(/\t/g, "  ").length / 2) + 1;
      const type = /^\d+\./.test(li[0].trim()) ? "ol" : "ul";
      while (stack.length > depth) out.push("</" + stack.pop() + ">");
      if (stack.length === depth && stack[depth - 1] !== type) {
        out.push("</" + stack.pop() + ">");
      }
      while (stack.length < depth) { out.push("<" + type + ">"); stack.push(type); }
      out.push("<li>" + renderInline(li[2]) + "</li>");
      i++; continue;
    }

    // Blockquote.
    const bq = line.match(/^\s*>\s?(.*)$/);
    if (bq) {
      closeTo(0);
      out.push("<blockquote>" + renderInline(bq[1]) + "</blockquote>");
      i++; continue;
    }

    // Paragraph: gather consecutive plain lines.
    closeTo(0);
    const para = [line];
    i++;
    while (
      i < lines.length &&
      !/^\s*$/.test(lines[i]) &&
      !/^\s*#{1,6}\s+/.test(lines[i]) &&
      !/^\s*(?:[-*]|\d+\.)\s+/.test(lines[i]) &&
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

function addMessage(role, text, opts) {
  opts = opts || {};
  const existing = messagesEl.querySelector(".welcome");
  if (existing) existing.remove();
  const row = document.createElement("div");
  row.className = "row " + role;

  const avatar = document.createElement("div");
  avatar.className = "avatar " + role;
  avatar.textContent = role === "user" ? "👤" : "🤖";

  const content = document.createElement("div");
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (opts.markdown) {
    bubble.classList.add("md");
    bubble.innerHTML = renderMarkdown(text);
  } else {
    bubble.textContent = text;
  }
  content.appendChild(bubble);

  row.appendChild(avatar);
  row.appendChild(content);
  messagesEl.appendChild(row);
  scrollToBottom();
  return { row, bubble, content };
}

function renderSources(container, sources) {
  if (!sources || sources.length === 0) return;
  const wrap = document.createElement("div");
  wrap.className = "sources";
  for (const s of sources) {
    const pill = document.createElement("span");
    pill.className = "source-pill";
    pill.textContent = "📄 " + s.name + (s.page != null ? " (p. " + s.page + ")" : "");
    wrap.appendChild(pill);
  }
  container.appendChild(wrap);
}

function setBusy(state) {
  busy = state;
  sendBtn.disabled = state;
  inputEl.disabled = state;
}

// --- Conversation history (sidebar) ----------------------------------------
function highlightActive() {
  convEl.querySelectorAll(".conv-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.id === currentId);
  });
}

function renderConversations(list) {
  convEl.innerHTML = "";
  if (!list || list.length === 0) {
    const empty = document.createElement("div");
    empty.className = "conv-empty";
    empty.textContent = T.noConversations;
    convEl.appendChild(empty);
    return;
  }
  for (const conv of list) {
    const item = document.createElement("div");
    item.className = "conv-item" + (conv.pinned ? " pinned" : "");
    item.dataset.id = conv.id;

    const title = document.createElement("div");
    title.className = "conv-title";
    title.textContent = conv.title;
    title.title = conv.title;

    const pin = document.createElement("button");
    pin.className = "conv-pin";
    pin.textContent = conv.pinned ? "📌" : "📍";
    pin.title = conv.pinned ? T.unpinTitle : T.pinTitle;
    pin.addEventListener("click", (e) => {
      e.stopPropagation();
      togglePin(conv.id, !conv.pinned);
    });

    const rename = document.createElement("button");
    rename.className = "conv-rename";
    rename.textContent = "✏️";
    rename.title = T.renameTitle;
    rename.addEventListener("click", (e) => {
      e.stopPropagation();
      renameConversation(conv.id, conv.title);
    });

    const del = document.createElement("button");
    del.className = "conv-delete";
    del.textContent = "🗑️";
    del.title = T.deleteTitle;
    del.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteConversation(conv.id);
    });

    item.appendChild(title);
    item.appendChild(pin);
    item.appendChild(rename);
    item.appendChild(del);
    item.addEventListener("click", () => openConversation(conv.id));
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

async function openConversation(id) {
  if (busy) return;
  currentId = id;
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

function startNewChat() {
  currentId = newId();
  renderWelcome();
  highlightActive();
  inputEl.focus();
}

function stageLabel(stage) {
  const key = "status" + stage.charAt(0).toUpperCase() + stage.slice(1);
  return T[key] || null;
}

async function send(question) {
  if (busy || !question.trim()) return;
  const q = question.trim();
  addMessage("user", q);
  inputEl.value = "";
  autoGrow();
  setBusy(true);

  // Bot bubble with a live status indicator that updates per pipeline stage.
  const { bubble, content } = addMessage("bot", "");
  const status = document.createElement("div");
  status.className = "status-line";
  status.innerHTML =
    '<div class="typing"><span></span><span></span><span></span></div>' +
    '<span class="status-text"></span>';
  const statusText = status.querySelector(".status-text");
  const answer = document.createElement("div");
  answer.className = "answer-body";
  bubble.appendChild(status);
  bubble.appendChild(answer);

  let raw = "";
  let done = null;

  try {
    const res = await fetch("/chat/events", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q, session_id: currentId }),
    });

    if (!res.ok || !res.body) {
      status.remove();
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
          if (label) statusText.textContent = label;
        } else if (event.type === "token") {
          // First token: switch the bubble from "thinking" to answering.
          if (raw === "") {
            bubble.classList.add("md");
            const answering = stageLabel("answering");
            if (answering) statusText.textContent = answering;
          }
          raw += event.text;
          answer.textContent = raw;
          scrollToBottom();
        } else if (event.type === "done") {
          done = event;
        } else if (event.type === "error") {
          status.remove();
          const detail = event.code === "auth" ? T.errorAuth : (event.detail || T.errorHttp(500));
          bubble.textContent = "⚠️ " + detail;
          return;
        }
      }
    }

    status.remove();
    let finalText = raw;
    if (done && done.note) finalText = done.note + "\n\n" + raw;
    answer.classList.add("md");
    answer.innerHTML = renderMarkdown(finalText);
    if (done) renderSources(content, done.sources);
    scrollToBottom();
    loadConversations();
  } catch (err) {
    status.remove();
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

// --- First-run setup (Gemini API key) --------------------------------------
const setupOverlay = document.getElementById("setup-overlay");
const setupKeyEl = document.getElementById("setup-key");
const setupSubmitEl = document.getElementById("setup-submit");
const setupErrorEl = document.getElementById("setup-error");

function showSetup() {
  setupOverlay.classList.add("show");
  setupKeyEl.focus();
}

async function submitApiKey() {
  const key = setupKeyEl.value.trim();
  if (!key) return;
  setupErrorEl.textContent = "";
  setupSubmitEl.disabled = true;
  setupSubmitEl.textContent = T.setupSaving;
  try {
    const res = await fetch("/config/api-key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: key }),
    });
    if (res.ok) {
      setupOverlay.classList.remove("show");
      setupKeyEl.value = "";
      inputEl.focus();
      return;
    }
    setupErrorEl.textContent = res.status === 401 ? T.setupInvalid : T.setupError;
  } catch (_) {
    setupErrorEl.textContent = T.setupError;
  } finally {
    setupSubmitEl.disabled = false;
    setupSubmitEl.textContent = T.setupSubmit;
  }
}

setupSubmitEl.addEventListener("click", submitApiKey);
setupKeyEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    submitApiKey();
  }
});

// Load the server-selected language, then render the localized UI.
(async () => {
  let needsApiKey = false;
  try {
    const res = await fetch("/config");
    if (res.ok) {
      const cfg = await res.json();
      if (cfg.language && I18N[cfg.language]) {
        LANG = cfg.language;
        T = I18N[LANG];
      }
      needsApiKey = Boolean(cfg.needs_api_key);
    }
  } catch (_) { /* fall back to English */ }
  applyLanguage();
  currentId = newId();
  await loadConversations();
  if (needsApiKey) {
    showSetup();
  } else {
    inputEl.focus();
  }
})();