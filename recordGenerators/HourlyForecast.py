import requests
import gzip
import uuid
import os
import shutil
import xml.dom.minidom
import logging,coloredlogs

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

apiKey = '21d8a80b3d6b444998a80b3d6b1449d3'

def getData(tecci, zipCode):
    fetchUrl = 'https://api.weather.com/v1/location/' + zipCode + ':4:US/forecast/hourly/360hour.xml?language=en-US&units=e&apiKey=' + apiKey

    #Fetch data

    response = requests.get(fetchUrl) 

    data = response.text

    newData = data[48:-11]
    
    l.debug('Gathering data for location id ' + tecci)
    #Write to .i2m file
    i2Doc = '<HourlyForecast id="000000000" locationKey="' + str(tecci) + '" isWxscan="0">' + '' + newData + '<clientKey>' + str(tecci) + '</clientKey></HourlyForecast>'

    f = open("./.temp/HourlyForecast.i2m", "a")
    f.write(i2Doc)
    f.close()

def makeDataFile():
    l.info("Writing an HourlyForecast record.")
    header = '<Data type="HourlyForecast">'
    footer = '</Data>'

    with open("./.temp/HourlyForecast.i2m", 'w') as doc:
        doc.write(header)

    for x, y in zip(tecciId, zipCodes):
        getData(x, y)
        
    with open("./.temp/HourlyForecast.i2m", 'a') as end:
        end.write(footer)


    dom = xml.dom.minidom.parse("./.temp/HourlyForecast.i2m")
    pretty_xml_as_string = dom.toprettyxml(indent = "  ")

    with open("./.temp/HourlyForecast.i2m", "w") as g:
        g.write(pretty_xml_as_string[23:])
        g.close()

    files = []
    commands = []
    with open("./.temp/HourlyForecast.i2m", 'rb') as f_in:
        with gzip.open("./.temp/HourlyForecast.gz", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    gZipFile = "./.temp/HourlyForecast.gz"

    files.append(gZipFile)
    command = commands.append('<MSG><Exec workRequest="storeData(File={0},QGROUP=__HourlyForecast__,Feed=HourlyForecast)" /><GzipCompressedMsg fname="HourlyForecast" /></MSG>')
    numFiles = len(files)

    bit.sendFile(files, commands, numFiles, 0)

    os.remove("./.temp/HourlyForecast.i2m")
    os.remove("./.temp/HourlyForecast.gz")