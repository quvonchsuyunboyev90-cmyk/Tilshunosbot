import asyncio
import threading
import os
import time
import json
import requests
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
RAPIDAPI_HOST = "free-api-live-football-data.p.rapidapi.com"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

app = Flask(__name__)

chat_histories = {}
MAX_HISTORY = 30

@app.route('/')
def home():
    return "Bot ishlab turibdi!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# ---------- SPORT API FUNKSIYASI ----------
def call_sport_api(endpoint_path, params=None):
    url = "https://" + RAPIDAPI_HOST + endpoint_path
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    try:
        response = requests.get(url, headers=headers, params=params or {}, timeout=20)
        print("[SPORT API] " + endpoint_path + " -> Status: " + str(response.status_code))
        return response
    except Exception as e:
        print("[SPORT API] XATO: " + str(e))
        return None

# ---------- GEMINI FUNKSIYASI ----------
def call_gemini_api(history):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key=" + GEMINI_API_KEY
    payload = {"contents": history}
    headers = {"Content-Type": "application/json"}
    return requests.post(url, json=payload, headers=headers, timeout=20)

def ask_gemini_with_history(chat_id, user_message):
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    history = chat_histories[chat_id]
    history.append({"role": "user", "parts": [{"text": user_message}]})
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
        chat_histories[chat_id] = history

    max_retries = 3
    wait_seconds = 3
    for attempt in range(max_retries):
        try:
            response = call_gemini_api(history)
            if response.status_code == 200:
                res_json = response.json()
                answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                history.append({"role": "model", "parts": [{"text": answer}]})
                chat_histories[chat_id] = history
                return answer
            elif response.status_code == 429:
                time.sleep(wait_seconds)
                wait_seconds = wait_seconds * 2
                continue
            else:
                history.pop()
                return "Google Server Xatosi (" + str(response.status_code) + ")."
        except Exception as e:
            if history:
                history.pop()
            return "Ichki xatolik: " + str(e)
    history.pop()
    return "Hozir juda ko'p so'rov keldi, keyinroq urinib ko'ring."

# ---------- TELEGRAM BUYRUQLARI ----------
@dp.message(Command("start"))
async def start_command(message: types.Message):
    chat_histories[message.chat.id] = []
    await message.answer("Salom! Sport tahlil boti.\n\n/apitest <yo'l> - API endpoint'ni sinash uchun\n/apidebug - kalitni tekshirish\n\nOddiy xabar yozsangiz, men bilan suhbatlashishingiz mumkin.")

@dp.message(Command("reset"))
async def reset_command(message: types.Message):
    chat_histories[message.chat.id] = []
    await message.answer("Suhbat tozalandi.")

@dp.message(Command("apidebug"))
async def apidebug_command(message: types.Message):
    key = RAPIDAPI_KEY or ""
    if len(key) < 8:
        info = "RAPIDAPI_KEY topilmadi yoki juda qisqa: '" + key + "'"
    else:
        info = "Uzunligi: " + str(len(key)) + "\nBoshi: " + key[:6] + "\nOxiri: " + key[-6:]
    await message.answer(info)

@dp.message(Command("apitest"))
async def apitest_command(message: types.Message):
    text = message.text or ""
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Foydalanish: /apitest /endpoint-yoli\nMasalan: /apitest /football-get-leagues-list-all")
        return

    endpoint_path = parts[1].strip()
    if not endpoint_path.startswith("/"):
        endpoint_path = "/" + endpoint_path

    await message.answer("So'rov yuborilmoqda: " + endpoint_path)

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, call_sport_api, endpoint_path)

    if response is None:
        await message.answer("So'rov muvaffaqiyatsiz tugadi (tarmoq xatosi).")
        return

    status = response.status_code
    try:
        body = response.json()
        body_text = json.dumps(body, indent=2, ensure_ascii=False)
    except Exception:
        body_text = response.text

    print("[APITEST] To'liq javob: " + body_text[:3000])

    preview = body_text[:3500]
    await message.answer("Status: " + str(status) + "\n\n" + preview)

@dp.message()
async def handle_message(message: types.Message):
    if message.text is None:
        await message.answer("Iltimos, matn ko'rinishida yozing.")
        return
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        loop = asyncio.get_event_loop()
        ai_response = await asyncio.wait_for(
            loop.run_in_executor(None, ask_gemini_with_history, message.chat.id, message.text),
            timeout=40
        )
    except Exception as e:
        print("[TELEGRAM] Xato: " + str(e))
        ai_response = "Nimadir xato ketdi, qayta urinib ko'ring."
    await message.answer(ai_response)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print(">>> Polling boshlandi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
