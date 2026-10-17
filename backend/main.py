# pyrefly: ignore[missing-import]
from fastapi import FastAPI, HTTPException
# pyrefly: ignore[missing-import]
from pydantic import BaseModel
from backend.agent.agent import query_graph
from backend.ingestion.scraper import scrape_prs
from backend.ingestion.llm_extractor import extract_decisions
from backend.ingestion.loader import load_graph
import json

app = FastAPI(
    title="Aura GraphRAG API",
    description="AI Agent API for GitHub Architectural Decision History",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Aura GraphRAG API is running. Visit /docs for Swagger UI."}

@app.post("/query")
def query_agent(request: QueryRequest):
    result = query_graph(request.question)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["answer"])
    return result

@app.post("/ingest")
def trigger_ingestion(repo: str = "fastapi/fastapi"):
    try:
        prs = scrape_prs(repo)
        for pr in prs:
            pr['decisions'] = extract_decisions(pr).get('decisions', [])
        with open("cache/raw_prs.json", "w", encoding="utf-8") as f:
            json.dump(prs, f, indent=2)
        load_graph(prs)
        return {"status": "success", "message": f"Ingestion complete for {len(prs)} PRs."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
