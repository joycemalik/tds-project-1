# Attachment Support Update - Summary

## Changes Made

Updated the codebase to support **attachments in both `/build` and `/revise` endpoints**.

---

## Files Modified

### 1. `llm_handler.py`

#### Updated `revise_app_with_llm()` function:

**Before:**
```python
def revise_app_with_llm(new_brief: str, existing_html: str) -> dict | None:
    # Only accepted brief and existing HTML
```

**After:**
```python
def revise_app_with_llm(new_brief: str, existing_html: str, attachments: list | None = None) -> dict | None:
    # Now accepts optional attachments parameter
    # Processes attachments intelligently based on MIME type
```

**New Features:**
- ✅ Accepts `attachments` parameter (list of dicts with `name` and `url`)
- ✅ Detects **image attachments** (data URIs) and embeds them directly
- ✅ Decodes **text/CSV attachments** and provides data for JavaScript logic
- ✅ Adds attachment context to the LLM prompt for intelligent integration
- ✅ Graceful error handling for malformed attachments

---

### 2. `main.py`

#### Updated `/build` endpoint:

**Before:**
```python
generated_files = generate_app_with_llm(req.brief)
```

**After:**
```python
# Convert Pydantic Attachment models to dicts for the LLM handler
attachments_list = [att.model_dump() for att in req.attachments] if req.attachments else None
generated_files = generate_app_with_llm(req.brief, attachments_list)
```

#### Updated `/revise` endpoint:

**Before:**
```python
revised_files = revise_app_with_llm(req.brief, existing_html, req.attachments)
```

**After:**
```python
# Convert Pydantic Attachment models to dicts for the LLM handler
attachments_list = [att.model_dump() for att in req.attachments] if req.attachments else None
revised_files = revise_app_with_llm(req.brief, existing_html, attachments_list)
```

**Why the conversion?**
- `req.attachments` is a list of Pydantic `Attachment` objects
- The LLM handler expects plain Python dicts
- `.model_dump()` converts Pydantic models to dicts

---

## How Attachments Are Processed

### Image Attachments (e.g., `image/png`, `image/jpeg`)
```
Input: { "name": "logo.png", "url": "data:image/png;base64,iVBORw0KG..." }
Output in prompt:
--- New Asset Attachment: logo.png ---
Incorporate this new asset. Use its full Data URI as a source URL:
```
data:image/png;base64,iVBORw0KG...
```
```

**Usage:** LLM will embed this in `<img src="data:image/png;base64,..." />`

### Text/CSV Attachments (e.g., `text/csv`, `text/plain`)
```
Input: { "name": "data.csv", "url": "data:text/csv;base64,bmFtZSxhZ2U..." }
Output in prompt:
--- New Data Attachment: data.csv ---
Incorporate this new data into the application logic:
```
name,age
John,30
Jane,25
```
```

**Usage:** LLM will embed this data in JavaScript arrays/objects

---

## Testing

### Test `/build` with Attachments

```python
# send_request_with_attachment.py
import requests
import base64

# Read and encode an image
with open("logo.png", "rb") as f:
    img_data = base64.b64encode(f.read()).decode()
    
payload = {
    "email": "test@example.com",
    "secret": "s3cr3t",
    "task": "logo-app",
    "round": 1,
    "nonce": "test-123",
    "brief": "Create a page that displays the provided logo image",
    "checks": ["Logo is visible", "Page has title"],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [
        {
            "name": "logo.png",
            "url": f"data:image/png;base64,{img_data}"
        }
    ]
}

response = requests.post("http://127.0.0.1:8000/build", json=payload)
print(response.json())
```

### Test `/revise` with Attachments

```python
payload = {
    "email": "test@example.com",
    "secret": "s3cr3t",
    "task": "logo-app",  # Same task name as before
    "round": 2,
    "nonce": "test-456",
    "brief": "Add a new chart using the provided CSV data",
    "checks": ["Chart is displayed", "Data is accurate"],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [
        {
            "name": "sales.csv",
            "url": f"data:text/csv;base64,{csv_data}"
        }
    ]
}

response = requests.post("http://127.0.0.1:8000/revise", json=payload)
print(response.json())
```

---

## Benefits

1. ✅ **Round 1 (Build)**: Can now create apps that use uploaded images, CSVs, or other data
2. ✅ **Round 2+ (Revise)**: Can add new features using new attachments without losing previous work
3. ✅ **Intelligent handling**: Images embedded as data URIs, text decoded and provided as data
4. ✅ **Backward compatible**: Works with or without attachments
5. ✅ **Error resilient**: Malformed attachments don't crash the system

---

## Next Steps

1. **Restart the server** to apply changes:
   ```powershell
   cd 'D:\iitm\tds\project 1\ds-project-builder'
   ..\\.venv\Scripts\python.exe -m uvicorn main:app --reload
   ```

2. **Test with attachments** using the examples above

3. **Monitor logs** for attachment processing messages:
   - `📄 Processing N attachment(s)...`
   - `⚠️ Could not process attachment...` (if errors)

All set! 🎉
