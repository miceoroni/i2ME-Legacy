import shutil
import requests
import logging,coloredlogs
from py2Lib import bit
import Util.MachineProductCfg as MPC
import records.LFRecord as LFR
import gzip
from os import remove
import xml.dom.minidom
import aiohttp, aiofiles, asyncio

l = logging.getLogger(__name__)
coloredlogs.install()

geocodes = []
coopIds = []

for i in MPC.getPrimaryLocations():
    coopIds.append(LFR.getCoopId(i))
    geocodes.append(LFR.getLatLong(i).replace('/', ','))

apiKey = "e1f10a1e78da46f5b10a1e78da96f525"

async def getData(coopId, geocode):
    fetchUrl = f"https://api.weather.com/v2/indices/wateringNeeds/daypart/7day?geocode={geocode}&language=en-US&format=xml&apiKey={apiKey}"
    data = ""
    
    async with aiohttp.ClientSession() as s:
        async with s.get(fetchUrl) as r:
            if r.status != 200:
                l.error(f"Failed to WateringNeeds -- status code {r.status}")
                return
            
            data = await r.text()
    
    newData = data[63:-26]

    i2Doc = f'\n  <WateringNeeds id="000000000" locationKey="{coopId}" isWxScan="0">\n    {newData}\n    <clientKey>{coopId}</clientKey>\n </WateringNeeds>'

    async with aiofiles.open('./.temp/WateringNeeds.i2m', 'a') as f:
        await f.write(i2Doc)
        await f.close()

async def makeRecord():
    loop = asyncio.get_running_loop()
    l.info("Writing WateringNeeds record.")

    header = '<Data type="WateringNeeds">'
    footer = '</Data>'

    async with aiofiles.open('./.temp/WateringNeeds.i2m', 'a') as doc:
        await doc.write(header)

    for (x, y) in zip(coopIds, geocodes):
        await getData(x,y)

    async with aiofiles.open('./.temp/WateringNeeds.i2m', 'a') as end:
        await end.write(footer)

    dom = xml.dom.minidom.parse('./.temp/WateringNeeds.i2m')
    xmlPretty = dom.toprettyxml(indent= "  ")

    async with aiofiles.open('./.temp/WateringNeeds.i2m', 'w') as g:
        await g.write(xmlPretty[23:])
        await g.close()

    
    # Compresss i2m to gzip
    with open ('./.temp/WateringNeeds.i2m', 'rb') as f_in:
        with gzip.open('./.temp/WateringNeeds.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    file = "./.temp/WateringNeeds.gz"
    command = '<MSG><Exec workRequest="storeData(File={0},QGROUP=__WateringNeeds__,Feed=WateringNeeds)" /><GzipCompressedMsg fname="WateringNeeds" /></MSG>'

    bit.sendFile([file], [command], 1, 0)

    remove('./.temp/WateringNeeds.i2m')
    remove('./.temp/WateringNeeds.gz')
