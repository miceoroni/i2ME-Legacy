import asyncio
# from re import A
from recordGenerators import DailyForecast,CurrentObservations,HourlyForecast,AirQuality,AirportDelays,PollenForecast,Breathing

"""
CurrentConditions: Every 5 minutes
Daily Forecasts, Hourlies, etc: 60 minutes
Alerts: 5 minutes
"""

print("i2MessageEncoder-Python\nDeveloped by mewtek\nData record generators by Floppaa & Goldblaze")

async def FiveMinUpdaters():
    CurrentObservations.makeDataFile()
    await asyncio.sleep(300)


async def HourUpdaters():
    DailyForecast.makeDataFile()
    HourlyForecast.makeDataFile()
    AirQuality.writeData()
    PollenForecast.makeDataFile()
    AirportDelays.writeData()
    Breathing.makeDataFile()
    await asyncio.sleep(3600)

loop = asyncio.get_event_loop()

hourtasks = loop.create_task(HourUpdaters())
fivemintasks = loop.create_task(FiveMinUpdaters())

try:
    loop.run_until_complete(hourtasks)
    loop.run_until_complete(fivemintasks)
except asyncio.CancelledError: pass