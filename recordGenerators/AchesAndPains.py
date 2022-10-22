import shutil
import requests
import logging,coloredlogs
from py2Lib import bit
import Util.MachineProductCfg as MPC
import records.LFRecord as LFR
import gzip
from os import remove
import xml.dom.minidom

l = logging.getLogger(__name__)
coloredlogs.install()

geocodes = []
coopIds = []

for i in MPC.getPrimaryLocations():
    coopIds.append(LFR.getCoopId(i))
    geocodes.append(LFR.getLatLong(i).replace('/', ','))

apiKey = "21d8a80b3d6b444998a80b3d6b1449d3"

def getData(coopId, geocode):
    fetchUrl = f"https://api.weather.com/v2/indices/achePain/daypart/7day?geocode={geocode}&language=en-US&format=xml&apiKey={apiKey}"

    res = requests.get(fetchUrl)

    if res.status_code != 200:
        l.error("DO NOT REPORT THE ERROR BELOW")
        l.error(f"Failed to write AchesAndPains record -- Status code {res.status_code}")
        return
    
    data = res.text
    newData = data[63:-26]

    i2Doc = f'\n  <AchesAndPains id="000000000" locationKey="{coopId}" isWxScan="0">\n    {newData}\n    <clientKey>{coopId}</clientKey>\n </AchesAndPains>'

    f = open('./.temp/AchesAndPains.i2m', 'a')
    f.write(i2Doc)
    f.close()

def makeRecord():
    l.info("Writing AchesAndPains record.")

    header = '<Data type="AchesAndPains">'
    footer = '</Data>'

    with open('./.temp/AchesAndPains.i2m', 'a') as doc:
        doc.write(header)

    for (x, y) in zip(coopIds, geocodes):
        getData(x,y)

    with open('./.temp/AchesAndPains.i2m', 'a') as end:
        end.write(footer)

    dom = xml.dom.minidom.parse('./.temp/AchesAndPains.i2m')
    xmlPretty = dom.toprettyxml(indent= "  ")

    with open('./.temp/AchesAndPains.i2m', 'w') as g:
        g.write(xmlPretty[23:])
        g.close()

    
    # Compresss i2m to gzip
    with open ('./.temp/AchesAndPains.i2m', 'rb') as f_in:
        with gzip.open('./.temp/AchesAndPains.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    file = "./.temp/AchesAndPains.gz"
    command = '<MSG><Exec workRequest="storeData(File={0},QGROUP=__AchesAndPains__,Feed=AchesAndPains)" /><GzipCompressedMsg fname="AchesAndPains" /></MSG>'

    bit.sendFile([file], [command], 1, 0)

    remove('./.temp/AchesAndPains.i2m')
    remove('./.temp/AchesAndPains.gz')