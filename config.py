import os
import keyring
import google.generativeai as genai

SERVICE_NAME = "futures-rag-lab"
KEY_NAME = "GEMINI_API_KEY"

def get_stored_api_key() -> str | None:
    """Retrieve API key from environment variable or system keyring."""
    if os.getenv("GEMINI_API_KEY"):
        return os.getenv("GEMINI_API_KEY")
    return keyring.get_password(SERVICE_NAME, KEY_NAME)

def delete_stored_api_key() -> None:
    """Delete stored API key from the system keyring."""
    try:
        keyring.delete_password(SERVICE_NAME, KEY_NAME)
        print("🗑️ Stored API key removed from system credential storage.")
    except keyring.errors.PasswordDeleteError:
        pass

def prompt_and_save_api_key(reason: str | None = None) -> str:
    """Prompt the user for their Gemini API key and store it securely."""
    print("\n" + "=" * 60)
    if reason:
        print(f"⚠️  {reason}")
    print("🔑 Gemini API key required.")
    print("👉 Get a free API key here: https://aistudio.google.com/app/apikey")
    print("=" * 60 + "\n")
    
    while True:
        api_key = input("Enter your Gemini API key: ").strip()
        if api_key:
            keyring.set_password(SERVICE_NAME, KEY_NAME, api_key)
            print("✅ API key securely saved to system credential storage!\n")
            return api_key
        print("❌ API key cannot be empty. Please try again.")

def validate_api_key(api_key: str) -> bool:
    """Test API key validity using a lightweight model listing call."""
    try:
        genai.configure(api_key=api_key)
        list(genai.list_models())
        return True
    except Exception:
        return False

def get_valid_api_key() -> str:
    """Retrieve a validated API key, prompting the user if missing or invalid."""
    api_key = get_stored_api_key()
    
    if not api_key:
        api_key = prompt_and_save_api_key("No stored API key found.")
    
    while not validate_api_key(api_key):
        delete_stored_api_key()
        api_key = prompt_and_save_api_key("The provided API key is invalid or rejected by Google.")
        
    return api_key