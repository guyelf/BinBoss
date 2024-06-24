from binBoss_notifications import send_telegram_message, notify_buying, notify_selling
from binBoss_prices_logic import is_price_up_percent, is_price_down_percent


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
    if is_price_up_percent(buying_price=current_buying_price, current_price=closing_price, percent=take_profit):
        # Place the market sell order
        sell_mrk_order = await client.create_order(symbol=symbol, side=client.SIDE_SELL,
                                                   type=client.ORDER_TYPE_MARKET, quantity=quantity)
        # updates the listener to the current buying price
        prices['current_selling_price'] = closing_price
        await notify_selling(symbol=symbol, selling_price=closing_price)
        await send_telegram_message(f"Sold with {take_profit} percent gain!\n{sell_mrk_order}")
        return True

    # buy lower than sale percent
    if is_price_down_percent(buying_price=current_selling_price, current_price=closing_price, percent=take_advantage):
        buying_mrk_order = await client.create_order(symbol=symbol, side=client.SIDE_BUY,
                                                     type=client, quantity=quantity)
        # updates the listener to the current selling price
        prices['current_buying_price'] = closing_price
        await notify_buying(symbol=symbol, buying_price=closing_price)
        await send_telegram_message(f"Bought lower than last selling price by {take_advantage} percent (gain!)\n{buying_mrk_order}")
        return True
    return False
