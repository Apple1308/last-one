import requests
import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from dotenv import load_dotenv
import os
import time
import math

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create bot and dispatcher objects
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()  # Create a Router object

# Cache variables
cached_data = None
last_updated = 0
CACHE_EXPIRATION = 24 * 60 * 60  # 24 hours in seconds

def get_exchange_rate():
    """
    Fetch exchange rate data from the API or use cached data if valid.
    """
    global cached_data, last_updated
    current_time = time.time()

    # Use cached data if it's still valid
    if cached_data is not None and (current_time - last_updated) < CACHE_EXPIRATION:
        logging.info("Using cached exchange rate data.")
        return cached_data

    # Fetch new data from API
    URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        data = response.json()

        # Convert API data to a dictionary for easier access
        rates = {item["Ccy"]: float(item["Rate"]) for item in data}
        cached_data = rates
        last_updated = current_time
        
        logging.info("Fetched new exchange rate data from API.")
        return rates
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching exchange rates: {e}")
        return None

@router.message(Command(commands=["start"]))
async def handle_start(message: types.Message):
    """
    Handle /start command and provide exchange rates for USD, EUR, RUB, and KZT to UZS.
    """
    exchange_data = get_exchange_rate()

    # Foydalanuvchining ismini olish
    user_name = message.from_user.first_name

    if exchange_data:
        # Valyuta kurslarini foydalanuvchiga yuborish
        response = (
            f"Assalomu alaykum, {user_name}! 👋\n"
            "Bu bot orqali USD, EUR, RUB va KZT valyutalarining O‘zbek so‘miga nisbatan kursini bilib olishingiz mumkin.\n\n"
            f"🔹 1 USD = {math.ceil(exchange_data.get('USD', 0))} UZS\n"
            f"🔹 1 EUR = {math.ceil(exchange_data.get('EUR', 0))} UZS\n"
            f"🔹 1 RUB = {math.ceil(exchange_data.get('RUB', 0))} UZS\n"
            f"🔹 1 KZT = {math.ceil(exchange_data.get('KZT', 0))} UZS\n\n"
            "💱 Valyuta kurslari avtomatik ravishda har kuni yangilanib boradi!\n"
            "🚀 Istalgan miqdordagi valyutani so‘mga aylantirish uchun uning qiymatini yuboring.\n"
            "Masalan: 100 → 100 USD, 100 EUR, 100 RUB va 100 KZT so‘mga nisbatan hisoblanadi."
        )
        await message.answer(response)
    else:
        await message.answer(f"Uzr, {user_name}, valyuta kurslarini olishda xatolik yuz berdi. Keyinroq qayta urinib ko‘ring.")

@router.message()
async def handle_currency(message: types.Message):
    """
    Handle user messages and provide exchange rates for the given amount in USD, EUR, and RUB to UZS.
    """
    exchange_data = get_exchange_rate()
    if exchange_data:
        try:
            # Foydalanuvchi yuborgan xabarni son sifatida o'qish
            amount = float(message.text)

            # Valyuta kurslarini hisoblash
            usd_to_uzs = int(amount * math.ceil(exchange_data.get('USD', 0)))
            
            eur_to_uzs = int(amount * math.ceil(exchange_data.get('EUR', 0)))
            rub_to_uzs = int(amount * math.ceil(exchange_data.get('RUB', 0)))
            kzt_to_uzs = int(amount * math.ceil(exchange_data.get('KZT', 0)))

            # Javobni shakllantirish
            response = (
                f"💵 Valyuta konvertatsiyasi natijalari:\n\n"
                f"🔹 {int(amount)} USD = {usd_to_uzs} UZS\n"
                f"🔹 {int(amount)} EUR = {eur_to_uzs} UZS\n"
                f"🔹 {int(amount)} RUB = {rub_to_uzs} UZS\n"
                f"🔹 {int(amount)} KZT = {kzt_to_uzs} UZS\n\n"
                f"📊 Kurslar har kuni yangilanadi va eng so'nggi ma'lumotlar asosida hisoblanadi.\n"
                f"💡 Istalgan miqdorni yuboring va natijani oling!"
            )
            await message.answer(response)
        except ValueError:
            # Agar foydalanuvchi noto'g'ri ma'lumot yuborsa
            await message.answer("Iltimos, to‘g‘ri qiymatni kiriting Masalan: 100 → 100 USD, 100 EUR, 100 RUB va 100 KZT so‘mga nisbatan hisoblanadi.")
    else:
        await message.answer("Failed to fetch exchange rates. Please try again later.")

async def main():
    """
    Main function to start the bot.
    """
    dp.include_router(router)  # Include the router in the dispatcher
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())