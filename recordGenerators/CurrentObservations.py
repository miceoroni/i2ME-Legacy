import requests
import py2Lib.bit as bit
import gzip
import uuid
import os
import shutil
import xml.dom.minidom
import logging,coloredlogs
import aiofiles
import aiohttp

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
    tecciId.append("T" + LFR.getCoopId(i))
    zipCodes.append(LFR.getZip(i))

# Obtain metro map city TECCI and zips:
for i in MPC.getMetroCities():
    tecciId.append("T" + LFR.getCoopId(i))
    zipCodes.append(LFR.getZip(i))


apiKey = '21d8a80b3d6b444998a80b3d6b1449d3'

async def getData(tecci, zipCode):
    l.debug('Gathering data for location id ' + tecci)
    fetchUrl = 'https://api.weather.com/v1/location/' + zipCode + ':4:US/observations/current.xml?language=en-US&units=e&apiKey=' + apiKey
    data = ""

    async with aiohttp.ClientSession() as s:
        async with s.get(fetchUrl) as r:
            data = await r.text()

    newData = data[67:-30]

    #Write to .i2m file
    i2Doc = '<CurrentObservations id="000000000" locationKey="' + str(tecci) + '" isWxscan="0">' + '' + newData + '<clientKey>' + str(tecci) + '</clientKey></CurrentObservations>'
    async with aiofiles.open("./.temp/CurrentObservations.i2m", 'a') as f:
        await f.write(i2Doc)
        await f.close()


async def makeDataFile():
    l.info("Writing a CurrentObservations record.")
    header = '<Data type="CurrentObservations">'
    footer = '</Data>'

    async with aiofiles.open("./.temp/CurrentObservations.i2m", 'w') as doc:
        await doc.write(header)

    for x, y in zip(tecciId, zipCodes):
        await getData(x, y)
        
    async with aiofiles.open("./.temp/CurrentObservations.i2m", 'a') as end:
        await end.write(footer)

    dom = xml.dom.minidom.parse("./.temp/CurrentObservations.i2m")
    pretty_xml_as_string = dom.toprettyxml(indent = "  ")

    async with aiofiles.open("./.temp/CurrentObservations.i2m", "w") as g:
        await g.write(pretty_xml_as_string[23:])
        await g.close()

    files = []
    commands = []

    """
        TODO: This can be ran in a seperate thread using loop.run_in_executor() according to the python discord.
        ! This should probably be implemented ASAP.
    """
    with open("./.temp/CurrentObservations.i2m", 'rb') as f_in:
        with gzip.open("./.temp/CurrentObservations.gz", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    gZipFile = "./.temp/CurrentObservations.gz"

    files.append(gZipFile)
    command = commands.append('<MSG><Exec workRequest="storeData(File={0},QGROUP=__CurrentObservations__,Feed=CurrentObservations)" /><GzipCompressedMsg fname="CurrentObservations" /></MSG>')
    numFiles = len(files)

    bit.sendFile(files, commands, numFiles, 0)

    os.remove("./.temp/CurrentObservations.i2m")
    os.remove("./.temp/CurrentObservations.gz")
