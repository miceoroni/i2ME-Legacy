import requests
import sys
import gzip
import uuid
import os
import shutil
import xml.dom.minidom
import logging,coloredlogs

sys.path.append("./py2lib")
sys.path.append("./Util")
sys.path.append("./records")
import bit
import MachineProductCfg as MPC
import LFRecord as LFR

l = logging.getLogger(__name__)
coloredlogs.install()

coopIds = []
geocodes = []


# Auto-grab the tecci and zip codes
for i in MPC.getPrimaryLocations():
    coopIds.append(LFR.getCoopId(i))
    geocodes.append(LFR.getLatLong(i).replace('/', ','))

print(coopIds, geocodes)

apiKey = '21d8a80b3d6b444998a80b3d6b1449d3'

def getData(coopId, geocode):
    fetchUrl = f"https://api.weather.com/v2/indices/breathing/daypart/7day?geocode={geocode}&language=en-US&format=xml&apiKey={apiKey}"

    #Fetch data

    response = requests.get(fetchUrl) 

    data = response.text

    newData = data[63:-26]
    
    l.debug('Gathering data for location id ' + coopId)
    #Write to .i2m file
    i2Doc = '<Breathing id="000000000" locationKey="' + str(coopId) + '" isWxscan="0">' + '' + newData + '<clientKey>' + str(coopId) + '</clientKey></Breathing>'

    f = open("./.temp/Breathing.i2m", "a")
    f.write(i2Doc)
    f.close()


def makeDataFile():
    l.info("Writing a Breathing forecast record.")
    header = '<Data type="Breathing">'
    footer = '</Data>'

    with open("./.temp/Breathing.i2m", 'w') as doc:
        doc.write(header)

    for x, y in zip(coopIds, geocodes):
        getData(x, y)
        
    with open("./.temp/Breathing.i2m", 'a') as end:
        end.write(footer)


    dom = xml.dom.minidom.parse("./.temp/Breathing.i2m")
    pretty_xml_as_string = dom.toprettyxml(indent = "  ")

    with open("./.temp/Breathing.i2m", "w") as g:
        g.write(pretty_xml_as_string[23:])
        g.close()

    files = []
    commands = []
    with open("./.temp/Breathing.i2m", 'rb') as f_in:
        with gzip.open("./.temp/Breathing.gz", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    gZipFile = "./.temp/Breathing.gz"

    files.append(gZipFile)
    command = commands.append('<MSG><Exec workRequest="storeData(File={0},QGROUP=__Breathing__,Feed=Breathing)" /><GzipCompressedMsg fname="Breathing" /></MSG>')
    numFiles = len(files)

    bit.sendFile(files, commands, numFiles, 0)

    os.remove("./.temp/Breathing.i2m")
    os.remove("./.temp/Breathing.gz")