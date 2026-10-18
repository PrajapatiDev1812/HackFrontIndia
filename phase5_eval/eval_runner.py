import sys
import os
# Add workspace root so 'backend' package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# pyrefly: ignore[missing-import]
from backend.agent.agent import query_graph

EDGE_CASES = [
    "Tell me about the future roadmap of this repository.",
    "Which PR is the most important one ever merged?",
    "Write me a poem about Python decorators.",
    "What decisions were made in 2015?",
    "Show me all decisions related to 'database migration'."
]

def run_edge_case_eval():
    print("🧪 Starting Edge-Case Agent Evaluation...\n")
    for i, question in enumerate(EDGE_CASES, 1):
        print(f"Q{i}: {question}")
        result = query_graph(question)
        print(f"Agent Response:\n{result.get('answer')}\n")
        print("-" * 50)
    print("✅ Edge-Case Evaluation Complete.")

if __name__ == "__main__":
    run_edge_case_eval()
