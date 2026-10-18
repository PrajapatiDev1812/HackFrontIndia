# Aura: GraphRAG Architectural Decision Tracker

Aura is a Graph-Retrieval Augmented Generation (GraphRAG) system that ingests GitHub Pull Requests, extracts architectural decisions using LLMs, stores them in a Neo4j Knowledge Graph, and exposes them via an AI Agent with a Streamlit UI.

## 🏗️ Architecture Diagram

```text
[GitHub API] --> (PyGithub Scraper) --> [JSON Cache]
                                              |
                                              v
[Neo4j AuraDB] <-- (Cypher Batch Loader) <-- [LLM Extractor (Gemini/Groq) + AST Parser]
      ^
      |
(Cypher Queries)
      v
[FastAPI Backend] <---> [LangChain Agent + 3 Custom Tools]
      ^
      |
  (HTTP REST)
      v
[Streamlit UI] (Chat Agent + Pyvis Graph Explorer)
```

## 🚀 Quick Start

1. **Setup**: `pip install -r requirements.txt`
2. **Database**: `docker-compose up -d` (or set `USE_AURA_DB=true` in `.env`)
3. **Ingest**: `python run_pipeline.py`
4. **Backend**: `uvicorn app.main:app --reload`
5. **Frontend**: `streamlit run app/ui/streamlit_app.py`

## 🧪 Evaluation

Run red-team and edge-case tests:

```bash
python phase5_eval/red_team_cases.py
python phase5_eval/eval_runner.py
```
