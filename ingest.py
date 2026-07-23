import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DATA_PATH = "./data"
DB_PATH = "./chroma_db"

def build_vector_db() -> bool:
    print("📁 Loading PDF documents from data directory...")
    if not os.path.exists(DATA_PATH) or not os.listdir(DATA_PATH):
        print(f"⚠️ Warning: '{DATA_PATH}' directory is empty or missing. Please add PDF files.")
        return False

    loader = PyPDFDirectoryLoader(DATA_PATH)
    docs = loader.load()
    print(f"📄 Loaded {len(docs)} document pages.")

    print("✂️ Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100
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
    print(f"✅ Successfully indexed {len(chunks)} chunks into '{DB_PATH}'!\n")
    return True

if __name__ == "__main__":
    build_vector_db()