import asyncio
from helpers.telegram_notifications import notify_on_order_fill_telegram, notify_buying


# 2 Get Current Market Prices
async def get_bid_ask_prices(client, symbol):
    order_book = await client.get_order_book(symbol=symbol)
    bid_price = float(order_book['bids'][0][0])
    ask_price = float(order_book['asks'][0][0])
    return bid_price, ask_price


async def place_order(client, symbol, quantity, spread, type):
    bid_price, ask_price = await get_bid_ask_prices(client, symbol)

    buy_price = round(bid_price * (1 - spread), 2)
    sell_price = round(ask_price * (1 + spread), 2)

    if type == 'buy':
        return await client.order_limit_buy(
            symbol=symbol,
            quantity=quantity,
            price='{:.2f}'.format(buy_price)
        )
    elif type == 'sell':
        return await client.order_limit_sell(
            symbol=symbol,
            quantity=quantity,
            price='{:.2f}'.format(sell_price)
        )
    else:
        raise Exception('buy/sell order was not provided')


# 3 Place buying/selling orders first:
async def place_orders(client, symbol, quantity, spread):
    buy_order = await place_order(client=client, symbol=symbol, quantity=quantity, spread=spread, type='buy')
    sell_order = await place_order(client=client, symbol=symbol, quantity=quantity, spread=spread, type='sell')

    return buy_order, sell_order


# 4 Monitor orders and update accordingly
protif = 0
async def market_making(client, symbol, quantity, spread=0.001, order_lifetime=30):
    print(f'Started Market Making strategy with {symbol} {quantity} {spread} {order_lifetime}')
    sell_trades = []
    buy_trades = []
    trades = []
    is_value_changed = False

    # Function to add a trade
    def add_trade(buy_price, sell_price, quantity):
        profit = (sell_price - buy_price) * quantity
        trades.append(profit)

    # Function to calculate total profit
    def calculate_accumulating_profit():
        return sum(trades)

    try:
        # Init before loop
        buy_order, sell_order = await place_orders(client, symbol, quantity, spread)
        print(f"Placed orders: Buy at {buy_order['price']}, Sell at {sell_order['price']}")
        buy_order_stat = await notify_on_order_fill_telegram(client=client, order_id=buy_order['orderId'],
                                                             symbol=symbol)
        sell_order_stat = await notify_on_order_fill_telegram(client=client, order_id=sell_order['orderId'],
                                                              symbol=symbol)
        while True:
            ############ Run a buy order only when you have a fulfilled sell-order ################
            if buy_order_stat == 'CANCELED' or sell_order_stat == 'FILLED':
                print(f" Buy Order ran")
                buy_order = await place_order(client=client, symbol=symbol, quantity=quantity, spread=spread, type='buy')
            if sell_order_stat == 'CANCELED' or buy_order_stat == 'FILLED':
                print(f" Sell Order ran")
                sell_order = await place_order(client=client, symbol=symbol, quantity=quantity, spread=spread, type='sell')
            ################################
            # Wait for the specified order lifetime
            # time.sleep(order_lifetime)
            await asyncio.sleep(order_lifetime)

            # Check if order is filled and notify
            buy_order_stat = await notify_on_order_fill_telegram(client=client, order_id=buy_order['orderId'],
                                                                 symbol=symbol)
            sell_order_stat = await notify_on_order_fill_telegram(client=client, order_id=sell_order['orderId'],
                                                                  symbol=symbol)

            try:
                if buy_order_stat in ['NEW', 'PARTIALLY_FILLED']:
                    print(f'Canceling buy order after {order_lifetime} seconds')
                    await client.cancel_order(symbol=symbol, orderId=buy_order['orderId'])

                if sell_order_stat in ['NEW', 'PARTIALLY_FILLED']:
                    print(f'Canceling sell order after {order_lifetime} seconds')
                    await client.cancel_order(symbol=symbol, orderId=sell_order['orderId'])

                # Continue if orders were submitted correctly
                if buy_order_stat == 'FILLED':
                    is_value_changed = True
                    buy_trades.append(buy_order)
                    await notify_buying(symbol=symbol, buying_price=buy_order['price'])
                    print("Buy completed successfully")

                if sell_order_stat == 'FILLED':
                    is_value_changed = True
                    sell_trades.append(sell_order)
                    await notify_buying(symbol=symbol, buying_price=sell_order['price'])
                    print("Sell completed successfully")

                if sell_order_stat == 'CANCELED' or buy_order_stat == 'CANCELED':
                    print("Order is canceled")

                print(f"Order statuses: BUY:{buy_order_stat} SELL:{sell_order_stat}")
                # Need to handle calculation where only one of the orders is completed
                if is_value_changed and buy_trades and sell_trades:
                    add_trade(buy_price=float(buy_trades[-1]['price']), sell_price=float(sell_trades[-1]['price']),
                              quantity=quantity)
                    profit = calculate_accumulating_profit()
                    print(f'Total profit: {profit}')
                    is_value_changed = False
                if profit < 0: # exit the loop if we start loosing money
                    return
            except Exception as e:
                print(f"Exception from simple-market-making-->IF:\n{e}")
                raise

    except Exception as e:
        print(f"Exception from simple-market-making:\n{e}")
        # Repeat the process
