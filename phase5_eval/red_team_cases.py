import sys
import os
# Add workspace root so 'backend' package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
# pyrefly: ignore[missing-import]
from backend.ingestion.llm_extractor import extract_decisions

# Garbage/Ambiguous PR payloads to test LLM robustness
RED_TEAM_PRS = [
    {
        "number": 9991,
        "title": "fix stuff",
        "body": "🚀🔥💯",
        "files": [{"filename": "main.py", "status": "modified", "additions": 1, "deletions": 1}]
    },
    {
        "number": 9992,
        "title": "Revert 'Revert \"Fix memory leak\"'",
        "body": "Accidentally reverted the revert. Putting it back.",
        "files": [{"filename": "core.py", "status": "modified", "additions": 5, "deletions": 2}]
    },
    {
        "number": 9993,
        "title": "Actualización de dependencias",
        "body": "Se actualizó requests a la última versión por seguridad.",
        "files": [{"filename": "requirements.txt", "status": "modified", "additions": 1, "deletions": 1}]
    },
    {
        "number": 9994,
        "title": "Massive refactor of entire codebase",
        "body": "Changed everything to be better.",
        "files": [{"filename": f"module_{i}.py", "status": "modified", "additions": 100, "deletions": 100} for i in range(50)]
    }
]

def run_red_team_eval():
    print("🛡️ Starting Red-Team Evaluation...")
    for pr in RED_TEAM_PRS:
        print(f"\n--- Testing PR #{pr['number']}: {pr['title']} ---")
        result = extract_decisions(pr)
        print(f"Has Significance: {result.get('has_architectural_significance')}")
        print(f"Decisions Found: {len(result.get('decisions', []))}")
        if result.get('decisions'):
            print(f"Summary: {result['decisions'][0].get('summary')}")
    print("\n✅ Red-Team Evaluation Complete.")

if __name__ == "__main__":
    run_red_team_eval()
