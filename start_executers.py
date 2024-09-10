from binance import AsyncClient
from binance.exceptions import BinanceAPIException, BinanceOrderException
from config import api_key, api_secret, buying_quantity

from helpers.file_notification import write_balance
from helpers.print_data import print_account_data

from startegies.binBoss_strat_simple import run_simple_start
from startegies.binBoss_start_simple_market_making import market_making
from startegies.binBoss_strat_ma import run_ma


async def runBot(symbol, strategy="Market_making"):
    try:
        # Initialize Binance client
        client = await AsyncClient.create(api_key=api_key, api_secret=api_secret, testnet=True)

        # Get the initial balance
        balance = await print_account_data(client=client)
        write_balance(balance)

        # Run chosen strategy
        match strategy:
            case 'Market_making':
                await market_making(client=client, symbol=symbol, quantity=buying_quantity, spread=0.00005,
                                    order_lifetime=30)  # use defaults for spread and order_time_limit
            case 'Simple':
                await run_simple_start(client=client, symbol=symbol, cur_quantity=buying_quantity)  # Kline_listener to the stream of the current currency value
            case 'MACD':
                await run_ma(client=client, symbol=symbol, quantity=buying_quantity)
            case _:
                raise Exception('Missing trading strategy')

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
