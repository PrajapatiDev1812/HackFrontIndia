import os
# pyrefly: ignore[missing-import]
from dotenv import load_dotenv
# pyrefly: ignore[missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI
# pyrefly: ignore[missing-import]
from langchain_groq import ChatGroq
from backend.agent.cypher_tools import find_decisions_by_file, get_chain_of_evidence, find_implicit_supersessions

# Support both older langchain AgentExecutor and modern LangChain 1.4+ create_agent
try:
    # pyrefly: ignore[missing-import]
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    # pyrefly: ignore[missing-import]
    from langchain_core.prompts import ChatPromptTemplate
    HAS_LEGACY_AGENT = True
except ImportError:
    # pyrefly: ignore[missing-import]
    from langchain.agents import create_agent
    HAS_LEGACY_AGENT = False

load_dotenv()

def get_setting(key: str, default: str = "") -> str:
    try:
        # pyrefly: ignore[missing-import]
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)

def get_llm():
    provider = get_setting("LLM_PROVIDER", "groq")
    if provider == "gemini":
        google_api_key = get_setting("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(model="gemini-3.8-flash", google_api_key=google_api_key, temperature=0)
    groq_api_key = get_setting("GROQ_API_KEY")
    return ChatGroq(model="qwen/qwen3.8-27b", groq_api_key=groq_api_key, temperature=0)

SYSTEM_PROMPT = """You are Aura, an expert AI assistant for software architecture history.
You ONLY answer based on the provided GraphRAG tools. NEVER hallucinate PR numbers, files, or decisions.
If tools return empty or insufficient data, state: "I don't have enough graph evidence to answer confidently."

ALWAYS format your final response exactly like this:
1. **Answer**: [Direct answer citing specific PR numbers and Decision summaries]
2. **Evidence Chain**: [List the PRs, files, or Decision IDs used]
3. **Confidence**: [Score 0-100]/100 — [One-line justification based on data richness]

Confidence Scoring Guide:
- 90-100: Multiple PRs + Decisions found, strong direct evidence.
- 70-89: 1-2 PRs found, decision extracted with high LLM confidence.
- 40-69: Indirect evidence only (file overlap, related topics).
- 0-39: Weak or no graph evidence.
"""

def create_aura_agent():
    tools = [find_decisions_by_file, get_chain_of_evidence, find_implicit_supersessions]
    llm = get_llm()
    
    if HAS_LEGACY_AGENT:
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        agent = create_tool_calling_agent(llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    else:
        return create_agent(llm, tools=tools, system_prompt=SYSTEM_PROMPT)

# Global agent instance
aura_agent = create_aura_agent()

def query_graph(user_question: str) -> dict:
    try:
        if HAS_LEGACY_AGENT:
            response = aura_agent.invoke({"input": user_question})
            return {"status": "success", "answer": response["output"]}
        else:
            response = aura_agent.invoke({"messages": [{"role": "user", "content": user_question}]})
            messages = response.get("messages", [])
            last_content = messages[-1].content if messages else "No response generated."
            if isinstance(last_content, list):
                last_content = "".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in last_content])
            return {"status": "success", "answer": str(last_content)}
    except Exception as e:
        return {"status": "error", "answer": f"Agent execution failed: {str(e)}"}
