import os
from typing import Optional
# pyrefly: ignore[missing-import]
from langchain.tools import tool
from backend import get_neo4j_driver

@tool
def find_decisions_by_file(file_path: str) -> str:
    """Find all architectural decisions related to a specific file or component path."""
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run("""
            MATCH (f:File)<-[:MODIFIES]-(pr:PR)-[:EXTRACTS]->(d:Decision)
            WHERE f.path CONTAINS $file_path
            RETURN pr.number AS pr_number, pr.title AS pr_title, d.summary AS summary, 
                   d.decision_type AS type, d.confidence AS confidence
            ORDER BY pr.merged_at DESC LIMIT 10
        """, file_path=file_path)
        records = [dict(r) for r in result]
    return str(records) if records else "No decisions found for this file."

@tool
def get_chain_of_evidence(decision_id: str) -> str:
    """Trace the full evidence chain (PR, commits, author, superseding PRs) for a specific decision ID."""
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run("""
            MATCH (pr:PR)-[:EXTRACTS]->(d:Decision {id: $decision_id})
            OPTIONAL MATCH (pr)-[:CONTAINS_COMMIT]->(c:Commit)
            OPTIONAL MATCH (author:Developer)-[:AUTHORED]->(pr)
            RETURN pr.number AS pr_number, d.summary AS decision_summary, 
                   collect(c.sha)[..3] AS sample_commits, author.login AS author
        """, decision_id=decision_id)
        records = [dict(r) for r in result]
    return str(records) if records else f"No evidence chain found for decision ID: {decision_id}"

@tool
def find_implicit_supersessions(pr_number: int) -> str:
    """Find newer PRs that modify the same files as a given PR, hinting at implicit supersession."""
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run("""
            MATCH (target_pr:PR {number: $pr_number})-[:MODIFIES]->(f:File)<-[:MODIFIES]-(newer_pr:PR)
            WHERE target_pr.id <> newer_pr.id 
              AND (newer_pr.merged_at > target_pr.merged_at OR newer_pr.state = 'open')
            RETURN newer_pr.number AS newer_pr_number, newer_pr.title AS newer_pr_title, 
                   count(f) AS overlap_count
            ORDER BY overlap_count DESC LIMIT 5
        """, pr_number=pr_number)
        records = [dict(r) for r in result]
    return str(records) if records else f"No implicit supersessions found for PR #{pr_number}."
