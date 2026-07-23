import sys
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser

from .config import get_valid_api_key, delete_stored_api_key

DB_PATH = "./chroma_db"
store = {}

def get_session_history(session_id: str):
    """Retrieve or create a chat history session."""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def get_retriever():
    """Initialize vector database retriever with Maximum Marginal Relevance (MMR)."""
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    
    # Increased k=6 and fetch_k=20 for higher context coverage
    return vector_db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 6, "fetch_k": 20, "lambda_mult": 0.7}
    )

def get_contextualized_query(query: str, session_id: str, llm) -> str:
    """Reformulate a user query into a standalone question using chat history."""
    history = get_session_history(session_id).messages
    if not history:
        return query

    contextualize_q_system_prompt = """Given a conversation history and the user's latest follow-up question, \
rephrase the follow-up question into a clear, fully standalone search query that explicitly names any core subject \
or entity referenced implicitly (e.g., replace pronouns like 'they', 'it', 'them' with the actual subject discussed). \
Do NOT answer the question, only output the reformulated standalone search query."""

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    
    query_rewriter = contextualize_q_prompt | llm | StrOutputParser()
    return query_rewriter.invoke({"chat_history": history, "question": query})

def get_rag_chain(retriever):
    """Construct and return the execution chain with conversation memory."""
    api_key = get_valid_api_key()

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=api_key,
    )

    qa_system_prompt = """You are an expert Futures Trading Assistant.
Analyze and synthesize the provided context to answer the user's question clearly and accurately.

Rules:
1. If the answer can be deduced or synthesized from the provided context, answer strictly based on the context.
2. If the context does NOT contain enough information to answer the question, you may provide a brief answer using your general financial knowledge, but you MUST start your response with the following explicit disclaimer:
   "ℹ️ *Note: This information was not found in your loaded documents. The answer below is based on general financial knowledge:*\n\n"

Context:
{context}"""

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def retrieve_with_rephrase(input_dict):
        history = input_dict.get("chat_history", [])
        question = input_dict["question"]
        
        if history:
            contextualize_q_system_prompt = """Given a conversation history and the user's latest follow-up question, \
rephrase the follow-up question into a clear, fully standalone search query that explicitly names any core subject \
or entity referenced implicitly (e.g., replace pronouns like 'they', 'it', 'them' with the actual subject discussed). \
Do NOT answer the question, only output the reformulated standalone search query."""

            contextualize_q_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", contextualize_q_system_prompt),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{question}"),
                ]
            )
            query_rewriter = contextualize_q_prompt | llm | StrOutputParser()
            standalone_question = query_rewriter.invoke(input_dict)
        else:
            standalone_question = question
            
        docs = retriever.invoke(standalone_question)
        return format_docs(docs)

    base_chain = (
        {
            "context": retrieve_with_rephrase,
            "question": lambda x: x["question"],
            "chat_history": lambda x: x["chat_history"],
        }
        | qa_prompt
        | llm
        | StrOutputParser()
    )

    chain_with_history = RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history",
    )

    return chain_with_history

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