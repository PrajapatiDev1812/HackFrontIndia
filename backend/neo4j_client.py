import os
# pyrefly: ignore[missing-import]
from dotenv import load_dotenv

# Try to load .env for local development
try:
    load_dotenv()
except:
    pass

def get_neo4j_driver():
    # pyrefly: ignore[missing-import]
    from neo4j import GraphDatabase, exceptions
    
    uri = None
    user = None
    password = None

    def _clean(v):
        if v is None:
            return None
        v = str(v).strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1].strip()
        return v

    # 1. Try Streamlit Cloud Secrets first
    try:
        # pyrefly: ignore[missing-import]
        import streamlit as st
        if hasattr(st, 'secrets'):
            for k in ["NEO4J_AURA_URI", "NEO4J_URI", "neo4j_aura_uri", "neo4j_uri"]:
                if k in st.secrets:
                    uri = _clean(st.secrets[k])
                    break
            for k in ["NEO4J_AURA_USERNAME", "NEO4J_USERNAME", "neo4j_aura_username", "neo4j_username"]:
                if k in st.secrets:
                    user = _clean(st.secrets[k])
                    break
            for k in ["NEO4J_AURA_PASSWORD", "NEO4J_PASSWORD", "neo4j_aura_password", "neo4j_password"]:
                if k in st.secrets:
                    password = _clean(st.secrets[k])
                    break
    except Exception:
        pass # Not running in Streamlit or secrets missing

    # 2. Fallback to Local .env
    use_aura = os.getenv("USE_AURA_DB", "true").lower() == "true"
    
    if not uri:
        uri = _clean(os.getenv("NEO4J_AURA_URI") if use_aura else os.getenv("NEO4J_URI"))
    if not user:
        user = _clean(os.getenv("NEO4J_AURA_USERNAME") if use_aura else os.getenv("NEO4J_USERNAME"))
    if not password:
        password = _clean(os.getenv("NEO4J_AURA_PASSWORD") if use_aura else os.getenv("NEO4J_PASSWORD"))

    # 3. Known Aura instance fallback defaults
    if not uri or "databases.neo4j.io" not in uri:
        uri = "neo4j+s://5ec661f4.databases.neo4j.io"
    
    if not password or "your_auradb_password_here" in password or password == "":
        password = "XXCR1TALQrmQ4wSEw2CsaEZ4a-9ASOvrva5GksFMwC0"

    # For instance 5ec661f4, username is 5ec661f4
    if "5ec661f4" in uri and (not user or user == "neo4j"):
        user = "5ec661f4"
    elif not user:
        user = "neo4j"

    # 4. Try connecting; if auth fails with neo4j, auto-recover with 5ec661f4
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        return driver
    except exceptions.AuthError:
        if "5ec661f4" in uri and user != "5ec661f4":
            fallback_driver = GraphDatabase.driver(uri, auth=("5ec661f4", password))
            fallback_driver.verify_connectivity()
            return fallback_driver
        raise

if __name__ == "__main__":
    try:
        driver = get_neo4j_driver()
        print("[OK] Successfully connected to Neo4j!")
        driver.close()
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
