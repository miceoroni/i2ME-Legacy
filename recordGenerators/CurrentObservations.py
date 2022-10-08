import requests
import bit
import gzip
import uuid
import os
import shutil
import xml.dom.minidom

tecciId = ['T72462058']
zipCodes = ['81242']


apiKey = '21d8a80b3d6b444998a80b3d6b1449d3'

def getData(tecci, zipCode):
    fetchUrl = 'https://api.weather.com/v1/location/' + zipCode + ':4:US/observations/current.xml?language=en-US&units=e&apiKey=' + apiKey

    #Fetch data

    response = requests.get(fetchUrl) 

    data = response.text

    newData = data[67:-30]

    print('Gathering data for location id ' + tecci)
    #Write to .i2m file
    i2Doc = '<CurrentObservations id="000000000" locationKey="' + str(tecci) + '" isWxscan="0">' + '' + newData + '<clientKey>' + str(tecci) + '</clientKey></CurrentObservations>'


    f = open("D:\\CurrentObservations.i2m", "a")
    f.write(i2Doc)
    f.close()

header = '<Data type="CurrentObservations">'
footer = '</Data>'

with open("D:\\CurrentObservations.i2m", 'w') as doc:
    doc.write(header)

for x, y in zip(tecciId, zipCodes):
    getData(x, y)
    
with open("D:\\CurrentObservations.i2m", 'a') as end:
    end.write(footer)

dom = xml.dom.minidom.parse("D:\\CurrentObservations.i2m")
pretty_xml_as_string = dom.toprettyxml(indent = "  ")

with open("D:\\CurrentObservations.i2m", "w") as g:
    g.write(pretty_xml_as_string[23:])
    g.close()

files = []
commands = []

with open("D:\\CurrentObservations.i2m", 'rb') as f_in:
    with gzip.open("D:\\CurrentObservations.gz", 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

gZipFile = "D:\\CurrentObservations.gz"

files.append(gZipFile)
command = commands.append('<MSG><Exec workRequest="storeData(File={0},QGROUP=__CurrentObservations__,Feed=CurrentObservations)" /><GzipCompressedMsg fname="CurrentObservations" /></MSG>')
numFiles = len(files)

bit.sendFile(files, commands, numFiles, 0)

os.remove("D:\\CurrentObservations.i2m")
os.remove("D:\\CurrentObservations.gz")
