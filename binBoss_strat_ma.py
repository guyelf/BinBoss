import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_ta as ta


# Client: AsyncClient
# Fetch historical data from Binance
async def get_historical_data(client, symbol, interval, lookback):
    klines = await client.get_historical_klines(symbol, interval, lookback)
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                         'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                         'taker_buy_quote_asset_volume', 'ignore'])
    data['close'] = data['close'].astype(float)
    return data


# Prepare the data
async def data_preparation(client, symbol):
    interval = client.KLINE_INTERVAL_1DAY
    lookback = '1 year ago UTC'
    df = await get_historical_data(client, symbol, interval, lookback)

    # Calculate the short-term and long-term moving averages
    df['SMA_50'] = ta.sma(df['close'], length=50)
    df['SMA_200'] = ta.sma(df['close'], length=200)

    # Generate buy and sell signals
    df['Signal'] = 0
    df['Signal'][50:] = np.where(df['SMA_50'][50:] > df['SMA_200'][50:], 1, 0)
    df['Position'] = df['Signal'].diff()

    # Print the signals
    print(df[['timestamp', 'close', 'SMA_50', 'SMA_200', 'Signal', 'Position']])

    return df


# Visualize the strategy
async def run_ma(client, symbol):
    # Return data_frame relevant for later calculations
    df = await data_preparation(client=client, symbol=symbol)

    plt.figure(figsize=(14, 7))
    plt.plot(df['close'], label='Close Price')
    plt.plot(df['SMA_50'], label='50-day SMA')
    plt.plot(df['SMA_200'], label='200-day SMA')

    # Plot buy signals
    plt.plot(df[df['Position'] == 1].index, df['SMA_50'][df['Position'] == 1], '^', markersize=10, color='g', lw=0,
             label='Buy Signal')

    # Plot sell signals
    plt.plot(df[df['Position'] == -1].index, df['SMA_50'][df['Position'] == -1], 'v', markersize=10, color='r', lw=0,
             label='Sell Signal')

    plt.title(f'{symbol} Moving Average Crossover Strategy')
    plt.legend(loc='best')
    plt.show()
