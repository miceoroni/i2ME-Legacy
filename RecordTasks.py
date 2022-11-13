import asyncio
from recordGenerators import Alerts,CurrentObservations,HourlyForecast,DailyForecast


""" This houses the tasks needed to update the data records concurrently 
    I have no idea if this is a messy way to do things, but it will be worked upon if it is.
"""

async def alertsTask():
    while True:
        await Alerts.makeRecord()
        await asyncio.sleep(60)

async def coTask():
    while True:
        await CurrentObservations.makeDataFile()
        await asyncio.sleep(5 * 60)

async def hfTask():
    while True:
        await HourlyForecast.makeDataFile()
        await asyncio.sleep(60 * 60)

async def dfTask():
    while True:
        await DailyForecast.makeDataFile()
        await asyncio.sleep(60 * 60)