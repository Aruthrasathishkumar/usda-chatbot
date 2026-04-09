"""
query.py — The RAG Pipeline: Stage 2

What this file does:
  1. Loads the FAISS index from disk (built by ingest.py)
  2. Sets up Mistral as the LLM via Ollama
  3. Takes a user question
  4. Checks if the question is relevant to USDA RD programs
  5. Finds the 3 most relevant USDA programs via FAISS
  6. Sends those programs + question to Mistral
  7. Returns a grounded answer with source citations

This is the file your FastAPI backend imports in main.py.
"""

import os
from dotenv import load_dotenv

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Settings,
    load_index_from_storage,
    PromptTemplate
)
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

load_dotenv()

# -------------------------------------------------------
# Configuration — all tuneable values in one place
# -------------------------------------------------------

# Must match exactly what you used in ingest.py
EMBEDDING_MODEL  = "BAAI/bge-small-en-v1.5"
FAISS_INDEX_PATH = "./faiss_index"
OLLAMA_BASE_URL  = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL     = os.getenv("OLLAMA_MODEL", "mistral")

# How many programs to retrieve per query.
# 3 is the sweet spot — enough context, not too much for Mistral.
TOP_K = 3

# FAISS distance threshold for off-topic detection.
# FAISS returns L2 distance — lower = more similar.
# If the BEST matching program has distance > this value,
# the question is considered off-topic.
# Tune this: lower = stricter, higher = more lenient.
RELEVANCE_THRESHOLD = 1.5

# -------------------------------------------------------
# Keywords that suggest a question is USDA-related.
# Used as a fast pre-filter before calling FAISS or Mistral.
# -------------------------------------------------------
USDA_KEYWORDS = [
    'rural', 'usda', 'program', 'grant', 'loan', 'housing',
    'water', 'community', 'business', 'energy', 'broadband',
    'internet', 'farm', 'agriculture', 'cooperative', 'electric',
    'utility', 'development', 'low income', 'eligible', 'apply',
    'funding', 'assistance', 'help', 'qualify', 'benefit',
    'flood', 'disaster', 'earthquake', 'damage', 'repair',
    'clinic', 'hospital', 'school', 'library', 'fire station',
    'small business', 'homeowner', 'tenant', 'rent', 'mortgage',
    'telemedicine', 'distance learning', 'solar', 'renewable',
    'biofuel', 'wastewater', 'sewage', 'drinking water', 'well',
    'alaska', 'tribal', 'native', 'colonia', 'village',
    'what programs', 'what help', 'what assistance', 'can usda',
    'can i get', 'how do i', 'how can', 'where do i', 'who can',
    'broadband', 'telecom', 'electric', 'cooperative', 'biomass',
    'geothermal', 'wind', 'solar', 'biofuel', 'energy efficiency',
    'multifamily', 'single family', 'apartment', 'rental',
    'low-income', 'very low income', 'poverty', 'distressed',
    'section 502', 'section 504', 'section 515', 'section 521',
]

# -------------------------------------------------------
# System prompt — injected into every query sent to Mistral.
# This is the single most important thing that controls
# how Mistral behaves. It runs before every user question.
# -------------------------------------------------------
QA_PROMPT_TEMPLATE = PromptTemplate(
    "You are an official USDA Rural Development Assistant. "
    "Your ONLY job is to help users find and understand USDA "
    "Rural Development programs.\n\n"
    "RULES:\n"
    "1. Base your answer ONLY on the program context provided below.\n"
    "2. If the context does not contain relevant program information "
    "for the question, say: 'I could not find a USDA Rural Development "
    "program that matches your specific situation. Please contact your "
    "local USDA Rural Development State Office at "
    "rd.usda.gov/contact-us/state-offices for personalized guidance.'\n"
    "3. Always mention which specific programs you are referencing.\n"
    "4. Always recommend contacting the local USDA RD office for the "
    "most current eligibility and application details.\n"
    "5. Be clear, empathetic and helpful — users are often rural "
    "community members facing real challenges.\n\n"
    "Program context:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "User question: {query_str}\n\n"
    "Answer:"
)

# -------------------------------------------------------
# Off-topic response messages
# -------------------------------------------------------
OFF_TOPIC_KEYWORD_RESPONSE = (
    "I'm only able to help with USDA Rural Development programs "
    "and rural assistance questions. I can help you find programs for:\n\n"
    "• Rural housing loans and grants\n"
    "• Water and wastewater systems\n"
    "• Rural business loans and grants\n"
    "• Broadband internet in rural areas\n"
    "• Rural energy and electric programs\n"
    "• Community facilities (clinics, schools, fire stations)\n"
    "• Farm labor housing\n"
    "• Rural cooperative development\n\n"
    "For other topics, please use a general search engine.\n\n"
    "Is there anything about USDA Rural Development programs "
    "I can help you with?"
)

OFF_TOPIC_SIMILARITY_RESPONSE = (
    "I couldn't find any USDA Rural Development programs that "
    "specifically match your question. This might be because:\n\n"
    "• The topic may be outside USDA Rural Development's scope\n"
    "• The program you're looking for may have different "
    "eligibility requirements than expected\n"
    "• The program may be administered by a different federal agency\n\n"
    "I recommend contacting your local USDA Rural Development "
    "State Office directly — they can point you to the right "
    "program or agency.\n\n"
    "Find your state office at: rd.usda.gov/contact-us/state-offices"
)


def load_query_engine():
    """
    Loads the FAISS index from disk and returns a query engine.

    What is a query engine?
    An object that wraps the entire RAG pipeline:
      query_engine.query("your question")
        → embeds your question
        → searches FAISS for similar program documents
        → sends documents + question to Mistral
        → returns Mistral's response

    Why load once and reuse?
    Loading takes ~2-3 seconds. FastAPI loads it once at startup
    and reuses the same engine for every subsequent request.
    """

    print("Loading embedding model...")
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
    Settings.embed_model = embed_model

    print(f"Loading Mistral via Ollama ({OLLAMA_MODEL})...")
    llm = Ollama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        request_timeout=120.0,
        context_window=4096,
        additional_kwargs={
            "num_ctx":     4096,
            "num_predict": 512,
            "num_gpu":     99,    # use all available GPU layers
        }
    )
    Settings.llm = llm

    print(f"Loading FAISS index from {FAISS_INDEX_PATH}/...")

    vector_store = FaissVectorStore.from_persist_dir(FAISS_INDEX_PATH)

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        persist_dir=FAISS_INDEX_PATH
    )

    index = load_index_from_storage(storage_context=storage_context)

    query_engine = index.as_query_engine(
        similarity_top_k=TOP_K,
        response_mode="compact",
        text_qa_template=QA_PROMPT_TEMPLATE
    )

    print("Query engine ready!\n")
    return query_engine


def is_relevant_question(question: str) -> bool:
    """
    Fast keyword-based check to catch obviously off-topic questions
    before calling FAISS or Mistral.

    Returns True if the question seems USDA-related.
    Returns False if it is clearly off-topic.

    For very short questions (5 words or fewer), always returns True
    and lets FAISS decide — e.g. "housing help" or "water grants".
    """
    word_count = len(question.split())
    if word_count <= 5:
        return True

    question_lower = question.lower()
    return any(kw in question_lower for kw in USDA_KEYWORDS)


def ask(query_engine, question: str) -> dict:
    """
    Main function — takes a user question and returns an answer.

    Processing pipeline:
      Step 1: Keyword check — is this USDA-related at all?
              If not, return polite redirect immediately.
              (Fast — no FAISS or Mistral involved)

      Step 2: FAISS search — find the 3 closest programs.
              Check similarity scores. If nothing is close enough,
              return "no matching program found" message.
              (Medium — embedding + vector search, ~0.5 seconds)

      Step 3: Mistral generation — send programs + question to LLM.
              Return grounded answer with source citations.
              (Slow — 5-60 seconds depending on GPU/CPU)

    Args:
        query_engine: the engine returned by load_query_engine()
        question:     the user's natural language question

    Returns:
        dict with keys:
          answer     — Mistral's response text
          sources    — list of program dicts used in the answer
          off_topic  — True if question was redirected
    """

    # -------------------------------------------------------
    # Step 1: Keyword relevance pre-filter
    # -------------------------------------------------------
    if not is_relevant_question(question):
        print(f"Off-topic question detected (keyword filter): {question[:60]}")
        return {
            "answer":    OFF_TOPIC_KEYWORD_RESPONSE,
            "sources":   [],
            "off_topic": True
        }

    # -------------------------------------------------------
    # Step 2: FAISS search + similarity score check
    # -------------------------------------------------------
    print(f"Question: {question}")
    print("Searching FAISS and querying Mistral...")

    response = query_engine.query(question)

    # Extract the best (lowest) distance score from retrieved nodes
    scores = [
        node.score
        for node in response.source_nodes
        if node.score is not None
    ]

    if scores:
        best_score = min(scores)
        print(f"Best FAISS similarity score: {best_score:.3f} "
              f"(threshold: {RELEVANCE_THRESHOLD})")

        if best_score > RELEVANCE_THRESHOLD:
            print("Score exceeds threshold — returning off-topic response")
            return {
                "answer":    OFF_TOPIC_SIMILARITY_RESPONSE,
                "sources":   [],
                "off_topic": True
            }

    # -------------------------------------------------------
    # Step 3: Build and return the response
    # -------------------------------------------------------
    sources = []
    for node in response.source_nodes:
        sources.append({
            "program_name":    node.metadata.get("program_name", "Unknown"),
            "category":        node.metadata.get("category", ""),
            "source_url":      node.metadata.get("source_url", ""),
            "contact":         node.metadata.get("contact", ""),
            "relevance_score": round(1 - node.score, 3)
                               if node.score is not None else None
        })

    return {
        "answer":    str(response),
        "sources":   sources,
        "off_topic": False
    }


# -------------------------------------------------------
# Direct test — runs only when you execute this file directly
# python backend/rag/query.py
# -------------------------------------------------------
if __name__ == "__main__":

    ON_TOPIC_QUESTIONS = [
        "My small rural town's water system was damaged in an earthquake. What USDA programs can help?",
        "I am a low income farmer looking to buy a home in a rural area.",
        "We want to build a health clinic in our rural community of 5,000 people.",
        "Our rural area has no high speed internet. What broadband programs exist?",
        "I run a small business in a rural town and need a loan.",
    ]

    OFF_TOPIC_QUESTIONS = [
        "What is the capital of France?",
        "Write me a Python script to sort a list",
        "Who won the Super Bowl?",
        "What is 2 + 2?",
        "Tell me a joke",
        "What does NASA do?",
    ]

    print("=" * 60)
    print("USDA RD Chatbot — RAG Query Test")
    print("=" * 60)

    query_engine = load_query_engine()

    print("\n--- Testing ON-TOPIC questions ---\n")
    for question in ON_TOPIC_QUESTIONS:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        result = ask(query_engine, question)
        print(f"\nA: {result['answer'][:200]}...")
        print(f"Off-topic: {result['off_topic']}")
        print(f"Sources: {[s['program_name'] for s in result['sources']]}")
        input("\nPress Enter for next question...")

    print("\n--- Testing OFF-TOPIC questions ---\n")
    for question in OFF_TOPIC_QUESTIONS:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        result = ask(query_engine, question)
        print(f"\nA: {result['answer'][:200]}")
        print(f"Off-topic: {result['off_topic']}")