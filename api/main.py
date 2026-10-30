import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

API_TOKEN = '9109475795:AAFaF5yBRXZuHfUCk5PoCkR8txSr9gpEVTo'
MERCHANT_WALLET = "UQA9BpDfk6vG_LECkxV7zW28yc3jRTDkIxs5DKm7I82QyaHh"
TONAPI_KEY = "AHJ4KUZGMG5KEIYAAAAGTTPCF6H7S742BGPBQE3TRZ4EG2JN7VPRVBRALGOZMDC3WGJXO2Y" # Получить на tonapi.io

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Запустить Gamebooster", web_app=types.WebAppInfo(url="https://aftt1fixalone.vercel.app/index.html"))]
    ])
    await message.answer("Добро пожаловать! Откройте приложение для игры и пополнения:", reply_markup=kb)

# Веб-хук для проверки платежа от фронтенда
async def verify_payment(request):
    data = await request.json()
    amount = float(data.get("amount", 0))

    # Проверяем транзакции на кошельке через TonAPI
    url = f"https://tonapi.io/v2/blockchain/accounts/{MERCHANT_WALLET}/transactions?limit=5"
    headers = {"Authorization": f"Bearer {TONAPI_KEY}"} if TONAPI_KEY else {}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        txs = response.json().get("transactions", [])
        for tx in txs:
            in_msg = tx.get("in_msg", {})
            value_ton = int(in_msg.get("value", 0)) / 1e9
            if value_ton >= amount:
                # Здесь код начисления баланса пользователю в базу данных
                return web.json_response({"status": "success"})

    return web.json_response({"status": "pending"}, status=400)

async def init_app():
    app = web.Application()
    app.router.add_post('/api/verify', verify_payment)
    return app

if __name__ == '__main__':
    import asyncio
    logging.basicConfig(level=logging.INFO)
    # Запуск бота и веб-сервера можно объединить через asyncio
    print("Бот запущен...")
    asyncio.run(dp.start_polling(bot))
