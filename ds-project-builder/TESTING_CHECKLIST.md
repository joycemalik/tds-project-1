# Testing Checklist for GitHub Pages Fix

## Pre-Test Setup

### 1. Verify Environment Variables
Check your `.env` file has all required values:

```bash
# In PowerShell:
cd 'D:\iitm\tds\project 1\ds-project-builder'
Get-Content .env
```

Required variables:
- ✅ `GITHUB_PAT` - Your GitHub Personal Access Token
- ✅ `GITHUB_USERNAME` - Your GitHub username  
- ✅ `PROJECT_SECRET` - Your API secret (must match what you send)
- ✅ `GOOGLE_API_KEY` - Your Google Gemini API key

### 2. Verify Dependencies
```powershell
uv pip list | Select-String -Pattern "PyGithub|google-generativeai|fastapi|requests"
```

Should show:
- PyGithub
- google-generativeai
- fastapi
- uvicorn
- requests

---

## Test Procedure

### Step 1: Start the Server

```powershell
cd 'D:\iitm\tds\project 1\ds-project-builder'
uvicorn main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

### Step 2: Send Test Request

**Option A - Using Python script** (RECOMMENDED):
```powershell
# In a NEW PowerShell window
cd 'D:\iitm\tds\project 1'
python send_request.py
```

**Option B - Using PowerShell**:
```powershell
$path = 'D:\iitm\tds\project 1\request,json'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/build' -Method Post -ContentType 'application/json' -Body (Get-Content -Path $path -Raw)
```

---

## Expected Server Logs Sequence

Watch the uvicorn terminal for this exact sequence:

```
✅ --- SECRET VERIFIED --- ✅
🤖 Sending brief to Gemini to generate code...
✅ Code generated successfully!
✅ --- CODE GENERATED --- ✅
📦 Creating/accessing GitHub repo named: mouse-follower
✅ Repo created successfully.
📄 Created index.html in repo.
📄 Created README.md in repo.
📄 Created LICENSE in repo.
📄 Created .github/workflows/deploy.yml in repo.
🔧 Enabling GitHub Pages via direct API call...
✅ GitHub Pages has been enabled.
⏳ Waiting for GitHub Pages to be ready at https://username.github.io/mouse-follower/...
✅ GitHub Pages is live and returning 200 OK!
🎉 Successfully pushed all files. Commit SHA: abc123def456...
✅ --- CODE PUSHED TO GITHUB --- ✅
📤 Sending evaluation notification to: https://httpbin.org/post
✅ Evaluation server responded with status: 200
✅ --- ENTIRE BUILD PROCESS COMPLETE --- ✅
```

---

## Verification Steps

### 1. Check GitHub Repository
Open browser and navigate to:
```
https://github.com/YOUR_USERNAME/YOUR_TASK_NAME
```

Verify:
- ✅ Repo exists and is public
- ✅ Contains: `index.html`, `README.md`, `LICENSE`, `.github/workflows/deploy.yml`
- ✅ All files have content (not empty)

### 2. Check GitHub Pages Settings
Go to:
```
https://github.com/YOUR_USERNAME/YOUR_TASK_NAME/settings/pages
```

Verify:
- ✅ Source is set to "Deploy from a branch"
- ✅ Branch is "main" or "master"
- ✅ Folder is "/ (root)"
- ✅ Status shows "Your site is live at https://YOUR_USERNAME.github.io/YOUR_TASK_NAME/"

### 3. Test the Live Page
Open browser to:
```
https://YOUR_USERNAME.github.io/YOUR_TASK_NAME/
```

Verify:
- ✅ Page loads with HTTP 200 OK
- ✅ Page shows the generated app content
- ✅ No 404 error

---

## Troubleshooting

### Issue: "GitHub Pages did not respond with 200 within 60 seconds"

**Possible Causes:**
1. GitHub is slow (this happens sometimes)
2. GitHub Actions workflow is still deploying
3. There's an issue with the `index.html` file

**Solutions:**
- Wait 2-3 more minutes and manually check the URL
- Check GitHub Actions tab: `https://github.com/USERNAME/REPO/actions`
- Verify the workflow ran successfully

---

### Issue: "Could not enable GitHub Pages. Status: 403"

**Cause:** GitHub PAT doesn't have correct permissions

**Solution:**
1. Go to https://github.com/settings/tokens
2. Regenerate your token with these scopes:
   - ✅ `repo` (all)
   - ✅ `workflow`
   - ✅ `admin:repo_hook`
3. Update `.env` with new token
4. Restart uvicorn

---

### Issue: "Could not enable GitHub Pages. Status: 404"

**Cause:** Repository doesn't exist or username is wrong

**Solution:**
- Verify `GITHUB_USERNAME` in `.env` matches your actual GitHub username (case-sensitive)
- Check if repo was created successfully in the logs

---

### Issue: Page shows 404 but repo exists

**Causes:**
1. No `index.html` file in root
2. GitHub Pages not properly enabled
3. Branch is wrong

**Solutions:**
1. Check repo files - ensure `index.html` exists in root
2. Manually enable Pages in Settings > Pages
3. Verify branch is set correctly (should be `main` or `master`)

---

## Success Criteria

All of these must be TRUE:

- ✅ Server logs show "GitHub Pages is live and returning 200 OK!"
- ✅ GitHub repo is public and contains all required files
- ✅ GitHub Pages settings show "Your site is live"
- ✅ Opening the `pages_url` in a browser shows the generated app
- ✅ Browser returns HTTP 200 (not 404, not 503)
- ✅ Evaluation server receives the POST with correct `repo_url`, `commit_sha`, and `pages_url`

---

## Performance Benchmarks

Typical timing (with good internet):
- Gemini API call: 5-15 seconds
- GitHub repo creation: 1-2 seconds
- File uploads: 2-5 seconds per file
- GitHub Pages enablement: 1 second
- GitHub Pages to be ready: 10-45 seconds
- **Total: ~30-90 seconds per build**

---

## Clean Up Test Repos

After testing, you may want to delete test repos:

```powershell
# Manually via GitHub web interface
# OR use GitHub API (be careful!)
```

Navigate to:
```
https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/settings
```

Scroll to bottom > "Danger Zone" > "Delete this repository"
