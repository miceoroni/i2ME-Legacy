import asyncio
import collections
from genericpath import exists
import gzip
from multiprocessing import Pool
import aiohttp
import json
import time as epochTime
import requests
import logging,coloredlogs

from os import path, mkdir, listdir, remove, cpu_count
from shutil import rmtree
from PIL import Image as PILImage
from wand.image import Image as wandImage
from wand.color import Color


radarType = "Radar-US"

l = logging.getLogger(__name__)
coloredlogs.install()

upperLeftX,upperLeftY,lowerRightX,lowerRightY = 0,0,0,0
xStart,xEnd,yStart,yEnd = 0,0,0,0
imgW = 0
imgH = 0

import sys
sys.path.append("./py2lib")
sys.path.append("./radar")
from RadarProcessor import *
import bit

async def getValidTimestamps(boundaries:ImageBoundaries) -> list:
    """Gets all valid UNIX timestamps for the TWCRadarMosaic product """
    l.info("Getting timestamps for the radar..")
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
                        l.debug(f"Ignoring {time} -- Not at the correct frame interval.")
                        continue

                    # Don't add frames that are expired
                    if (time < (datetime.utcnow().timestamp() - epochTime.time()) / 1000 - boundaries.Expiration):
                        l.debug(f"Ignoring {time} -- Expired.")
                        continue

                    times.append(time)

    return times

def downloadRadarTile(url, p, fn):
    img = requests.get(url, stream=True)
    ts = fn.split("_")[0]
    download = True
    
    # Make the path if it doesn't exist
    if exists(f"./.temp/tiles/output/{ts}.tiff"):
        l.debug("Not downloading tiles for timestamp " + str(ts) + " since a frame for it already exists." )
        download = False
    if not path.exists(p):
        mkdir(p)
        l.debug(f"Download {ts}")
    if exists(f"{p}/{fn}"): 
        l.debug(f"Not downloading new tiles for {ts} as they already exist.")
        download = False

    if (img.status_code == 200 and download):
        with open(f'{p}/{fn}', 'wb') as tile:
            for data in img:
                tile.write(data)
    elif (img.status_code != 200):
        l.error("ERROR DOWNLOADING " + p + "\nSTATUS CODE " + str(img.status_code))
    elif (download == False):
        pass



def getImageBoundaries() -> ImageBoundaries:
    """ Gets the image boundaries for the specified radar definition """
    with open('radar/ImageSequenceDefs.json', 'r') as f:
        ImageSequenceDefs = json.loads(f.read())
  
    seqDef = ImageSequenceDefs['ImageSequenceDefs'][radarType]

    return ImageBoundaries(
        LowerLeftLong = seqDef['LowerLeftLong'],
        LowerLeftLat= seqDef['LowerLeftLat'],
        UpperRightLong= seqDef['UpperRightLong'],
        UpperRightLat= seqDef['UpperRightLat'],
        VerticalAdjustment= seqDef['VerticalAdjustment'],
        OGImgW= seqDef['OriginalImageWidth'],
        OGImgH= seqDef['OriginalImageHeight'],
        ImagesInterval= seqDef['ImagesInterval'],
        Expiration= seqDef['Expiration']
    )

def CalculateBounds(upperRight:LatLong, lowerLeft:LatLong, upperLeft:LatLong, lowerRight: LatLong):
    """ Calculates the image bounds for radar stitching & tile downloading """
    upperRightTile:Point = WorldCoordinateToTile(LatLongProject(upperRight.x, upperRight.y))
    lowerLeftTile:Point = WorldCoordinateToTile(LatLongProject(lowerLeft.x, lowerLeft.y))
    upperLeftTile:Point = WorldCoordinateToTile(LatLongProject(upperLeft.x, upperLeft.y))
    lowerRightTile:Point = WorldCoordinateToTile(LatLongProject(lowerRight.x,lowerRight.y))

    upperLeftPx:Point = WorldCoordinateToPixel(LatLongProject(upperLeft.x, upperLeft.y))
    lowerRightPx:Point = WorldCoordinateToPixel(LatLongProject(lowerRight.x,lowerRight.y))

    global upperLeftX,upperLeftY,lowerRightX,lowerRightY
    global xStart,xEnd,yStart,yEnd
    global imgW,imgH

    upperLeftX = upperLeftPx.x - upperLeftTile.x * 256
    upperLeftY = upperLeftPx.y - upperLeftTile.y * 256
    lowerRightX = lowerRightPx.x - upperLeftTile.x * 256
    lowerRightY = lowerRightPx.y - upperLeftTile.y * 256

    # Set the xStart, xEnd, yStart, and yEnd positions so we can download tiles that are within the tile coordinate regions
    xStart = int(upperLeftTile.x)
    xEnd = int(upperRightTile.x)
    yStart = int(upperLeftTile.y)
    yEnd = int(lowerLeftTile.y)

    # Set the image width & height based off the x and y tile amounts

    # These should amount to the amount of tiles needed to be downloaded
    # for both the x and y coordinates.
    xTiles:int = xEnd - xStart
    yTiles:int = yEnd - yStart

    imgW = 256 * (xTiles + 1)
    imgH = 256 * (yTiles + 1)
    print(f"{imgW} x {imgH}")

def convertPaletteToWXPro(filepath:str):
    """ Converts the color palette of a radar frame to one acceptable to the i2 """
    img = wandImage(filename = filepath)

    
    rainColors = [
        Color('rgb(64,204,85'), # lightest green
        Color('rgb(0,153,0'), # med green
        Color('rgb(0,102,0)'), # darkest green
        Color('rgb(191,204,85)'), # yellow
        Color('rgb(191,153,0)'), # orange
        Color('rgb(255,51,0)'), # ...
        Color('rgb(191,51,0)'), # red
        Color('rgb(64,0,0)') # dark red
    ]

    mixColors = [
        Color('rgb(253,130,215)'), # light purple
        Color('rgb(208,94,176)'), # ...
        Color('rgb(190,70,150)'), # ...
        Color('rgb(170,50,130)') # dark purple
    ]

    snowColors = [
        Color('rgb(150,150,150)'), # dark grey
        Color('rgb(180,180,180)'), # light grey
        Color('rgb(210,210,210)'), # grey
        Color('rgb(230,230,230)') # white
    ]

    # Replace rain colors
    img.opaque_paint(Color('rgb(99, 235, 99)'), rainColors[0], 7000.0)
    img.opaque_paint(Color('rgb(28,158,52)'), rainColors[1], 7000.0)
    img.opaque_paint(Color('rgb(0, 63, 0)'), rainColors[2], 7000.0)

    img.opaque_paint(Color('rgb(251,235,2)'), rainColors[3], 7000.0)
    img.opaque_paint(Color('rgb(238, 109, 2)'), rainColors[4], 7000.0)
    img.opaque_paint(Color('rgb(210,11,6)'), rainColors[5], 7000.0)
    img.opaque_paint(Color('rgb(169,5,3)'), rainColors[6], 7000.0)
    img.opaque_paint(Color('rgb(128,0,0)'), rainColors[7], 7000.0)

    # Replace mix colors
    img.opaque_paint(Color('rgb(255,160,207)'), mixColors[0], 7000.0)
    img.opaque_paint(Color('rgb(217,110,163)'), mixColors[1], 7000.0)
    img.opaque_paint(Color('rgb(192,77,134)'), mixColors[2], 7000.0)
    img.opaque_paint(Color('rgb(174,51,112)'), mixColors[3], 7000.0)
    img.opaque_paint(Color('rgb(146,13,79)'), mixColors[3], 7000.0)

    # Replace snow colors
    img.opaque_paint(Color('rgb(138,248,255)'), snowColors[0], 7000.0)
    img.opaque_paint(Color('rgb(110,203,212)'), snowColors[1], 7000.0)
    img.opaque_paint(Color('rgb(82,159,170)'), snowColors[2], 7000.0)
    img.opaque_paint(Color('rgb(40,93,106)'), snowColors[3], 7000.0)
    img.opaque_paint(Color('rgb(13,49,64)'), snowColors[3]), 7000.0

    img.compression = 'lzw'
    img.save(filename=filepath)



def getTime(timestamp) -> str:
    time:datetime = datetime.utcfromtimestamp(timestamp).strftime("%m/%d/%Y %H:%M:%S")
        
    return str(time)


async def makeRadarImages():
    """ Creates proper radar frames for the i2 """
    l.info("Downloading frames for the Regional Radar...")
    
    combinedCoordinates = []

    boundaries = getImageBoundaries()
    upperRight:LatLong = boundaries.GetUpperRight()
    lowerLeft:LatLong = boundaries.GetLowerLeft()
    upperLeft:LatLong = boundaries.GetUpperLeft()
    lowerRight:LatLong = boundaries.GetLowerRight()

    CalculateBounds(upperRight, lowerLeft, upperLeft, lowerRight)
    times = await getValidTimestamps(boundaries)

    # Get rid of invalid radar frames 
    for i in listdir('./.temp/tiles/output'):
        if i.split('.')[0] not in [str(x) for x in times] and i != "Thumbs.db":
            l.debug(f"Deleting {i} as it is no longer valid.")
            remove("./.temp/tiles/output/" + i)
    
    # Collect coordinates for the frame tiles
    for y in range(yStart, yEnd):
        if y <= yEnd:
            for x in range(xStart, xEnd):
                if x <= xEnd:
                    combinedCoordinates.append(Point(x,y))

    # Create urls, paths, and filenames to download tiles for.
    urls = []
    paths = []
    filenames = []
    for i in range(0, len(times)):
        for c in range(0, len(combinedCoordinates)):
            if not exists(f'./.temp/tiles/output/{times[i]}.tiff'):
                urls.append(f"https://api.weather.com/v3/TileServer/tile?product=twcRadarMosaic&ts={str(times[i])}&xyz={combinedCoordinates[c].x}:{combinedCoordinates[c].y}:6&apiKey=21d8a80b3d6b444998a80b3d6b1449d3")
                paths.append(f"./.temp/tiles/{times[i]}")
                filenames.append(f"{times[i]}_{combinedCoordinates[c].x}_{combinedCoordinates[c].y}.png")

    l.debug(len(urls))
    if len(urls) != 0 and len(urls) >= 6:
        with Pool(cpu_count() - 1) as p:
            p.starmap(downloadRadarTile, zip(urls, paths, filenames))
            p.close()
            p.join()
    elif len(urls) < 6 and len(urls) != 0:     # We don't need to run more threads than we need to, that's how we get halted.
        with Pool(len(urls)) as p:
            p.starmap(downloadRadarTile, zip(urls, paths, filenames))
            p.close()
            p.join()
    elif len(urls) == 0:
        l.info("No new radar frames need to be downloaded.")
        return

    # Stitch them all together!

    imgsToGenerate = []
    framesToComposite = []
    finished = []
    files = []

    for t in times:
        imgsToGenerate.append(PILImage.new("RGB", (imgW, imgH)))

    # Stitch the frames together
    for i in range(0, len(imgsToGenerate)):
        if not exists(F"./.temp/tiles/output/{times[i]}.tiff"):
            l.debug(f"Generate frame for {times[i]}")
            for c in combinedCoordinates:
                path = f"./.temp/tiles/{times[i]}/{times[i]}_{c.x}_{c.y}.png"

                xPlacement = (c.x - xStart) * 256
                yPlacement = (c.y - yStart) * 256

                placeTile = PILImage.open(path)

                imgsToGenerate[i].paste(placeTile, (xPlacement, yPlacement))
            
            # Don't render it with an alpha channel
            imgsToGenerate[i].save(f"./.temp/tiles/output/{times[i]}.tiff", compression = 'tiff_lzw')
            framesToComposite.append(f"./.temp/tiles/output/{times[i]}.tiff") # Store the path so we can composite it using WAND and PIL

            # Remove the tileset as we don't need it anymore!
            rmtree(f'./.temp/tiles/{times[i]}')

    # Composite images for the i2
    imgsProcessed = 0 
    for img in framesToComposite:
        imgsProcessed += 1
        l.debug("Attempting to composite " + img)
        l.info(f"Processing radar frame {imgsProcessed} / 36")

        # Crop the radar images something that the i2 will actually take
        img_raw = wandImage(filename=img)
        img_raw.crop(upperLeftX, upperLeftY, width = int(lowerRightX - upperLeftX), height = int(lowerRightY - upperLeftY))
        img_raw.compression = 'lzw'
        img_raw.save(filename=img)
        
        # Resize using PIL
        imgPIL = PILImage.open(img)
        imgPIL = imgPIL.resize((boundaries.OGImgW, boundaries.OGImgH), 0)
        imgPIL.save(img)

        convertPaletteToWXPro(img)

        finished.append(img)

    commands = []
    # Send them all to the i2!
    for i in range(0, len(finished)):
        commands.append( '<MSG><Exec workRequest="storePriorityImage(FileExtension=.tiff,File={0},Location=US,ImageType=Radar,IssueTime=' + getTime(times[i]) + ')"/></MSG>' )
        # print(file + "\n" + command)
        
        bit.sendFile([finished[i]], [commands[i]], 1, 0)

    l.info("Downloaded and sent Regional Radar frames!")



# print(getTime(1665880800))


if __name__ == "__main__":
    asyncio.run(makeRadarImages())
