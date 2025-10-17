# send_request.py
import requests
import json

# The URL of your local FastAPI endpoint
url = "http://127.0.0.1:8000/revise" 

payload = {
  "email": "test-from-python@example.com",
  "secret": "s3cr3t",
  "task": "indian-monopoly", 
  "round": 2, 
  "nonce": "nonce-abc-round2",
  "brief": "build a board, pieces, and a dice roller for the Indian Monopoly game, improve it, add animations.", # <-- NEW brief
  "checks": [
    "Repo has MIT license",
    "README.md is professional",
    "index.html functions as a Monopoly game",
    "Properties can be bought and sold",
    "User portfolio is displayed correctly"
  ],
  "evaluation_url": "https://httpbin.org/post",
  "attachments": []
}

print("🚀 Sending REVISE request to the API...")

try:
    # Send the POST request.
    # The `json` parameter automatically converts the dictionary to a JSON string
    # and sets the "Content-Type" header to "application/json".
    response = requests.post(url, json=payload)

    # Check the HTTP status code from the server
    if response.status_code == 200:
        print("✅ Success! Server responded with:")
        print(response.json()) # Print the JSON response from the server
    else:
        print(f"❌ Error! Server responded with status code: {response.status_code}")
        print("Response body:")
        print(response.text)

except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection Error: Could not connect to the server at {url}.")
    print("Please make sure your FastAPI server is running.")