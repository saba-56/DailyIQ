
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("GEMINI_API_KEY was not found in backend/.env")
else:
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents="Reply with exactly: Gemini connected successfully."
        )
        print(response.text)
    except Exception as e:
        print("Gemini connection failed:", e)
