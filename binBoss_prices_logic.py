# Check logic for buying profit defined by percent
def is_price_up_percent(buying_price, current_price, percent):
    new_percent = ((current_price - buying_price) / buying_price) * 100
    is_up = percent <= new_percent
    return is_up, new_percent


# Check logic for selling profit defined by percent
def is_price_down_percent(buying_price, current_price, percent):
    neg_percent = -1 * percent
    new_percent = (((current_price - buying_price) / buying_price) * 100)
    is_down = neg_percent >= new_percent
    return is_down, new_percent


# Check logic for buying profit defined by value
def is_price_up_val(buying_price, current_price, val):
    return current_price >= buying_price + val


# Check logic for selling profit defined by value
def is_price_down_val(buying_price, current_price, val):
    return current_price <= buying_price - val
