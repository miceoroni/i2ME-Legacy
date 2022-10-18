import asyncio
import logging,coloredlogs
from recordGenerators import DailyForecast,CurrentObservations,HourlyForecast,AirQuality,AirportDelays,PollenForecast,Breathing


l = logging.getLogger(__name__)
coloredlogs.install(logger=l)


"""
CurrentConditions: Every 5 minutes
Daily Forecasts, Hourlies, etc: 60 minutes
Alerts: 5 minutes
"""
l.info("Starting i2RecordCollector")
l.info("Developed by mewtek32, Floppaa, and Goldblaze")


async def FiveMinUpdaters():
    while True:
        CurrentObservations.makeDataFile()
        l.debug("Sleeping for 5 minutes...")
        await asyncio.sleep(300)


async def HourUpdaters():
    while True:
        DailyForecast.makeDataFile()
        HourlyForecast.makeDataFile()
        AirQuality.writeData()
        PollenForecast.makeDataFile()
        AirportDelays.writeData()
        Breathing.makeDataFile()
        l.debug("Sleeping for an hour...")
        await asyncio.sleep(3600)

loop = asyncio.get_event_loop()

hourtasks = loop.create_task(HourUpdaters())
fivemintasks = loop.create_task(FiveMinUpdaters())

try:
    loop.run_until_complete(hourtasks)
    loop.run_until_complete(fivemintasks)
except asyncio.CancelledError: pass