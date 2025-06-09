import requests
import json
import os
import time

# Set this to the IP and port of your backend server (e.g., "http://192.168.1.100:8001")
BACKEND_URL = os.getenv("BACKEND_URL", "http://192.168.1.142:8001")

def test_root():
    url = f"{BACKEND_URL}/"
    print(f"[TEST FRONTEND] Sending GET {url}")
    resp = requests.get(url)
    print(f"[TEST FRONTEND] Received: {resp.status_code} {resp.text}")

def test_health():
    url = f"{BACKEND_URL}/health"
    print(f"[TEST FRONTEND] Sending GET {url}")
    resp = requests.get(url)
    print(f"[TEST FRONTEND] Received: {resp.status_code} {resp.text}")

def test_query(prompt):
    url = f"{BACKEND_URL}/query"
    payload = {"prompt": prompt}
    print(f"[TEST FRONTEND] Sending POST {url} with payload: {payload}")
    resp = requests.post(url, json=payload)
    print(f"[TEST FRONTEND] Received: {resp.status_code} {resp.text}")
    if resp.status_code == 200:
        try:
            data = resp.json()
            print(f"[TEST FRONTEND] JSON response: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"[TEST FRONTEND] Error parsing JSON: {e}")

if __name__ == "__main__":
    print("[TEST FRONTEND] Starting test frontend script")
    test_root()
    time.sleep(1)
    test_health()
    time.sleep(1)
    test_query("Recommend me some moody alternative rock from the 1990s")
