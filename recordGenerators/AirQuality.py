import requests
import gzip
import os
import shutil
import xml.dom.minidom

import sys
sys.path.append("./py2lib")
sys.path.append("./Util")
sys.path.append("./records")
import bit
import MachineProductCfg as MPC
import LFRecord as LFR

locationIds = []
zipCodes = []
epaIds = []

for i in MPC.getPrimaryLocations():
    locationIds.append(LFR.getCoopId(i))
    zipCodes.append(LFR.getZip(i))
    epaIds.append(LFR.getEpaId(i))

apiKey = '21d8a80b3d6b444998a80b3d6b1449d3'

def getData(epaId, zipcode):
    url = f"https://api.weather.com/v1/location/{zipcode}:4:US/airquality.xml?language=en-US&apiKey={apiKey}"

    res = requests.get(url=url)

    data = res.text
    newData = data[57:-11]

    # Write to i2doc file
    i2Doc = f'<AirQuality id="000000000" locationKey="{epaId}" isWxScan=0>' + '' + newData + f'<clientKey="{epaId}"></AirQuality>' 

    f = open("D:\\AirQuality.xml", 'a')
    f.write(i2Doc)
    f.close()

def writeData():

    # Check to see if we even have EPA ids, as some areas don't have air quality reports
    if (epaIds != None or epaIds != ['']):
        header = '<Data type="AirQuality">'
        footer = "</Data>"

        with open("D:\\AirQuality.i2m", 'w') as doc:
            doc.write(header)

        for (x, y) in zip(epaIds, zipCodes):
            getData(x, y)

        with open("D:\\AirQuality.i2m", 'a') as end:
            end.write(footer)

        dom = xml.dom.minidom.parse("D:\\AirQuality.i2m")
        xml = dom.toprettyxml(indent = "  ")

        with open("D:\\AirQuality.i2m", 'w') as g:
            g.write(xml)
            g.close()

        files = []
        commands = []
        with open("D:\\AirQuality.i2m", 'rb') as f_in:
            with gzip.open("D:\\AirQuality.xml", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        gZipFile = "D:\\AirQuality.gz"

        files.append(gZipFile)
        comand = commands.append('<MSG><Exec workRequest="storeData(File={0},QGROUP=__AirQuality__,Feed=AirQuality)" /><GzipCompressedMsg fname="AirQuality" /></MSG>')
        numFiles = len(files)

        bit.sendFile(files, commands, numFiles, 0)

        os.remove("D:\\AirQuality.i2m")
        os.remove("D:\\AirQuality.gz")
    else:
        print("Ignoring AirQuality data collection -- No epaIds for primary locations.")


    