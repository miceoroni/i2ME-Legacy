import asyncio
from genericpath import exists
import gzip
from lib2to3.pytree import convert
from tkinter.filedialog import Open
import aiohttp
import aiofiles
import json
import time as epochTime
from RadarProcessor import *
from os import path, mkdir, listdir, remove
from shutil import copyfile, rmtree, copyfileobj
from PIL import Image as PILImage
from wand.image import Image as wandImage
from wand.display import display
from wand.drawing import Drawing
from wand.color import Color


radarType = "Radar-US"

upperLeftX,upperLeftY,lowerRightX,lowerRightY = 0,0,0,0
xStart,xEnd,yStart,yEnd = 0,0,0,0
imgW = 0
imgH = 0

import sys
sys.path.append("./py2lib")
import bit

async def getValidTimestamps(boundaries:ImageBoundaries) -> list:
    """Gets all valid UNIX timestamps for the TWCRadarMosaic product """

    times = []

    async with aiohttp.ClientSession() as session:
        url = "https://api.weather.com/v3/TileServer/series/productSet?apiKey=21d8a80b3d6b444998a80b3d6b1449d3&filter=twcRadarMosaic"
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
                

async def downloadRadarTile(x, y, timestamp):
    """ Downloads the specified radar tile matching the timestamp, x, and y coordinates. """
    # Make the directory for the tile to sit in.
    if not path.exists('tiles/' + str(timestamp)):
        mkdir('tiles/' + str(timestamp)) 

    async with aiohttp.ClientSession() as session:
        url = f"https://api.weather.com/v3/TileServer/tile?product=twcRadarMosaic&ts={str(timestamp)}&xyz={x}:{y}:6&apiKey=21d8a80b3d6b444998a80b3d6b1449d3"

        if not path.exists(f'tiles/{timestamp}/{timestamp}_{x}_{y}.png'):
            async with session.get(url) as r:
                data = await r.read()

                async with aiofiles.open(f'tiles/{timestamp}/{timestamp}_{x}_{y}.png', 'wb') as f:
                    await f.write(data)
                    await f.close()
                    

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
    img.opaque_paint(Color('rgb(255,160,207)'), mixColors[0], 100.0)
    img.opaque_paint(Color('rgb(217,110,163)'), mixColors[1], 100.0)
    img.opaque_paint(Color('rgb(192,77,134)'), mixColors[2], 100.0)
    img.opaque_paint(Color('rgb(174,51,112)'), mixColors[3], 100.0)
    img.opaque_paint(Color('rgb(146,13,79)'), mixColors[3], 100.0)

    # Replace snow colors
    img.opaque_paint(Color('rgb(138,248,255)'), snowColors[0], 7000.0)
    img.opaque_paint(Color('rgb(110,203,212)'), snowColors[1], 7000.0)
    img.opaque_paint(Color('rgb(82,159,170)'), snowColors[2], 7000.0)
    img.opaque_paint(Color('rgb(40,93,106)'), snowColors[3], 7000.0)
    img.opaque_paint(Color('rgb(13,49,64)'), snowColors[3]), 7000.0

    img.format = 'tiff'
    img.background_color = Color('black')
    img.alpha_channel = 'remove'
    img.compression = 'lzw'
    img.save(filename=filepath.replace('png', 'tiff'))
    remove(filepath) 



def getTime(timestamp) -> str:
    time:datetime = datetime.utcfromtimestamp(timestamp).strftime("%m/%d/%Y %H:%M:%S")
        
    return str(time)


async def makeRadarImages():
    """ Creates proper radar frames for the i2 """
    
    combinedCoordinates = []

    boundaries = getImageBoundaries()
    upperRight:LatLong = boundaries.GetUpperRight()
    lowerLeft:LatLong = boundaries.GetLowerLeft()
    upperLeft:LatLong = boundaries.GetUpperLeft()
    lowerRight:LatLong = boundaries.GetLowerRight()

    CalculateBounds(upperRight, lowerLeft, upperLeft, lowerRight)
    times = await getValidTimestamps(boundaries)

    # # Get rid of invalid tiles
    # for i in range(0, len(listdir('tiles/'))):
    #     dir = listdir('tiles/')[i]

    #     if int(dir) not in times and int(dir) != "output":
    #         print("Clearing invalid timestamp " + dir)
    #         rmtree('tiles/' + dir)

    # # Get rid of invalid radar frames 
    # for i in range(0, len(listdir('tiles/output'))):
    #     frame = listdir('titles/output')[i]
    #     if frame not in str(times): remove('tiles/output/' + frame)
    

    for t in range(0, len(times)):
        print("Downloading tiles for timestamp " + str(times[t]) + f" (#{t})")

        # Download all needed radar tiles to make 1 frame
        for y in range(yStart, yEnd):
            if y <= yEnd:
                for x in range(xStart, xEnd):
                    if x <= xEnd:
                        await downloadRadarTile(x, y + 1, times[t])

                        combinedCoordinates.append(Point(x,y + 1))

    # Stitch them all together!

    imgsToGenerate = []
    finishedImages = []
    files = []

    for t in times:
        imgsToGenerate.append(PILImage.new("RGBA", (imgW, imgH)))


    for i in range(0, len(imgsToGenerate)):
        if not exists(F"tiles/output/{times[i]}.png"):
            print(f"GENERATE {times[i]}.png")
            for c in combinedCoordinates:
                path = f"tiles/{times[i]}/{times[i]}_{c.x}_{c.y}.png"

                xPlacement = (c.x - xStart) * 256
                yPlacement = (c.y - yStart) * 256

                placeTile = PILImage.open(path)

                imgsToGenerate[i].paste(placeTile, (xPlacement, yPlacement))
            
            imgsToGenerate[i].save(f"tiles/output/{times[i]}.png")
        finishedImages.append(f"tiles/output/{times[i]}.png") # Store the path so we can composite it using WAND and PIL

    # Composite images so that the i2 will take them without a fuss
    for img in finishedImages:
        print("Attempting to composite " + img)

        # Crop the radar images something that the i2 will actually take
        img_raw = wandImage(filename=img)

        # print(upperLeftX, upperLeftY, int(lowerRightX - upperLeftX), int(lowerRightY - upperLeftY))
        img_raw.crop(upperLeftX, upperLeftY, int(lowerRightX - upperLeftX), int(lowerRightY - upperLeftY))
        # img_raw.resize(boundaries.OGImgW, boundaries.OGImgH, 'box', 0)
        # img_raw.transform(f'{boundaries.OGImgW}x{boundaries.OGImgH}')
        img_raw.save(filename=img)
        
        imgPIL = PILImage.open(img)
        imgPIL = imgPIL.resize((boundaries.OGImgW, boundaries.OGImgH), 0)
        imgPIL.save(img)

        convertPaletteToWXPro(img)

    commands = []
    # Send them all to the i2!
    for img in range(0, len(finishedImages)):
        files = []
        commands = []
        
        files.append( f'tiles/output/{times[i]}.tiff' )
        commands.append( '<MSG><Exec workRequest="storePriorityImage(FileExtension=.tiff,File={0},Location=US,ImageType=Radar,IssueTime=' + getTime(times[img]) + ')"/></MSG>' )
        # print(file + "\n" + command)
        
        bit.sendFile(files, commands, 1, 0)
        
        commands.pop(0)
        files.pop(0)



# print(getTime(1665880800))


loop = asyncio.get_event_loop()

radarTask = loop.create_task(makeRadarImages())

try:
    loop.run_until_complete(radarTask)
except asyncio.CancelledError: pass