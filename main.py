import os
import sys
import shutil
from ingest import build_vector_db
from rag_chain import get_retriever, get_rag_chain, handle_api_error

DB_PATH = "./chroma_db"

def main():
    print("=" * 50)
    print("📈 Modern SOTA Futures Trading RAG Assistant")
    print("=" * 50)

    # 1. Check if vector database exists
    if not os.path.exists(DB_PATH) or not os.listdir(DB_PATH):
        print("🔍 Vector database not found. Building database...")
        success = build_vector_db()
        if not success:
            print("❌ Ingestion failed. Please place PDF files in the './data' directory and try again.")
            sys.exit(1)
    else:
        print("✅ Vector database found.")

    # 2. Try loading retriever; auto-rebuild if embedding dimension mismatch occurs
    try:
        retriever = get_retriever()
        chain = get_rag_chain(retriever)
    except Exception as e:
        error_msg = str(e)
        if "dimension" in error_msg.lower() or "embedding" in error_msg.lower():
            print("\n🔄 Detected embedding model update/mismatch.")
            print("🧹 Re-building vector database automatically...")
            shutil.rmtree(DB_PATH, ignore_errors=True)
            
            success = build_vector_db()
            if not success:
                sys.exit(1)
                
            retriever = get_retriever()
            chain = get_rag_chain(retriever)
        else:
            print(f"❌ Initialization Error: {e}")
            handle_api_error(e)
            sys.exit(1)

    # 3. Interactive CLI Loop
    print("\n🤖 Assistant is ready! Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            query = input("❓ Enter your trading query: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                print("👋 Exiting. Goodbye!")
                break

            print("\n🤔 Thinking...")
            
            source_docs = retriever.invoke(query)
            
            print("\n💡 Answer:")
            for chunk in chain.stream(query):
                print(chunk, end="", flush=True)
            print("\n")

            if source_docs:
                print("📚 Sources referenced:")
                sources = set()
                for doc in source_docs:
                    source_name = os.path.basename(doc.metadata.get("source", "Unknown"))
                    page = doc.metadata.get("page", None)
                    page_str = f" (Page {page + 1})" if page is not None else ""
                    sources.add(f"  • {source_name}{page_str}")
                for source in sources:
                    print(source)
            
            print("\n" + "-" * 50)

        except KeyboardInterrupt:
            print("\n👋 Exiting. Goodbye!")
            break
        except Exception as e:
            handle_api_error(e)

if __name__ == "__main__":
    main()