"""User-facing text catalog for English and Hungarian.

Centralizes every string shown in the interactive CLI so the assistant can run
fully localized. Keys are shared across languages; :func:`t` resolves and
formats the message for the active language, falling back to English.
"""

from __future__ import annotations

from typing import Literal

Language = Literal["en", "hu"]

SUPPORTED_LANGUAGES: tuple[Language, ...] = ("en", "hu")

# Localized display names for the language picker.
LANGUAGE_NAMES: dict[Language, str] = {
    "en": "English",
    "hu": "Magyar (Hungarian)",
}

# Extra words that end a chat session, per language (in addition to exit/quit).
EXIT_COMMANDS: dict[Language, set[str]] = {
    "en": {"exit", "quit"},
    "hu": {"kilep", "kilép", "kilepes", "kilépés", "vege", "vége"},
}

MESSAGES: dict[str, dict[Language, str]] = {
    "banner_title": {
        "en": "📈 Modern SOTA Futures Trading RAG Assistant",
        "hu": "📈 Futures Kereskedési Tudástár",
    },
    # --- Wizard --------------------------------------------------------------
    "choose_provider": {
        "en": "Which model backend would you like to use?",
        "hu": "Melyik modell-hátteret szeretné használni?",
    },
    "provider_option_gemini": {
        "en": "Google Gemini (hosted, needs an API key)",
        "hu": "Google Gemini (felhő alapú, API-kulcs szükséges)",
    },
    "provider_option_local": {
        "en": "Local model via Ollama (offline, no API key)",
        "hu": "Helyi modell Ollamán keresztül (offline, nincs API-kulcs)",
    },
    "choose_interface": {
        "en": "How would you like to interact with the assistant?",
        "hu": "Hogyan szeretne az asszisztenssel kommunikálni?",
    },
    "interface_option_web": {
        "en": "Web UI (browser chat interface)",
        "hu": "Webes felület (böngészős csevegő)",
    },
    "interface_option_cli": {
        "en": "Command line (chat in this terminal)",
        "hu": "Parancssor (csevegés ebben a terminálban)",
    },
    "invalid_choice": {
        "en": "❌ Invalid choice. Please enter one of: {options}",
        "hu": "❌ Érvénytelen választás. Adja meg az alábbiak egyikét: {options}",
    },
    # --- API key -------------------------------------------------------------
    "api_key_required": {
        "en": "🔑 Gemini API key required.",
        "hu": "🔑 Gemini API-kulcs szükséges.",
    },
    "api_key_get_link": {
        "en": "👉 Get a free API key here: https://aistudio.google.com/app/apikey",
        "hu": "👉 Ingyenes API-kulcs itt igényelhető: https://aistudio.google.com/app/apikey",
    },
    "api_key_enter": {
        "en": "Enter your Gemini API key: ",
        "hu": "Adja meg a Gemini API-kulcsát: ",
    },
    "api_key_empty": {
        "en": "❌ API key cannot be empty. Please try again.",
        "hu": "❌ Az API-kulcs nem lehet üres. Próbálja újra.",
    },
    "api_key_saved": {
        "en": "✅ API key securely saved to system credential storage!",
        "hu": "✅ Az API-kulcs biztonságosan elmentve a rendszer kulcstárolójába!",
    },
    "api_key_none_stored": {
        "en": "No stored API key found.",
        "hu": "Nincs elmentett API-kulcs.",
    },
    "api_key_invalid": {
        "en": "The provided API key is invalid or rejected by Google.",
        "hu": "A megadott API-kulcs érvénytelen, vagy a Google elutasította.",
    },
    # --- Knowledge base ------------------------------------------------------
    "kb_preparing": {
        "en": "⏳ Preparing knowledge base (first run may download the embedding model)...",
        "hu": "⏳ Tudásbázis előkészítése (első futáskor letöltődhet a beágyazó modell)...",
    },
    "kb_ready": {
        "en": "✅ Knowledge base ready.",
        "hu": "✅ A tudásbázis készen áll.",
    },
    "kb_failed": {
        "en": "❌ Ingestion failed. Add data files to './data' and try again.",
        "hu": "❌ A betöltés sikertelen. Helyezzen adatfájlokat a './data' mappába, majd próbálja újra.",
    },
    # --- Local model ---------------------------------------------------------
    "local_using": {
        "en": "🤖 Using local Ollama model '{model}' at {url}",
        "hu": "🤖 Helyi Ollama modell használata: '{model}' ({url})",
    },
    "local_unreachable": {
        "en": "❌ Could not reach the local LLM.",
        "hu": "❌ A helyi nyelvi modell nem érhető el.",
    },
    "local_hint_intro": {
        "en": "   Make sure Ollama is running and the model is pulled:",
        "hu": "   Győződjön meg róla, hogy az Ollama fut és a modell le van töltve:",
    },
    "local_details": {
        "en": "   Details: {error}",
        "hu": "   Részletek: {error}",
    },
    "local_ready": {
        "en": "✅ Local model ready.",
        "hu": "✅ A helyi modell készen áll.",
    },
    # --- Chat loop -----------------------------------------------------------
    "chat_ready": {
        "en": "🤖 Assistant is ready! Type 'exit' or 'quit' to stop.",
        "hu": "🤖 Az asszisztens készen áll! A kilépéshez írja be: 'kilép' vagy 'exit'.",
    },
    "chat_prompt": {
        "en": "❓ Enter your trading query: ",
        "hu": "❓ Írja be a kereskedési kérdését: ",
    },
    "thinking": {
        "en": "🟡 Thinking...",
        "hu": "🟡 Gondolkodom...",
    },
    "answer_label": {
        "en": "💡 Answer:",
        "hu": "💡 Válasz:",
    },
    "sources_label": {
        "en": "📚 Sources referenced:",
        "hu": "📚 Felhasznált források:",
    },
    "exiting": {
        "en": "👋 Exiting. Goodbye!",
        "hu": "👋 Kilépés. Viszlát!",
    },
    # --- Errors --------------------------------------------------------------
    "runtime_auth_error": {
        "en": "❌ Runtime authentication/model error detected.",
        "hu": "❌ Futásidejű hitelesítési/modellhiba történt.",
    },
    "restart_hint": {
        "en": "Please restart the application to enter a valid API key.",
        "hu": "Indítsa újra az alkalmazást egy érvényes API-kulcs megadásához.",
    },
    "init_auth_error": {
        "en": "❌ Authentication/model error during initialization.",
        "hu": "❌ Hitelesítési/modellhiba az inicializálás során.",
    },
    "init_error": {
        "en": "❌ Initialization error: {error}",
        "hu": "❌ Inicializálási hiba: {error}",
    },
    # --- Web UI handoff ------------------------------------------------------
    "web_starting": {
        "en": "🌐 Starting web UI at http://{host}:{port} (press Ctrl+C to stop)...",
        "hu": "🌐 Webes felület indítása: http://{host}:{port} (leállítás: Ctrl+C)...",
    },
    # --- AWS S3 Storage --------------------------------------------------------
    "s3_enable_prompt": {
        "en": "☁️  Enable AWS S3 Cloud Storage for documents? (y/N)",
        "hu": "☁️  Engedélyezi az AWS S3 Cloud tárolást a dokumentumokhoz? (i/N)",
    },
    "s3_credentials_missing": {
        "en": "⚠️  AWS credentials not found in environment or settings.",
        "hu": "⚠️  AWS hitelesítő adatok nem találhatók a környezeti változókban vagy beállításokban.",
    },
    "s3_access_key_prompt": {
        "en": "Enter your AWS Access Key ID: ",
        "hu": "Adja meg az AWS Access Key ID-t: ",
    },
    "s3_secret_key_prompt": {
        "en": "Enter your AWS Secret Access Key: ",
        "hu": "Adja meg az AWS Secret Access Key-t: ",
    },
    "s3_region_prompt": {
        "en": "Enter AWS Region [default: eu-central-1]: ",
        "hu": "Adja meg az AWS régiót [alapértelmezett: eu-central-1]: ",
    },
    "s3_bucket_prompt": {
        "en": "Enter S3 Bucket Name [default: futures-rag-lab-docs]: ",
        "hu": "Adja meg az S3 bucket nevét [alapértelmezett: futures-rag-lab-docs]: ",
    },
    "s3_checking_access": {
        "en": "🔍 Checking S3 bucket access...",
        "hu": "🔍 S3 bucket hozzáférés ellenőrzése...",
    },
    "s3_access_success": {
        "en": "✅ S3 bucket access verified successfully.",
        "hu": "✅ S3 bucket hozzáférés sikeresen ellenőrizve.",
    },
    "s3_access_failed": {
        "en": "❌ Failed to access S3 bucket. Please check your credentials and bucket name.",
        "hu": "❌ S3 bucket elérése sikertelen. Ellenőrizze a hitelesítő adatokat és a bucket nevét.",
    },
    "s3_disabled": {
        "en": "📁 Using local storage for documents.",
        "hu": "📁 Helyi tárolás használata a dokumentumokhoz.",
    },
    "s3_enabled": {
        "en": "☁️  AWS S3 storage enabled for documents.",
        "hu": "☁️  AWS S3 tárolás engedélyezve a dokumentumokhoz.",
    },
}


def t(language: str, key: str, **kwargs: object) -> str:
    """Return the localized, formatted message for ``key``.

    Falls back to English when a language or key is missing so the app never
    crashes on an untranslated string.
    """
    entry = MESSAGES.get(key, {})
    template = entry.get(language) or entry.get("en") or key
    return template.format(**kwargs) if kwargs else template
