import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: API key not found.")
    raise SystemExit(1)

url = "https://generativelanguage.googleapis.com/v1beta/models"

response = requests.get(
    url,
    params={"key": api_key},
    timeout=30
)

print("HTTP STATUS:", response.status_code)

if response.status_code != 200:
    print("API ERROR:", response.text[:1000])
    raise SystemExit(1)

data = response.json()

print("\nAVAILABLE MODELS:\n")

for model in data.get("models", []):
    name = model.get("name", "")
    methods = model.get("supportedGenerationMethods", [])

    if "generateContent" in methods:
        print("Model:", name)
        print("Methods:", methods)
        print("-" * 45)

if data.get("nextPageToken"):
    print("\nMore models are available on another page.")