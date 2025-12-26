#!/usr/bin/env python3
"""
Orchestrate 1,000 parallel Codegen agent runs to analyze all Zeeeepa repos.
Each agent analyzes one repo with repomix and rates for enterprise CI/CD compatibility.
"""

import os
import json
import time
import requests
from typing import List, Dict

# Codegen API configuration
CODEGEN_API_BASE = os.getenv("CODEGEN_API_URL", "https://api.codegen.com")
CODEGEN_API_KEY = os.getenv("CODEGEN_API_KEY")

# Target branch for all ratings
TARGET_BRANCH = "repo-ratings"
TARGET_REPO = "Zeeeepa/snow-code"

# Agent instruction template
AGENT_INSTRUCTION = """Analyze repository {repo_name} for enterprise CI/CD compatibility.

**Your task:**
1. Clone repo: {clone_url}
2. Run: `repomix` in the repo directory
3. Analyze the repomix output for:
   - Project structure and organization
   - Build system compatibility (npm/yarn/maven/gradle/cargo/etc)
   - CI/CD readiness (presence of .github/workflows, .gitlab-ci.yml, etc)
   - Testing infrastructure
   - Documentation quality
   - Dependency management
   - Container/Docker support
   - Code quality and complexity
   
4. Generate rating report:
   - **Enterprise CI/CD Score**: 0-10
   - **Build System**: Identified build tool(s)
   - **CI/CD Ready**: Yes/No + confidence level
   - **Testing Coverage**: Estimated level
   - **Documentation**: Score 0-10
   - **Complexity**: Low/Medium/High
   - **Recommended Actions**: List of improvements for CI/CD

5. Save to file: `ratings/{repo_name}.json`
6. Commit and push to branch: {target_branch}
   - Message: "Add CI/CD rating for {repo_name}"
   - All agents push to the SAME branch

**Output format (JSON):**
```json
{{
  "repo_name": "{repo_name}",
  "clone_url": "{clone_url}",
  "analyzed_at": "ISO-8601 timestamp",
  "repomix_summary": {{
    "total_files": 0,
    "total_lines": 0,
    "languages": {{}},
    "structure": "description"
  }},
  "cicd_rating": {{
    "overall_score": 0,
    "build_system": "",
    "cicd_ready": false,
    "cicd_confidence": 0.0,
    "testing_coverage": "",
    "documentation_score": 0,
    "complexity": "",
    "recommended_actions": []
  }}
}}
```

**IMPORTANT:**
- Create branch {target_branch} if it doesn't exist
- Fetch latest from {target_branch} before pushing
- Handle merge conflicts (your file should be unique: ratings/{repo_name}.json)
- Use `git pull --rebase origin {target_branch}` before pushing
"""

def fetch_all_repos() -> List[Dict]:
    """Fetch all 1,000 repos from GitHub API via Codegen"""
    print("📥 Fetching all 1,000 repositories...")
    
    all_repos = []
    for page in range(1, 11):  # Pages 1-10
        print(f"  Fetching page {page}/10...")
        # In actual implementation, call view_all_repos tool
        # For now, placeholder structure
        pass
    
    print(f"✅ Fetched {len(all_repos)} repositories")
    return all_repos

def create_agent_run(repo_info: Dict, index: int) -> str:
    """Create a Codegen agent run for one repo analysis"""
    
    instruction = AGENT_INSTRUCTION.format(
        repo_name=repo_info['name'],
        clone_url=repo_info['clone_url'],
        target_branch=TARGET_BRANCH
    )
    
    payload = {
        "repo": TARGET_REPO,
        "message": instruction,
        "source": "api"
    }
    
    headers = {
        "Authorization": f"Bearer {CODEGEN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{CODEGEN_API_BASE}/v1/agent-runs",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 200:
        run_id = response.json().get('id')
        print(f"  ✅ [{index:4d}/1000] Created agent run for {repo_info['name']} (ID: {run_id})")
        return run_id
    else:
        print(f"  ❌ [{index:4d}/1000] Failed for {repo_info['name']}: {response.text}")
        return None

def orchestrate_analysis():
    """Main orchestration function"""
    
    print("=" * 80)
    print("🚀 CODEGEN AGENT ORCHESTRATION: 1,000 REPO ANALYSIS")
    print("=" * 80)
    print()
    
    # Step 1: Fetch all repos
    repos = fetch_all_repos()
    
    if not repos:
        print("⚠️  No repositories fetched. Need to implement view_all_repos API calls.")
        print()
        print("To execute this script properly:")
        print("1. Set CODEGEN_API_KEY environment variable")
        print("2. Implement fetch_all_repos() to call view_all_repos for pages 1-10")
        print("3. Run this script: python3 orchestrate_1000_agents.py")
        return
    
    # Step 2: Create agent runs (respecting rate limits)
    print()
    print(f"📊 Creating {len(repos)} agent runs...")
    print(f"⏱️  Rate limit: 30 runs/minute = ~{len(repos)//30} minutes total")
    print()
    
    agent_run_ids = []
    
    for i, repo in enumerate(repos, start=1):
        run_id = create_agent_run(repo, i)
        if run_id:
            agent_run_ids.append(run_id)
        
        # Rate limiting: 30 requests per minute
        if i % 30 == 0:
            print(f"⏸️  Sleeping 60s for rate limit... ({i}/{len(repos)} completed)")
            time.sleep(60)
    
    print()
    print("=" * 80)
    print(f"✅ ORCHESTRATION COMPLETE: {len(agent_run_ids)} agents launched")
    print("=" * 80)
    print()
    print(f"📋 Agent runs created: {len(agent_run_ids)}")
    print(f"🌿 All pushing to branch: {TARGET_BRANCH}")
    print(f"📁 Results will be in: ratings/*.json")
    print()
    print("⏱️  Estimated completion time: 30-45 minutes")
    print("🔍 Monitor progress at: https://github.com/Zeeeepa/snow-code/tree/repo-ratings")

if __name__ == "__main__":
    if not CODEGEN_API_KEY:
        print("❌ ERROR: CODEGEN_API_KEY environment variable not set!")
        print()
        print("Get your API key from: https://codegen.com/settings")
        print("Then run: export CODEGEN_API_KEY='your-key-here'")
        exit(1)
    
    orchestrate_analysis()

