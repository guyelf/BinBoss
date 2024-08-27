from datetime import datetime


async def check_order_status(client, order_id, symbol):
    order = await client.get_order(symbol=symbol, orderId=order_id)
    return order['status'], float(order['executedQty']), float(order['cummulativeQuoteQty'])


# Helper function getting data from webSocket
async def get_order_book(client, symbol):
    order_book = await client.get_order_book(symbol=symbol)
    print(datetime.now(), ' ', order_book)


# Helper function to get the current price of the transaction (buying/selling)
def get_price_from_order(order):
    fills = order['fills']
    last_trade = fills[-1]
    price = float(last_trade['price'])
    return price
