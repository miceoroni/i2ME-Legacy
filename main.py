import asyncio
from asyncio.log import logger
from asyncore import loop
import logging,coloredlogs
from recordGenerators import Alerts,CurrentObservations,DailyForecast,HourlyForecast,AirportDelays,AirQuality,HeatingAndCooling,PollenForecast,Breathing, AchesAndPains, MosquitoActivity, WateringNeeds, TideForecast
from radar import TWCRadarCollector
import os
from datetime import datetime

l = logging.getLogger(__name__)
coloredlogs.install(logger=l)

useRadarServer = True

# Create dirs and files
if not os.path.exists('.temp/'):
    os.makedirs('.temp/')

if not os.path.exists('.temp/tiles/'):
    os.makedirs('.temp/tiles/')

if not os.path.exists('.temp/tiles/output/'):
    os.makedirs('.temp/tiles/output/')

if not os.path.exists('.temp/msgId.txt'):
    print("Creating initial msgId file")
    with open('.temp/msgId.txt', "w") as f:
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
        await Alerts.makeRecord()
        await asyncio.sleep(60)

async def FiveMinUpdaters():
    while True:
        await CurrentObservations.makeDataFile()
        l.debug("Sleeping for 5 minutes...")
        await asyncio.sleep(5 * 60)

async def HourUpdaters():
    while True:
        await DailyForecast.makeDataFile()
        await HourlyForecast.makeDataFile()
        # AirQuality.writeData()
        # PollenForecast.makeDataFile()
        # AirportDelays.writeData()
        # Breathing.makeDataFile()
        # HeatingAndCooling.makeRecord()
        # WateringNeeds.makeRecord()
        # MosquitoActivity.makeRecord()
        # AchesAndPains.makeRecord()
        # TideForecast.makeRecord()
        l.debug("Sleeping for an hour...")
        await asyncio.sleep(60 * 60)

async def radarCollector():
    mosaicUpdateIntervals = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
    satradUpdateIntervals = [0, 10, 20, 30, 40, 50]

    while True:
        # Server takes ~15 - 35 seconds on average to fully generate a frame, use 40 seconds
        # to make sure the radar frame is fully good to go
        if datetime.now().minute in mosaicUpdateIntervals and datetime.now().second == 40:
            await TWCRadarCollector.collect("radarmosaic")

        if datetime.now().minute in satradUpdateIntervals and datetime.now().second == 45:
            await TWCRadarCollector.collect("satrad")
        
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
alertTask = loop.create_task(grabAlertsLoop())
CCtask = loop.create_task(FiveMinUpdaters())
ForecastsTask = loop.create_task(HourUpdaters())

if useRadarServer: radarTask = loop.create_task(radarCollector())

try:
    loop.run_until_complete(alertTask)
    loop.run_until_complete(CCtask)
    loop.run_until_complete(ForecastsTask)
    if useRadarServer: loop.run_until_complete(radarTask)
except asyncio.CancelledError: pass