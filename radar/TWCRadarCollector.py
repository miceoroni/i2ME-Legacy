import asyncio
import aiohttp
import aiofiles
import logging, coloredlogs
from py2Lib import bit
from datetime import datetime
from os import path, mkdir

l = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")

async def getValidTimestamps(radarType:str) -> list:
    times = []
    maxImages = 0
    url = None
    series = None

    async with aiohttp.ClientSession() as s:
        if (radarType == "satrad"):
            maxImages = 12
            url = "https://api.weather.com/v3/TileServer/series/productSet?apiKey=21d8a80b3d6b444998a80b3d6b1449d3&filter=satrad"
            series = 'satrad'

        elif (radarType == "radarmosaic"):
            maxImages = 36
            url = "https://api.weather.com/v3/TileServer/series/productSet?apiKey=21d8a80b3d6b444998a80b3d6b1449d3&filter=twcRadarMosaic"
            series = 'twcRadarMosaic'

        else:
            l.error(f'Invalid series filter "{radarType}" -- Valid filters include "satrad", "radarmosaic"')
            return times

        async with s.get(url) as r:
            res = await r.json()

            for t in range(0, len(res['seriesInfo'][series]['series'])):
                if (t <= (maxImages - 1)):
                    time = res['seriesInfo'][series]['series'][t]['ts']
                    
                    times.append(time)

    return times

async def downloadRadarFrames(radarType:str, timestamps: list) -> list:
    url_root = None
    imagesToSend = []

    if (radarType == "satrad"):
        url_root = "https://unix.dog/~mewtek/i2-radar/satrad/"
    elif (radarType == "radarmosaic"):
        url_root = "https://unix.dog/~mewtek/i2-radar/radarmosaic/"
    else:
        l.error(f'Invalid radar type "{radarType}" -- Valid radar types include "satrad", "radarmosaic"')
        return

    async with aiohttp.ClientSession() as s:

        for ts in timestamps:
            if path.exists(f".temp/output/{radarType}/{ts}.tiff"):
                l.debug(f"{radarType}/{ts}.tiff exists, skipping.")
                continue
            
            async with s.get(url_root + f"{ts}.tiff") as r:
                l.info(f"Downloading {radarType} frame {timestamps.index(ts) + 1} / {len(timestamps)}")

                if r.status == 404:
                    l.warning(f"Failed to download {radarType}/{ts}.tiff -- Server likely has not generated this frame yet.")
                    continue

                f = await aiofiles.open(f'.temp/output/{radarType}/{ts}.tiff', mode='wb')
                await f.write(await r.read())
                await f.close()

                imagesToSend.append(f'.temp/output/{radarType}/{ts}.tiff')

    return imagesToSend


def getTime(timestamp) -> str:
    time:datetime = datetime.utcfromtimestamp(timestamp).strftime("%m/%d/%Y %H:%M:%S")
        
    return str(time)

async def collect(radarType: str):

    if radarType != "satrad" or radarType != "radarmosaic":
        l.error(f'Invalid radar type "{radarType}" -- Valid radar types include "satrad", "radarmosaic"')
        return

    ts = await getValidTimestamps(radarType)
    frames = await downloadRadarFrames(radarType, ts)

    commands = []
    for i in range(0, len(frames)):
        commands.append( '<MSG><Exec workRequest="storePriorityImage(FileExtension=.tiff,File={0},Location=US,ImageType=Radar,IssueTime=' + getTime(ts[i]) + ')"/></MSG>' )

        bit.sendFile([frames[i]], [commands[i]], 1, 0)
