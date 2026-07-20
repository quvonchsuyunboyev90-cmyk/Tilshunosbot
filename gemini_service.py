import asyncio
import requests
from config import GEMINI_API_KEY


def call_gemini_api(history):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent?key=" + GEMINI_API_KEY
    )

    payload = {
        "contents": history
    }

    headers = {
        "Content-Type": "application/json"
    }

    return requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=25
    )


def call_gemini_simple(prompt_text):
    history = [
        {
            "role": "user",
            "parts": [{"text": prompt_text}]
        }
    ]

    max_retries = 3
    wait_seconds = 3

    for _ in range(max_retries):
        try:
            response = call_gemini_api(history)

            if response.status_code == 200:
                data = response.json()

                return data["candidates"][0]["content"]["parts"][0]["text"]

            if response.status_code == 429:
                time.sleep(wait_seconds)
                wait_seconds *= 2
                continue

            return f"Google Server Xatosi ({response.status_code})"

        except Exception as e:
            return str(e)

    return "Gemini hozir band."
