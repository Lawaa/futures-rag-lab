// --- Localization Dictionary ---------------------------------------------
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

    // Top Navigation
    navLegalCodes: "Legal Codes",
    navDomainConfig: "Domain Config",
    navDocs: "Docs",

    // Knowledge Base Modal
    kbTitle: "Knowledge Base Manager",
    kbUploadBtn: "Upload & Index",
    thDoc: "Document",
    thSize: "Size",
    thUploaded: "Uploaded",
    thActions: "Actions",
    btnDelete: "Delete",
    kbLoading: "Loading documents…",
    kbEmpty: "No documents found for this profile.",
    kbSelectFile: "Please select a file first.",
    kbUploading: "Uploading & indexing…",
    kbUploadSuccess: "Document uploaded and indexed successfully!",
    kbUploadFail: "Upload failed.",

    // Legal Corpus Modal
    legalModalTitle: "Official Legal Codes (Ptk. & Btk.)",
    legalModalSubtitle: "Hungarian Legal & Regulatory Compliance Corpus",
    legalModalIntro: "Select the official legal statutes to cache and index into the Legal & Regulatory Compliance domain vector store. Cached statutes are checked conditionally via HTTP ETag to prevent redundant re-downloads.",
    badgeCached: "Cached & Ready",
    badgeUpdate: "Update Available",
    badgeAvailable: "Available",
    badgeDownloading: "Downloading...",
    legalRemote: "Remote",
    legalNotSynced: "Not synced yet",
    legalSelectStatute: "Please select at least one legal statute to index.",
    legalSyncing: "Syncing and indexing legal corpora…",
    legalSuccess: "Legal statutes synced and indexed successfully!",
    btnClose: "Close",
    btnSyncLegal: "Sync Selected Statutes from Netjogtár (njt.hu) 🏛️",
    legalProviderBadge: "Official Source: Nemzeti Jogszabálytár (njt.hu)",
    legalProviderSub: "Authoritative Hungarian Gazette and Ministry of Justice Corpus",
    legalLiveSyncLabel: "Netjogtár / NJT Live Sync",
    legalSourceLabel: "Source: Nemzeti Jogszabálytár (njt.hu)",
    legalCustomUrlLabel: "Custom Netjogtár URL or Statute Identifier (Optional):",

    // Settings Modal
    settingsHeader: "⚙️ System Settings & Customization",
    settingsBranding: "Branding & Identity",
    settingsAppName: "Application Display Name",
    settingsAppNameHint: "Updates the interface header, browser tab, and page branding live.",
    settingsBtnSaveName: "Update Brand Name",
    settingsAppearance: "Interface Appearance",
    settingsColorTheme: "Color Theme",
    settingsLanguage: "Language",
    settingsBackend: "Backend Architecture",
    stLlmProvider: "LLM Provider:",
    stModel: "Model:",
    stStorage: "Storage:",
    stRagService: "RAG Service:",
    storageLocal: "Local Filesystem",
    storageS3: "Amazon S3 Bucket",
    statusActiveReady: "Active & Ready",
    statusNeedsKey: "Needs API Key",
    statusInit: "Initializing",
    settingsQuickSetup: "Quick Setup & Tools",
    settingsRerunWizard: "🔄 Rerun Onboarding Wizard",
    settingsDevTools: "Developer Tools & Benchmarks",
    settingsViewBm: "📊 View Benchmark Analytics",
    settingsRunBm: "⚡ Run Benchmark Evaluator",

    // Document Viewer Modal
    docViewerTitle: "Document Preview",
    docViewerSubtitle: "Full Document",
    docViewerLoading: "Loading document preview…",

    // Sources Card
    sourcesTitle: "Referenced Sources",
    sourcesPillTitle: "Click to preview document",

    // Profile Modal
    profModalTitle: "🛡️ Tenant & Domain Profile",
    profId: "Profile ID",
    profName: "Display Name",
    profDesc: "Description (Router summary)",
    profPrompt: "System Prompt (Persona & Instructions)",
    profGuardrails: "Domain Guardrails",
    profGuardCitations: "<strong>Enforce Citations:</strong> Require explicit source document/page references for assertions",
    profGuardPhi: "<strong>Anonymize PII/PHI:</strong> Automatically redact SSN, MRN, phone, email, and patient identifiers",
    profBtnNew: "+ New Profile",
    profBtnSave: "Save Profile",
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

    // Top Navigation
    navLegalCodes: "Törvénytár",
    navDomainConfig: "Domain Beállítások",
    navDocs: "Tudásbázis",

    // Knowledge Base Modal
    kbTitle: "Tudásbázis Kezelő",
    kbUploadBtn: "Feltöltés és Indexelés",
    thDoc: "Dokumentum",
    thSize: "Méret",
    thUploaded: "Feltöltve",
    thActions: "Műveletek",
    btnDelete: "Törlés",
    kbLoading: "Dokumentumok betöltése…",
    kbEmpty: "Nincsenek dokumentumok ehhez a profilhoz.",
    kbSelectFile: "Kérjük, válasszon ki egy fájlt először.",
    kbUploading: "Feltöltés és indexelés…",
    kbUploadSuccess: "A dokumentum feltöltése és indexelése sikeres!",
    kbUploadFail: "A feltöltés sikertelen.",

    // Legal Corpus Modal
    legalModalTitle: "Hivatalos Törvénykönyvek (Ptk. & Btk.)",
    legalModalSubtitle: "Magyar Jogi és Megfelelőségi Törvénytár",
    legalModalIntro: "Válassza ki a gyorsítótárazni és a Jogi és Megfelelőségi domain vektoradatbázisába indexelni kívánt hivatalos jogszabályokat. A mentett törvényeket a rendszer HTTP ETag alapján ellenőrzi, elkerülve a felesleges ismételt letöltéseket.",
    badgeCached: "Gyorsítótárazva és Kész",
    badgeUpdate: "Frissítés Elérhető",
    badgeAvailable: "Elérhető",
    badgeDownloading: "Letöltés...",
    legalRemote: "Távoli",
    legalNotSynced: "Még nincs szinkronizálva",
    legalSelectStatute: "Kérjük, jelöljön ki legalább egy törvényt az indexeléshez.",
    legalSyncing: "Törvénytár szinkronizálása és indexelése…",
    legalSuccess: "A jogszabályok szinkronizálása és indexelése sikeresen befejeződött!",
    btnClose: "Bezárás",
    btnSyncLegal: "Kijelölt Törvények Szinkronizálása a Netjogtárból 🏛️",
    legalProviderBadge: "Hivatalos Forrás: Nemzeti Jogszabálytár (njt.hu)",
    legalProviderSub: "Hiteles Magyar Közlönykiadó és Igazságügyi szövegtár",
    legalLiveSyncLabel: "Netjogtár / NJT Élő Szinkronizáció",
    legalSourceLabel: "Forrás: Nemzeti Jogszabálytár (njt.hu)",
    legalCustomUrlLabel: "Egyéni Netjogtár Hivatkozás vagy Azonosító (opcionális):",

    // Settings Modal
    settingsHeader: "⚙️ Rendszerbeállítások és Testreszabás",
    settingsBranding: "Márka és Megjelenés",
    settingsAppName: "Alkalmazás Megjelenített Neve",
    settingsAppNameHint: "A felület fejlécének, böngészőfülének és márkájának élő frissítése.",
    settingsBtnSaveName: "Márkanév Frissítése",
    settingsAppearance: "Felület Megjelenése",
    settingsColorTheme: "Színtéma",
    settingsLanguage: "Nyelv",
    settingsBackend: "Háttérrendszer Architektúra",
    stLlmProvider: "LLM Szolgáltató:",
    stModel: "Modell:",
    stStorage: "Tároló:",
    stRagService: "RAG Szolgáltatás:",
    storageLocal: "Helyi Fájlrendszer",
    storageS3: "Amazon S3 Felhőtár",
    statusActiveReady: "Aktiválva és Kész",
    statusNeedsKey: "API Kulcs Szükséges",
    statusInit: "Inicializálás",
    settingsQuickSetup: "Gyors Beállítás és Eszközök",
    settingsRerunWizard: "🔄 Bevezető Varázsló Újrafuttatása",
    settingsDevTools: "Fejlesztői Eszközök és Benchmarkok",
    settingsViewBm: "📊 Benchmark Elemzések Megtekintése",
    settingsRunBm: "⚡ Benchmark Értékelő Futtatása",

    // Document Viewer Modal
    docViewerTitle: "Dokumentum Előnézet",
    docViewerSubtitle: "Teljes Dokumentum",
    docViewerLoading: "Dokumentum előnézet betöltése…",

    // Sources Card
    sourcesTitle: "Hivatkozott Források",
    sourcesPillTitle: "Kattintson a dokumentum előnézetéhez",

    // Profile Modal
    profModalTitle: "🛡️ Bérlői és Domain Profil",
    profId: "Profil azonosító",
    profName: "Megjelenítendő név",
    profDesc: "Leírás (Router összegzés)",
    profPrompt: "Rendszerutasítás / System Prompt",
    profGuardrails: "Domain Biztonsági Korlátok",
    profGuardCitations: "<strong>Kötelező Hivatkozások:</strong> Konkrét forrásdokumentum- és oldalhivatkozások megkövetelése az állításokhoz",
    profGuardPhi: "<strong>Személyes/Egészségügyi Adatok Anonimizálása:</strong> TAJ, azonosítók, telefonszám, email automatikus kitakarása",
    profBtnNew: "+ Új profil",
    profBtnSave: "Profil mentése",
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
const activeConvTitleEl = document.getElementById("chatTitleHeader") || document.getElementById("active-conv-title");
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
const settingAccentPreset = document.getElementById("setting-accent-preset");
const settingAccentPrimary = document.getElementById("setting-accent-primary");
const settingAccentSecondary = document.getElementById("setting-accent-secondary");
const hexAccentPrimary = document.getElementById("hex-accent-primary");
const hexAccentSecondary = document.getElementById("hex-accent-secondary");
const btnResetAccents = document.getElementById("btn-reset-accents");
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
const domainDropdownTrigger = document.getElementById("domainDropdownTrigger");
const domainActiveIcon = document.getElementById("domainActiveIcon");
const domainActiveName = document.getElementById("domainActiveName");
const domainDropdownMenu = document.getElementById("domainDropdownMenu");
const btnProfileConfig = document.getElementById("btn-profile-config");
const btnKbManager = document.getElementById("btn-kb-manager");
const btnBenchmarks = document.getElementById("btn-benchmarks");

// Modals: Profile, KB, Benchmarks, DocViewer
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
const btnViewBenchmarks = document.getElementById("btn-view-benchmarks");
const btnRunBenchmarks = document.getElementById("btn-run-benchmarks");
const benchmarkRunStatus = document.getElementById("benchmark-run-status");

// Document Inspector Pane (Panel 3 - In-workspace glass panel)
const docInspectorPane = document.getElementById("docInspectorPane");
const docInspectorClose = document.getElementById("docInspectorClose");
const btnToggleInspector = document.getElementById("btn-toggle-inspector");
const btnToggleGraph = document.getElementById("btn-toggle-graph");
const docGraphWidget = document.getElementById("docGraphWidget");
const docGraphSvg = document.getElementById("docGraphSvg");
const graphInfoBtn = document.getElementById("graphInfoBtn");
const btnExpandGraph = document.getElementById("btnExpandGraph");
const graphTooltipPopover = document.getElementById("graphTooltipPopover");
const modalGraphViewer = document.getElementById("modal-graph-viewer");
const graphModalClose = document.getElementById("graphModalClose");
const graphModalTitle = document.getElementById("graphModalTitle");
const graphModalSubtitle = document.getElementById("graphModalSubtitle");
const graphModalSvg = document.getElementById("graphModalSvg");
const nodeDetailTitle = document.getElementById("nodeDetailTitle");
const nodeDetailBadge = document.getElementById("nodeDetailBadge");
const nodeDetailDesc = document.getElementById("nodeDetailDesc");
const nodeConnectionsList = document.getElementById("nodeConnectionsList");
const btnViewPdf = document.getElementById("btn-view-pdf");
const docTypeBadge = document.getElementById("docTypeBadge");
const docViewerTitle = document.getElementById("docViewerTitle");
const docViewerSubtitle = document.getElementById("docViewerSubtitle");
const docViewerDownloadBtn = document.getElementById("docViewerDownloadBtn");
const docViewerClose = document.getElementById("docViewerClose") || docInspectorClose;
const docViewerLoading = document.getElementById("docViewerLoading");
const docViewerContent = document.getElementById("docViewerContent");
const docViewerIcon = document.getElementById("docViewerIcon");
const navLegal = document.getElementById("nav-legal");
const navSettings = document.getElementById("nav-settings");
const composerDocBtn = document.getElementById("composer-doc-btn");
const composerPromptBtn = document.getElementById("composer-prompt-btn");
const docViewerModal = docInspectorPane; // backward compatibility fallback

// Fullscreen Original PDF Viewer Modal
const modalPdfViewer = document.getElementById("modal-pdf-viewer");
const pdfModalTitle = document.getElementById("pdfModalTitle");
const pdfModalPageInfo = document.getElementById("pdfModalPageInfo");
const pdfModalFrame = document.getElementById("pdfModalFrame");
const pdfModalClose = document.getElementById("pdfModalClose");
const pdfZoomIn = document.getElementById("pdfZoomIn");
const pdfZoomOut = document.getElementById("pdfZoomOut");
const pdfZoomReset = document.getElementById("pdfZoomReset");
const pdfZoomLevel = document.getElementById("pdfZoomLevel");
const pdfModalDownloadBtn = document.getElementById("pdfModalDownloadBtn");

let activePdfFilename = null;
let activePdfPage = 1;
let currentPdfZoom = 100;

// Legal Corpora Modal
const modalLegalCorpus = document.getElementById("legalCorpusModal");
const legalCorpusClose = document.getElementById("legalCorpusClose");
const btnCloseLegalModal = document.getElementById("btn-close-legal-modal");
const btnSyncLegalCorpora = document.getElementById("btn-sync-legal-corpora");
const legalCorporaList = document.getElementById("legalCorporaList");
const legalSyncProgressContainer = document.getElementById("legalSyncProgressContainer");
const legalSyncProgressBar = document.getElementById("legalSyncProgressBar");
const legalSyncStatus = document.getElementById("legalSyncStatus");
const btnLegalCorpora = document.getElementById("btn-legal-corpora");
let legalCorporaData = [];
const currentTurnSources = new Map();

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

// --- Dynamic 2-Color Accent Theming ---------------------------------------
const DEFAULT_ACCENT_PRIMARY = "#38bdf8";
const DEFAULT_ACCENT_SECONDARY = "#c084fc";

const ACCENT_PRESETS = {
  cyan_violet: { primary: "#38bdf8", secondary: "#c084fc" },
  electric_blue: { primary: "#00f2fe", secondary: "#4facfe" },
  emerald_purple: { primary: "#10b981", secondary: "#a855f7" },
  sunset_neon: { primary: "#f97316", secondary: "#ec4899" },
  matrix_glow: { primary: "#22c55e", secondary: "#06b6d4" },
  synthwave: { primary: "#f43f5e", secondary: "#8b5cf6" },
};

function hexToRgba(hex, alpha = 1) {
  let clean = (hex || "#38bdf8").replace("#", "");
  if (clean.length === 3) clean = clean.split("").map(c => c + c).join("");
  const num = parseInt(clean, 16);
  if (isNaN(num)) return `rgba(56, 189, 248, ${alpha})`;
  const r = (num >> 16) & 255;
  const g = (num >> 8) & 255;
  const b = num & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function hexToRgbValues(hex) {
  let clean = (hex || "#38bdf8").replace("#", "");
  if (clean.length === 3) clean = clean.split("").map(c => c + c).join("");
  const num = parseInt(clean, 16);
  if (isNaN(num)) return "56, 189, 248";
  const r = (num >> 16) & 255;
  const g = (num >> 8) & 255;
  const b = num & 255;
  return `${r}, ${g}, ${b}`;
}

function getSavedAccentColors() {
  const primary = localStorage.getItem("rag_accent_primary") || DEFAULT_ACCENT_PRIMARY;
  const secondary = localStorage.getItem("rag_accent_secondary") || DEFAULT_ACCENT_SECONDARY;
  return { primary, secondary };
}

function applyAccentColors(primary, secondary, save = true) {
  const root = document.documentElement;
  root.style.setProperty("--accent-primary", primary);
  root.style.setProperty("--accent-secondary", secondary);
  root.style.setProperty("--accent-primary-rgb", hexToRgbValues(primary));
  root.style.setProperty("--accent-secondary-rgb", hexToRgbValues(secondary));
  root.style.setProperty("--accent-primary-glow", hexToRgba(primary, 0.35));
  root.style.setProperty("--accent-secondary-glow", hexToRgba(secondary, 0.35));
  root.style.setProperty("--accent", primary);
  root.style.setProperty("--violet-accent", secondary);

  if (save) {
    localStorage.setItem("rag_accent_primary", primary);
    localStorage.setItem("rag_accent_secondary", secondary);
  }

  if (settingAccentPrimary) settingAccentPrimary.value = primary;
  if (settingAccentSecondary) settingAccentSecondary.value = secondary;
  if (hexAccentPrimary) hexAccentPrimary.textContent = primary.toUpperCase();
  if (hexAccentSecondary) hexAccentSecondary.textContent = secondary.toUpperCase();

  if (settingAccentPreset) {
    let matched = "custom";
    for (const [key, p] of Object.entries(ACCENT_PRESETS)) {
      if (p.primary.toLowerCase() === primary.toLowerCase() && p.secondary.toLowerCase() === secondary.toLowerCase()) {
        matched = key;
        break;
      }
    }
    settingAccentPreset.value = matched;
  }

  if (typeof KNOWLEDGE_GRAPH_NODES !== "undefined") {
    if (KNOWLEDGE_GRAPH_NODES.QUERY) {
      KNOWLEDGE_GRAPH_NODES.QUERY.fill = primary;
      KNOWLEDGE_GRAPH_NODES.QUERY.glow = hexToRgba(primary, 0.6);
    }
    if (KNOWLEDGE_GRAPH_NODES.DOC) {
      KNOWLEDGE_GRAPH_NODES.DOC.fill = secondary;
      KNOWLEDGE_GRAPH_NODES.DOC.glow = hexToRgba(secondary, 0.6);
    }
  }
}

function initAccentColors() {
  const { primary, secondary } = getSavedAccentColors();
  applyAccentColors(primary, secondary, false);
}

if (settingAccentPrimary) {
  settingAccentPrimary.addEventListener("input", (e) => {
    const sec = settingAccentSecondary ? settingAccentSecondary.value : DEFAULT_ACCENT_SECONDARY;
    applyAccentColors(e.target.value, sec, true);
  });
}

if (settingAccentSecondary) {
  settingAccentSecondary.addEventListener("input", (e) => {
    const pri = settingAccentPrimary ? settingAccentPrimary.value : DEFAULT_ACCENT_PRIMARY;
    applyAccentColors(pri, e.target.value, true);
  });
}

if (settingAccentPreset) {
  settingAccentPreset.addEventListener("change", (e) => {
    const presetKey = e.target.value;
    if (presetKey in ACCENT_PRESETS) {
      const { primary, secondary } = ACCENT_PRESETS[presetKey];
      applyAccentColors(primary, secondary, true);
    }
  });
}

if (btnResetAccents) {
  btnResetAccents.addEventListener("click", () => {
    applyAccentColors(DEFAULT_ACCENT_PRIMARY, DEFAULT_ACCENT_SECONDARY, true);
  });
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
    if (typeof T[key] === "string") {
      if (T[key].includes("<") && T[key].includes(">")) {
        el.innerHTML = T[key];
      } else {
        el.textContent = T[key];
      }
    }
  });
  if (inputEl) inputEl.placeholder = T.placeholder;
  if (setupKeyEl) setupKeyEl.placeholder = T.setupPlaceholder;
  if (settingLanguage) settingLanguage.value = LANG;
  const customUrlInput = document.getElementById("legal-custom-url");
  if (customUrlInput) customUrlInput.placeholder = T.legalCustomUrlPlaceholder || "";
  applyTheme(getSavedTheme());
  renderSuggestions();
  if (legalCorporaData && legalCorporaData.length > 0) {
    renderLegalCorporaList();
  }
  if (profiles && profiles.length > 0) {
    renderProfilesDropdown();
    updateActiveDomainTrigger();
  }
  loadBackendStatus();
}

if (settingLanguage) {
  settingLanguage.addEventListener("change", async (e) => {
    LANG = e.target.value;
    T = I18N[LANG] || I18N.en;
    applyLanguage();
    try {
      await fetch("/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language: LANG }),
      });
    } catch (_) { /* ignore */ }
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
  // Match standard paired double asterisks and underscores across lines
  s = s.replace(/\*\*([\s\S]+?)\*\*/g, '<strong class="font-bold">$1</strong>');
  s = s.replace(/__([\s\S]+?)__/g, '<strong class="font-bold">$1</strong>');

  // Handle unclosed bold markers (e.g. "**After the initial..." or "**Note:...") up to sentence boundary or tag/line end
  s = s.replace(/\*\*([^*<]+?)(?=[.!?]|<|$)/g, '<strong class="font-bold">$1</strong>');
  // Strip any remaining stray asterisks
  s = s.replace(/\*\*/g, "");

  s = s.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, "$1<em>$2</em>");
  s = s.replace(/(^|[^_\w])_([^_\n]+)_(?!_)/g, "$1<em>$2</em>");
  s = s.replace(
    /\[([a-zA-Z0-9_\-.\s]+\.(?:pdf|txt|md))(?:\s*\(p\.\s*(\d+)\))?\]/gi,
    (m, doc, page) => {
      const pageArg = page ? Number(page) : "null";
      const icon = doc.toLowerCase().endsWith(".pdf") ? "📕" : (doc.toLowerCase().endsWith(".md") ? "📝" : "📄");
      const label = page ? `${doc} (p. ${page})` : doc;
      return `<span class="source-chip source-pill-clickable neon-pill neon-pill-cyan" onclick="openDocumentViewer('${escapeHtml(doc)}', ${pageArg})" title="Inspect in Document Panel">${icon} ${escapeHtml(label)}</span>`;
    }
  );
  s = s.replace(
    /\[((?:Ptk\.|Btk\.)\s*\d+:[0-9A-Za-z.\s]+§|\d+:[0-9A-Za-z.\s]+§|§\s*\d+:[0-9A-Za-z.]+)\]/gi,
    (m, sec) => {
      const docName = sec.toLowerCase().includes("btk") ? "Btk." : "Ptk.";
      return `<span class="source-chip source-pill-clickable neon-pill neon-pill-violet" onclick="openDocumentViewer('${docName}', null, null, '${escapeHtml(sec)}')" title="Inspect Legal Section in Inspector">⚖️ ${escapeHtml(sec)}</span>`;
    }
  );
  s = s.replace(/(\b\d+:\d+\.?\s*§(?:\s*\[[^\]]+\])?)/g, '<span class="legal-clause-token">$1</span>');
  s = s.replace(/\u0000(\d+)\u0000/g, (_, i) => "<code>" + codes[+i] + "</code>");
  return s;
}

function sanitizeDocumentText(rawText) {
  if (!rawText) return "";
  let text = String(rawText);
  text = text.replace(/\\n/g, "\n").replace(/\\r/g, "");
  text = text.replace(/[\u00A0\u1680\u180e\u2000-\u200a\u202f\u205f\u3000\ufeff]/g, " ");
  text = text.replace(/[\u200B-\u200D]/g, "");
  // Strip isolated standalone line/page numbers on their own lines (e.g., "\n10\n" or "^10\n")
  text = text.replace(/(^|\n)\s*\d+\s*(?=\n|$)/g, "$1");
  text = text.replace(/^\s*\d+\s*\n/g, "");
  text = text.replace(/(\d+:\d+\.?)\s*§/g, "$1 §");
  text = text.replace(/\n{3,}/g, "\n\n");
  return text.trim();
}

function renderMarkdown(src) {
  const clean = sanitizeDocumentText(src);
  const lines = escapeHtml(clean).replace(/\r\n/g, "\n").split("\n");
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

    const legalSec = line.match(/^\s*(\d+:\d+\.?\s*§.*?)$/);
    if (legalSec) {
      closeTo(0);
      out.push('<div class="legal-section-header">⚖️ ' + renderInline(legalSec[1]) + '</div>');
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
// --- Message Rendering & Welcome -----------------------------------------
function renderWelcome() {
  messagesEl.innerHTML = "";
  resetInspectorState();

  const appLayout = document.getElementById("appLayout");
  if (appLayout) appLayout.classList.remove("has-active-chat");

  const welcome = document.createElement("div");
  welcome.className = "welcome";
  welcome.id = "welcome";

  const logoWrap = document.createElement("div");
  logoWrap.className = "welcome-logo-wrap";
  const logo = document.createElement("img");
  logo.src = "/static/logo.png";
  logo.alt = "Platform Logo";
  logo.className = "welcome-logo hover:scale-105";
  logo.id = "welcome-logo";
  logoWrap.appendChild(logo);

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

  welcome.append(logoWrap, badge, h2, p, sug);
  messagesEl.appendChild(welcome);
  renderSuggestions();
  if (activeConvTitleEl) {
    activeConvTitleEl.textContent = currentAppName;
    delete activeConvTitleEl.dataset.isCustom;
  }
}

window.copyMessageText = function (btn) {
  const bubble = btn.closest(".msg-bubble");
  if (!bubble) return;
  const body = bubble.querySelector(".answer-body") || bubble.querySelector(".msg-text-content") || bubble;
  navigator.clipboard.writeText(body.innerText || "").then(() => {
    btn.textContent = "✓";
    setTimeout(() => { btn.textContent = "📋"; }, 2000);
  });
};

function addMessage(role, text, opts) {
  opts = opts || {};
  const existing = messagesEl.querySelector(".welcome");
  if (existing) existing.remove();

  const appLayout = document.getElementById("appLayout");
  if (appLayout) appLayout.classList.add("has-active-chat");

  const row = document.createElement("div");
  row.className = "msg-row " + role;

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";

  if (role === "bot") {
    const cardHeader = document.createElement("div");
    cardHeader.className = "msg-card-header";
    cardHeader.innerHTML = `
      <div class="ai-header-left">
        <svg class="ai-emblem-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="var(--accent-primary, #06b6d4)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="var(--accent-primary, #06b6d4)" fill-opacity="0.2"/>
          <path d="M2 17L12 22L22 17" stroke="var(--accent-secondary, #8b5cf6)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M2 12L12 17L22 12" stroke="var(--accent-primary, #06b6d4)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span class="ai-header-title">AI generated synthesis</span>
      </div>
      <span class="ai-status-pill">Active RAG</span>
    `;
    bubble.appendChild(cardHeader);
  }

  const contentWrap = document.createElement("div");
  contentWrap.className = role === "bot" ? "answer-body" : "msg-text-content";

  if (opts.markdown) {
    contentWrap.innerHTML = renderMarkdown(text);
  } else {
    contentWrap.textContent = text;
  }
  bubble.appendChild(contentWrap);

  if (role === "bot") {
    const footer = document.createElement("div");
    footer.className = "msg-card-footer";
    footer.innerHTML = `
      <span>Verified Knowledge Synthesis</span>
      <div class="msg-card-actions">
        <button class="msg-action-btn" title="Helpful" onclick="this.style.color='#34d399'">👍</button>
        <button class="msg-action-btn" title="Not helpful" onclick="this.style.color='#ef4444'">👎</button>
        <button class="msg-action-btn" title="Copy response" onclick="copyMessageText(this)">📋</button>
      </div>
    `;
    bubble.appendChild(footer);
  }

  row.appendChild(bubble);
  messagesEl.appendChild(row);
  scrollToBottom();
  return { row, bubble, bodyEl: contentWrap };
}

function renderSources(container, sources) {
  if (!sources || sources.length === 0) return;
  const card = document.createElement("div");
  card.className = "sources-card";

  const title = document.createElement("div");
  title.className = "sources-title";
  title.textContent = T.sourcesTitle || "Referenced Sources";
  card.appendChild(title);

  const list = document.createElement("div");
  list.className = "sources-list";
  currentTurnSources.clear();
  for (const s of sources) {
    const snip = s.snippet || s.highlight_text || s.chunk_content;
    const sectionId = s.section_id || null;
    const chunk = s.chunk_content || s.snippet || s.highlight_text || "";
    if (snip || sectionId || chunk) {
      const srcObj = { snippet: snip, sectionId, page: s.page, chunkContent: chunk, name: s.name };
      currentTurnSources.set(s.name.toLowerCase(), srcObj);
      if (s.page != null) {
        currentTurnSources.set(`${s.name.toLowerCase()}:${s.page}`, srcObj);
      }
    }
    const isLegal = s.name.toLowerCase().includes("ptk") || s.name.toLowerCase().includes("btk");
    const pill = document.createElement("span");
    pill.className = `source-chip source-pill-clickable neon-pill ${isLegal ? "neon-pill-violet" : "neon-pill-cyan"}`;
    pill.setAttribute("role", "button");
    pill.setAttribute("tabindex", "0");
    pill.title = T.sourcesPillTitle || "Click to inspect in Document Panel";

    const icon = s.name.toLowerCase().endsWith(".pdf") ? "📕" : (s.name.toLowerCase().endsWith(".md") ? "📝" : "📄");
    const secLabel = sectionId ? ` [${sectionId}]` : "";
    const pageLabel = s.page != null ? ` (p. ${s.page})` : "";
    pill.textContent = `${icon} ${s.name}${secLabel}${pageLabel}`;
    pill.addEventListener("click", () => {
      openDocumentViewer(s.name, s.page, snip, sectionId);
    });
    list.appendChild(pill);
  }
  card.appendChild(list);

  const footer = container.querySelector(".msg-card-footer");
  if (footer) {
    container.insertBefore(card, footer);
  } else {
    container.appendChild(card);
  }
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
    activeConvTitleEl.textContent = q;
  }

  const { bubble, bodyEl } = addMessage("bot", "");
  const statusPill = document.createElement("div");
  statusPill.className = "streaming-status-pill";
  statusPill.textContent = stageLabel("preparing") || "Preparing search…";

  const answer = document.createElement("div");
  answer.className = "answer-stream-content";

  if (bodyEl) {
    bodyEl.innerHTML = "";
    bodyEl.appendChild(statusPill);
    bodyEl.appendChild(answer);
  } else {
    bubble.appendChild(statusPill);
    bubble.appendChild(answer);
  }

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
    if (bodyEl) {
      bodyEl.innerHTML = renderMarkdown(finalText);
    } else {
      answer.innerHTML = renderMarkdown(finalText);
    }
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
  currentTurnSources.clear();
  resetInspectorState();
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
  currentTurnSources.clear();
  resetInspectorState();
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
      if (stStorage) {
        stStorage.textContent = cfg.use_s3_storage 
          ? (T.storageS3 || "Amazon S3 Bucket") 
          : (T.storageLocal || "Local Filesystem");
      }
      if (stReady) {
        const readyText = cfg.ready 
          ? (T.statusActiveReady || "Active & Ready") 
          : (cfg.needs_api_key ? (T.statusNeedsKey || "Needs API Key") : (T.statusInit || "Initializing"));
        stReady.textContent = readyText;
        stReady.className = "status-badge " + (cfg.ready ? "ready" : "not-ready");
      }
    }
  } catch (_) { /* ignore */ }
}

// --- Profiles & Custom Domain Controller ---------------------------------
const DOMAIN_ICONS = {
  default: "🌐",
  legal: "⚖️",
  healthcare: "🏥",
  finance: "📊",
  trading: "📈",
};

function getDomainIcon(profile) {
  if (!profile) return "🌐";
  const id = (profile.id || "").toLowerCase();
  if (DOMAIN_ICONS[id]) return DOMAIN_ICONS[id];
  if (id.includes("legal") || id.includes("compli")) return "⚖️";
  if (id.includes("health") || id.includes("medic")) return "🏥";
  if (id.includes("fin") || id.includes("quant") || id.includes("trad")) return "📊";
  return "🌐";
}

function updateActiveDomainTrigger() {
  const p = profiles.find((x) => x.id === currentProfileId) || profiles[0];
  if (!p) return;
  const pName = (p.names && p.names[LANG]) || p.name || p.id;
  if (domainActiveIcon) domainActiveIcon.textContent = getDomainIcon(p);
  if (domainActiveName) domainActiveName.textContent = pName;
  if (profileSelectEl) profileSelectEl.value = p.id;
  updateActiveProfileLabel();
}

function selectProfile(id) {
  currentProfileId = id;
  updateActiveDomainTrigger();
  if (btnLegalCorpora) {
    btnLegalCorpora.style.display = id === "legal" ? "inline-flex" : "none";
  }
  if (domainDropdownMenu) {
    domainDropdownMenu.querySelectorAll(".domain-item").forEach((item) => {
      const isCurrent = item.dataset.profileId === id;
      item.classList.toggle("active", isCurrent);
      const checkEl = item.querySelector(".domain-item-check");
      if (checkEl) checkEl.textContent = isCurrent ? "✓" : "";
    });
  }
  if (id === "legal") {
    checkAndPromptLegalCorpora();
  }
}

function closeDomainDropdown() {
  if (domainDropdownMenu) domainDropdownMenu.classList.remove("show");
  if (domainDropdownTrigger) domainDropdownTrigger.setAttribute("aria-expanded", "false");
}

function toggleDomainDropdown() {
  if (!domainDropdownMenu) return;
  const willOpen = !domainDropdownMenu.classList.contains("show");
  domainDropdownMenu.classList.toggle("show", willOpen);
  if (domainDropdownTrigger) {
    domainDropdownTrigger.setAttribute("aria-expanded", willOpen ? "true" : "false");
  }
}

if (domainDropdownTrigger) {
  domainDropdownTrigger.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleDomainDropdown();
  });
}

function renderProfilesDropdown() {
  if (profileSelectEl) profileSelectEl.innerHTML = "";
  if (domainDropdownMenu) domainDropdownMenu.innerHTML = "";

  for (const p of profiles) {
    const pName = (p.names && p.names[LANG]) || p.name || p.id;
    const pDesc = (p.descriptions && p.descriptions[LANG]) || p.description || "";
    if (profileSelectEl) {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = pName;
      profileSelectEl.appendChild(opt);
    }

    if (domainDropdownMenu) {
      const item = document.createElement("div");
      item.className = "domain-item" + (p.id === currentProfileId ? " active" : "");
      item.setAttribute("role", "menuitem");
      item.dataset.profileId = p.id;
      const icon = getDomainIcon(p);
      item.innerHTML = `
        <div class="domain-item-icon">${icon}</div>
        <div class="domain-item-body">
          <div class="domain-item-title">${escapeHtml(pName)}</div>
          <div class="domain-item-desc">${escapeHtml(pDesc)}</div>
        </div>
        <div class="domain-item-check">${p.id === currentProfileId ? "✓" : ""}</div>
      `;
      item.addEventListener("click", () => {
        selectProfile(p.id);
        closeDomainDropdown();
      });
      domainDropdownMenu.appendChild(item);
    }
  }
}

async function loadProfiles() {
  try {
    const res = await fetch("/profiles");
    if (res.ok) {
      const data = await res.json();
      profiles = data.profiles || [];
      renderProfilesDropdown();

      if (!profiles.some((p) => p.id === currentProfileId) && profiles.length > 0) {
        currentProfileId = profiles[0].id;
      }
      updateActiveDomainTrigger();
    }
  } catch (_) { /* ignore */ }
}

function updateActiveProfileLabel() {
  const p = profiles.find((x) => x.id === currentProfileId);
  if (kbActiveProfileEl) {
    kbActiveProfileEl.textContent = p ? ((p.names && p.names[LANG]) || p.name) : currentProfileId;
  }
}

if (profileSelectEl) {
  profileSelectEl.addEventListener("change", (e) => {
    selectProfile(e.target.value);
  });
}

btnProfileConfig.addEventListener("click", () => {
  const p = profiles.find((x) => x.id === currentProfileId);
  if (p) {
    profIdEl.value = p.id;
    profIdEl.disabled = true;
    profNameEl.value = (p.names && p.names[LANG]) || p.name || "";
    profDescEl.value = (p.descriptions && p.descriptions[LANG]) || p.description || "";
    profPromptEl.value = (p.system_prompts && p.system_prompts[LANG]) || p.system_prompt || "";
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
  kbDocsList.innerHTML = '<tr><td colspan="4" class="text-muted">' + (T.kbLoading || "Loading documents…") + '</td></tr>';
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
    kbDocsList.innerHTML = `<tr><td colspan="4" class="text-muted">${T.kbEmpty || "No documents found for this profile."}</td></tr>`;
    return;
  }
  for (const doc of docs) {
    const tr = document.createElement("tr");
    const tdName = document.createElement("td");
    tdName.textContent = doc.filename;
    const tdSize = document.createElement("td");
    tdSize.textContent = formatBytes(doc.size);
    const tdTime = document.createElement("td");
    tdTime.textContent = doc.last_modified ? new Date(doc.last_modified).toLocaleDateString(LANG === "hu" ? "hu-HU" : "en-US") : "-";
    const tdActions = document.createElement("td");
    const delBtn = document.createElement("button");
    delBtn.className = "kb-btn-delete";
    delBtn.textContent = T.btnDelete || "Delete";
    delBtn.title = T.btnDelete || "Delete";
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
    kbUploadStatus.textContent = T.kbSelectFile || "Please select a file first.";
    kbUploadStatus.className = "status-msg error";
    return;
  }
  const formData = new FormData();
  formData.append("file", file);
  kbUploadStatus.textContent = T.kbUploading || "Uploading & indexing…";
  kbUploadStatus.className = "status-msg";
  kbUploadBtn.disabled = true;
  try {
    const res = await fetch(`/documents/upload?profile_id=${encodeURIComponent(currentProfileId)}`, {
      method: "POST",
      body: formData,
    });
    if (res.ok) {
      kbUploadStatus.textContent = T.kbUploadSuccess || "Document uploaded and indexed successfully!";
      kbUploadStatus.className = "status-msg success";
      kbFileInput.value = "";
      await loadKbDocuments();
    } else {
      const err = await res.json().catch(() => ({}));
      kbUploadStatus.textContent = err.detail || T.kbUploadFail || "Upload failed.";
      kbUploadStatus.className = "status-msg error";
    }
  } catch (_) {
    kbUploadStatus.textContent = "Network error uploading document.";
    kbUploadStatus.className = "status-msg error";
  } finally {
    kbUploadBtn.disabled = false;
  }
});


// --- Document Preview Modal & Highlighting --------------------------------
function highlightSnippetInElement(containerEl, snippet, sectionId = null) {
  if (!containerEl) return false;

  // 1. First, search DOM container for specific statutory section marker (e.g., "6:58. §")
  let effectiveSec = sectionId ? sectionId.trim() : null;
  if (!effectiveSec && snippet) {
    const secMatch = snippet.match(/(\b\d+:\d+\.\s*§|\b\d+\.\s*§)/);
    if (secMatch) effectiveSec = secMatch[1].trim();
  }

  if (effectiveSec) {
    const normSec = effectiveSec.replace(/\s+/g, " ");
    const secPattern = new RegExp(effectiveSec.replace(".", "\\.").replace(/\s+/g, "\\s*"));
    const walker = document.createTreeWalker(containerEl, NodeFilter.SHOW_TEXT, null, false);
    let node;
    while ((node = walker.nextNode())) {
      const val = node.nodeValue || "";
      if (val.includes(normSec) || secPattern.test(val)) {
        const parent = node.parentElement;
        const block = (parent && parent.closest("p, div, li, h1, h2, h3, h4, h5, h6")) || parent;
        if (block && block !== containerEl) {
          const mark = document.createElement("mark");
          mark.className = "extracted-highlight";
          mark.innerHTML = block.innerHTML;
          block.innerHTML = "";
          block.appendChild(mark);
          setTimeout(() => {
            mark.scrollIntoView({ behavior: "smooth", block: "center" });
          }, 150);
          return true;
        } else if (node.parentNode) {
          const mark = document.createElement("mark");
          mark.className = "extracted-highlight";
          mark.textContent = val;
          node.parentNode.replaceChild(mark, node);
          setTimeout(() => {
            mark.scrollIntoView({ behavior: "smooth", block: "center" });
          }, 150);
          return true;
        }
      }
    }
  }

  // 2. Candidate sentence matching with sentence-boundary expansion
  if (!snippet) return false;
  const cleanSnippet = snippet
    .replace(/\*\*/g, "")
    .replace(/(^|\n)\s*\d+\s*(?=\n|$)/g, "$1")
    .trim();
  if (cleanSnippet.length < 5) return false;

  const walker = document.createTreeWalker(containerEl, NodeFilter.SHOW_TEXT, null, false);
  let node;
  const textNodes = [];
  while ((node = walker.nextNode())) {
    if (node.nodeValue && node.nodeValue.trim().length > 0) {
      textNodes.push(node);
    }
  }

  const sentences = cleanSnippet
    .split(/(?<=[.!?\n])\s+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 20);

  const fullSentences = sentences.filter((s) => /^[A-Z0-9„"']/.test(s));

  const candidates = [
    cleanSnippet,
    ...(fullSentences.length > 0 ? fullSentences : sentences),
    cleanSnippet.slice(0, 80).trim(),
    cleanSnippet.slice(0, 40).trim(),
  ];

  for (const target of candidates) {
    if (!target || target.length < 6) continue;
    for (const textNode of textNodes) {
      const idx = textNode.nodeValue.indexOf(target);
      if (idx !== -1) {
        // Expand backwards to natural sentence boundary (ignore single newlines, stop at .!? or double newline)
        let startIdx = idx;
        while (startIdx > 0 && !/[.!?]/.test(textNode.nodeValue[startIdx - 1])) {
          if (textNode.nodeValue[startIdx - 1] === "\n" && startIdx > 1 && textNode.nodeValue[startIdx - 2] === "\n") {
            break;
          }
          startIdx--;
        }
        while (startIdx < idx && /\s/.test(textNode.nodeValue[startIdx])) {
          startIdx++;
        }

        // Expand forward to natural sentence boundary
        let endIdx = idx + target.length;
        while (endIdx < textNode.nodeValue.length && !/[.!?]/.test(textNode.nodeValue[endIdx])) {
          if (textNode.nodeValue[endIdx] === "\n" && endIdx + 1 < textNode.nodeValue.length && textNode.nodeValue[endIdx + 1] === "\n") {
            break;
          }
          endIdx++;
        }
        if (endIdx < textNode.nodeValue.length && /[.!?]/.test(textNode.nodeValue[endIdx])) {
          endIdx++;
        }

        const before = textNode.nodeValue.substring(0, startIdx);
        const match = textNode.nodeValue.substring(startIdx, endIdx);
        const after = textNode.nodeValue.substring(endIdx);

        const parent = textNode.parentNode;
        if (!parent) continue;

        const mark = document.createElement("mark");
        mark.className = "extracted-highlight";
        mark.textContent = match;

        const fragment = document.createDocumentFragment();
        if (before) fragment.appendChild(document.createTextNode(before));
        fragment.appendChild(mark);
        if (after) fragment.appendChild(document.createTextNode(after));

        parent.replaceChild(fragment, textNode);
        setTimeout(() => {
          mark.scrollIntoView({ behavior: "smooth", block: "center" });
        }, 150);
        return true;
      }
    }
  }
  return false;
}

const KNOWLEDGE_GRAPH_NODES = {
  QUERY: {
    key: "QUERY",
    label: "QUERY",
    badge: "User Prompt",
    title: "Active Natural Language Query",
    fill: "#38bdf8",
    glow: "#06b6d4",
    desc: "The user query submitted to the Multi-Domain RAG Assistant, translated or routed based on domain rules (e.g. Hungarian preservation for Legal).",
    connections: ["Embeddings Pipeline", "Synthesized Response"]
  },
  SYNTHESIS: {
    key: "SYNTHESIS",
    label: "SYNTHESIS",
    badge: "RAG Synthesis",
    title: "AI Knowledge Synthesis",
    fill: "#818cf8",
    glow: "#6366f1",
    desc: "The generated response compiled from verified knowledge retrieved across domain-specific corpora.",
    connections: ["User Query", "Retrieved Document Chunk"]
  },
  EMBED: {
    key: "EMBED",
    label: "EMBED",
    badge: "Vector Space",
    title: "ChromaDB Embedding Space",
    fill: "#a78bfa",
    glow: "#8b5cf6",
    desc: "Dense semantic vector representations generated by the embedding model (e.g. text-embedding-3-small or multilingual models) for similarity search.",
    connections: ["User Query", "Retrieved Document Chunk"]
  },
  DOC: {
    key: "DOC",
    label: "DOC",
    badge: "Source File",
    title: "Source Document / Page",
    fill: "#c084fc",
    glow: "#a855f7",
    desc: "The verified source file indexed in the knowledge base (PDF, Markdown, or Law Corpus).",
    connections: ["Statutory Clause / §", "Retrieved Document Chunk"]
  },
  CLAUSE: {
    key: "CLAUSE",
    label: "CLAUSE",
    badge: "Statutory §",
    title: "Referenced Section / Clause",
    fill: "#f472b6",
    glow: "#ec4899",
    desc: "Specific statutory section (e.g., Ptk. 6:58. §, Btk. 222. §) or contract clause identified during semantic search.",
    connections: ["Source Document", "Domain Legal Norm"]
  },
  NORM: {
    key: "NORM",
    label: "NORM",
    badge: "Standard",
    title: "Domain Standard / Norm",
    fill: "#34d399",
    glow: "#10b981",
    desc: "Overarching legal framework or market regulation governing the active topic.",
    connections: ["Statutory Clause / §"]
  }
};

function renderDocumentGraph(docName, sectionId) {
  if (!docGraphSvg) return;
  const pill = document.getElementById("graphDocPill");
  if (pill) pill.textContent = sectionId || docName || "Knowledge Nodes";

  const primaryColor = getComputedStyle(document.documentElement).getPropertyValue("--accent-primary").trim() || "#38bdf8";
  const secondaryColor = getComputedStyle(document.documentElement).getPropertyValue("--accent-secondary").trim() || "#c084fc";

  const nodes = [
    { key: "QUERY", x: 45, y: 48, r: 10, label: "QUERY", fill: primaryColor, glow: primaryColor },
    { key: "SYNTHESIS", x: 130, y: 30, r: 12, label: "SYNTHESIS", fill: "#818cf8", glow: "#6366f1" },
    { key: "EMBED", x: 130, y: 68, r: 9, label: "EMBED", fill: "#a78bfa", glow: "#8b5cf6" },
    { key: "DOC", x: 220, y: 48, r: 14, label: "DOC", fill: secondaryColor, glow: secondaryColor },
    { key: "CLAUSE", x: 310, y: 28, r: 11, label: "CLAUSE", fill: "#f472b6", glow: "#ec4899" },
    { key: "NORM", x: 315, y: 70, r: 10, label: "NORM", fill: "#34d399", glow: "#10b981" },
  ];

  const links = [
    { x1: 45, y1: 48, x2: 130, y2: 30 },
    { x1: 45, y1: 48, x2: 130, y2: 68 },
    { x1: 130, y1: 30, x2: 220, y2: 48 },
    { x1: 130, y1: 68, x2: 220, y2: 48 },
    { x1: 220, y1: 48, x2: 310, y2: 28 },
    { x1: 220, y1: 48, x2: 315, y2: 70 },
  ];

  let svgHtml = `
    <defs>
      <filter id="glow-filter" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
        <feMerge>
          <feMergeNode in="coloredBlur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>
  `;

  for (const l of links) {
    svgHtml += `<line x1="${l.x1}" y1="${l.y1}" x2="${l.x2}" y2="${l.y2}" stroke="${hexToRgba(secondaryColor, 0.45)}" stroke-width="2" stroke-dasharray="3,2"/>`;
  }

  for (const n of nodes) {
    const safeDoc = (docName || "").replace(/'/g, "\\'").replace(/"/g, '&quot;');
    const safeSec = (sectionId || "").replace(/'/g, "\\'").replace(/"/g, '&quot;');
    svgHtml += `
      <g class="graph-node-group" style="cursor: pointer;" data-node-key="${n.key}" onclick="openKnowledgeGraphModal('${safeDoc}', '${safeSec}', '${n.key}')">
        <title>${n.label}: Click to inspect concept topology</title>
        <circle cx="${n.x}" cy="${n.y}" r="${n.r + 3}" fill="${n.glow}" opacity="0.3" filter="url(#glow-filter)"/>
        <circle cx="${n.x}" cy="${n.y}" r="${n.r}" fill="${n.fill}" stroke="#fff" stroke-width="1.5"/>
        <text x="${n.x}" y="${n.y + 3}" font-size="6.5" font-weight="700" fill="#0b0f17" text-anchor="middle" font-family="sans-serif">${n.label.slice(0, 3)}</text>
      </g>
    `;
  }

  docGraphSvg.innerHTML = svgHtml;
}

// Fullscreen Interactive Knowledge Graph Modal Functions
function openKnowledgeGraphModal(docName, sectionId, activeNodeKey = "DOC") {
  if (!modalGraphViewer) return;

  if (graphModalTitle) {
    graphModalTitle.textContent = `Document Knowledge Graph: ${docName || "Active Sources"}`;
  }
  if (graphModalSubtitle) {
    graphModalSubtitle.textContent = `Visualizing semantic relationships, vector embeddings & statutory topology for ${sectionId || docName || "referenced context"}`;
  }

  const primaryColor = getComputedStyle(document.documentElement).getPropertyValue("--accent-primary").trim() || "#38bdf8";
  const secondaryColor = getComputedStyle(document.documentElement).getPropertyValue("--accent-secondary").trim() || "#c084fc";

  const modalNodes = [
    { key: "QUERY", x: 100, y: 190, r: 24, label: "QUERY", fill: primaryColor, glow: primaryColor },
    { key: "SYNTHESIS", x: 260, y: 110, r: 28, label: "SYNTHESIS", fill: "#818cf8", glow: "#6366f1" },
    { key: "EMBED", x: 260, y: 270, r: 22, label: "EMBED", fill: "#a78bfa", glow: "#8b5cf6" },
    { key: "DOC", x: 440, y: 190, r: 32, label: "DOC CHUNK", fill: secondaryColor, glow: secondaryColor },
    { key: "CLAUSE", x: 620, y: 110, r: 26, label: "CLAUSE §", fill: "#f472b6", glow: "#ec4899" },
    { key: "NORM", x: 630, y: 270, r: 24, label: "NORM", fill: "#34d399", glow: "#10b981" },
  ];

  const modalLinks = [
    { x1: 100, y1: 190, x2: 260, y2: 110 },
    { x1: 100, y1: 190, x2: 260, y2: 270 },
    { x1: 260, y1: 110, x2: 440, y2: 190 },
    { x1: 260, y1: 270, x2: 440, y2: 190 },
    { x1: 440, y1: 190, x2: 620, y2: 110 },
    { x1: 440, y1: 190, x2: 630, y2: 270 },
    { x1: 620, y1: 110, x2: 630, y2: 270 },
  ];

  if (graphModalSvg) {
    let svg = `
      <defs>
        <filter id="modal-glow-filter" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="6" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
    `;

    for (const l of modalLinks) {
      svg += `<line x1="${l.x1}" y1="${l.y1}" x2="${l.x2}" y2="${l.y2}" stroke="${hexToRgba(secondaryColor, 0.45)}" stroke-width="3" stroke-dasharray="6,4"/>`;
    }

    for (const n of modalNodes) {
      const isSelected = n.key === activeNodeKey;
      svg += `
        <g class="modal-graph-node" data-key="${n.key}" style="cursor: pointer;">
          <circle cx="${n.x}" cy="${n.y}" r="${n.r + 8}" fill="${n.glow}" opacity="${isSelected ? '0.6' : '0.25'}" filter="url(#modal-glow-filter)"/>
          <circle cx="${n.x}" cy="${n.y}" r="${n.r}" fill="${n.fill}" stroke="${isSelected ? '#fff' : 'rgba(255,255,255,0.7)'}" stroke-width="${isSelected ? '3.5' : '2'}"/>
          <text x="${n.x}" y="${n.y + 4}" font-size="9" font-weight="700" fill="#0b0f17" text-anchor="middle" font-family="sans-serif">${n.label}</text>
        </g>
      `;
    }

    graphModalSvg.innerHTML = svg;

    graphModalSvg.querySelectorAll(".modal-graph-node").forEach((nodeEl) => {
      const key = nodeEl.getAttribute("data-key");
      nodeEl.addEventListener("click", () => {
        selectGraphNodeDetails(key, docName, sectionId);
        openKnowledgeGraphModal(docName, sectionId, key);
      });
      nodeEl.addEventListener("mouseenter", () => {
        selectGraphNodeDetails(key, docName, sectionId);
      });
    });
  }

  selectGraphNodeDetails(activeNodeKey, docName, sectionId);
  modalGraphViewer.classList.add("show");
}

function selectGraphNodeDetails(nodeKey, docName, sectionId) {
  const meta = KNOWLEDGE_GRAPH_NODES[nodeKey] || KNOWLEDGE_GRAPH_NODES.DOC;
  if (nodeDetailTitle) nodeDetailTitle.textContent = meta.title;
  if (nodeDetailBadge) nodeDetailBadge.textContent = meta.badge;
  if (nodeDetailDesc) {
    let extra = "";
    if (nodeKey === "DOC" && docName) extra = ` Active File: <strong>${escapeHtml(docName)}</strong>.`;
    if (nodeKey === "CLAUSE" && sectionId) extra = ` Cited Clause: <strong>${escapeHtml(sectionId)}</strong>.`;
    nodeDetailDesc.innerHTML = `${meta.desc}${extra}`;
  }
  if (nodeConnectionsList) {
    nodeConnectionsList.innerHTML = meta.connections.map((c) => `
      <div class="node-conn-item">
        <span class="conn-type">LINKED:</span>
        <span>${escapeHtml(c)}</span>
      </div>
    `).join("");
  }
}

function closeKnowledgeGraphModal() {
  if (modalGraphViewer) {
    modalGraphViewer.classList.remove("show");
  }
}

window.openKnowledgeGraphModal = openKnowledgeGraphModal;

if (graphInfoBtn && graphTooltipPopover) {
  graphInfoBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    graphTooltipPopover.classList.toggle("hidden");
  });
}
if (btnExpandGraph) {
  btnExpandGraph.addEventListener("click", () => {
    const docName = docViewerTitle ? docViewerTitle.textContent : "Document";
    const secId = docViewerSubtitle ? docViewerSubtitle.textContent : "";
    openKnowledgeGraphModal(docName, secId, "DOC");
  });
}
if (graphModalClose) {
  graphModalClose.addEventListener("click", closeKnowledgeGraphModal);
}

function closeDocumentInspector() {
  if (docInspectorPane) {
    docInspectorPane.classList.remove("open");
    const appLayout = document.getElementById("appLayout");
    if (appLayout) appLayout.classList.remove("inspector-open");
  }
}

function resetInspectorState() {
  closeDocumentInspector();
  // Reset inspector content to placeholder
  if (docViewerContent) {
    docViewerContent.innerHTML = `
      <div class="inspector-placeholder">
        <div class="placeholder-icon">📖</div>
        <h4>Document Inspector</h4>
        <p>Click any source citation badge in a response to view the verified legal text and highlighted clauses here.</p>
      </div>
    `;
  }
  // Reset inspector header metadata
  if (docViewerTitle) docViewerTitle.textContent = T.docViewerTitle || "Document Inspector";
  if (docViewerSubtitle) docViewerSubtitle.textContent = T.docViewerSubtitle || "Full Verified Document";
  if (docTypeBadge) docTypeBadge.textContent = "TEXT";
  if (docViewerIcon) docViewerIcon.textContent = "📄";
  if (docViewerLoading) docViewerLoading.style.display = "none";
  // Reset graph widget to initial state
  if (docGraphSvg) docGraphSvg.innerHTML = "";
  if (graphTooltipPopover) graphTooltipPopover.classList.add("hidden");
  // Reset node detail inspector
  if (nodeDetailTitle) nodeDetailTitle.textContent = "";
  if (nodeDetailBadge) nodeDetailBadge.textContent = "";
  if (nodeDetailDesc) nodeDetailDesc.textContent = "";
  if (nodeConnectionsList) nodeConnectionsList.innerHTML = "";
  // Clear active file references and turn sources
  activePdfFilename = null;
  activePdfPage = 1;
  currentTurnSources.clear();
}

function escapeRegex(string) {
  return (string || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

let currentTextFontSize = 15;

// Universal High-Resolution Full Document Viewer (PDF, TXT, MD, Legal Corpora)
async function openUniversalDocumentViewer(filename, page = 1, targetSnippet = "") {
  if (!modalPdfViewer) return;
  activePdfFilename = filename;
  activePdfPage = page || 1;
  currentPdfZoom = 100;
  currentTextFontSize = 15;

  const isPdf = filename.toLowerCase().endsWith(".pdf");
  const isLegal = filename.toLowerCase().includes("ptk") || filename.toLowerCase().includes("btk");

  if (pdfModalTitle) pdfModalTitle.textContent = filename;
  if (pdfModalPageInfo) {
    pdfModalPageInfo.textContent = isPdf
      ? `Page ${activePdfPage} · Original Source PDF`
      : (isLegal ? "Official Legal Statute Corpus · Full Reader" : "Full Document Reader");
  }

  const univDocIcon = document.getElementById("univDocIcon");
  if (univDocIcon) {
    univDocIcon.textContent = isPdf ? "📕" : (isLegal ? "⚖️" : (filename.toLowerCase().endsWith(".md") ? "📝" : "📄"));
  }

  const profileParam = currentProfileId ? `?profile_id=${encodeURIComponent(currentProfileId)}` : "";
  const downloadUrl = `/documents/${encodeURIComponent(filename)}/download${profileParam}`;
  if (pdfModalDownloadBtn) {
    pdfModalDownloadBtn.href = downloadUrl;
    pdfModalDownloadBtn.download = filename;
  }

  const pdfZoomGroup = document.getElementById("univPdfZoomGroup");
  const textZoomGroup = document.getElementById("univTextZoomGroup");
  const textContainer = document.getElementById("univTextContainer");
  const textLoading = document.getElementById("univTextLoading");
  const textContent = document.getElementById("univTextContent");

  if (isPdf) {
    if (pdfZoomGroup) pdfZoomGroup.style.display = "flex";
    if (textZoomGroup) textZoomGroup.style.display = "none";
    if (textContainer) textContainer.style.display = "none";
    if (pdfModalFrame) {
      pdfModalFrame.style.display = "block";
      pdfModalFrame.src = `${downloadUrl}#page=${activePdfPage}&zoom=100&toolbar=1`;
    }
    if (pdfZoomLevel) pdfZoomLevel.textContent = "100%";
  } else {
    if (pdfZoomGroup) pdfZoomGroup.style.display = "none";
    if (textZoomGroup) textZoomGroup.style.display = "flex";
    if (pdfModalFrame) {
      pdfModalFrame.style.display = "none";
      pdfModalFrame.src = "about:blank";
    }
    if (textContainer) {
      textContainer.style.display = "block";
      textContainer.style.fontSize = `${currentTextFontSize}px`;
    }
    if (textLoading) textLoading.style.display = "flex";
    if (textContent) textContent.innerHTML = "";

    try {
      let fullText = "";
      const ctxRes = await fetch(`/documents/${encodeURIComponent(filename)}/context?${profileParam ? profileParam.slice(1) : ""}`);
      if (ctxRes.ok) {
        const ctxData = await ctxRes.json();
        fullText = ctxData.full_text || "";
      }
      if (!fullText) {
        const dlRes = await fetch(downloadUrl);
        if (dlRes.ok) {
          fullText = await dlRes.text();
        }
      }

      if (textLoading) textLoading.style.display = "none";

      if (textContent) {
        if (!fullText) {
          textContent.innerHTML = `<div class="text-muted" style="text-align: center; padding: 40px 0;">Could not load document text for ${escapeHtml(filename)}.</div>`;
        } else {
          const sanitized = sanitizeDocumentText(fullText);
          let renderedHtml = renderMarkdown(sanitized);

          if (targetSnippet) {
            const cleanTarget = sanitizeDocumentText(targetSnippet).slice(0, 70).trim();
            if (cleanTarget) {
              const regex = new RegExp("(" + escapeRegex(cleanTarget) + ")", "i");
              if (regex.test(renderedHtml)) {
                renderedHtml = renderedHtml.replace(regex, '<mark class="full-doc-highlight" id="fullDocActiveHighlight">$1</mark>');
              }
            }
          }

          textContent.innerHTML = renderedHtml;

          setTimeout(() => {
            const hl = document.getElementById("fullDocActiveHighlight");
            if (hl) {
              hl.scrollIntoView({ behavior: "smooth", block: "center" });
            }
          }, 120);
        }
      }
    } catch (err) {
      console.warn("Failed to load full document text:", err);
      if (textLoading) textLoading.style.display = "none";
      if (textContent) {
        textContent.innerHTML = `<div class="text-muted" style="text-align: center; padding: 40px 0;">Failed to load document text.</div>`;
      }
    }
  }

  modalPdfViewer.classList.add("show");
}

function openFullscreenPdfViewer(filename, page = 1) {
  openUniversalDocumentViewer(filename, page);
}

function closeFullscreenPdfViewer() {
  if (!modalPdfViewer) return;
  modalPdfViewer.classList.remove("show");
  if (pdfModalFrame) {
    pdfModalFrame.src = "about:blank";
  }
}

function updatePdfZoom(delta) {
  if (delta === 0) {
    currentPdfZoom = 100;
  } else {
    currentPdfZoom = Math.max(50, Math.min(250, currentPdfZoom + delta));
  }
  if (pdfZoomLevel) pdfZoomLevel.textContent = `${currentPdfZoom}%`;
  if (pdfModalFrame && activePdfFilename) {
    const profileParam = currentProfileId ? `?profile_id=${encodeURIComponent(currentProfileId)}` : "";
    pdfModalFrame.src = `/documents/${encodeURIComponent(activePdfFilename)}/download${profileParam}#page=${activePdfPage}&zoom=${currentPdfZoom}&toolbar=1`;
  }
}

if (pdfModalClose) {
  pdfModalClose.addEventListener("click", closeFullscreenPdfViewer);
}
if (pdfZoomIn) {
  pdfZoomIn.addEventListener("click", () => updatePdfZoom(25));
}
if (pdfZoomOut) {
  pdfZoomOut.addEventListener("click", () => updatePdfZoom(-25));
}
if (pdfZoomReset) {
  pdfZoomReset.addEventListener("click", () => updatePdfZoom(0));
}

const univFontDecrease = document.getElementById("univFontDecrease");
const univFontIncrease = document.getElementById("univFontIncrease");
if (univFontDecrease) {
  univFontDecrease.addEventListener("click", () => {
    currentTextFontSize = Math.max(12, currentTextFontSize - 2);
    const textContainer = document.getElementById("univTextContainer");
    if (textContainer) textContainer.style.fontSize = `${currentTextFontSize}px`;
  });
}
if (univFontIncrease) {
  univFontIncrease.addEventListener("click", () => {
    currentTextFontSize = Math.min(26, currentTextFontSize + 2);
    const textContainer = document.getElementById("univTextContainer");
    if (textContainer) textContainer.style.fontSize = `${currentTextFontSize}px`;
  });
}

function renderExtractedContextCard(opts) {
  if (!docViewerContent) return;
  docViewerContent.innerHTML = "";

  const cleanPre = opts.precedingContext ? sanitizeDocumentText(opts.precedingContext) : "";
  const cleanPost = opts.succeedingContext ? sanitizeDocumentText(opts.succeedingContext) : "";

  const card = document.createElement("div");
  card.className = "extracted-context-card";
  card.innerHTML = `
    <div class="extracted-context-meta">
      <div class="extracted-badge-row">
        <span class="context-type-badge">${opts.isPdf ? "Extracted RAG Chunk" : "Verified Source"}</span>
        ${opts.page != null ? `<span class="context-page-badge">Page ${opts.page}</span>` : ""}
        ${opts.targetSection ? `<span class="context-section-badge">${escapeHtml(opts.targetSection)}</span>` : ""}
      </div>
    </div>
    <div class="context-container">
      ${cleanPre ? `
        <div class="context-preceding">
          <div class="context-preceding-label">Preceding Context</div>
          <div class="context-preceding-body">${renderMarkdown(cleanPre)}</div>
        </div>
      ` : ""}
      <div class="extracted-chunk-body" id="extractedChunkText"></div>
      ${cleanPost ? `
        <div class="context-succeeding">
          <div class="context-succeeding-label">Succeeding Context</div>
          <div class="context-succeeding-body">${renderMarkdown(cleanPost)}</div>
        </div>
      ` : ""}
    </div>
  `;

  docViewerContent.appendChild(card);

  const chunkBody = card.querySelector("#extractedChunkText");
  if (chunkBody) {
    chunkBody.innerHTML = renderMarkdown(opts.chunkText);
    highlightSnippetInElement(chunkBody, opts.highlightText, opts.targetSection);
  }
}

window.openDocumentViewer = async function (filename, page = null, snippet = null, sectionId = null) {
  if (docInspectorPane) {
    docInspectorPane.classList.add("open");
    const appLayout = document.getElementById("appLayout");
    if (appLayout) appLayout.classList.add("inspector-open");
  }

  let effectiveFile = filename;
  const lowerName = filename.toLowerCase();
  if (lowerName.includes("ptk")) {
    effectiveFile = "ptk_2013_v.txt";
  } else if (lowerName.includes("btk")) {
    effectiveFile = "btk_2012_c.txt";
  }

  const isPdf = effectiveFile.toLowerCase().endsWith(".pdf");
  const isLegal = effectiveFile.toLowerCase().includes("ptk") || effectiveFile.toLowerCase().includes("btk");

  if (docViewerTitle) docViewerTitle.textContent = filename;
  if (docViewerSubtitle) {
    if (sectionId) {
      docViewerSubtitle.textContent = page != null ? `${sectionId} (Page ${page})` : `${sectionId}`;
    } else {
      docViewerSubtitle.textContent = page != null ? `Page ${page}` : "Full Document";
    }
  }

  if (docTypeBadge) {
    docTypeBadge.textContent = isPdf ? (page != null ? `PDF · p. ${page}` : "PDF") : (isLegal ? "LEGAL" : (effectiveFile.endsWith(".md") ? "MD" : "TXT"));
  }

  if (docViewerDownloadBtn) {
    docViewerDownloadBtn.href = `/documents/${encodeURIComponent(effectiveFile)}/download?profile_id=${encodeURIComponent(currentProfileId)}`;
    docViewerDownloadBtn.download = effectiveFile;
  }

  if (docViewerIcon) {
    docViewerIcon.textContent = isPdf ? "📕" : (effectiveFile.toLowerCase().endsWith(".md") ? "📝" : "📄");
  }

  const btnViewFullDoc = document.getElementById("btn-view-full-doc") || btnViewPdf;
  if (btnViewFullDoc) {
    btnViewFullDoc.style.display = "inline-flex";
    btnViewFullDoc.onclick = () => openUniversalDocumentViewer(effectiveFile, page || 1, snippet);
  }

  renderDocumentGraph(filename, sectionId);

  // Retrieve source chunk and snippet information from current turn
  const key = filename.toLowerCase();
  const effKey = effectiveFile.toLowerCase();
  const srcInfo = (page != null ? currentTurnSources.get(`${key}:${page}`) : null) ||
                  (page != null ? currentTurnSources.get(`${effKey}:${page}`) : null) ||
                  currentTurnSources.get(key) ||
                  currentTurnSources.get(effKey);

  let targetSnippet = snippet;
  let targetSection = sectionId;
  let targetChunk = null;

  if (srcInfo) {
    if (typeof srcInfo === "object") {
      targetSnippet = targetSnippet || srcInfo.snippet || srcInfo.highlight_text;
      targetSection = targetSection || srcInfo.sectionId;
      targetChunk = srcInfo.chunkContent || srcInfo.chunk_content || targetSnippet;
    } else if (typeof srcInfo === "string" && !targetSnippet) {
      targetSnippet = srcInfo;
      targetChunk = srcInfo;
    }
  }

  if (docViewerLoading) docViewerLoading.style.display = "flex";

  // Fetch expanded document context with preceding/succeeding context lines and full-sentence highlight
  try {
    const queryParams = new URLSearchParams();
    if (page != null) queryParams.set("page", page);
    if (targetSnippet) queryParams.set("snippet", targetSnippet);
    if (currentProfileId) queryParams.set("profile_id", currentProfileId);

    const res = await fetch(`/documents/${encodeURIComponent(effectiveFile)}/context?${queryParams.toString()}`);
    if (res.ok) {
      const data = await res.json();
      if (docViewerLoading) docViewerLoading.style.display = "none";

      const chunkToRender = targetChunk || data.highlight || targetSnippet || data.full_text;
      const highlightSentence = data.highlight || targetSnippet || "";
      const preContext = data.preceding_context || "";
      const postContext = data.succeeding_context || "";
      if (btnViewFullDoc) {
        btnViewFullDoc.onclick = () => openUniversalDocumentViewer(effectiveFile, data.page || page || 1, highlightSentence || targetSnippet || snippet);
      }

      renderExtractedContextCard({
        isPdf,
        effectiveFile,
        page: data.page || page,
        targetSection,
        chunkText: chunkToRender,
        highlightText: highlightSentence,
        precedingContext: preContext,
        succeedingContext: postContext,
      });
      return;
    }
  } catch (err) {
    console.warn("Context fetch failed, falling back to local rendering:", err);
  }

  // Fallback if /context is unavailable
  if (docViewerLoading) docViewerLoading.style.display = "none";
  renderExtractedContextCard({
    isPdf,
    effectiveFile,
    page,
    targetSection,
    chunkText: targetChunk || targetSnippet || `Extracted text from ${filename}.`,
    highlightText: targetSnippet || "",
    precedingContext: "",
    succeedingContext: "",
  });
};

if (docInspectorClose) {
  docInspectorClose.addEventListener("click", closeDocumentInspector);
}
if (docViewerClose && docViewerClose !== docInspectorClose) {
  docViewerClose.addEventListener("click", closeDocumentInspector);
}

if (btnToggleInspector) {
  btnToggleInspector.addEventListener("click", () => {
    if (docInspectorPane) {
      docInspectorPane.classList.toggle("open");
      const appLayout = document.getElementById("appLayout");
      if (appLayout) appLayout.classList.toggle("inspector-open", docInspectorPane.classList.contains("open"));
    }
  });
}

if (btnToggleGraph && docGraphWidget) {
  btnToggleGraph.addEventListener("click", () => {
    docGraphWidget.classList.toggle("hidden");
    btnToggleGraph.classList.toggle("active", !docGraphWidget.classList.contains("hidden"));
  });
}

if (navLegal) {
  navLegal.addEventListener("click", () => {
    loadLegalCorpora();
    if (modalLegalCorpus) modalLegalCorpus.classList.add("show");
  });
}

if (navSettings) {
  navSettings.addEventListener("click", () => {
    if (modalSettings) modalSettings.classList.add("show");
  });
}

if (composerDocBtn) {
  composerDocBtn.addEventListener("click", () => {
    if (btnToggleInspector) btnToggleInspector.click();
  });
}

if (composerPromptBtn) {
  composerPromptBtn.addEventListener("click", () => {
    const sug = T.suggestions || [];
    if (sug.length > 0) {
      const nextSug = sug[Math.floor(Math.random() * sug.length)];
      inputEl.value = nextSug;
      autoGrow();
      inputEl.focus();
    }
  });
}

// --- Legal Corpora Management ---------------------------------------------
async function loadLegalCorpora() {
  if (!legalCorporaList) return;
  try {
    const res = await fetch("/legal/corpora");
    if (res.ok) {
      const data = await res.json();
      legalCorporaData = data.corpora || [];
      renderLegalCorporaList();
    } else {
      legalCorporaList.innerHTML = `<div class="status-msg error">Failed to load legal corpora list.</div>`;
    }
  } catch (err) {
    legalCorporaList.innerHTML = `<div class="status-msg error">Error fetching legal corpora: ${escapeHtml(err.message)}</div>`;
  }
}

function renderLegalCorporaList() {
  if (!legalCorporaList) return;
  legalCorporaList.innerHTML = "";

  if (legalCorporaData.length === 0) {
    legalCorporaList.innerHTML = `<div class="text-muted">${T.legalNotSynced || "No legal corpora configured."}</div>`;
    return;
  }

  for (const c of legalCorporaData) {
    const item = document.createElement("label");
    item.className = "legal-corpus-item";

    const badgeClass = c.status === "cached" ? "badge-cached" : (c.status === "update_available" ? "badge-update" : "badge-available");
    const badgeLabel = c.status === "cached" ? (T.badgeCached || "Cached & Ready") : (c.status === "update_available" ? (T.badgeUpdate || "Update Available") : (T.badgeAvailable || "Available"));

    const sizeStr = c.size_bytes > 0 ? (c.size_bytes / 1024).toFixed(1) + " KB" : (T.legalRemote || "Remote");
    const dateStr = c.last_synced ? new Date(c.last_synced).toLocaleString(LANG === "hu" ? "hu-HU" : "en-US") : (T.legalNotSynced || "Not synced yet");
    const sourceLabel = c.source || (T.legalSourceLabel || (LANG === "hu" ? "Forrás: Nemzeti Jogszabálytár (njt.hu)" : "Source: Nemzeti Jogszabálytár (njt.hu)"));
    const sourceUrl = c.source_url || c.url || "https://njt.hu";

    item.innerHTML = `
      <input type="checkbox" value="${escapeHtml(c.id)}" ${c.is_active || c.status === "cached" ? "checked" : ""} />
      <div class="legal-corpus-item-body">
        <div class="legal-corpus-header-line">
          <span class="legal-corpus-name">${escapeHtml(c.name)}</span>
          <span class="legal-corpus-badge ${badgeClass}">${badgeLabel}</span>
        </div>
        <div class="legal-corpus-desc">${escapeHtml(c.description)}</div>
        <div class="legal-corpus-meta">
          <span>📦 ${sizeStr}</span>
          <span>🕒 ${dateStr}</span>
          <span class="legal-source-tag">🏛️ ${escapeHtml(sourceLabel)}</span>
          <a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer" class="legal-source-link" onclick="event.stopPropagation()">🌐 njt.hu</a>
        </div>
      </div>
    `;
    legalCorporaList.appendChild(item);
  }
}

async function checkAndPromptLegalCorpora() {
  try {
    const res = await fetch("/legal/corpora");
    if (res.ok) {
      const data = await res.json();
      legalCorporaData = data.corpora || [];
      renderLegalCorporaList();
      const hasCached = legalCorporaData.some((c) => c.status === "cached" && c.is_active);
      if (!hasCached && modalLegalCorpus) {
        modalLegalCorpus.classList.add("show");
      }
    }
  } catch (_) { /* ignore */ }
}

async function syncLegalCorpora() {
  if (!legalCorporaList) return;
  const checkboxes = legalCorporaList.querySelectorAll("input[type='checkbox']:checked");
  const activeCorpora = Array.from(checkboxes).map((cb) => cb.value);

  const customUrlInput = document.getElementById("legal-custom-url");
  const customUrl = customUrlInput ? customUrlInput.value.trim() : "";

  if (activeCorpora.length === 0 && !customUrl) {
    if (legalSyncProgressContainer) legalSyncProgressContainer.style.display = "block";
    if (legalSyncStatus) {
      legalSyncStatus.textContent = T.legalSelectStatute || "Please select at least one legal statute to index.";
      legalSyncStatus.style.color = "var(--danger)";
    }
    return;
  }

  if (legalSyncProgressContainer) legalSyncProgressContainer.style.display = "block";
  if (legalSyncProgressBar) legalSyncProgressBar.style.width = "40%";
  if (legalSyncStatus) {
    legalSyncStatus.textContent = T.legalSyncing || "Checking remote ETags & indexing into Legal vector store…";
    legalSyncStatus.style.color = "var(--text-muted)";
  }
  if (btnSyncLegalCorpora) btnSyncLegalCorpora.disabled = true;

  try {
    const res = await fetch("/legal/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ active_corpora: activeCorpora }),
    });
    if (legalSyncProgressBar) legalSyncProgressBar.style.width = "100%";
    if (res.ok) {
      const result = await res.json();
      if (legalSyncStatus) {
        legalSyncStatus.textContent = T.legalSuccess || result.message || "Legal statutes synced and indexed successfully!";
        legalSyncStatus.style.color = "var(--success)";
      }

      await loadLegalCorpora();
      setTimeout(() => {
        if (modalLegalCorpus) modalLegalCorpus.classList.remove("show");
        if (legalSyncProgressContainer) legalSyncProgressContainer.style.display = "none";
      }, 1200);
    } else {
      const err = await res.json().catch(() => ({}));
      if (legalSyncStatus) {
        legalSyncStatus.textContent = err.detail || "Sync failed.";
        legalSyncStatus.style.color = "var(--danger)";
      }
    }
  } catch (e) {
    if (legalSyncStatus) {
      legalSyncStatus.textContent = "Network error syncing legal corpora.";
      legalSyncStatus.style.color = "var(--danger)";
    }
  } finally {
    if (btnSyncLegalCorpora) btnSyncLegalCorpora.disabled = false;
  }
}

if (legalCorpusClose) {
  legalCorpusClose.addEventListener("click", () => {
    if (modalLegalCorpus) modalLegalCorpus.classList.remove("show");
  });
}
if (btnCloseLegalModal) {
  btnCloseLegalModal.addEventListener("click", () => {
    if (modalLegalCorpus) modalLegalCorpus.classList.remove("show");
  });
}
if (btnSyncLegalCorpora) {
  btnSyncLegalCorpora.addEventListener("click", syncLegalCorpora);
}
if (btnLegalCorpora) {
  btnLegalCorpora.addEventListener("click", () => {
    loadLegalCorpora();
    if (modalLegalCorpus) modalLegalCorpus.classList.add("show");
  });
}

// --- Benchmarks Viewer & Runner ------------------------------------------
async function loadBenchmarkReport() {
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
        bmReportContent.textContent = "No benchmark report found. Click 'Run Benchmark Evaluator' in Settings to evaluate models.";
      }
    } else {
      bmReportContent.textContent = "Failed to fetch benchmark report.";
    }
  } catch (_) {
    bmReportContent.textContent = "Network error loading benchmark report.";
  }
}

if (btnBenchmarks) {
  btnBenchmarks.addEventListener("click", async () => {
    modalBenchmarks.classList.add("show");
    await loadBenchmarkReport();
  });
}

if (btnViewBenchmarks) {
  btnViewBenchmarks.addEventListener("click", async () => {
    modalSettings.classList.remove("show");
    modalBenchmarks.classList.add("show");
    await loadBenchmarkReport();
  });
}

if (btnRunBenchmarks) {
  btnRunBenchmarks.addEventListener("click", async () => {
    if (!benchmarkRunStatus) return;
    benchmarkRunStatus.textContent = "Running embedding model benchmarks… this may take 30–60s.";
    benchmarkRunStatus.className = "status-msg";
    btnRunBenchmarks.disabled = true;
    try {
      const res = await fetch("/benchmarks/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ top_k: 5, num_samples: 5 }),
      });
      if (res.ok) {
        const data = await res.json();
        benchmarkRunStatus.textContent = data.message || "Benchmark evaluation completed successfully!";
        benchmarkRunStatus.className = "status-msg success";
        if (modalBenchmarks.classList.contains("show")) {
          await loadBenchmarkReport();
        }
      } else {
        const err = await res.json().catch(() => ({}));
        benchmarkRunStatus.textContent = err.detail || "Benchmark run failed.";
        benchmarkRunStatus.className = "status-msg error";
      }
    } catch (err) {
      benchmarkRunStatus.textContent = "Network error while executing benchmarks.";
      benchmarkRunStatus.className = "status-msg error";
    } finally {
      btnRunBenchmarks.disabled = false;
    }
  });
}

bmClose.addEventListener("click", () => modalBenchmarks.classList.remove("show"));

// Keyboard shortcuts (Escape key closes modals, inspector & domain dropdown)
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeDomainDropdown();
    closeDocumentInspector();
    closeFullscreenPdfViewer();
    closeKnowledgeGraphModal();
    if (graphTooltipPopover) graphTooltipPopover.classList.add("hidden");
    if (modalBenchmarks) modalBenchmarks.classList.remove("show");
    if (modalSettings) modalSettings.classList.remove("show");
    if (modalProfile) modalProfile.classList.remove("show");
    if (modalKb) modalKb.classList.remove("show");
    if (modalLegalCorpus) modalLegalCorpus.classList.remove("show");
  }
});

// Overlay click to close
window.addEventListener("click", (e) => {
  if (e.target === modalPdfViewer) closeFullscreenPdfViewer();
  if (e.target === modalGraphViewer) closeKnowledgeGraphModal();
  if (graphTooltipPopover && !graphTooltipPopover.contains(e.target) && e.target !== graphInfoBtn) {
    graphTooltipPopover.classList.add("hidden");
  }
  if (e.target === modalProfile) modalProfile.classList.remove("show");
  if (e.target === modalKb) modalKb.classList.remove("show");
  if (e.target === modalBenchmarks) modalBenchmarks.classList.remove("show");
  if (e.target === modalSettings) modalSettings.classList.remove("show");
  if (e.target === modalLegalCorpus) modalLegalCorpus.classList.remove("show");

  // Close domain dropdown when clicking outside
  if (
    domainDropdownTrigger &&
    domainDropdownMenu &&
    !domainDropdownTrigger.contains(e.target) &&
    !domainDropdownMenu.contains(e.target)
  ) {
    closeDomainDropdown();
  }
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
  initAccentColors();
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
