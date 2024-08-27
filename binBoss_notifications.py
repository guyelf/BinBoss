from config import telegram_bot_token, telegram_chat_id, test_balance_txt_name
from datetime import datetime
import json as json
from helpers.orders import check_order_status
from telegram import Bot

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
        print(f"from Telegram: {e}")


# Buying/ Selling notifications with just the price
async def notify_buying(symbol, buying_price):
    message = f"Buying price {buying_price} symbol:{symbol}"
    print(message)
    await send_telegram_message(message)


# Notify on order status, returns the order status
async def notify_on_order_fill_telegram(client, order_id, symbol):
    order_status, executed_qty, spent_usdt = await check_order_status(client=client, order_id=order_id, symbol=symbol)

    if order_status == 'FILLED':
        message = f"Order filled: {executed_qty} {symbol} bought for {spent_usdt} USDT."
        await send_telegram_message(message)
    elif order_status == 'PARTIALLY_FILLED':
        message = f"Order partially filled: {executed_qty} {symbol} bought so far."
        await send_telegram_message(message)
    return order_status


async def notify_selling(symbol, selling_price):
    message = f"Selling price {selling_price} symbol:{symbol}"
    print(message)
    await send_telegram_message(message)
