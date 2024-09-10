def pretty_print_balance(balances):
    # Print balances
    for balance in balances:
        asset = balance['asset']
        free_balance = balance['free']
        locked_balance = balance['locked']
        print(f"Asset: {asset}, Free: {free_balance}, Locked: {locked_balance}")


# Gets a client
# Returns account balance and prints it to the console
async def print_account_data(client):
    # Get account information
    account_info = await client.get_account()

    # Extract balances
    balance = account_info['balances'][:5]

    # Notify the balance to console and text file
    pretty_print_balance(balance)
    return balance
