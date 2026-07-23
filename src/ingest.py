import os
import glob
import json
import hashlib
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DATA_PATH = "./data"
DB_PATH = "./chroma_db"
MANIFEST_PATH = "./chroma_db/.data_manifest.json"

def get_data_fingerprint() -> str:
    """Generate a combined hash of all files in DATA_PATH based on their content and modification time."""
    if not os.path.exists(DATA_PATH):
        return ""
    
    files = sorted(glob.glob(os.path.join(DATA_PATH, "*")))
    fingerprint_data = []

    for filepath in files:
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            # Combine filename, size, and last modified timestamp
            fingerprint_data.append(f"{os.path.basename(filepath)}:{stat.st_size}:{stat.st_mtime}")

    combined_str = "|".join(fingerprint_data)
    return hashlib.md5(combined_str.encode("utf-8")).hexdigest()

def is_data_changed() -> bool:
    """Check if the data directory has changed compared to the stored manifest."""
    current_fingerprint = get_data_fingerprint()
    if not os.path.exists(MANIFEST_PATH):
        return True
    
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            stored_data = json.load(f)
            return stored_data.get("fingerprint") != current_fingerprint
    except Exception:
        return True

def save_manifest() -> None:
    """Save the current data fingerprint to disk."""
    current_fingerprint = get_data_fingerprint()
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({"fingerprint": current_fingerprint}, f, indent=2)

def build_vector_db() -> bool:
    print("📁 Loading documents (PDF, TXT, MD) from data directory...")
    if not os.path.exists(DATA_PATH) or not os.listdir(DATA_PATH):
        print(f"⚠️ Warning: '{DATA_PATH}' directory is empty or missing. Please add data files.")
        return False

    pdf_loader = DirectoryLoader(DATA_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader)
    txt_loader = DirectoryLoader(DATA_PATH, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
    md_loader = DirectoryLoader(DATA_PATH, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})

    docs = []
    docs.extend(pdf_loader.load())
    docs.extend(txt_loader.load())
    docs.extend(md_loader.load())

    print(f"📄 Loaded {len(docs)} total document source pages/files.")

    print("✂️ Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(docs)
    print(f"🧩 Created {len(chunks)} text chunks.")

    print("🧠 Generating embeddings with BAAI/bge-small-en-v1.5 and saving to ChromaDB...")
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    
    save_manifest()
    print(f"✅ Successfully indexed {len(chunks)} chunks into '{DB_PATH}'!\n")
    return True

if __name__ == "__main__":
    build_vector_db()