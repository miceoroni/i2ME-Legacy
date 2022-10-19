import requests
import gzip
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

locationIds = []
zipCodes = []
airports = []

for i in MPC.getPrimaryLocations():
    locationIds.append(LFR.getCoopId(i))
    zipCodes.append(LFR.getZip(i))

airports = MPC.getAirportCodes()
print(airports)

apiKey = '21d8a80b3d6b444998a80b3d6b1449d3'

def getData(airport):
    url = f"https://api.weather.com/v1/airportcode/{airport}/airport/delays.xml?language=en-US&apiKey={apiKey}"

    res = requests.get(url=url)

    data = res.text
    newData = data[48:-11]

    # Write to i2doc file
    i2Doc = f'<AirportDelays id="000000000" locationKey="{airport}" isWxScan="0">' + '' + newData + f'<clientKey>{airport}</clientKey></AirportDelays>' 

    f = open("./.temp/AirportDelays.i2m", 'a')
    f.write(i2Doc)
    f.close()

def writeData():
    useData = False
    airportsWithDelays = []

    for x in airports:
        # Do a quick check to see if the airport in question has a delay or not
        res = requests.get(f"https://api.weather.com/v1/airportcode/{x}/airport/delays.xml?language=en-US&apiKey={apiKey}")

        if (res.status_code != 200):
            l.debug(f"[AIRPORT DELAYS] No delays for {x} found, skipping..")
        else:
            airportsWithDelays.append(x)
            l.debug(f"[AIRPORT DELAYS] {x} has a delay! Writing a file..")
            useData = True

    if (useData):
        l.info("Writing an AirportDelays record.")
        header = '<Data type="AirportDelays">'
        footer = "</Data>"

        with open("./.temp/AirportDelays.i2m", 'w') as doc:
            doc.write(header)

        for x in airportsWithDelays:
            getData(x)

        with open("./.temp/AirportDelays.i2m", 'a') as end:
            end.write(footer)

        dom = xml.dom.minidom.parse("./.temp/AirportDelays.i2m")
        prettyXml = dom.toprettyxml(indent="  ")

        with open("./.temp/AirportDelays.i2m", 'w') as g:
            g.write(prettyXml)
            g.close()

        files = []
        commands = []
        with open("./.temp/AirportDelays.i2m", 'rb') as f_in:
            with gzip.open("./.temp/AirportDelays.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        gZipFile = "./.temp/AirportDelays.gz"

        files.append(gZipFile)
        comand = commands.append('<MSG><Exec workRequest="storeData(File={0},QGROUP=__AirportDelays__,Feed=AirportDelays)" /><GzipCompressedMsg fname="AirportDelays" /></MSG>')
        numFiles = len(files)

        bit.sendFile(files, commands, numFiles, 0)

        os.remove("./.temp/AirportDelays.i2m")
        os.remove("./.temp/AirportDelays.gz")
    else:
        l.info("No airport delays found.")
