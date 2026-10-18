# 🎯 Aura: 5-Slide Pitch Deck Outline

## Slide 1: The Problem
- **Title**: "Where did that architectural decision come from?"
- **Content**: Developers waste hours digging through closed PRs, commit histories, and Slack threads to understand *why* a system was built a certain way. Context is lost.

## Slide 2: The Solution
- **Title**: "Aura: Institutional Memory as a Knowledge Graph"
- **Content**: Aura automatically ingests GitHub history, uses LLMs to extract *architectural decisions* (not just code changes), and maps them into a queryable Neo4j graph.

## Slide 3: How It Works (The Magic)
- **Title**: "From Raw PRs to Structured Insights"
- **Content**:
  1. **Scrape**: PyGithub fetches PRs, diffs, and commits.
  2. **Extract**: Gemini/Groq + Tree-sitter AST parsing extracts structured decisions (Summary, Rationale, Confidence).
  3. **Query**: LangChain Agent uses 3 custom Cypher tools to answer natural language questions with cited evidence.

## Slide 4: Live Demo
- **Title**: "See It In Action"
- **Content**: [Placeholder for GIF/Screenshot of Streamlit UI showing a user asking "Why was jsonable_encoder refactored?" and the Agent returning a 95% confidence answer with a visual graph chain of evidence].

## Slide 5: Why It Matters (The Impact)
- **Title**: "Faster Onboarding, Safer Refactors"
- **Content**:
  - ✅ Reduces "bus factor" risk.
  - ✅ Prevents re-introducing deprecated patterns (via implicit supersession detection).
  - ✅ 100% Free-Tier compatible (Neo4j Aura Free, Gemini Flash, Streamlit Cloud).
