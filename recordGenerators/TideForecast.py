import shutil
from xmlrpc.client import DateTime
import requests
import logging,coloredlogs
import datetime
from py2Lib import bit
import Util.MachineProductCfg as MPC
import records.LFRecord as LFR
import gzip
from os import remove
import xml.dom.minidom

l = logging.getLogger(__name__)
coloredlogs.install()

geocodes = []
tideStations = []

for i in MPC.getTideStations():
    tideStations.append(i)
    geocodes.append(LFR.getLatLong(i))

apiKey = "21d8a80b3d6b444998a80b3d6b1449d3"

def getData(tideStation, geocode):
    today = datetime.date.today()
    startDate = today.strftime('%Y%m%d')
    endDate_unformatted = datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=5)
    endDate = endDate_unformatted.strftime('%Y%m%d')

    fetchUrl = f"https://api.weather.com/v1/geocode/{geocode}/forecast/tides.xml?language=en-US&units=e&startDate={startDate}&endDate={endDate}&apiKey={apiKey}"

    res = requests.get(fetchUrl)

    if res.status_code != 200:
        l.error("DO NOT REPORT THE ERROR BELOW")
        l.error(f"Failed to write TidesForecast record -- Status code {res.status_code}")
        return
    
    data = res.text
    newData = data[53:-16]

    i2Doc = f'\n  <TidesForecast id="000000000" locationKey="{tideStation}" isWxScan="0">\n    {newData}\n    <clientKey>{tideStation}</clientKey>\n </TidesForecast>'

    f = open('./.temp/TidesForecast.i2m', 'a')
    f.write(i2Doc)
    f.close()

def makeRecord():
    if len(tideStations) < 1:
        l.debug("Skipping TidesForecast -- No locations.")
        return

    l.info("Writing TidesForecast record.")

    header = '<Data type="TidesForecast">'
    footer = '</Data>'

    with open('./.temp/TidesForecast.i2m', 'a') as doc:
        doc.write(header)

    for (x, y) in zip(tideStations, geocodes):
        getData(x,y)

    with open('./.temp/TidesForecast.i2m', 'a') as end:
        end.write(footer)

    dom = xml.dom.minidom.parse('./.temp/TidesForecast.i2m')
    xmlPretty = dom.toprettyxml(indent= "  ")

    with open('./.temp/TidesForecast.i2m', 'w') as g:
        g.write(xmlPretty[23:])
        g.close()

    
    # Compresss i2m to gzip
    with open ('./.temp/TidesForecast.i2m', 'rb') as f_in:
        with gzip.open('./.temp/TidesForecast.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    file = "./.temp/TidesForecast.gz"
    command = '<MSG><Exec workRequest="storeData(File={0},QGROUP=__TidesForecast__,Feed=TidesForecast)" /><GzipCompressedMsg fname="TidesForecast" /></MSG>'

    bit.sendFile([file], [command], 1, 0)

    remove('./.temp/TidesForecast.i2m')
    remove('./.temp/TidesForecast.gz')