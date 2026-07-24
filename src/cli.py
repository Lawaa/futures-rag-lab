"""Interactive command-line interface for the RAG assistant."""

from __future__ import annotations

import logging
import sys

from .bootstrap import build_service, ensure_vector_db
from .credentials import delete_stored_api_key, get_stored_api_key, store_api_key
from .llm import check_llm_available, is_authentication_error, validate_api_key
from .logging_config import set_log_level
from .rag_service import DEFAULT_SESSION_ID, RagService
from .settings import Settings, get_settings

_EXIT_COMMANDS = {"exit", "quit"}


def _prompt_for_api_key(reason: str | None = None) -> str:
    print("\n" + "=" * 60)
    if reason:
        print(f"⚠️  {reason}")
    print("🔑 Gemini API key required.")
    print("👉 Get a free API key here: https://aistudio.google.com/app/apikey")
    print("=" * 60 + "\n")

    while True:
        api_key = input("Enter your Gemini API key: ").strip()
        if api_key:
            store_api_key(api_key)
            print("✅ API key securely saved to system credential storage!\n")
            return api_key
        print("❌ API key cannot be empty. Please try again.")


def _resolve_api_key(settings: Settings) -> str:
    """Return a validated API key, prompting the user as needed."""
    api_key = get_stored_api_key() or _prompt_for_api_key("No stored API key found.")
    while not validate_api_key(api_key, settings):
        delete_stored_api_key()
        api_key = _prompt_for_api_key("The provided API key is invalid or rejected by Google.")
    return api_key


def _resolve_llm_credentials(settings: Settings) -> str | None:
    """Prepare the configured LLM backend, returning an API key if applicable."""
    if settings.uses_gemini:
        return _resolve_api_key(settings)

    # Local Ollama backend: no key needed, but verify the server is reachable.
    print(
        f"\n🤖 Using local Ollama model '{settings.ollama_model}' "
        f"at {settings.ollama_base_url}"
    )
    ok, error = check_llm_available(settings)
    if not ok:
        print("❌ Could not reach the local LLM.")
        print("   Make sure Ollama is running and the model is pulled:")
        print("     • ollama serve")
        print(f"     • ollama pull {settings.ollama_model}")
        print(f"   Details: {error}")
        sys.exit(1)
    print("✅ Local model ready.")
    return None


def _print_sources(retrieval_sources) -> None:
    if not retrieval_sources:
        return
    print("📚 Sources referenced:")
    for source in retrieval_sources:
        print(f"  • {source}")


def _chat_loop(service: RagService, session_id: str = DEFAULT_SESSION_ID) -> None:
    print("\n🤖 Assistant is ready! Type 'exit' or 'quit' to stop.\n")
    while True:
        try:
            query = input("❓ Enter your trading query: ").strip()
            if not query:
                continue
            if query.lower() in _EXIT_COMMANDS:
                print("👋 Exiting. Goodbye!")
                return

            print("\n🟡 Thinking...")
            retrieval = service.retrieve(query, session_id)

            print("\n💡 Answer:")
            for token in service.stream_answer(query, retrieval, session_id):
                print(token, end="", flush=True)
            print("\n")

            _print_sources(retrieval.sources)
            print("\n" + "-" * 50)

        except KeyboardInterrupt:
            print("\n👋 Exiting. Goodbye!")
            return
        except Exception as error:
            if is_authentication_error(error):
                print("\n❌ Runtime authentication/model error detected.")
                delete_stored_api_key()
                print("Please restart the application to enter a valid API key.")
                sys.exit(1)
            raise


def run() -> None:
    """Entry point for the interactive CLI."""
    # Keep the conversation clean: suppress INFO logs from the pipeline so the
    # assistant's answers stand out. Warnings and errors still surface.
    set_log_level(logging.WARNING)
    settings = get_settings()

    print("=" * 50)
    print("📈 Modern SOTA Futures Trading RAG Assistant")
    print("=" * 50)

    print("\n⏳ Preparing knowledge base (first run may download the embedding model)...")
    if not ensure_vector_db(settings):
        print("❌ Ingestion failed. Add data files to './data' and try again.")
        sys.exit(1)
    print("✅ Knowledge base ready.")

    api_key = _resolve_llm_credentials(settings)

    try:
        service = build_service(settings, api_key)
    except Exception as error:
        if is_authentication_error(error):
            print("\n❌ Authentication/model error during initialization.")
            if settings.uses_gemini:
                delete_stored_api_key()
            print("Please restart the application to enter a valid API key.")
            sys.exit(1)
        print(f"❌ Initialization error: {error}")
        sys.exit(1)

    _chat_loop(service)


if __name__ == "__main__":
    run()