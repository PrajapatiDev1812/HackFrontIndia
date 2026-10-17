import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# pyrefly: ignore[missing-import]
import streamlit as st
import requests
import json
try:
    from frontend.graph_viz import generate_graph_html
except ImportError:
    from graph_viz import generate_graph_html

st.set_page_config(page_title="Aura GraphRAG", page_icon="🌟", layout="wide")

API_BASE_URL = "http://localhost:8000"

st.sidebar.title("⚙️ Aura Settings")
st.sidebar.success("✅ Connected to Local FastAPI")
st.sidebar.markdown("---")
st.sidebar.info("Target: fastapi/fastapi\nLLM: Gemini 1.5 Flash\nDB: Neo4j AuraDB")

st.title("🌟 Aura: GitHub Architectural Decision Explorer")

tab1, tab2 = st.tabs(["💬 Chat Agent", "🕸️ Graph Explorer"])

with tab1:
    st.subheader("Ask about architectural decisions")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("e.g., What decisions were made regarding performance?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Querying the knowledge graph..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/query", json={"question": prompt})
                    result = response.json()
                    
                    if result.get("status") == "success":
                        answer = result["answer"]
                        st.markdown(answer)
                        
                        # Extract confidence score for gauge (simple regex fallback)
                        import re
                        conf_match = re.search(r'(\d{1,3})/100', answer)
                        if conf_match:
                            score = int(conf_match.group(1))
                            st.markdown("**Confidence Gauge:**")
                            st.progress(score / 100, text=f"{score}/100 — {'High' if score >= 80 else 'Medium' if score >= 50 else 'Low'} Confidence")
                    else:
                        st.error(result.get("answer", "Unknown error"))
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to FastAPI backend. Is `uvicorn backend.main:app` running?")
        
        st.session_state.messages.append({"role": "assistant", "content": answer if 'answer' in locals() else "Error"})

with tab2:
    st.subheader("Knowledge Graph Visualization")
    st.info("Visualizing the latest extracted Decisions, PRs, and Files.")
    
    try:
        # Fetch a sample query to get nodes for the graph
        response = requests.post(f"{API_BASE_URL}/query", json={"question": "Show me recent architectural decisions"})
        result = response.json()
        
        if result.get("status") == "success":
            html_graph = generate_graph_html()
            st.components.v1.html(html_graph, height=600, scrolling=True)
        else:
            st.warning("No graph data available yet. Run ingestion first.")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to FastAPI backend.")
