import asyncio, aiofiles
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

l.info("Starting i2RecordCollector")
l.info("Developed by mewtek32, Floppaa, Goldblaze, and needlenose")

async def createTemp():
    """ Used on a first time run, creates necessary files & directories for the message encoder to work properly. """
    if not (os.path.exists('./.temp/')):
        l.info("Creating necessary directories & files..")
        os.mkdir('./.temp')
        
        # Used for the record generator
        os.mkdir('./.temp/tiles/')
        os.mkdir('./.temp/tiles/output/')

        # Used for radar server downloads
        os.mkdir('./.temp/output')
        os.mkdir('./.temp/output/radarmosaic')
        os.mkdir('./.temp/output/satrad')

        # Create msgId file for bit.py
        async with aiofiles.open('./.temp/msgId.txt', 'w') as msgId:
            await msgId.write('410080515')
            await msgId.close()
    else:
        l.debug(".temp file exists")
        return


async def main():
    await createTemp()

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