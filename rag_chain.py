import sys
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from config import get_valid_api_key, delete_stored_api_key

DB_PATH = "./chroma_db"

def get_retriever():
    """Initialize vector database retriever with Maximum Marginal Relevance (MMR)."""
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    
    # Using MMR to fetch diverse relevant context
    return vector_db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "fetch_k": 10, "lambda_mult": 0.7}
    )

def get_rag_chain(retriever):
    """Construct and return the execution chain."""
    api_key = get_valid_api_key()

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

def handle_api_error(e: Exception) -> None:
    """Check for auth/not-found runtime errors and clear invalid keys."""
    error_msg = str(e)
    if any(code in error_msg for code in ["401", "UNAUTHENTICATED", "API_KEY_INVALID", "NOT_FOUND"]):
        print("\n❌ Runtime Authentication/Model Error detected.")
        delete_stored_api_key()
        print("Please restart the application to enter a valid API key.")
        sys.exit(1)
    else:
        raise e