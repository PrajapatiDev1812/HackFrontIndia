import os
import json
import logging
# pyrefly: ignore[missing-import]
from github import Github
# pyrefly: ignore[missing-import]
from dotenv import load_dotenv

load_dotenv()

def scrape_prs(repo_name: str = "fastapi/fastapi"):
    token = os.getenv("GITHUB_TOKEN")
    max_prs = int(os.getenv("MAX_PRS", 20))
    
    g = Github(token)
    repo = g.get_repo(repo_name)
    pulls = repo.get_pulls(state='all', sort='updated', direction='desc')
    
    pr_data = []
    for pr in pulls[:max_prs]:
        pr_info = {
            "id": pr.id,
            "number": pr.number,
            "title": pr.title,
            "body": pr.body or "",
            "state": pr.state,
            "author": pr.user.login,
            "created_at": str(pr.created_at),
            "merged_at": str(pr.merged_at) if pr.merged_at else None,
            "files": [{"filename": f.filename, "status": f.status, "additions": f.additions, "deletions": f.deletions} for f in pr.get_files()[:10]],
            "commits": [{"sha": c.sha, "message": c.commit.message} for c in pr.get_commits()[:5]]
        }
        pr_data.append(pr_info)
        
    os.makedirs("cache", exist_ok=True)
    with open("cache/raw_prs.json", "w", encoding="utf-8") as f:
        json.dump(pr_data, f, indent=2)
    print(f"✅ Scraped {len(pr_data)} PRs to cache/raw_prs.json")
    return pr_data

if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    scrape_prs()
