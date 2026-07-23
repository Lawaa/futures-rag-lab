import os
import sys
from ingest import build_vector_db
from rag_chain import get_rag_chain

DB_PATH = "./chroma_db"

def main():
    print("=" * 50)
    print("📈 Futures Trading RAG Assistant")
    print("=" * 50)

    # 1. Check if vector database exists; if not, run ingestion pipeline
    if not os.path.exists(DB_PATH) or not os.listdir(DB_PATH):
        print("🔍 Vector database not found. Starting initial ingestion process...")
        success = build_vector_db()
        if not success:
            print("❌ Ingestion failed. Please place PDF files in the './data' directory and try again.")
            sys.exit(1)
    else:
        print("✅ Vector database found. Loading model pipeline...\n")

    # 2. Initialize RAG Chain
    try:
        chain = get_rag_chain()
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        sys.exit(1)

    # 3. Interactive CLI Loop
    print("🤖 Assistant is ready! Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            query = input("❓ Enter your trading query: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                print("👋 Exiting. Goodbye!")
                break

            print("\n🤔 Thinking...")
            response = chain.invoke(query)
            print(f"\n💡 Answer:\n{response}\n")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n👋 Exiting. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error processing query: {e}\n")

if __name__ == "__main__":
    main()