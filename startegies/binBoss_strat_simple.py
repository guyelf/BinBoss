import asyncio
from helpers.orders import get_price_from_order
from helpers.telegram_notifications import send_telegram_message, notify_buying, notify_selling
from helpers.prices_logic import is_price_up_percent, is_price_down_percent
from binance import BinanceSocketManager
from datetime import datetime
from helpers.orders import get_order_book
import time


# Strategies

# Simple Strategy (TesT)
# Returns True if strategy executed otherwise - False
async def simpleStrategy(client, closing_price, prices, symbol, quantity):
    current_buying_price = prices['current_buying_price']
    current_selling_price = prices['current_selling_price']
    # Simple strategy HyperParameter
    percents = {'take_profit_selling': 0.5, 'take_advantage_buying': 2}
    # take profit percent
    take_profit = percents['take_profit_selling']
    take_advantage = percents['take_advantage_buying']
    # Sell per take profit percent
    # Per selling price
    is_up, new_percent = is_price_up_percent(buying_price=current_selling_price, current_price=closing_price,
                                             percent=take_profit)
    if is_up:
        # Place the market sell order
        sell_mrk_order = await client.create_order(symbol=symbol, side=client.SIDE_SELL,
                                                   type=client.ORDER_TYPE_MARKET, quantity=quantity)
        # updates the listener to the current buying price
        prices['current_selling_price'] = closing_price
        await notify_selling(symbol=symbol, selling_price=closing_price)

        await send_telegram_message(
            f"Sold with {new_percent} percent gain\ntake profit: {take_profit}\n{sell_mrk_order}")
        return True

    # buy lower than sale percent
    # From last selling price
    is_down, new_percent = is_price_down_percent(buying_price=current_selling_price, current_price=closing_price,
                                                 percent=take_advantage)
    if is_down:
        buying_mrk_order = await client.create_order(symbol=symbol, side=client.SIDE_BUY,
                                                     type=client, quantity=quantity)
        # updates the listener to the current selling price
        prices['current_buying_price'] = closing_price
        await notify_buying(symbol=symbol, buying_price=closing_price)
        await send_telegram_message(
            f"Bought lower than last selling price by {new_percent} percent (gain!)\ntake profit:{take_advantage}\n{buying_mrk_order}")
        return True
    return False


# Using webSocket w/ API request
# Gets the current kline stream of the given symbol
# Keeps an open connection to the Binance API by the encapsulated While True loop inside
# Executes Simple strategy
async def run_simple_start(client, symbol='BTCUSDT', cur_quantity=0.0):
    print("Started Simple strategy")

    # First order
    side = client.SIDE_BUY
    order_type = client.ORDER_TYPE_MARKET
    order = await client.create_order(symbol=symbol, side=side, type=order_type, quantity=cur_quantity)
    print("First Order: ", order)
    # Get buying price
    buying_price = get_price_from_order(order)
    await notify_buying(symbol, buying_price)

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
            time.sleep(5)
            await asyncio.sleep(5)
            res = await stream.recv()
            closing_price = float(res['k']['c'])
            cur_symbol = res['k']['s']
            # Check current values
            print(
                f"{datetime.now()} {cur_symbol} {closing_price} | last buying price {price_dict['current_buying_price']} | last selling price {price_dict['current_selling_price']}")
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
