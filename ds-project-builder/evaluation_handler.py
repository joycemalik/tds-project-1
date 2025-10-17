# evaluation_handler.py
import requests
import time
import json

def notify_evaluation_server(url: str, payload: dict):
    """
    Sends a POST request to the evaluation server with exponential backoff.
    """
    max_retries = 5
    for i in range(max_retries):
        try:
            print(f"📞 Notifying evaluation server at {url} (Attempt {i+1}/{max_retries})")
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=15 # Set a 15-second timeout
            )

            if response.status_code == 200:
                print("✅ Notification successful!")
                print(f"Server responded with: {response.text}")
                return True
            else:
                print(f"❌ Notification failed with status: {response.status_code}, body: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ A network error occurred: {e}")

        # If not the last attempt, wait before retrying
        if i < max_retries - 1:
            delay = 2 ** i  # 1, 2, 4, 8 seconds
            print(f"Retrying in {delay} second(s)...")
            time.sleep(delay)

    print("🚫 All notification attempts failed.")
    return False