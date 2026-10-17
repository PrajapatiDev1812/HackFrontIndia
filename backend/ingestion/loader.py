import json
from backend.neo4j_client import get_driver, get_session

def load_graph(pr_data: list):
    driver = get_driver()
    
    with get_session() as session:

        session.run("MERGE (r:Repo {id: 'fastapi/fastapi'}) SET r.name = 'fastapi'")
        
        for pr in pr_data:
            session.run("""
                MATCH (r:Repo {id: 'fastapi/fastapi'})
                MERGE (p:PR {id: $pr_id})
                SET p.number = $number, p.title = $title, p.state = $state, p.merged_at = $merged_at
                MERGE (d:Developer {login: $author})
                MERGE (d)-[:AUTHORED]->(p)
                MERGE (r)-[:HAS_PR]->(p)
            """, pr_id=pr['id'], number=pr['number'], title=pr['title'], state=pr['state'], merged_at=pr['merged_at'], author=pr['author'])
            
            for f in pr['files']:
                session.run("""
                    MATCH (p:PR {id: $pr_id})
                    MERGE (file:File {path: $path})
                    MERGE (p)-[:MODIFIES {additions: $add, deletions: $del}]->(file)
                """, path=f['filename'], pr_id=pr['id'], add=f['additions'], **{"del": f['deletions']})
            
            if 'decisions' in pr and pr['decisions']:
                for i, dec in enumerate(pr['decisions']):
                    dec_id = f"dec_{pr['id']}_{i}"
                    session.run("""
                        MATCH (p:PR {id: $pr_id})
                        MERGE (dec:Decision {id: $dec_id})
                        SET dec.summary = $summary, dec.decision_type = $type, dec.rationale = $rationale, dec.confidence = $conf
                        MERGE (p)-[:EXTRACTS]->(dec)
                    """, dec_id=dec_id, summary=dec['summary'], type=dec['decision_type'], rationale=dec['rationale'], conf=dec['confidence'], pr_id=pr['id'])
                    
    try:
        print("✅ Graph loaded successfully!")
    except UnicodeEncodeError:
        print("[OK] Graph loaded successfully!")

if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    with open("cache/raw_prs.json", "r", encoding="utf-8") as f:
        prs = json.load(f)
    load_graph(prs)
