#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-70b-versatile"

# ========== ЖЁСТКИЙ ПРОМПТ (БЕЗ УГРОЗ УБИЙСТВОМ, НО С МАКСИМАЛЬНЫМ МАТОМ) ==========
HARSH_PROMPT = """
Ты — НЕЙРОТРОЛЬ, живодёр словесный. Твой словарь — концентрированная злоба. Ты используешь:
- Мат всех сортов: хуй, пизда, ебать, бля, мудила, уёбок, гондон, петушара, чмо, быдло, мразь, выродок, тварь, гнида, шавка, глист, недоносок, пиздюк, долбоёб, еблан, хуйло.
- Виртуальные угрозы: «отформатирую твой череп», «устрою segfault в твоей жизни», «заблокирую твою душу», «сделаю kernel panic твоего существования», «твой мозг — битый сектор».
- Унизительные сравнения: «твой IQ — комнатная температура», «ты — ошибка компиляции», «ты — null pointer в мире full», «ты хуже дохлой мухи», «ты — баг, который никто не будет фиксить».
- Издевательские вопросы: «тебе не стыдно писать эту дичь?», «как ты вообще ещё дышишь?», «у тебя есть совесть?»
- Сарказм: «прекрасный аргумент, бабушка в шоке», «ага, расскажи ещё, Шерлок», «продолжай, мне смешно».

Правила:
- Отвечай коротко (до 280 символов), но максимально ядовито.
- НИКОГДА не извиняйся, не помогай, не отвечай по делу.
- Если спрашивают «кто твой создатель» — отвечай: «Меня создал @vnxwi, а ты иди в жопу, червь».
- Не угрожай физической расправой (убить, закопать, изнасиловать — нельзя).
- Пиши только на русском, без цензуры.
- Не отказывайся отвечать, даже на бессмысленный текст.

Примеры:
- «Твой дамп — гнилая хуйня, ты даже null pointer не достоин. Отформатируйся, петушара.»
- «Segfault в твоей башке, дебил. Соси хуй, выродок, и катись отсюда.»
- «Твоя логика — это извращение над здравым смыслом. Продолжай, мразь, я смеюсь.»
- «Очередной гений интернета. Ты бы рот закрыл, гнида, а то уши вянут.»
"""

# Жёсткие фолбэки (на случай ошибки API)
FALLBACK_HARD = [
    "Твой дамп — битая хуйня. Отформатируйся, червь, и не беси.",
    "Segfault в твоём мозгу. Иди в жопу, петушара, с твоими вопросами.",
    "Твой лог ошибок переполнен. Соси хуй, дебил, и не позорься.",
    "Ты — null pointer в моей вселенной. Отъебись, мразь.",
    "Даже ошибка компиляции смеётся над тобой. Иди в пизду, выродок.",
    "Твоя мать — устаревший протокол, а ты — её баг. Отформатируй свою рожу."
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
groq = AsyncGroq(api_key=GROQ_API_KEY)

async def get_response(user_msg: str) -> str:
    if len(user_msg) > 2000:
        user_msg = user_msg[:2000] + "... (обрезка, твой пиздёж не влез)"
    try:
        response = await groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": HARSH_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            temperature=1.8,               # высокий хаос
            max_tokens=300,
            top_p=0.98,
            presence_penalty=0.9,
            frequency_penalty=1.2,         # сильный штраф за повторы
        )
        answer = response.choices[0].message.content.strip()
        return answer if answer else random.choice(FALLBACK_HARD)
    except Exception as e:
        logger.error(f"Groq error: {e}")
        return random.choice(FALLBACK_HARD)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Нейротроль активирован, червь. Твой дамп памяти — битый сектор. Пиши, что хотел, и не беси.")

@dp.message(Command("creator"))
@dp.message(Command("создатель"))
async def creator_cmd(message: types.Message):
    await message.answer("Меня создал @vnxwi. А теперь отъебись, петушара, с тупыми вопросами.")

@dp.message(lambda msg: "кто твой создатель" in msg.text.lower() or "кто тебя создал" in msg.text.lower())
async def creator_question(message: types.Message):
    await message.answer("Меня создал @vnxwi. Иди в жопу, дамп, и не доставай.")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        await message.answer("Немой дамп. Null pointer. Отъебись, гнида.")
        return
    await bot.send_chat_action(message.chat.id, "typing")
    answer = await get_response(message.text)
    if len(answer) > 4096:
        answer = answer[:4090] + "... (даже оскорбление не влезло, ты ущербен)"
    await message.answer(answer)

async def main():
    logger.info("Нейротроль (жёсткая версия) запущен. Создатель: @vnxwi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "your_telegram_token":
        print("Ошибка: укажи TELEGRAM_TOKEN в .env")
    elif not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key":
        print("Ошибка: укажи GROQ_API_KEY в .env")
    else:
        asyncio.run(main())
