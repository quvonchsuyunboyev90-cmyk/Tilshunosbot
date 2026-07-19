import asyncio
import threading
import os
import time
import requests
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

app = Flask(__name__)

chat_histories = {}
MAX_HISTORY = 30

SYSTEM_INSTRUCTION = "Siz professional AI Repetitorsiz. Foydalanuvchiga chet tillarini o'rganishda yordam berasiz. Agar xato yozsa, muloyimlik bilan xatosini tushuntirib, to'g'ri variantini ko'rsating. Doimo o'zbek tilida, qisqa va tushunarli javob qaytaring. Oldingi suhbatni yodda tuting va shu asosda javob bering."

@app.route('/')
def home():
    return "Bot ishlab turibdi!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

def call_gemini_api(history):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key=" + GEMINI_API_KEY
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": history
    }
    headers = {"Content-Type": "application/json"}
    return requests.post(url, json=payload, headers=headers, timeout=20)

def ask_gemini_with_history(chat_id, user_message):
    print("[GEMINI] So'rov: " + str(user_message))

    if chat_id not in chat_histories:
        chat_histories[chat_id] = []

    history = chat_histories[chat_id]
    history.append({"role": "user", "parts": [{"text": user_message}]})

    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
        chat_histories[chat_id] = history

    max_retries = 4
    wait_seconds = 3

    for attempt in range(max_retries):
        try:
            response = call_gemini_api(history)
            print("[GEMINI] Status: " + str(response.status_code) + " (urinish " + str(attempt + 1) + ")")

            if response.status_code == 200:
                res_json = response.json()
                answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                history.append({"role": "model", "parts": [{"text": answer}]})
                chat_histories[chat_id] = history
                return answer

            elif response.status_code == 429:
                print("[GEMINI] Limit tugagan, " + str(wait_seconds) + " soniya kutib qayta urinamiz...")
                time.sleep(wait_seconds)
                wait_seconds = wait_seconds * 2
                continue

            else:
                print("[GEMINI] TO'LIQ XATO: " + response.text)
                history.pop()
                return "Google Server Xatosi (" + str(response.status_code) + "). Qayta urinib ko'ring."

        except Exception as e:
            print("[GEMINI] KUTILMAGAN XATO: " + str(e))
            if history:
                history.pop()
            return "Ichki xatolik: " + str(e)

    history.pop()
    return "Hozir juda ko'p foydalanuvchi so'rov yubordi. Iltimos, bir daqiqadan keyin qayta yozing."

@dp.message(Command("start"))
async def start_command(message: types.Message):
    chat_histories[message.chat.id] = []
    await message.answer("Salom! Men sizning shaxsiy AI Repetitoringizman. Qaysi tilni o'rganamiz?")

@dp.message(Command("reset"))
async def reset_command(message: types.Message):
    chat_histories[message.chat.id] = []
    await message.answer("Suhbat tarixi tozalandi. Yangidan boshlaymiz!")

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
