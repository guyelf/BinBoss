import asyncio
from start_executers import runBot


# Preferable percents: 3% take_profit (gain) buying 5% take_advantage (loss)
# Testing 0.5% gain and 2% loss
async def main():
    await runBot(symbol='ETHUSDT')


# Run Main
asyncio.run(main())
