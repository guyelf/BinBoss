import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.exceptions import BinanceAPIException, BinanceOrderException
from binBoss_notifications import notify_buying, send_telegram_message, write_balance
from binBoss_strat_ma import run_ma
from binBoss_strat_simple import simpleStrategy
from config import api_key, api_secret, buying_quantity
from datetime import datetime


################## Async BinanceSocketManager ##################
# Helper function getting data from webSocket, makes calculations then place an API request (in Non-blocking/async manner)
async def get_order_book(client, symbol):
    order_book = await client.get_order_book(symbol=symbol)
    print(datetime.now(), ' ', order_book)


# Helper function to get the current price of the transaction (buying/selling)
def get_price_from_order(order):
    fills = order['fills']
    last_trade = fills[-1]
    price = float(last_trade['price'])
    return price


# Using webSocket w/ API request
# Gets the current, kline stream of the given symbol
# Keeps an open connection to the Binance API by the encapsulated While True loop inside
async def run_kline_listener(client, symbol='BTCUSDT', buying_price=0.0, cur_quantity=0.0):
    quantity = cur_quantity
    if buying_price == 0 or quantity == 0:
        quantity = 1
        print(f"Default values are ON")
    price_dict = {'current_buying_price': buying_price, 'current_selling_price': buying_price}
    bm = BinanceSocketManager(client)
    num_runs = 0
    async with bm.kline_socket(symbol=symbol) as stream:
        while True:
            # Get current kline stream value
            res = await stream.recv()
            closing_price = float(res['k']['c'])
            cur_symbol = res['k']['s']
            # Check current values
            print(
                f"{datetime.now()} {cur_symbol} {closing_price} | last buying price {price_dict['current_buying_price']} | last selling price {price_dict['current_selling_price']}")
            # execute trading strategy
            # MA strategy
            # await run_ma(client=client, symbol=symbol)
            # simple strategy (till the end)
            is_executed = await simpleStrategy(client=client, symbol=symbol, closing_price=closing_price,
                                               prices=price_dict, quantity=quantity)
            if is_executed:
                num_runs = num_runs + 1
            # terminate run after 5 successful runs
            if num_runs == 5:
                # test_count = 0
                print(f"Finished execution of {num_runs} attempts successfully")
                await asyncio.gather(get_order_book(client, symbol),
                                     send_telegram_message("Finished buying successfully ;)"))
                break


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
        side = client.SIDE_BUY
        order_type = client.ORDER_TYPE_MARKET
        quantity = buying_quantity
        order = await client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print("Order: ", order)
        # Extracting the buying price for later use
        buying_price = get_price_from_order(order)
        await notify_buying(symbol, buying_price)
        # Kline_listener to the stream of the current currency value
        await run_kline_listener(client=client, symbol=symbol, buying_price=buying_price, cur_quantity=quantity)
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
