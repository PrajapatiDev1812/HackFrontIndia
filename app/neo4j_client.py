import os
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.neo4j_client import (
    get_neo4j_credentials,
    get_neo4j_driver,
    get_driver,
    get_session
)

if __name__ == "__main__":
    try:
        driver = get_neo4j_driver()
        driver.verify_connectivity()
        print("✅ Successfully connected to Neo4j!")
        driver.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
