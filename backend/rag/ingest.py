"""
ingest.py — The RAG Pipeline: Stage 1

What this file does:
  1. Connects to PostgreSQL and fetches all 12 USDA programs
  2. Wraps each program in a LlamaIndex Document object
  3. Converts each document's text into a vector (embedding)
  4. Stores all vectors in a FAISS index
  5. Saves the index to disk so query.py can load it later

Run this file ONCE (or whenever your program data changes).
You do NOT run this on every user query — that would be too slow.
"""

import os
import sys
import psycopg2
import faiss

from dotenv import load_dotenv

# LlamaIndex core components
from llama_index.core import (
    VectorStoreIndex,   # builds the searchable index
    StorageContext,     # manages where data is stored
    Document,           # wrapper around a piece of text
    Settings            # global config for LLM and embeddings
)

# FAISS integration for LlamaIndex
from llama_index.vector_stores.faiss import FaissVectorStore

# Local embedding model (runs on your machine, no API key needed)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# -------------------------------------------------------
# Load environment variables from .env file
# -------------------------------------------------------
load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "rd_chatbot"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD")
}

# -------------------------------------------------------
# Constants
# -------------------------------------------------------

# EMBEDDING_MODEL: This is the local AI model that converts
# text into vectors. BAAI/bge-small-en-v1.5 is a small,
# fast model (only ~130MB) that works great for English
# document search. It downloads automatically on first run.
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# EMBEDDING_DIMENSION: The number of dimensions in each vector.
# bge-small produces 384-dimensional vectors. This number MUST
# match the model you chose — FAISS needs to know this upfront
# to set up its index structure.
EMBEDDING_DIMENSION = 384

# FAISS_INDEX_PATH: Where to save the vector index on disk.
# This path is relative to the project root (usda-chatbot/).
FAISS_INDEX_PATH = "./faiss_index"


def fetch_programs_from_db():
    """
    Connects to PostgreSQL and fetches all programs.
    Returns a list of dictionaries — one per program.
    
    Why fetch from PostgreSQL instead of programs.json?
    PostgreSQL is your single source of truth. If you add more
    programs to the database later, ingest.py automatically
    picks them up without any code changes.
    """
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id, name, category, description, 
            eligibility, funding_info, how_to_apply, 
            contact, source_url
        FROM programs
        ORDER BY id;
    """)
    
    # cursor.description gives column names
    columns = [desc[0] for desc in cursor.description]
    
    # zip pairs each column name with its value for each row
    programs = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    print(f"Fetched {len(programs)} programs from database.")
    return programs


def create_documents(programs):
    """
    Converts raw program dictionaries into LlamaIndex Document objects.
    
    What is a Document?
    A Document is LlamaIndex's wrapper around a piece of text.
    It has two parts:
      - text: the actual content the AI will read and reason over
      - metadata: structured data attached to the document
                  (not embedded, but returned alongside results)
    
    Why combine all fields into one text block?
    The embedding model converts the ENTIRE text block into one vector.
    The more relevant information in that block, the better the
    vector captures the program's meaning. A user asking about
    "earthquake water damage grants" will match a document that
    mentions "emergency", "water", "disaster", and "grants" — all
    in the same text block.
    """
    documents = []
    
    for program in programs:
        # Build one rich text block per program.
        # This is what gets embedded (converted to a vector).
        # Think of it as writing a summary card for each program.
        text = f"""
Program Name: {program['name']}
Category: {program['category']}

Description:
{program['description']}

Who Is Eligible:
{program['eligibility']}

Funding Information:
{program['funding_info']}

How to Apply:
{program['how_to_apply']}

Contact:
{program['contact']}
        """.strip()
        
        # Metadata travels with the document but is NOT embedded.
        # It gets returned when this document is retrieved, so your
        # chatbot can show the program name and link to the user.
        metadata = {
            "program_id":   program['id'],
            "program_name": program['name'],
            "category":     program['category'],
            "source_url":   program['source_url'],
            "contact":      program['contact']
        }
        
        doc = Document(text=text, metadata=metadata)
        documents.append(doc)
        print(f"  Created document: {program['name']}")
    
    return documents


def build_faiss_index(documents):
    """
    Takes a list of Documents and builds a searchable FAISS index.
    
    Step by step:
    1. Set up the embedding model (converts text → vectors)
    2. Create an empty FAISS index of the right size
    3. Wrap FAISS in LlamaIndex's FaissVectorStore
    4. Feed all documents through the embedding model
    5. Store each document's vector in FAISS
    6. Save everything to disk
    
    What is FAISS doing exactly?
    Imagine plotting 12 dots in a 384-dimensional space — one dot
    per program. Each dot's position is determined by the program's
    meaning. Programs about water are clustered together. Programs
    about housing are in another cluster. When a user asks a question,
    you plot that question as a dot too, and FAISS finds the closest
    program dots. That is semantic search.
    """
    
    print("\nSetting up embedding model...")
    print(f"Model: {EMBEDDING_MODEL}")
    print("(First run downloads ~130MB — subsequent runs use cache)")
    
    # HuggingFaceEmbedding loads the embedding model locally.
    # It downloads to ~/.cache/huggingface/ on first use.
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
    
    # Set this as the global embedding model for LlamaIndex.
    # Any LlamaIndex operation that needs to embed text will
    # automatically use this model.
    Settings.embed_model = embed_model
    
    # We are NOT using an LLM during ingestion — only for querying.
    # Setting llm=None prevents LlamaIndex from trying to call Ollama.
    Settings.llm = None
    
    print("\nCreating FAISS index...")
    
    # faiss.IndexFlatL2 creates an index that uses L2 (Euclidean)
    # distance to measure similarity between vectors.
    # EMBEDDING_DIMENSION tells FAISS the size of each vector (384).
    # "Flat" means it compares against every vector — fine for 12 docs,
    # would need optimization for millions of documents.
    faiss_index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
    
    # FaissVectorStore wraps the raw FAISS index in LlamaIndex's
    # interface, so LlamaIndex can store and retrieve from it.
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    
    # StorageContext tells LlamaIndex WHERE to store things.
    # Here we tell it: use FAISS as the vector store.
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )
    
    print("Embedding documents and storing in FAISS...")
    print("(Each document is converted to a 384-dimensional vector)\n")
    
    # VectorStoreIndex.from_documents does the heavy lifting:
    #   - Takes each Document's text
    #   - Runs it through the embedding model → gets a vector
    #   - Stores the vector + metadata in FAISS
    # show_progress=True prints a progress bar
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )
    
    return index, storage_context


def save_index(index, storage_context):
    """
    Saves the FAISS index and all metadata to disk.
    
    Why save to disk?
    Building the index takes time (downloading the embedding model,
    embedding all documents). If you did this on every user query,
    each query would take 30+ seconds just for setup. Instead, you
    build once and save. query.py loads it in ~1 second.
    
    What gets saved to disk?
    - faiss_index/vector_store.json  → the FAISS vectors
    - faiss_index/docstore.json      → the document texts + metadata
    - faiss_index/index_store.json   → the index structure
    """
    
    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    
    print(f"\nSaving index to {FAISS_INDEX_PATH}/...")
    storage_context.persist(persist_dir=FAISS_INDEX_PATH)
    print("Index saved successfully!")


def main():
    print("=" * 60)
    print("USDA RD Chatbot — RAG Ingestion Pipeline")
    print("=" * 60)
    
    # Step 1: Get programs from PostgreSQL
    programs = fetch_programs_from_db()
    
    if not programs:
        print("No programs found in database. Run seed_data.py first.")
        sys.exit(1)
    
    # Step 2: Convert to LlamaIndex Documents
    print("\nCreating LlamaIndex documents...")
    documents = create_documents(programs)
    print(f"Created {len(documents)} documents.")
    
    # Step 3: Build the FAISS index
    index, storage_context = build_faiss_index(documents)
    
    # Step 4: Save to disk
    save_index(index, storage_context)
    
    # Step 5: Quick sanity check
    print("\n" + "=" * 60)
    print("Ingestion complete!")
    print(f"  Programs embedded: {len(documents)}")
    print(f"  Index saved to: {FAISS_INDEX_PATH}/")
    print(f"  Embedding model: {EMBEDDING_MODEL}")
    print(f"  Vector dimensions: {EMBEDDING_DIMENSION}")
    print("\nYou can now run query.py to test the search.")
    print("=" * 60)


if __name__ == "__main__":
    main()