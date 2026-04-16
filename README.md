# 🌾 USDA Rural Development AI Assistant

A full-stack AI system that transforms complex government programs into **simple, conversational, and actionable guidance** using Retrieval-Augmented Generation (RAG).

🔗 **Live Demo (Frontend Preview):**  https://aruthrasathishkumar.github.io/usda-chatbot/

> **Note:** This live demo is frontend-only (hosted on GitHub Pages).
- The backend (FastAPI + RAG + PostgreSQL + Ollama) runs locally by design  
- AI responses, semantic search, and data retrieval require local backend setup  

💡 This is a deliberate product decision to ensure **privacy + zero external API dependency**.

## 🧠 What This Project Does

USDA Rural Development offers **100+ programs**, but:

- Information is fragmented across multiple pages  
- Eligibility rules are complex and hard to understand  
- Users don’t know which program applies to them  

This system solves that by enabling:

👉 **Natural language discovery of government programs**

Example:

    User: "My rural community lost clean water access. What programs can help?"

    Bot:  Recommends relevant USDA programs with funding details,
          eligibility, and official links.

## ⚡ Key Features

- 💬 Conversational AI interface - Ask in plain English  
- 🔍 RAG (Retrieval-Augmented Generation) - Answers grounded in real USDA data  
- 📚 Semantic search (FAISS) - Finds programs by meaning, not keywords  
- 🔗 Source citations - Every response links to official USDA pages  
- 🚫 Off-topic detection - Prevents hallucinations and irrelevant answers  
- 🧭 Program browser - Explore all 73 programs by category  
- 💾 Chat history persistence - Stored in PostgreSQL for analytics  

## 🏗️ Architecture

    Browser (React + Tailwind UI)
            │
            │  user query
            ▼
    FastAPI Backend (port 8000)
            │
            ├── PostgreSQL (programs + chat history)
            │
            └── RAG Pipeline
                  │
                  ├── Embed query (BAAI/bge-small)
                  ├── FAISS similarity search (top K programs)
                  ├── Relevance filtering (threshold check)
                  └── Mistral 7B (via Ollama)
                          │
                          ▼
                  Grounded AI response + citations

## 🛠️ Tech Stack

| Layer | Technology | Why this choice |
|---|---|---|
| Frontend | React + Tailwind CSS + Vite | Fast UI development |
| Backend | FastAPI | High-performance Python APIs |
| Database | PostgreSQL | Structured data + chat history |
| LLM | Mistral 7B (Ollama) | Local inference, privacy-first |
| RAG | LlamaIndex | Clean retrieval pipeline |
| Embeddings | BAAI/bge-small | High semantic accuracy |
| Vector DB | FAISS | Ultra-fast similarity search |
| Scraping | Selenium + BeautifulSoup | Dynamic USDA data extraction |

## ⚙️ How It Works

1. User describes situation  
2. Query converted into embedding  
3. FAISS retrieves relevant programs  
4. Low-relevance filtered out  
5. Mistral generates grounded response  
6. User receives answer + citations  


## 💡 System Design Decisions

### Why RAG?

- Prevents hallucination  
- Uses real USDA data  
- Fully controllable knowledge base  

### Why FAISS?

- Zero infrastructure  
- No network latency  
- Perfect for small dataset  

### Why local LLM?

- No API cost  
- Privacy-first  
- No external dependency  

### Why no BM25?

- Dataset small (174 programs)  
- Vector search sufficient  
- Avoids extra latency  


## 📂 Project Structure

    usda-chatbot/
    │
    ├── backend/
    │   ├── main.py
    │   ├── database.py
    │   └── rag/
    │       ├── ingest.py
    │       └── query.py
    │
    ├── frontend/
    │   ├── src/
    │   │   ├── components/
    │   │   ├── hooks/
    │   │   └── App.jsx
    │
    ├── scripts/
    │   ├── seed_data.py
    │   └── verify_data.py
    │
    ├── faiss_index/
    └── README.md


## 💻 Local Setup

### Backend

    cd backend
    python -m venv venv
    venv\Scripts\activate

    pip install -r requirements.txt

    ollama serve

    uvicorn backend.main:app --reload --port 8000

### Build Vector Index

    python backend/rag/ingest.py

### Frontend

    cd frontend
    npm install
    npm run dev


## 📊 Why This Project Stands Out

- Real-world government use case  
- Production-grade RAG system  
- Fully local AI (privacy-first)  
- Full-stack + AI + system design  
- Scalable architecture  


## 🚀 Future Improvements

- Streaming responses  
- Multi-language support  
- State-based personalization  
- Automated data refresh  
- Hybrid search  
- User accounts  


## 🧩 Key Concept

> RAG transforms static government data into an intelligent conversational system.


## 📌 Summary

From:

❌ Complex websites  
❌ Manual searching  
❌ Confusing eligibility  

To:

✅ Conversational discovery  
✅ Personalized recommendations  
✅ Actionable insights  

This is not just a chatbot.

This is a **real-world AI system designed to improve access to public resources at scale.**
