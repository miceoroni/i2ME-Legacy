import requests
import gzip
import uuid
import os
import shutil
import xml.dom.minidom
import logging,coloredlogs
import aiohttp, aiofiles, asyncio, asyncio

import sys
sys.path.append("./py2lib")
sys.path.append("./Util")
sys.path.append("./records")
import bit
import MachineProductCfg as MPC
import LFRecord as LFR

l = logging.getLogger(__name__)
coloredlogs.install()

tecciId = []
zipCodes = []

# Auto-grab the tecci and zip codes
for i in MPC.getPrimaryLocations():
    tecciId.append(LFR.getCoopId(i))
    zipCodes.append(LFR.getZip(i))

for i in MPC.getMetroCities():
    tecciId.append(LFR.getCoopId(i))
    zipCodes.append(LFR.getZip(i))


apiKey = '21d8a80b3d6b444998a80b3d6b1449d3'

async def getData(tecci, zipCode):
    l.debug('Gathering data for location id ' + tecci)
    fetchUrl = 'https://api.weather.com/v1/location/' + zipCode + ':4:US/forecast/hourly/360hour.xml?language=en-US&units=e&apiKey=' + apiKey
    data = ""

    #Fetch data
    async with aiohttp.ClientSession() as s:
        async with s.get(fetchUrl) as r:
            data = await r.text()

    newData = data[48:-11]
    
    #Write to .i2m file
    i2Doc = '<HourlyForecast id="000000000" locationKey="' + str(tecci) + '" isWxscan="0">' + '' + newData + '<clientKey>' + str(tecci) + '</clientKey></HourlyForecast>'

    async with aiofiles.open('./.temp/HourlyForecast.i2m', 'a') as f:
        await f.write(i2Doc)
        await f.close()


async def makeDataFile():
    loop = asyncio.get_running_loop()
    l.info("Writing an HourlyForecast record.")
    header = '<Data type="HourlyForecast">'
    footer = '</Data>'

    async with aiofiles.open("./.temp/HourlyForecast.i2m", 'w') as doc:
        await doc.write(header)

    
    for x, y in zip(tecciId, zipCodes):
        await getData(x, y)
        
    async with aiofiles.open("./.temp/HourlyForecast.i2m", 'a') as end:
        await end.write(footer)


    dom = xml.dom.minidom.parse("./.temp/HourlyForecast.i2m")
    pretty_xml_as_string = dom.toprettyxml(indent = "  ")

    async with aiofiles.open("./.temp/HourlyForecast.i2m", "w") as g:
        await g.write(pretty_xml_as_string[23:])
        await g.close()

    files = []
    commands = []
    with open("./.temp/HourlyForecast.i2m", 'rb') as f_in:
        with gzip.open("./.temp/HourlyForecast.gz", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    gZipFile = "./.temp/HourlyForecast.gz"

    files.append(gZipFile)
    command = commands.append('<MSG><Exec workRequest="storeData(File={0},QGROUP=__HourlyForecast__,Feed=HourlyForecast)" /><GzipCompressedMsg fname="HourlyForecast" /></MSG>')
    numFiles = len(files)

    await loop.run_in_executor(None, bit.sendFile(files, commands, numFiles, 0))

    os.remove("./.temp/HourlyForecast.i2m")
    os.remove("./.temp/HourlyForecast.gz")