import sys
import os
import json

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.ingestion.scraper import scrape_prs
from backend.ingestion.llm_extractor import extract_decisions
from backend.ingestion.loader import load_graph

def main():
    print("🚀 Starting Aura Ingestion Pipeline...", flush=True)
    prs = scrape_prs()
    
    for pr in prs:
        print(f"🔍 Extracting PR #{pr['number']}...", flush=True)
        extraction = extract_decisions(pr)
        pr['decisions'] = extraction.get('decisions', [])
        
    with open("cache/raw_prs.json", "w", encoding="utf-8") as f:
        json.dump(prs, f, indent=2)
        
    print("💾 Loading data into Neo4j...", flush=True)
    load_graph(prs)
    print("🎉 Pipeline complete!", flush=True)

if __name__ == "__main__":
    main()
