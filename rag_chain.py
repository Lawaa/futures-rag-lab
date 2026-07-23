import sys
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from config import get_valid_api_key, delete_stored_api_key

DB_PATH = "./chroma_db"

def get_rag_chain():
    # Dynamically retrieve and validate the API key (prompts user if missing/invalid)
    api_key = get_valid_api_key()

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=api_key,
        #temperature=0.2
    )

    template = """You are an expert Futures Trading Assistant.
Answer the user's question based strictly on the provided context. If the answer cannot be deduced from the context, state clearly: "I cannot find this information in the provided knowledge base."

Context:
{context}

Question: {question}

Answer:"""

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain

def invoke_chain_safely(chain, question: str) -> str:
    """Helper function to execute the chain and handle runtime API authentication errors."""
    try:
        return chain.invoke(question)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "UNAUTHENTICATED" in error_msg or "API_KEY_INVALID" in error_msg or "NOT_FOUND" in error_msg:
            print("\n❌ Invalid or expired API key detected during runtime.")
            delete_stored_api_key()
            print("Please restart the application to enter a valid API key.")
            sys.exit(1)
        else:
            raise e