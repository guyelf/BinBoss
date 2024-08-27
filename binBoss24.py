import asyncio
import time

from binance import AsyncClient, BinanceSocketManager
from binance.exceptions import BinanceAPIException, BinanceOrderException
from binBoss_notifications import notify_buying, send_telegram_message, write_balance
from startegies.binBoss_strat_ma import run_ma
from startegies.binBoss_strat_simple import simpleStrategy
from config import api_key, api_secret, buying_quantity
from helpers.orders import get_price_from_order
from startegies.binBoss_start_simple_market_making import market_making
from startegies.binBoss_strat_simple import run_kline_listener_simple

################## Async BinanceSocketManager ##################

# Preferable percents: 3% take_profit (gain) buying 5% take_advantage (loss)
# Testing 0.5% gain and 2% loss

# Helper function to prettify start balance
def pretty_print_balance(balances):
    # Print balances
    for balance in balances:
        asset = balance['asset']
        free_balance = balance['free']
        locked_balance = balance['locked']
        print(f"Asset: {asset}, Free: {free_balance}, Locked: {locked_balance}")


async def main():

    try:
        # Initialize Binance client
        client = await AsyncClient.create(api_key=api_key, api_secret=api_secret, testnet=True)

        # Get account information
        account_info = await client.get_account()

        # Extract balances
        balance = account_info['balances'][:5]

        # Notify the balance to console and text file
        pretty_print_balance(balance)
        write_balance(balance=balance)

        # Define order
        symbol = 'ETHUSDT'
        exchange_info = await client.get_exchange_info()
        # print(f"exchange info {exchange_info}")
        side = client.SIDE_BUY
        order_type = client.ORDER_TYPE_MARKET
        quantity = buying_quantity
        order = await client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print("Order: ", order)

        # Extracting the buying price for later use
        buying_price = get_price_from_order(order)
        await notify_buying(symbol, buying_price)

        # Kline_listener to the stream of the current currency value
        # await run_kline_listener_simple(client=client, symbol=symbol, buying_price=buying_price, cur_quantity=quantity)
        await market_making(client=client, symbol=symbol, quantity=quantity, spread=0.00005, order_lifetime=30) # use defaults for spread and order_time_limit
    except BinanceAPIException as e:
        # Handle API exception (e.g., insufficient funds, invalid API keys)
        print(f"Binance API Exception: {e}")
    except BinanceOrderException as e:
        # Handle order exception (e.g., invalid order parameters)
        print(f"Binance Order Exception: {e}")
    except Exception as e:
        # Handle general exception
        print(f"Exception: {e}")
    finally:
        # Close connection
        await client.close_connection()


#if __name__ == "__main__":
asyncio.run(main())
