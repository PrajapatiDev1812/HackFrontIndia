import os
from dotenv import load_dotenv

# Try to load .env for local development
try:
    load_dotenv()
except:
    pass

def get_neo4j_driver():
    from neo4j import GraphDatabase
    
    # 1. Try Streamlit Cloud Secrets first
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'NEO4J_AURA_URI' in st.secrets:
            uri = st.secrets["NEO4J_AURA_URI"]
            user = st.secrets.get("NEO4J_AURA_USERNAME", "neo4j")
            password = st.secrets["NEO4J_AURA_PASSWORD"]
            return GraphDatabase.driver(uri, auth=(user, password))
    except Exception:
        pass # Not running in Streamlit or secrets missing

    # 2. Fallback to Local .env
    use_aura = os.getenv("USE_AURA_DB", "false").lower() == "true"
    
    if use_aura:
        uri = os.getenv("NEO4J_AURA_URI")
        user = os.getenv("NEO4J_AURA_USERNAME")
        password = os.getenv("NEO4J_AURA_PASSWORD")
    else:
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")

    if not all([uri, user, password]):
        raise ValueError("Missing Neo4j credentials. Check .env file or Streamlit Secrets.")

    return GraphDatabase.driver(uri, auth=(user, password))

if __name__ == "__main__":
    try:
        driver = get_neo4j_driver()
        driver.verify_connectivity()
        print("✅ Successfully connected to Neo4j!")
        driver.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
