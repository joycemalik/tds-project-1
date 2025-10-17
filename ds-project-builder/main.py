# main.py

import os # <-- Import the os module
import re
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
from dotenv import load_dotenv
from llm_handler import generate_app_with_llm
from github_handler import create_and_push_to_github 
from evaluation_handler import notify_evaluation_server # <-- IMPORT NOTIFIER


load_dotenv() # <-- Load variables from .env file

app = FastAPI()

def sanitize_repo_name(task_name: str) -> str:
    """
    Sanitize task name to create a valid GitHub repository name.
    - Converts to lowercase
    - Replaces spaces with hyphens
    - Removes special characters (keeps only alphanumeric, hyphens, underscores)
    - Ensures it doesn't start/end with hyphens
    """
    # Convert to lowercase and replace spaces with hyphens
    sanitized = task_name.lower().strip()
    sanitized = re.sub(r'\s+', '-', sanitized)
    
    # Remove any characters that aren't alphanumeric, hyphens, or underscores
    sanitized = re.sub(r'[^a-z0-9\-_]', '', sanitized)
    
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    
    # Ensure the name is not empty and doesn't exceed GitHub's 100 char limit
    if not sanitized:
        sanitized = "generated-app"
    
    return sanitized[:100]  # GitHub repo name max length

# --- Pydantic models (no changes here) ---
class Attachment(BaseModel):
    name: str
    url: str

class BuildRequest(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: List[str]
    evaluation_url: str
    attachments: Optional[List[Attachment]] = None

# --- Update the API endpoint ---
# main.py

# ... (other imports are the same) ...

from dotenv import load_dotenv
from llm_handler import generate_app_with_llm # <-- IMPORT our new function

load_dotenv()
app = FastAPI()

# ... (Pydantic models are the same) ...

@app.post("/build")
async def build_endpoint(req: BuildRequest):
    
    # 1. Verify Secret (no change here)
    expected_secret = os.getenv("PROJECT_SECRET")
    if req.secret != expected_secret:
        raise HTTPException(status_code=403, detail="Invalid secret")
    print("✅ --- SECRET VERIFIED --- ✅")

    # 2. Generate code using the LLM
    # We pass the 'brief' from the request to our new function.
    generated_files = generate_app_with_llm(req.brief)
    
    # 3. Check if files were generated and print them
    if not generated_files:
        return {"status": "error", "message": "LLM failed to generate code"}
    print("✅ --- CODE GENERATED --- ✅")

    # 3. Add a LICENSE file (as required by the project brief)
    generated_files["LICENSE"] = "MIT License\n\nCopyright (c) 2025\n\nPermission is hereby granted..."

    workflow_content = """
    name: Deploy to GitHub Pages
    on:
      push:
        branches: [ "main" ]
      workflow_dispatch:
    concurrency:
      group: "pages"
      cancel-in-progress: true
    permissions:
      contents: read
      pages: write
      id-token: write
    jobs:
      deploy:
        environment:
          name: github-pages
          url: ${{ steps.deployment.outputs.page_url }}
        runs-on: ubuntu-latest
        steps:
          - name: Checkout
            uses: actions/checkout@v4
          - name: Setup Pages
            uses: actions/configure-pages@v5
          - name: Upload artifact
            uses: actions/upload-pages-artifact@v3
            with:
              path: '.'
          - name: Deploy to GitHub Pages
            id: deployment
            uses: actions/deploy-pages@v4
    """

    generated_files[".github/workflows/deploy.yml"] = workflow_content
    
    # 4. Create repo and push files to GitHub
    # Sanitize the task name to create a valid GitHub repo name
    repo_name = sanitize_repo_name(req.task)
    print(f"📝 Using sanitized repo name: {repo_name} (from task: {req.task})")
    
    github_details = create_and_push_to_github(repo_name, generated_files)
    if not github_details:
        return {"status": "error", "message": "Failed to push to GitHub"}
    print("✅ --- CODE PUSHED TO GITHUB --- ✅")    # 5. Prepare and send the final notification
    evaluation_payload = {
        "email": req.email,
        "task": req.task,
        "round": req.round,
        "nonce": req.nonce,
        "repo_url": github_details["repo_url"],
        "commit_sha": github_details["commit_sha"],
        "pages_url": github_details["pages_url"],
    }
    notify_evaluation_server(req.evaluation_url, evaluation_payload)
    
    print("✅ --- ENTIRE BUILD PROCESS COMPLETE --- ✅")
    return {"status": "complete", "details": github_details}

@app.get("/")
def read_root():
    return {"message": "API is running."}