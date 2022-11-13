import asyncio
from recordGenerators import CurrentObservations,HourlyForecast,DailyForecast


""" This houses the tasks needed to update the data records concurrently 
    I have no idea if this is a messy way to do things, but it will be worked upon if it is.
"""

async def coTask():
    while True:
        await CurrentObservations.makeDataFile()
        asyncio.sleep(5 * 60)

async def hfTask():
    while True:
        await HourlyForecast.makeDataFile()
        asyncio.sleep(60 * 60)

async def dfTask():
    while True:
        await DailyForecast.makeDataFile()
        asyncio.sleep(60 * 60)