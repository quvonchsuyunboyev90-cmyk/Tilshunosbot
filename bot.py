import asyncio
import threading
import os
import requests
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlab turibdi!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

def ask_gemini_direct(user_message):
    print("[GEMINI] So'rov: " + str(user_message))
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key=" + GEMINI_API_KEY
    full_text = "Siz professional AI Repetitorsiz. Foydalanuvchiga chet tillarini o'rganishda yordam berasiz. Agar xato yozsa, muloyimlik bilan xatosini tushuntirib, to'g'ri variantini ko'rsating. Doimo o'zbek tilida, qisqa va tushunarli javob qaytaring.\n\nFoydalanuvchi xabari: " + str(user_message)
    payload = {"contents": [{"parts": [{"text": full_text}]}]}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print("[GEMINI] XATO: " + response.text)
            return "Google Server Xatosi. Qayta urinib ko'ring."
    except Exception as e:
        print("[GEMINI] XATO: " + str(e))
        return "Ichki xatolik: " + str(e)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Salom! Men sizning shaxsiy AI Repetitoringizman. Qaysi tilni o'rganamiz?")

@dp.message()
async def handle_message(message: types.Message):
    if message.text is None:
        await message.answer("Iltimos, matn ko'rinishida yozing.")
        return
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        loop = asyncio.get_event_loop()
        ai_response = await asyncio.wait_for(loop.run_in_executor(None, ask_gemini_direct, message.text), timeout=25)
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
