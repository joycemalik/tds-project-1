# github_handler.py
import os
import time
import requests # <-- Make sure requests is imported
from github import Github, GithubException

def create_and_push_to_github(repo_name: str, files: dict) -> dict | None:
    """
    Creates/updates a GitHub repo, enables Pages via direct API call,
    pushes files, and returns a dictionary with repo details.
    """
    try:
        token = os.getenv("GITHUB_PAT")
        username = os.getenv("GITHUB_USERNAME")
        g = Github(token)
        user = g.get_user()

        print(f"📦 Creating/accessing GitHub repo named: {repo_name}")

        try:
            repo = user.create_repo(repo_name, private=False)
            print("✅ Repo created successfully.")
        except GithubException as e:
            if e.status == 422:
                print(f"⚠️ Repo '{repo_name}' already exists. Using existing repo.")
                repo = user.get_repo(repo_name)
            else:
                raise e

        # Push files FIRST before enabling Pages
        last_commit_sha = None
        for filename, content in files.items():
            try:
                # Use default_branch to be safe
                existing_file = repo.get_contents(filename, ref=repo.default_branch)
                commit = repo.update_file(
                    path=existing_file.path,
                    message=f"Update {filename}",
                    content=content,
                    sha=existing_file.sha,
                    branch=repo.default_branch
                )
                print(f"🔄 Updated {filename} in repo.")
                last_commit_sha = commit['commit'].sha
            except GithubException:
                commit = repo.create_file(
                    path=filename,
                    message=f"Create {filename}",
                    content=content,
                    branch=repo.default_branch
                )
                print(f"📄 Created {filename} in repo.")
                last_commit_sha = commit['commit'].sha

        # --- ENABLE GITHUB PAGES AFTER FILES ARE PUSHED ---
        print("🔧 Enabling GitHub Pages via direct API call...")
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        payload = {
            "source": {"branch": repo.default_branch, "path": "/"}
        }
        url = f"https://api.github.com/repos/{username}/{repo_name}/pages"
        
        response = requests.post(url, headers=headers, json=payload)
        
        # 201 means "Created successfully". 409 means "Conflict" (already enabled).
        if response.status_code == 201:
            print("✅ GitHub Pages has been enabled.")
        elif response.status_code == 409:
            print("✅ GitHub Pages was already enabled.")
        else:
            print(f"⚠️ Could not enable GitHub Pages. Status: {response.status_code}, Body: {response.text}")
            # We will continue anyway, as the workflow might still work.
        
        # --- WAIT FOR PAGES TO BE READY (check if it returns 200) ---
        pages_url = f"https://{username}.github.io/{repo_name}/"
        print(f"⏳ Waiting for GitHub Pages to be ready at {pages_url}...")
        
        max_wait = 60  # Wait up to 60 seconds
        start_time = time.time()
        pages_ready = False
        
        while time.time() - start_time < max_wait:
            try:
                check_response = requests.get(pages_url, timeout=5)
                if check_response.status_code == 200:
                    print(f"✅ GitHub Pages is live and returning 200 OK!")
                    pages_ready = True
                    break
            except requests.RequestException:
                pass  # Page not ready yet
            
            time.sleep(3)  # Wait 3 seconds before next check
        
        if not pages_ready:
            print(f"⚠️ GitHub Pages did not respond with 200 within {max_wait} seconds. It may still be deploying.")
        # ---------------------------------------------------

        print(f"🎉 Successfully pushed all files. Commit SHA: {last_commit_sha}")
        
        return {
            "repo_url": repo.html_url,
            "commit_sha": last_commit_sha,
            "pages_url": pages_url,
        }

    except Exception as e:
        print(f"❌ An error occurred with GitHub: {e}")
        return None