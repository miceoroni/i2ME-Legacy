import requests
import sys
import gzip
import uuid
import os
import shutil
import xml.dom.minidom

sys.path.append("./py2lib")
sys.path.append("./Util")
sys.path.append("./records")
import bit
import MachineProductCfg as MPC
import LFRecord as LFR


pollenIds = []
geocodes = []


# Auto-grab the tecci and zip codes
for i in MPC.getPrimaryLocations():
    pollenIds.append(LFR.getPollenInfo(i))
    geocodes.append(LFR.getLatLong(i).replace('/', ','))

print(pollenIds, geocodes)

apiKey = '21d8a80b3d6b444998a80b3d6b1449d3'

def getData(pollenId, geocode):
    fetchUrl = f"https://api.weather.com/v2/indices/pollen/daypart/7day?geocode={geocode}&language=en-US&format=xml&apiKey={apiKey}"

    #Fetch data

    response = requests.get(fetchUrl) 

    data = response.text

    newData = data[63:-26]
    
    print('[POLLEN FORECAST] Gathering data for location id ' + pollenId)
    #Write to .i2m file
    i2Doc = '<PollenForecast id="000000000" locationKey="' + str(pollenId) + '" isWxscan="0">' + '' + newData + '<clientKey>' + str(pollenId) + '</clientKey></PollenForecast>'

    f = open("D:\\PollenForecast.i2m", "a")
    f.write(i2Doc)
    f.close()


def makeDataFile():
    header = '<Data type="PollenForecast">'
    footer = '</Data>'

    with open("D:\\PollenForecast.i2m", 'w') as doc:
        doc.write(header)

    for x, y in zip(pollenIds, geocodes):
        getData(x, y)
        
    with open("D:\\PollenForecast.i2m", 'a') as end:
        end.write(footer)


    dom = xml.dom.minidom.parse("D:\\PollenForecast.i2m")
    pretty_xml_as_string = dom.toprettyxml(indent = "  ")

    with open("D:\\PollenForecast.i2m", "w") as g:
        g.write(pretty_xml_as_string[23:])
        g.close()

    files = []
    commands = []
    with open("D:\\PollenForecast.i2m", 'rb') as f_in:
        with gzip.open("D:\\PollenForecast.gz", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    gZipFile = "D:\\PollenForecast.gz"

    files.append(gZipFile)
    command = commands.append('<MSG><Exec workRequest="storeData(File={0},QGROUP=__PollenForecast__,Feed=PollenForecast)" /><GzipCompressedMsg fname="PollenForecast" /></MSG>')
    numFiles = len(files)

    bit.sendFile(files, commands, numFiles, 0)

    os.remove("D:\\PollenForecast.i2m")
    os.remove("D:\\PollenForecast.gz")