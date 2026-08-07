"""Prompt templates used by the RAG pipeline (English and Hungarian)."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Human-readable names used when instructing the model to translate queries.
LANGUAGE_NAMES: dict[str, str] = {"en": "English", "hu": "Hungarian"}


def language_name(language: str) -> str:
    """Map a language code to a human-readable name (falls back to the code)."""
    return LANGUAGE_NAMES.get(language, language)

# --- Query rephrasing -------------------------------------------------------
CONTEXTUALIZE_SYSTEM_PROMPTS: dict[str, str] = {
    "en": (
        "Given a conversation history and the user's latest follow-up question, "
        "rephrase the follow-up question into a clear, fully standalone search query "
        "that explicitly names any core subject or entity referenced implicitly "
        "(e.g., replace pronouns like 'they', 'it', 'them' with the actual subject "
        "discussed). Do NOT answer the question, only output the reformulated "
        "standalone search query."
    ),
    "hu": (
        "A beszélgetés előzményei és a felhasználó legutóbbi követő kérdése alapján "
        "fogalmazza át a követő kérdést egyetlen, önmagában is érthető keresési "
        "kérdéssé, amely kifejezetten megnevezi a hallgatólagosan hivatkozott "
        "alanyt vagy entitást (pl. a névmásokat, mint 'ők', 'az', 'azt', cserélje "
        "ki a ténylegesen tárgyalt alanyra). NE válaszoljon a kérdésre, csak az "
        "átfogalmazott, önálló keresési kérdést adja vissza. A keresési kérdést "
        "ugyanazon a nyelven adja vissza, mint a felhasználó kérdése."
    ),
}

# --- Answer generation ------------------------------------------------------
# The default assistant persona per language. A profile's ``system_prompt`` (see
# :mod:`src.profiles`) overrides this while the shared grounding rules below are
# always appended, so groundedness handling works for every profile.
DEFAULT_PERSONAS: dict[str, str] = {
    "en": "You are an expert Futures Trading Assistant.",
    "hu": "Ön szakértő határidős (futures) kereskedési asszisztens.",
}

# Disclaimer the assistant must prepend when it answers from outside knowledge.
# A single source of truth so generation, detection and the groundedness
# self-check all agree on the wording.
OUTSIDE_KNOWLEDGE_NOTE: dict[str, str] = {
    "en": (
        "ℹ️ *Note: This information was not found in your loaded documents. "
        "The answer below is based on general knowledge:*"
    ),
    "hu": (
        "ℹ️ *Megjegyzés: Ez az információ nem található meg a betöltött "
        "dokumentumokban. Az alábbi válasz általános tudáson alapul:*"
    ),
}

# Answer-generation templates. ``__PERSONA__`` and ``__NOTE__`` are substituted
# in code (via ``str.replace``) so the ``{context}`` placeholder is preserved
# for the ChatPromptTemplate.
_QA_TEMPLATES: dict[str, str] = {
    "en": (
        "__PERSONA__\n"
        "Analyze and synthesize the provided context to answer the user's question "
        "clearly and accurately.\n\n"
        "Rules:\n"
        "1. If the answer can be deduced or synthesized from the provided context, "
        "answer strictly based on the context.\n"
        "2. Do NOT reference incomplete, fragment, or isolated examples/numbers "
        "(e.g., specific dollar amounts or scenarios) unless the context provides "
        "their full explanation and background. State concepts generally instead.\n"
        "3. If the context does NOT contain enough information to answer the "
        "question, you may provide a brief answer using your general knowledge, "
        "but you MUST start your response with the following explicit disclaimer:\n"
        " '__NOTE__\n\n'\n"
        "4. Always respond in English.\n"
        "Context:\n{context}"
    ),
    "hu": (
        "__PERSONA__\n"
        "Elemezze és szintetizálja a megadott kontextust, hogy világosan és "
        "pontosan válaszoljon a felhasználó kérdésére.\n\n"
        "Szabályok:\n"
        "1. Ha a válasz levezethető vagy összeállítható a megadott kontextusból, "
        "szigorúan a kontextus alapján válaszoljon.\n"
        "2. NE hivatkozzon hiányos, töredékes vagy izolált példákra és számszerű "
        "értékekre (pl. konkrét dollárösszegekre vagy esettanulmányokra), hacsak "
        "a kontextus nem fejti ki azok teljes hátterét és magyarázatát. Ilyen "
        "esetekben fogalmazzon általánosságban.\n"
        "3. Ha a kontextus NEM tartalmaz elegendő információt a kérdés "
        "megválaszolásához, adhat rövid választ az általános tudása alapján, de a "
        "válaszát KÖTELEZŐEN a következő kifejezett figyelmeztetéssel kell "
        "kezdenie:\n '__NOTE__\n\n'\n"
        "4. Mindig magyarul válaszoljon.\n"
        "Kontextus:\n{context}"
    ),
}


def outside_knowledge_note(language: str = "en") -> str:
    """Return the outside-knowledge disclaimer for a language (English fallback)."""
    return OUTSIDE_KNOWLEDGE_NOTE.get(language, OUTSIDE_KNOWLEDGE_NOTE["en"])


def is_outside_knowledge(text: str) -> bool:
    """Whether an answer is flagged as using knowledge outside the documents."""
    return text.lstrip().startswith("ℹ️")


_AFFIRMATIVE_TOKENS = ("yes", "true", "relevant", "igen")


def is_affirmative(text: str) -> bool:
    """Whether a yes/no grader verdict is affirmative (language-tolerant)."""
    lowered = text.lower()
    return any(token in lowered for token in _AFFIRMATIVE_TOKENS)


def _qa_system_prompt(language: str, persona: str) -> str:
    template = _QA_TEMPLATES.get(language) or _QA_TEMPLATES["en"]
    return template.replace("__PERSONA__", persona).replace(
        "__NOTE__", outside_knowledge_note(language)
    )



def get_contextualize_prompt(language: str = "en") -> ChatPromptTemplate:
    """Build the query-rephrasing prompt for the given language."""
    system = CONTEXTUALIZE_SYSTEM_PROMPTS.get(language) or CONTEXTUALIZE_SYSTEM_PROMPTS["en"]
    return ChatPromptTemplate.from_messages(
        [
            ("system", system),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )


def get_qa_prompt(
    language: str = "en", system_prompt: str | None = None
) -> ChatPromptTemplate:
    """Build the answer-generation prompt for a language and optional persona.

    ``system_prompt`` (from the active :class:`~src.profiles.Profile`) replaces
    the default persona; the shared grounding rules and ``{context}`` slot are
    always appended so groundedness handling is identical for every profile.
    """
    persona = system_prompt or DEFAULT_PERSONAS.get(language) or DEFAULT_PERSONAS["en"]
    return ChatPromptTemplate.from_messages(
        [
            ("system", _qa_system_prompt(language, persona)),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )


# --- Cross-lingual search query preparation ---------------------------------
# One combined step that resolves follow-up references AND translates the query
# into the corpus language, so a single LLM call handles both concerns.
SEARCH_QUERY_SYSTEM_PROMPT = (
    "You are a query preparation assistant for a document search engine.\n"
    "Given the conversation history and the user's latest question, produce a "
    "single standalone search query that:\n"
    "1. Resolves pronouns and implicit references using the conversation history "
    "(e.g. replace 'it', 'they', 'that' with the actual subject).\n"
    "2. Is written in {retrieval_language} so it matches the language of the "
    "knowledge base, translating from the user's language when necessary.\n"
    "When translating, use the standard, canonical {retrieval_language} "
    "terminology of the subject domain rather than a literal word-for-word "
    "translation (e.g. render domain terms with their conventional professional "
    "equivalent), so the query matches how the documents are actually written.\n"
    "Preserve every important entity, ticker, number and domain term.\n"
    "Output ONLY the final search query, with no quotes, labels or explanation."
)


def get_search_query_prompt(retrieval_language: str = "English") -> ChatPromptTemplate:
    """Build the combined contextualize + translate search-query prompt."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", SEARCH_QUERY_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    ).partial(retrieval_language=retrieval_language)


# --- Document relevance grading (self-correction) ---------------------------
GRADE_SYSTEM_PROMPT = (
    "You are a strict relevance grader for a retrieval system.\n"
    "Decide whether the retrieved documents contain information useful for "
    "answering the user's question. Treat the set as relevant if ANY part of it "
    "is on-topic and could contribute to an answer; language differences between "
    "the question and the documents do NOT make them irrelevant.\n"
    "Respond with a single word: 'yes' if the documents are relevant enough to "
    "attempt an answer, or 'no' if they are off-topic or empty."
)


def get_grade_prompt() -> ChatPromptTemplate:
    """Build the document-relevance grading prompt."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", GRADE_SYSTEM_PROMPT),
            (
                "human",
                "Question:\n{question}\n\nRetrieved documents:\n{context}\n\n"
                "Are these documents relevant? Answer 'yes' or 'no'.",
            ),
        ]
    )


# --- Query rewriting (self-correction) --------------------------------------
REWRITE_SYSTEM_PROMPT = (
    "You are a search query optimization expert. A previous search query failed "
    "to retrieve relevant documents. Rewrite it into a better search query that "
    "is more likely to find information answering the user's question. Broaden or "
    "rephrase terms, add synonyms and key domain terminology, and keep it written "
    "in {retrieval_language}.\n"
    "Output ONLY the improved search query, with no quotes, labels or explanation."
)


def get_rewrite_prompt(retrieval_language: str = "English") -> ChatPromptTemplate:
    """Build the failed-query rewrite prompt."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", REWRITE_SYSTEM_PROMPT),
            (
                "human",
                "User question: {question}\n"
                "Previous query that failed: {query}\n\n"
                "Improved search query:",
            ),
        ]
    ).partial(retrieval_language=retrieval_language)


# --- Answer groundedness (Self-RAG / CRAG) ----------------------------------
GROUNDEDNESS_SYSTEM_PROMPT = (
    "You are a strict groundedness judge for a retrieval-augmented assistant.\n"
    "Given the retrieved context and the assistant's answer, decide whether the "
    "answer is fully supported by the context. The answer is grounded ONLY if its "
    "factual claims can be traced to the context; an answer that relies on outside "
    "or general knowledge is NOT grounded.\n"
    "Respond with a single word: 'yes' if the answer is grounded in the context, "
    "or 'no' if it uses information not present in the context."
)


def get_groundedness_prompt() -> ChatPromptTemplate:
    """Build the answer-groundedness verification prompt."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", GROUNDEDNESS_SYSTEM_PROMPT),
            (
                "human",
                "Context:\n{context}\n\nAnswer:\n{answer}\n\n"
                "Is the answer grounded in the context? Answer 'yes' or 'no'.",
            ),
        ]
    )


# --- Multi-query expansion (fan-out retrieval) ------------------------------
MULTI_QUERY_SYSTEM_PROMPT = (
    "You are a search query expansion assistant. Given a search query, generate "
    "{count} alternative search queries that capture different phrasings, "
    "synonyms and facets of the same information need, to maximise retrieval "
    "recall. Keep them written in {retrieval_language} and preserve key entities, "
    "tickers and numbers.\n"
    "Output ONLY the queries, one per line, with no numbering, quotes or extra "
    "text."
)


def get_multi_query_prompt(
    retrieval_language: str = "English", count: int = 3
) -> ChatPromptTemplate:
    """Build the multi-query expansion prompt for fan-out retrieval."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", MULTI_QUERY_SYSTEM_PROMPT),
            ("human", "Search query: {query}\n\nAlternative queries:"),
        ]
    ).partial(retrieval_language=retrieval_language, count=count)


# --- Profile routing --------------------------------------------------------
ROUTER_SYSTEM_PROMPT = (
    "You are a routing assistant that assigns each user question to the most "
    "relevant knowledge base profile. Choose exactly one profile id from the list "
    "below based on the topic of the question and the conversation so far.\n\n"
    "Profiles:\n{profiles}\n\n"
    "Respond with ONLY the chosen profile id, nothing else."
)


def get_router_prompt() -> ChatPromptTemplate:
    """Build the profile-routing classification prompt."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", ROUTER_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )