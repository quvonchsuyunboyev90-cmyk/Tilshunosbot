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

# --- Render "uxlab qolmasin" uchun mini web-server ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlab turibdi!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# --- Gemini funksiyasi ---
def ask_gemini_direct(user_message: str) -> str:
    print(f"[GEMINI] So'rov: {user_message}")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"
    full_text = (
        "Siz professional AI Repetitorsiz. Foydalanuvchiga chet tillarini o'rganishda yordam berasiz. "
        "Agar xato yozsa, muloyimlik bilan xatosini tushuntirib, to'g'ri variantini ko'rsating. "
        "Doimo o'zbek tilida, qisqa va tushunarli javob qaytaring.\n\n"
        f"Foydalanuvchi xabari: {user_message}"
    )
    payload = {"contents": [{"parts": [{"text": full_text}]}]}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"[GEMINI] XATO: {response.text}")
            return "Google Server Xatosi. Qayta urinib ko'ring."
    except Exception as e:
        print(f"[GEMINI] XATO: {e}")
        return f"Ichki xatolik: {e}"

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Salom! Men sizning shaxsiy AI Repetitoringizman. 👋\nQaysi tilni o'rganamiz?")

@dp.message()
async def handle_message(message: types.Message):
    if not message
  
