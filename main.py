import asyncio
from asyncio.log import logger
from asyncore import loop
import logging,coloredlogs
from radar import TWCRadarCollector
import os
from datetime import datetime
import RecordTasks

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

async def main():
    alertsTask = asyncio.create_task(RecordTasks.alertsTask())
    coTask = asyncio.create_task(RecordTasks.coTask())
    hfTask = asyncio.create_task(RecordTasks.hfTask())
    dfTask = asyncio.create_task(RecordTasks.dfTask())

    # In theory, these should all run concurrently without problems
    await alertsTask
    await coTask
    await hfTask
    await dfTask

if __name__ == "__main__":
    asyncio.run(main())