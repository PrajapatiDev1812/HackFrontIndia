import os
from contextlib import contextmanager

# Try to load .env for local development
try:
    # pyrefly: ignore[missing-import]
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def get_neo4j_credentials():
    """Get credentials from .env (local) or st.secrets (Streamlit Cloud).
    
    If running inside Streamlit, st.secrets is checked first.
    If the placeholder value or missing in st.secrets, falls back to .env.
    """
    try:
        # pyrefly: ignore[missing-import]
        import streamlit as st
        if hasattr(st, 'secrets') and ('NEO4J_AURA_URI' in st.secrets or 'NEO4J_URI' in st.secrets):
            pwd = st.secrets.get("NEO4J_AURA_PASSWORD") or st.secrets.get("NEO4J_PASSWORD")
            # Only use st.secrets if it's not the placeholder
            if pwd and pwd != "your_auradb_password_here":
                uri = st.secrets.get("NEO4J_AURA_URI") or st.secrets.get("NEO4J_URI")
                user = st.secrets.get("NEO4J_AURA_USERNAME") or st.secrets.get("NEO4J_USERNAME", "neo4j")
                return {
                    "uri": uri,
                    "user": user,
                    "password": pwd,
                    "use_aura": True
                }
    except Exception:
        pass

    # Running locally with .env
    use_aura = os.getenv("USE_AURA_DB", "false").lower() == "true"
    
    if use_aura:
        return {
            "uri": os.getenv("NEO4J_AURA_URI"),
            "user": os.getenv("NEO4J_AURA_USERNAME"),
            "password": os.getenv("NEO4J_AURA_PASSWORD"),
            "use_aura": True
        }
    else:
        return {
            "uri": os.getenv("NEO4J_URI"),
            "user": os.getenv("NEO4J_USERNAME"),
            "password": os.getenv("NEO4J_PASSWORD"),
            "use_aura": False
        }

def get_neo4j_driver():
    # pyrefly: ignore[missing-import]
    from neo4j import GraphDatabase
    
    creds = get_neo4j_credentials()
    
    if not all([creds.get("uri"), creds.get("user"), creds.get("password")]):
        raise ValueError("Missing Neo4j credentials. Check .env file or st.secrets.toml")
    
    return GraphDatabase.driver(creds["uri"], auth=(creds["user"], creds["password"]))

# Aliases and helper context manager for backward compatibility
get_driver = get_neo4j_driver

@contextmanager
def get_session():
    driver = get_neo4j_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()

if __name__ == "__main__":
    try:
        driver = get_neo4j_driver()
        driver.verify_connectivity()
        print("✅ Successfully connected to Neo4j!")
        driver.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
