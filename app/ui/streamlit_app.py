import sys
import os
# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# pyrefly: ignore[missing-import]
import streamlit as st
import json
import re

# Direct Agent & Graph imports (No FastAPI HTTP dependency for Streamlit Cloud)
try:
    from backend.agent.agent import query_graph
except ImportError:
    try:
        from app.agent.agent import query_graph
    except ImportError:
        from agent.agent import query_graph

try:
    from frontend.graph_viz import generate_graph_html
except ImportError:
    try:
        from graph_viz import generate_graph_html
    except ImportError:
        from app.ui.graph_viz import generate_graph_html

st.set_page_config(page_title="Aura GraphRAG", page_icon="🌟", layout="wide")

st.sidebar.title("⚙️ Aura Settings")
st.sidebar.success("☁️ Running on Streamlit Cloud")
st.sidebar.markdown("---")
st.sidebar.info("Target: fastapi/fastapi\nLLM: Gemini / Groq\nDB: Neo4j AuraDB")

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
                    result = query_graph(prompt)
                    answer = result.get("answer", "No answer found")
                    st.markdown(answer)

                    # Extract confidence score for gauge (simple regex fallback)
                    conf_match = re.search(r'(\d{1,3})/100', answer)
                    if conf_match:
                        score = int(conf_match.group(1))
                        st.markdown("**Confidence Gauge:**")
                        st.progress(score / 100, text=f"{score}/100 — {'High' if score >= 80 else 'Medium' if score >= 50 else 'Low'} Confidence")
                except Exception as e:
                    answer = f"Error querying graph: {str(e)}"
                    st.error(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

with tab2:
    st.subheader("Knowledge Graph Visualization")
    st.info("Visualizing the latest extracted Decisions, PRs, and Files directly from Neo4j AuraDB.")

    try:
        html_graph = generate_graph_html()
        st.components.v1.html(html_graph, height=600, scrolling=True)
    except Exception as e:
        st.error(f"Error loading graph visualization: {str(e)}")
