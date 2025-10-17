# send_request.py
import requests
import json

# The URL of your local FastAPI endpoint
url = "http://127.0.0.1:8000/build"

# Define the JSON payload as a Python dictionary.
# Make sure the 'secret' matches the one in your .env file!
payload = {
  "email": "test-from-python@example.com",
  "secret": "s3cr3t", # <-- IMPORTANT: Use your correct secret
  "task": "mouse follower",
  "round": 1,
  "nonce": "nonce-xyz",
  "brief": "Create a mouse follower that tracks the user's mouse movements and displays the coordinates on the screen. and as a game add a button that changes the background color randomly when clicked.",
  "checks": [
    "Repo has MIT license"
    "README.md is professional",
    "Page displays correct mouse coordinates",
    "Mouse follower works smoothly",
    "url is hosted on GitHub Pages"
  ],
  "evaluation_url": "https://httpbin.org/post",
  "attachments": []
}

print("🚀 Sending request to the API...")

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