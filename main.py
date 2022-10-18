import asyncio
import logging,coloredlogs
from recordGenerators import DailyForecast,CurrentObservations,HourlyForecast,AirQuality,AirportDelays,PollenForecast,Breathing,Alerts
from radar import TWCRadarProcessor, RadarProcessor


l = logging.getLogger(__name__)
coloredlogs.install(logger=l)


"""
CurrentConditions: Every 5 minutes
Daily Forecasts, Hourlies, etc: 60 minutes
Alerts: 5 minutes
"""
l.info("Starting i2RecordCollector")
l.info("Developed by mewtek32, Floppaa, and Goldblaze")

async def grabAlertsLoop():
    while True:
        Alerts.makeRecord()
        await asyncio.sleep(60)

async def RadarProcessingLoop():
    while True:
        await TWCRadarProcessor.makeRadarImages()
        await asyncio.sleep(30 * 60)

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
        l.debug("Sleeping for an hour...")
        await asyncio.sleep(60 * 60)

async def main():
    # Create loops
    asyncio.create_task(grabAlertsLoop())
    asyncio.create_task(FiveMinUpdaters())
    asyncio.create_task(HourUpdaters())
    asyncio.create_task(RadarProcessingLoop())

if __name__ == "__main__":
    asyncio.run(main())