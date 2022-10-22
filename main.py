import asyncio
from asyncio.log import logger
from asyncore import loop
import logging,coloredlogs
from recordGenerators import Alerts,CurrentObservations,DailyForecast,HourlyForecast,AirportDelays,AirQuality,HeatingAndCooling,PollenForecast,Breathing
from radar import TWCRadarProcessor, RadarProcessor
import os

l = logging.getLogger(__name__)
coloredlogs.install(logger=l)

# Create dirs and files
if not os.path.exists('./.temp/'):
    os.makedirs('./.temp/')

if not os.path.exists('./.temp/tiles/'):
    os.makedirs('./.temp/tiles/')

if not os.path.exists('./.temp/tiles/output/'):
    os.makedirs('./.temp/tiles/output/')

if not os.path.exists('./.temp/msgId.txt'):
    print("Creating initial msgId file")
    with open('./.temp/msgId.txt', "w") as f:
        f.write("410080515")


"""
CurrentConditions: Every 5 minutes
Daily Forecasts, Hourlies, etc: 60 minutes
Alerts: 5 minutes
"""
l.info("Starting i2RecordCollector")
l.info("Developed by mewtek32, Floppaa, Goldblaze, and needlenose")

async def grabAlertsLoop():
    while True:
        Alerts.makeRecord()
        await asyncio.sleep(60)


# THIS IS BROKEN AT THE MOMENT -- COME BACK LATER.
# async def RadarProcessingLoop():
#     while True:
#         await TWCRadarProcessor.makeRadarImages()
#         await asyncio.sleep(30 * 60)

async def FiveMinUpdaters():
    while True:
        CurrentObservations.makeDataFile()
        l.debug("Sleeping for 5 minutes...")
        await asyncio.sleep(5 * 60)

async def HourUpdaters():
    while True:
        DailyForecast.makeDataFile()
        HourlyForecast.makeDataFile()
        AirQuality.writeData()
        PollenForecast.makeDataFile()
        AirportDelays.writeData()
        Breathing.makeDataFile()
        HeatingAndCooling.makeRecord()
        l.debug("Sleeping for an hour...")
        await asyncio.sleep(60 * 60)

loop = asyncio.get_event_loop()
alertTask = loop.create_task(grabAlertsLoop())
CCtask = loop.create_task(FiveMinUpdaters())
ForecastsTask = loop.create_task(HourUpdaters())

try:
    loop.run_until_complete(alertTask)
    loop.run_until_complete(CCtask)
    loop.run_until_complete(ForecastsTask)
except asyncio.CancelledError: pass