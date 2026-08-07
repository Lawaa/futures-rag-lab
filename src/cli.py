"""Interactive command-line interface and unified startup wizard.

Running the app drops the user into a short guided setup:

1. Choose the interface language (English or Hungarian).
2. Choose the model backend (hosted Gemini or a local Ollama model).
3. Provide/validate the Gemini API key when needed (local models skip this).
4. Choose how to interact: browser web UI or this terminal.

The same wizard powers both entry points, so ``uv run main.py`` is the single
way to launch the assistant.
"""

from __future__ import annotations

import configparser
import logging
import os
import sys
from pathlib import Path

from . import i18n
from .bootstrap import build_service, ensure_vector_db
from .credentials import delete_stored_api_key, get_stored_api_key, store_api_key
from .llm import check_llm_available, is_authentication_error, validate_api_key
from .logging_config import set_log_level
from .rag_service import DEFAULT_SESSION_ID, RagService
from .s3_service import S3StorageService
from .settings import Settings, get_settings

_BASE_EXIT_COMMANDS = {"exit", "quit"}


def _persist_aws_credentials_to_file(
    access_key: str | None, secret_key: str | None, credentials_path: Path | None = None
) -> None:
    """Write AWS credentials to the standard ~/.aws/credentials file under [default].

    Saves the access key and secret key so boto3 can automatically resolve
    credentials via its default credential provider chain.
    """
    if not access_key or not secret_key:
        return

    target_path = credentials_path or (Path.home() / ".aws" / "credentials")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    config = configparser.ConfigParser()
    if target_path.exists():
        config.read(target_path, encoding="utf-8")

    if "default" not in config.sections():
        config.add_section("default")

    config.set("default", "aws_access_key_id", access_key)
    config.set("default", "aws_secret_access_key", secret_key)

    with target_path.open("w", encoding="utf-8") as f:
        config.write(f)


def _persist_s3_credentials_to_env(settings: Settings, env_path: Path | None = None) -> None:
    """Write non-sensitive S3 configuration to the local .env file for persistence.

    Updates or creates the .env file with non-sensitive AWS settings (excluding
    RAG_AWS_SECRET_ACCESS_KEY) so users don't need to re-enter configuration on
    subsequent runs.
    """
    target_env = env_path or Path(".env")
    env_lines = []

    # Read existing .env file if it exists
    if target_env.exists():
        env_lines = target_env.read_text(encoding="utf-8").splitlines()

    # Remove any existing S3-related lines to avoid duplicates (including legacy secret keys)
    s3_keys = {
        "RAG_USE_S3_STORAGE",
        "RAG_AWS_ACCESS_KEY_ID",
        "RAG_AWS_SECRET_ACCESS_KEY",
        "RAG_AWS_REGION",
        "RAG_AWS_S3_BUCKET_NAME",
    }
    filtered_lines = [line for line in env_lines if not any(line.startswith(key + "=") for key in s3_keys)]

    # Append non-sensitive S3 configuration (RAG_AWS_SECRET_ACCESS_KEY is deliberately excluded)
    filtered_lines.append(f"RAG_USE_S3_STORAGE={str(settings.use_s3_storage).lower()}")
    if settings.aws_access_key_id:
        filtered_lines.append(f"RAG_AWS_ACCESS_KEY_ID={settings.aws_access_key_id}")
    if settings.aws_region:
        filtered_lines.append(f"RAG_AWS_REGION={settings.aws_region}")
    if settings.aws_s3_bucket_name:
        filtered_lines.append(f"RAG_AWS_S3_BUCKET_NAME={settings.aws_s3_bucket_name}")

    # Write back to .env
    target_env.write_text("\n".join(filtered_lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# Interactive selection helpers
# --------------------------------------------------------------------------- #
def _select_language() -> str:
    """Ask the user for a language before any localized text is shown."""
    languages = list(i18n.SUPPORTED_LANGUAGES)
    print("\n🌐 Choose your language / Válasszon nyelvet:")
    for index, code in enumerate(languages, start=1):
        print(f"  {index}. {i18n.LANGUAGE_NAMES[code]}")

    valid = {str(i) for i in range(1, len(languages) + 1)}
    while True:
        choice = input("> ").strip()
        if choice in valid:
            return languages[int(choice) - 1]
        print("❌ Invalid choice / Érvénytelen választás.")


def _choose(language: str, prompt_key: str, options: list[tuple[str, str]]) -> str:
    """Prompt the user to pick a numbered option; return the selected key."""
    print("\n" + i18n.t(language, prompt_key))
    for index, (_, label_key) in enumerate(options, start=1):
        print(f"  {index}. {i18n.t(language, label_key)}")

    valid = [str(i) for i in range(1, len(options) + 1)]
    while True:
        choice = input("> ").strip()
        if choice in valid:
            return options[int(choice) - 1][0]
        print(i18n.t(language, "invalid_choice", options=", ".join(valid)))


# --------------------------------------------------------------------------- #
# Credential handling
# --------------------------------------------------------------------------- #
def _prompt_for_api_key(language: str, reason: str | None = None) -> str:
    print("\n" + "=" * 60)
    if reason:
        print(f"⚠️  {reason}")
    print(i18n.t(language, "api_key_required"))
    print(i18n.t(language, "api_key_get_link"))
    print("=" * 60 + "\n")

    while True:
        api_key = input(i18n.t(language, "api_key_enter")).strip()
        if api_key:
            store_api_key(api_key)
            print(i18n.t(language, "api_key_saved") + "\n")
            return api_key
        print(i18n.t(language, "api_key_empty"))


def _resolve_api_key(settings: Settings) -> str:
    """Return a validated API key, prompting the user as needed."""
    language = settings.language
    api_key = get_stored_api_key() or _prompt_for_api_key(
        language, i18n.t(language, "api_key_none_stored")
    )
    while not validate_api_key(api_key, settings):
        delete_stored_api_key()
        api_key = _prompt_for_api_key(language, i18n.t(language, "api_key_invalid"))
    return api_key


def _resolve_llm_credentials(settings: Settings) -> str | None:
    """Prepare the configured LLM backend, returning an API key if applicable."""
    language = settings.language
    if settings.uses_gemini:
        return _resolve_api_key(settings)

    # Local Ollama backend: no key needed, but verify the server is reachable.
    print(
        "\n"
        + i18n.t(
            language,
            "local_using",
            model=settings.ollama_model,
            url=settings.ollama_base_url,
        )
    )
    ok, error = check_llm_available(settings)
    if not ok:
        print(i18n.t(language, "local_unreachable"))
        print(i18n.t(language, "local_hint_intro"))
        print("     • ollama serve")
        print(f"     • ollama pull {settings.ollama_model}")
        print(i18n.t(language, "local_details", error=error))
        sys.exit(1)
    print(i18n.t(language, "local_ready"))
    return None


def _resolve_s3_credentials(settings: Settings) -> Settings:
    """Resolve AWS S3 credentials and configuration through interactive prompts.

    Returns updated settings with S3 configuration if enabled, otherwise
    returns settings with use_s3_storage=False.
    """
    language = settings.language

    # Ask user if they want to enable S3 storage
    print("\n" + i18n.t(language, "s3_enable_prompt"))
    choice = input("> ").strip().lower()

    # Accept "y", "yes", "i", "igen" (Hungarian for yes)
    if choice not in {"y", "yes", "i", "igen"}:
        print("\n" + i18n.t(language, "s3_disabled"))
        return settings.model_copy(update={"use_s3_storage": False})

    # User wants S3 - check if credentials are already set
    access_key = settings.aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = settings.aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY")

    if not access_key or not secret_key:
        aws_cred_file = Path.home() / ".aws" / "credentials"
        if aws_cred_file.exists():
            cp = configparser.ConfigParser()
            cp.read(aws_cred_file, encoding="utf-8")
            if "default" in cp:
                if not access_key:
                    access_key = cp["default"].get("aws_access_key_id")
                if not secret_key:
                    secret_key = cp["default"].get("aws_secret_access_key")

    if not access_key or not secret_key:
        print("\n" + i18n.t(language, "s3_credentials_missing"))

        # Prompt for missing credentials
        while not access_key:
            access_key = input(i18n.t(language, "s3_access_key_prompt")).strip()
            if not access_key:
                print(i18n.t(language, "api_key_empty"))

        while not secret_key:
            secret_key = input(i18n.t(language, "s3_secret_key_prompt")).strip()
            if not secret_key:
                print(i18n.t(language, "api_key_empty"))

    # Prompt for region (with default)
    region_input = input(i18n.t(language, "s3_region_prompt")).strip()
    region = region_input if region_input else settings.aws_region

    # Prompt for bucket name (with default)
    bucket_input = input(i18n.t(language, "s3_bucket_prompt")).strip()
    bucket = bucket_input if bucket_input else settings.aws_s3_bucket_name

    # Update settings with provided values
    updated_settings = settings.model_copy(
        update={
            "use_s3_storage": True,
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "aws_region": region,
            "aws_s3_bucket_name": bucket,
        }
    )

    # Validate S3 bucket access
    print("\n" + i18n.t(language, "s3_checking_access"))
    try:
        s3_service = S3StorageService(updated_settings)
        if s3_service.check_bucket_access():
            print(i18n.t(language, "s3_access_success"))
            print("\n" + i18n.t(language, "s3_enabled"))
            # Persist secret credentials to ~/.aws/credentials and non-sensitive settings to .env
            _persist_aws_credentials_to_file(access_key, secret_key)
            _persist_s3_credentials_to_env(updated_settings)
            return updated_settings
        else:
            print(i18n.t(language, "s3_access_failed"))
            print("\n" + i18n.t(language, "s3_disabled"))
            return settings.model_copy(update={"use_s3_storage": False})
    except Exception as error:
        print(i18n.t(language, "s3_access_failed"))
        print(f"   Error: {error}")
        print("\n" + i18n.t(language, "s3_disabled"))
        return settings.model_copy(update={"use_s3_storage": False})


# --------------------------------------------------------------------------- #
# CLI chat loop
# --------------------------------------------------------------------------- #
def _print_sources(language: str, retrieval_sources) -> None:
    if not retrieval_sources:
        return
    print(i18n.t(language, "sources_label"))
    for source in retrieval_sources:
        print(f"  • {source}")


def _chat_loop(
    service: RagService, language: str, session_id: str = DEFAULT_SESSION_ID
) -> None:
    exit_commands = _BASE_EXIT_COMMANDS | i18n.EXIT_COMMANDS.get(language, set())
    print("\n" + i18n.t(language, "chat_ready") + "\n")
    while True:
        try:
            query = input(i18n.t(language, "chat_prompt")).strip()
            if not query:
                continue
            if query.lower() in exit_commands:
                print(i18n.t(language, "exiting"))
                return

            print("\n" + i18n.t(language, "thinking"))
            retrieval = service.retrieve(query, session_id)

            print("\n" + i18n.t(language, "answer_label"))
            for token in service.stream_answer(query, retrieval, session_id):
                print(token, end="", flush=True)
            print("\n")

            _print_sources(language, retrieval.sources)
            print("\n" + "-" * 50)

        except KeyboardInterrupt:
            print("\n" + i18n.t(language, "exiting"))
            return
        except Exception as error:
            if is_authentication_error(error):
                print("\n" + i18n.t(language, "runtime_auth_error"))
                delete_stored_api_key()
                print(i18n.t(language, "restart_hint"))
                sys.exit(1)
            raise


# --------------------------------------------------------------------------- #
# Launch modes
# --------------------------------------------------------------------------- #
def _launch_cli(settings: Settings, api_key: str | None) -> None:
    """Build the service and start the terminal chat loop."""
    language = settings.language
    try:
        service = build_service(settings, api_key)
    except Exception as error:
        if is_authentication_error(error):
            print("\n" + i18n.t(language, "init_auth_error"))
            if settings.uses_gemini:
                delete_stored_api_key()
            print(i18n.t(language, "restart_hint"))
            sys.exit(1)
        print(i18n.t(language, "init_error", error=error))
        sys.exit(1)

    _chat_loop(service, language)


def _launch_web_ui(settings: Settings) -> None:
    """Hand off to the FastAPI server, propagating the wizard's choices.

    The API reads configuration through :func:`get_settings`, so the choices are
    published as ``RAG_*`` environment variables and the settings cache is
    cleared before uvicorn imports the app.
    """
    import uvicorn

    os.environ["RAG_LANGUAGE"] = settings.language
    os.environ["RAG_LLM_PROVIDER"] = settings.llm_provider
    os.environ["RAG_OLLAMA_MODEL"] = settings.ollama_model
    os.environ["RAG_OLLAMA_BASE_URL"] = settings.ollama_base_url

    # Export non-sensitive AWS settings to environment (secret key is loaded via AWS default provider chain)
    os.environ["RAG_USE_S3_STORAGE"] = str(settings.use_s3_storage)
    os.environ["RAG_AWS_ACCESS_KEY_ID"] = settings.aws_access_key_id or ""
    os.environ["RAG_AWS_REGION"] = settings.aws_region or ""
    os.environ["RAG_AWS_S3_BUCKET_NAME"] = settings.aws_s3_bucket_name or ""

    # Clear settings cache immediately after setting environment variables
    get_settings.cache_clear()

    print(
        "\n"
        + i18n.t(
            settings.language,
            "web_starting",
            host=settings.api_host,
            port=settings.api_port,
        )
    )
    uvicorn.run(
        "src.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def run() -> None:
    """Unified interactive entry point for the assistant."""
    # Keep the conversation clean: suppress INFO logs from the pipeline so the
    # assistant's answers stand out. Warnings and errors still surface.
    set_log_level(logging.WARNING)

    # 1. Language.
    language = _select_language()

    print("\n" + "=" * 50)
    print(i18n.t(language, "banner_title"))
    print("=" * 50)

    # 2. Model backend.
    provider = _choose(
        language,
        "choose_provider",
        [
            ("gemini", "provider_option_gemini"),
            ("ollama", "provider_option_local"),
        ],
    )

    settings = get_settings().model_copy(
        update={"language": language, "llm_provider": provider}
    )

    # 3. Credentials (API key for Gemini, reachability check for local).
    api_key = _resolve_llm_credentials(settings)

    # 4. AWS S3 Storage (optional cloud storage for documents).
    settings = _resolve_s3_credentials(settings)

    # 5. Interface.
    interface = _choose(
        language,
        "choose_interface",
        [
            ("web", "interface_option_web"),
            ("cli", "interface_option_cli"),
        ],
    )

    # Prepare the knowledge base (localized progress messages).
    print("\n" + i18n.t(language, "kb_preparing"))
    if not ensure_vector_db(settings):
        print(i18n.t(language, "kb_failed"))
        sys.exit(1)
    print(i18n.t(language, "kb_ready"))

    if interface == "web":
        _launch_web_ui(settings)
    else:
        _launch_cli(settings, api_key)


if __name__ == "__main__":
    run()