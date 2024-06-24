from config import telegram_bot_token, telegram_chat_id, test_balance_txt_name
from telegram import Bot
import json as json
from datetime import datetime

# Constants
telegram_bot = Bot(token=telegram_bot_token)


# Notifications:

# File
# Appends the given balance to text file
def write_balance(balance):
    write_time = str(datetime.now())
    try:
        balance_str = json.dumps(balance, indent=2)
        file_path = test_balance_txt_name
        with open(file_path, 'a') as file:
            file.writelines([f"\n{write_time}\n", balance_str, "\n\n---------------------------------------"])
        print(f"Balance written to: {file_path}")
    except Exception as e:
        print(f"From binance_notification: {e}")


# Telegram:
async def send_telegram_message(message="Hello world"):
    try:
        await telegram_bot.send_message(chat_id=telegram_chat_id, text=message)
    except Exception as e:
        print(e)


# Buying/ Selling notifications with just the price
async def notify_buying(symbol, buying_price):
    message = f"Buying price {buying_price} symbol:{symbol}"
    print(message)
    await send_telegram_message(message)


async def notify_selling(symbol, selling_price):
    message = f"Selling price {selling_price} symbol:{symbol}"
    print(message)
    await send_telegram_message(message)
