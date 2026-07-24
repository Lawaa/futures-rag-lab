"""Prompt templates used by the RAG pipeline."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

CONTEXTUALIZE_SYSTEM_PROMPT = (
    "Given a conversation history and the user's latest follow-up question, "
    "rephrase the follow-up question into a clear, fully standalone search query "
    "that explicitly names any core subject or entity referenced implicitly "
    "(e.g., replace pronouns like 'they', 'it', 'them' with the actual subject "
    "discussed). Do NOT answer the question, only output the reformulated "
    "standalone search query."
)

QA_SYSTEM_PROMPT = (
    "You are an expert Futures Trading Assistant.\n"
    "Analyze and synthesize the provided context to answer the user's question "
    "clearly and accurately.\n\n"
    "Rules:\n"
    "1. If the answer can be deduced or synthesized from the provided context, "
    "answer strictly based on the context.\n"
    "2. If the context does NOT contain enough information to answer the "
    "question, you may provide a brief answer using your general financial "
    "knowledge, but you MUST start your response with the following explicit "
    "disclaimer:\n"
    " 'ℹ️ *Note: This information was not found in your loaded documents. "
    "The answer below is based on general financial knowledge:*\n\n'\n"
    "Context:\n{context}"
)

CONTEXTUALIZE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", CONTEXTUALIZE_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", QA_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)