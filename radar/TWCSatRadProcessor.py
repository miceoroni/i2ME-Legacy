import asyncio
import aiohttp
import time as epochTime
import datetime
import requests
from RadarProcessor import *
from os import mkdir, path
from genericpath import exists


upperLeftX,upperLeftY,lowerRightX,lowerRightY = 0,0,0,0
xStart,xEnd,yStart,yEnd = 0,0,0,0
imgW = 0
imgH = 0

async def getValidTimestamps(boundaries:ImageBoundaries) -> list:
    """Gets all valid UNIX timestamps for the TWCRadarMosaic product """
    print("Getting timestamps for the radar..")
    times = []

    async with aiohttp.ClientSession() as session:
        url = "https://api.weather.com/v3/TileServer/series/productSet?apiKey=e1f10a1e78da46f5b10a1e78da96f525&filter=twcRadarMosaic"
        async with session.get(url) as r:
            response = await r.json()

            for t in range(0, len(response['seriesInfo']['twcRadarMosaic']['series'])):

                if (t <= 35):
                    time = response['seriesInfo']['twcRadarMosaic']['series'][t]['ts']
                    
                    # Don't add frames that aren't at the correct interval
                    if (time % boundaries.ImageInterval != 0):
                        print(f"Ignoring {time} -- Not at the correct frame interval.")
                        continue

                    # Don't add frames that are expired
                    if (time < (datetime.utcnow().timestamp() - epochTime.time()) / 1000 - boundaries.Expiration):
                        print(f"Ignoring {time} -- Expired.")
                        continue

                    times.append(time)

        return times

def downloadRadarTile(url, p, fn):
    img = requests.get(url, stream=True)
    ts = fn.split("_")[0]
    download = True
    
    # Make the path if it doesn't exist
    if exists(f"tiles/output/{ts}.tiff"):
        print("Not downloading tiles for timestamp " + str(ts) + " since a frame for it already exists." )
        download = False
    if not path.exists(p):
        mkdir(p)
        print(f"Download {ts}")
    if exists(f"{p}/{fn}"): 
        print(f"Not downloading new tiles for {ts} as they already exist.")
        download = False

    if (img.status_code == 200 and download):
        with open(f'{p}/{fn}', 'wb') as tile:
            for data in img:
                tile.write(data)
    elif (img.status_code != 200):
        print("ERROR DOWNLOADING " + p + "\nSTATUS CODE " + str(img.status_code))
    elif (download == False):
        pass

