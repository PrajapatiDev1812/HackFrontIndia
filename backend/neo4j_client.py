import os
from contextlib import contextmanager
from typing import Generator
# pyrefly: ignore[missing-import]
from neo4j import GraphDatabase, Driver, Session
# pyrefly: ignore[missing-import]
from dotenv import load_dotenv

load_dotenv()

USE_AURA_DB = os.getenv("USE_AURA_DB", "false").lower() == "true"

def get_neo4j_driver() -> Driver:
    if USE_AURA_DB:
        uri = os.getenv("NEO4J_AURA_URI")
        user = os.getenv("NEO4J_AURA_USERNAME")
        password = os.getenv("NEO4J_AURA_PASSWORD")
    else:
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")

    if not all([uri, user, password]):
        raise ValueError("Missing Neo4j credentials in .env file.")

    return GraphDatabase.driver(uri, auth=(user, password))

# Aliases and helper context manager for backward compatibility
get_driver = get_neo4j_driver

@contextmanager
def get_session() -> Generator[Session, None, None]:
    driver = get_neo4j_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()

if __name__ == "__main__":
    driver = get_neo4j_driver()
    try:
        driver.verify_connectivity()
        print("✅ Successfully connected to Neo4j!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        driver.close()
