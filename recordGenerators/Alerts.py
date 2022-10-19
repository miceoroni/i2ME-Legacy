import requests
import json
import os
from datetime import datetime,timedelta
from Util.MachineProductCfg import getZones
import time
import pytz
import xml.dom.minidom
import shutil
import gzip
import logging,coloredlogs


import sys
sys.path.append("./py2lib")
import bit

l = logging.getLogger(__name__)
coloredlogs.install()

#Zones/Counties to fetch alerts for
zones = getZones()

#You can safely edit the API key here. Make sure to include the ' before and after the key
headlineApiKey = '21d8a80b3d6b444998a80b3d6b1449d3'
detailsApiKey = '21d8a80b3d6b444998a80b3d6b1449d3'

k = 0
def getAlerts(location):
    global k
    fetchUrl = 'https://api.weather.com/v3/alerts/headlines?areaId=' + location + ':US&format=json&language=en-US&apiKey=' + headlineApiKey
    response = requests.get(fetchUrl)

    theCode = response.status_code
    
    #Our global variables
    
    
    #Set the actions based on response code
    if theCode == 204:
        print('No alerts for area ' + location + '.\n')
        return
    elif theCode == 403:
        print("Uh oh! Your API key may not be authorized for alerts. Tsk Tsk. Maybe you shouldn't pirate IBM data :)\n")
        return
    elif theCode == 401:
        print("Uh oh! This request requires authentication. Maybe you shouldn't try to access resources for IBM employee's only :)\n")
        return
    elif theCode == 404:
        print("Uh oh! The requested resource cannot be found. This means either the URL is wrong or IBM is having technical difficulties :(\n Or.... They deleted the API :O\n")
        return
    elif theCode == 405:
        print("Uh oh! Got a 405! This means that somehow.... someway..... this script made an invalid request. So sad..... So terrible..... :(\n")
        return
    elif theCode == 406:
        print("Uh oh! Got a 406! This means that IBM doesn't like us. :(\n")
        return
    elif theCode == 408:
        print("Uh oh! We were too slow in providing IBM our alert request. Although I prefer to say we were Slowly Capable! :)\n")
        return
    elif theCode == 500:
        print("Uh oh! Seems IBM's on call IT Tech spilled coffee on the server! Looks like no alerts for a while. Please check back later :)\n")
        return
    elif theCode == 502 or theCode == 503 or theCode == 504:
        print("Uh oh! This is why you don't have interns messing with the server configuration. Please stand by while IBM's on call IT Tech resolves the issue :)\n")
        return
    elif theCode == 200:
        pass

    #Alright lets map our headline variables.
    l.debug('Found Alert for ' + location + '\n')
    dataH = response.json()
    alertsRoot = dataH['alerts']

    for x in alertsRoot:
        detailKey = x['detailKey']
        #Lets get map our detail variables.
        detailsUrl = 'https://api.weather.com/v3/alerts/detail?alertId=' + detailKey + '&format=json&language=en-US&apiKey=' + detailsApiKey
        detailsResponse = requests.get(detailsUrl)
        dataD = detailsResponse.json()
        detailsRoot = dataD['alertDetail']
        theDetailsText = detailsRoot['texts']
        detailsText = theDetailsText[0]
        descriptionRaw = detailsText['description']
        language = detailsText['languageCode']
        Identifier = location + '_' + x['phenomena'] + '_' + x['significance'] + '_' + str(x['processTimeUTC'])
        
        #Is this for a NWS Zone or County?
        last4 = location[2:]
        locationType = None
        if 'C' in last4:
            locationType = 'C'
        elif 'Z' in last4:
            locationType = 'Z'

        #theIdent = str(Identifier)
        thecheck = open('alertmanifest.txt', "r")
        check = thecheck.read()
        
        if check.find(Identifier) != -1:
            l.debug("Alert already sent...")
            return
        k += 1 #We have an alert to send!
        
        #Lets Map Our Vocal Codes!
        vocalCheck = x['phenomena'] + '_' + x['significance']
        vocalCode = None
    
        if vocalCheck == 'HU_W':
            vocalCode = '<bVocHdlnCd>HE001</bVocHdlnCd>'
        elif vocalCheck == 'TY_W':
            vocalCode = '<bVocHdlnCd>HE002</bVocHdlnCd>'
        elif vocalCheck == 'HI_W':
            vocalCode = '<bVocHdlnCd>HE003</bVocHdlnCd>'
        elif vocalCheck == 'TO_A':
            vocalCode = '<bVocHdlnCd>HE004</bVocHdlnCd>'
        elif vocalCheck == 'SV_A':
            vocalCode = '<bVocHdlnCd>HE005</bVocHdlnCd>'
        elif vocalCheck == 'HU_A':
            vocalCode = '<bVocHdlnCd>HE006</bVocHdlnCd>'
        elif vocalCheck == 'TY_A':
            vocalCode = '<bVocHdlnCd>HE007</bVocHdlnCd>'
        elif vocalCheck == 'TR_W':
            vocalCode = '<bVocHdlnCd>HE008</bVocHdlnCd>'
        elif vocalCheck == 'TR_A':
            vocalCode = '<bVocHdlnCd>HE009</bVocHdlnCd>'
        elif vocalCheck == 'TI_W':
            vocalCode = '<bVocHdlnCd>HE010</bVocHdlnCd>'
        elif vocalCheck == 'HI_A':
            vocalCode = '<bVocHdlnCd>HE011</bVocHdlnCd>'
        elif vocalCheck == 'TI_A':
            vocalCode = '<bVocHdlnCd>HE012</bVocHdlnCd>'
        elif vocalCheck == 'BZ_W':
            vocalCode = '<bVocHdlnCd>HE013</bVocHdlnCd>'
        elif vocalCheck == 'IS_W':
            vocalCode = '<bVocHdlnCd>HE014</bVocHdlnCd>'
        elif vocalCheck == 'WS_W':
            vocalCode = '<bVocHdlnCd>HE015</bVocHdlnCd>'
        elif vocalCheck == 'HW_W':
            vocalCode = '<bVocHdlnCd>HE016</bVocHdlnCd>'
        elif vocalCheck == 'LE_W':
            vocalCode = '<bVocHdlnCd>HE017</bVocHdlnCd>'
        elif vocalCheck == 'ZR_Y':
            vocalCode = '<bVocHdlnCd>HE018</bVocHdlnCd>'
        elif vocalCheck == 'CF_W':
            vocalCode = '<bVocHdlnCd>HE019</bVocHdlnCd>'
        elif vocalCheck == 'LS_W':
            vocalCode = '<bVocHdlnCd>HE020</bVocHdlnCd>'
        elif vocalCheck == 'WW_Y':
            vocalCode = '<bVocHdlnCd>HE021</bVocHdlnCd>'
        elif vocalCheck == 'LB_Y':
            vocalCode = '<bVocHdlnCd>HE022</bVocHdlnCd>'
        elif vocalCheck == 'LE_Y':
            vocalCode = '<bVocHdlnCd>HE023</bVocHdlnCd>'
        elif vocalCheck == 'BZ_A':
            vocalCode = '<bVocHdlnCd>HE024</bVocHdlnCd>'
        elif vocalCheck == 'WS_A':
            vocalCode = '<bVocHdlnCd>HE025</bVocHdlnCd>'
        elif vocalCheck == 'FF_A':
            vocalCode = '<bVocHdlnCd>HE026</bVocHdlnCd>'
        elif vocalCheck == 'FA_A':
            vocalCode = '<bVocHdlnCd>HE027</bVocHdlnCd>'
        elif vocalCheck == 'FA_Y':
            vocalCode = '<bVocHdlnCd>HE028</bVocHdlnCd>'
        elif vocalCheck == 'HW_A':
            vocalCode = '<bVocHdlnCd>HE029</bVocHdlnCd>'
        elif vocalCheck == 'LE_A':
            vocalCode = '<bVocHdlnCd>HE030</bVocHdlnCd>'
        elif vocalCheck == 'SU_W':
            vocalCode = '<bVocHdlnCd>HE031</bVocHdlnCd>'
        elif vocalCheck == 'LS_Y':
            vocalCode = '<bVocHdlnCd>HE032</bVocHdlnCd>'
        elif vocalCheck == 'CF_A':
            vocalCode = '<bVocHdlnCd>HE033</bVocHdlnCd>'
        elif vocalCheck == 'ZF_Y':
            vocalCode = '<bVocHdlnCd>HE034</bVocHdlnCd>'
        elif vocalCheck == 'FG_Y':
            vocalCode = '<bVocHdlnCd>HE035</bVocHdlnCd>'
        elif vocalCheck == 'SM_Y':
            vocalCode = '<bVocHdlnCd>HE036</bVocHdlnCd>'
        elif vocalCheck == 'EC_W':
            vocalCode = '<bVocHdlnCd>HE037</bVocHdlnCd>'
        elif vocalCheck == 'EH_W':
            vocalCode = '<bVocHdlnCd>HE038</bVocHdlnCd>'
        elif vocalCheck == 'HZ_W':
            vocalCode = '<bVocHdlnCd>HE039</bVocHdlnCd>'
        elif vocalCheck == 'FZ_W':
            vocalCode = '<bVocHdlnCd>HE040</bVocHdlnCd>'
        elif vocalCheck == 'HT_Y':
            vocalCode = '<bVocHdlnCd>HE041</bVocHdlnCd>'
        elif vocalCheck == 'WC_Y':
            vocalCode = '<bVocHdlnCd>HE042</bVocHdlnCd>'
        elif vocalCheck == 'FR_Y':
            vocalCode = '<bVocHdlnCd>HE043</bVocHdlnCd>'
        elif vocalCheck == 'EC_A':
            vocalCode = '<bVocHdlnCd>HE044</bVocHdlnCd>'
        elif vocalCheck == 'EH_A':
            vocalCode = '<bVocHdlnCd>HE045</bVocHdlnCd>'
        elif vocalCheck == 'HZ_A':
            vocalCode = '<bVocHdlnCd>HE046</bVocHdlnCd>'
        elif vocalCheck == 'DS_W':
            vocalCode = '<bVocHdlnCd>HE047</bVocHdlnCd>'
        elif vocalCheck == 'WI_Y':
            vocalCode = '<bVocHdlnCd>HE048</bVocHdlnCd>'
        elif vocalCheck == 'SU_Y':
            vocalCode = '<bVocHdlnCd>HE049</bVocHdlnCd>'
        elif vocalCheck == 'AS_Y':
            vocalCode = '<bVocHdlnCd>HE050</bVocHdlnCd>'
        elif vocalCheck == 'WC_W':
            vocalCode = '<bVocHdlnCd>HE051</bVocHdlnCd>'
        elif vocalCheck == 'FZ_A':
            vocalCode = '<bVocHdlnCd>HE052</bVocHdlnCd>'
        elif vocalCheck == 'WC_A':
            vocalCode = '<bVocHdlnCd>HE053</bVocHdlnCd>'
        elif vocalCheck == 'AF_W':
            vocalCode = '<bVocHdlnCd>HE054</bVocHdlnCd>'
        elif vocalCheck == 'AF_Y':
            vocalCode = '<bVocHdlnCd>HE055</bVocHdlnCd>'
        elif vocalCheck == 'DU_Y':
            vocalCode = '<bVocHdlnCd>HE056</bVocHdlnCd>'
        elif vocalCheck == 'LW_Y':
            vocalCode = '<bVocHdlnCd>HE057</bVocHdlnCd>'
        elif vocalCheck == 'LS_A':
            vocalCode = '<bVocHdlnCd>HE058</bVocHdlnCd>'
        elif vocalCheck == 'HF_W':
            vocalCode = '<bVocHdlnCd>HE059</bVocHdlnCd>'
        elif vocalCheck == 'SR_W':
            vocalCode = '<bVocHdlnCd>HE060</bVocHdlnCd>'
        elif vocalCheck == 'GL_W':
            vocalCode = '<bVocHdlnCd>HE061</bVocHdlnCd>'
        elif vocalCheck == 'HF_A':
            vocalCode = '<bVocHdlnCd>HE062</bVocHdlnCd>'
        elif vocalCheck == 'UP_W':
            vocalCode = '<bVocHdlnCd>HE063</bVocHdlnCd>'
        elif vocalCheck == 'SE_W':
            vocalCode = '<bVocHdlnCd>HE064</bVocHdlnCd>'
        elif vocalCheck == 'SR_A':
            vocalCode = '<bVocHdlnCd>HE065</bVocHdlnCd>'
        elif vocalCheck == 'GL_A':
            vocalCode = '<bVocHdlnCd>HE066</bVocHdlnCd>'
        elif vocalCheck == 'MF_Y':
            vocalCode = '<bVocHdlnCd>HE067</bVocHdlnCd>'
        elif vocalCheck == 'MS_Y':
            vocalCode = '<bVocHdlnCd>HE068</bVocHdlnCd>'
        elif vocalCheck == 'SC_Y':
            vocalCode = '<bVocHdlnCd>HE069</bVocHdlnCd>'
        elif vocalCheck == 'UP_Y':
            vocalCode = '<bVocHdlnCd>HE073</bVocHdlnCd>'
        elif vocalCheck == 'LO_Y':
            vocalCode = '<bVocHdlnCd>HE074</bVocHdlnCd>'
        elif vocalCheck == 'AF_V':
            vocalCode = '<bVocHdlnCd>HE075</bVocHdlnCd>'
        elif vocalCheck == 'UP_A':
            vocalCode = '<bVocHdlnCd>HE076</bVocHdlnCd>'
        elif vocalCheck == 'TAV_W':
            vocalCode = '<bVocHdlnCd>HE077</bVocHdlnCd>'
        elif vocalCheck == 'TAV_A':
            vocalCode = '<bVocHdlnCd>HE078</bVocHdlnCd>'
        elif vocalCheck == 'TO_W':
            vocalCode = '<bVocHdlnCd>HE110</bVocHdlnCd>'
        else:
            vocalCode = '<bVocHdlnCd />'

        #Do some date/time conversions
        EndTimeUTCEpoch = x['expireTimeUTC']
        EndTimeUTC = datetime.utcfromtimestamp(EndTimeUTCEpoch).strftime('%Y%m%d%H%M')
        #EndTimeUTC = EndTimeUTCString.astimezone(pytz.UTC)
        
        expireTimeEpoch = x['expireTimeUTC']
        expireTimeUTC = datetime.utcfromtimestamp(expireTimeEpoch).strftime('%Y%m%d%H%M')
        
        #V3 Alert API doesn't give us issueTime in UTC. So we have to convert ourselves. Ughhh!!
        iTLDTS = x['issueTimeLocal']
        iTLDTO = datetime.strptime(iTLDTS, '%Y-%m-%dT%H:%M:%S%z')
        issueTimeToUTC = iTLDTO.astimezone(pytz.UTC)
        issueTimeUtc = issueTimeToUTC.strftime('%Y%m%d%H%M')
        
        processTimeEpoch = x['processTimeUTC']
        processTime = datetime.fromtimestamp(processTimeEpoch).strftime('%Y%m%d%H%M%S')

        #What is the action of this alert?
        Action = None
        if x['messageType'] == 'Update':
            Action = 'CON'
        elif x['messageType'] == 'New':
            Action = 'NEW'
    
        #Fix description to replace new lines with space and add XML escape Chars. when needed
        
        description = ' '.join(descriptionRaw.splitlines())
        description = description.replace('&', '&amp;')
        description = description.replace('<', '&lt;')
        description = description.replace('>', '&gt;')
        description = description.replace('-', '')
        description = description.replace(':', '')

        #Is this alert urgent?
        urgency ='piss'
        if vocalCheck == 'TO_W' or vocalCheck == 'SV_W' or vocalCheck == 'FF_W':
            urgency = 'BEUrgent'
        else:
            urgency = 'BERecord'

        alertMsg = '<BERecord id="0000" locationKey="' + location + '_' + x['phenomena'] + '_' + x['significance'] + '_' + x['eventTrackingNumber'] + '_' + x['officeCode'] + '" isWxscan="0"><action>NOT_USED</action><BEHdr><bPIL>' + x['productIdentifier'] + '</bPIL><bWMOHdr>NOT_USED</bWMOHdr><bEvent><eActionCd eActionPriority="' + str(x['messageTypeCode']) + '">' + Action + '</eActionCd><eOfficeId eOfficeNm="' + x['officeName'] + '">' + x['officeCode'] + '</eOfficeId><ePhenom>' + x['phenomena'] + '</ePhenom><eSgnfcnc>' + x['significance'] + '</eSgnfcnc><eETN>' + x['eventTrackingNumber'] + '</eETN><eDesc>' + x['eventDescription'] + '</eDesc><eStTmUTC>NOT_USED</eStTmUTC><eEndTmUTC>' + EndTimeUTC + '</eEndTmUTC><eSvrty>' + str(x['severityCode']) + '</eSvrty><eTWCIId>NOT_USED</eTWCIId><eExpTmUTC>' + expireTimeUTC + '</eExpTmUTC></bEvent><bLocations><bLocCd bLoc="' + x['areaName'] + '" bLocTyp="' + locationType + '">' + location + '</bLocCd><bStCd bSt="' + x['adminDistrict'] + '">' + x['adminDistrictCode'] + '</bStCd><bUTCDiff>NOT_USED</bUTCDiff><bTzAbbrv>NOT_USED</bTzAbbrv><bCntryCd>NOT_USED</bCntryCd></bLocations><bSgmtChksum>' + x['identifier'] + '</bSgmtChksum><procTm>' + processTime + '</procTm></BEHdr><BEData><bIssueTmUTC>' + issueTimeUtc + '</bIssueTmUTC><bHdln><bHdlnTxt>' + x['headlineText'] + '</bHdlnTxt>' + vocalCode + '</bHdln><bParameter>NOT_USED</bParameter><bNarrTxt bNarrTxtLang="en-US"><bLn>' + description + '</bLn></bNarrTxt><bSrchRslt>NOT_USED</bSrchRslt></BEData><clientKey>' + location + '_' + x['phenomena'] + '_' + x['significance'] + '_' + x['eventTrackingNumber'] + '_' + x['officeCode'] + '</clientKey></BERecord>'
       
        #Append BERecord
        with open('./.temp/BERecord.xml', "a") as b:
            b.write(alertMsg)
            b.close()
        
        #Add our alert to the manifest so we don't keep sending in the same alert every 60 seconds unless an update is issued.
        with open('alertmanifest.txt', "a") as c:
            c.write('\n' + location + '_' + x['phenomena'] + '_' + x['significance'] + '_' + str(x['processTimeUTC']))
            c.close()


# TODO: This should be converted into a function so it works better with async, that way we're not getting hung up on that time.sleep() call.

def makeRecord():
    with open("./.temp/BERecord.xml", 'a') as BERecord:
        BERecord.write('<Data type="BERecord">')
        BERecord.close()

    for z in zones:
        getAlerts(z)
    
    with open('./.temp/BERecord.xml', 'a') as BERecord:
        BERecord.write("</Data>")
        BERecord.close()

    dom = xml.dom.minidom.parse("./.temp/BERecord.xml")
    pretty_xml_as_string = dom.toprettyxml(indent = "    ")

    with open("./.temp/BERecord.i2m", 'w') as h:
        h.write(pretty_xml_as_string[23:])
        h.close()

    # If we don't need to send the i2 an alert, we don't need to gzip it.
    if k > 0:
        l.info("Sending alert(s) to the IntelliStar 2!")
        with open("./.temp/BERecord.i2m", 'rb') as f_in:
            with gzip.open("./.temp/BERecord.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
        files = []
        commands = []
        gZipFile = "./.temp/BERecord.gz"
        files.append(gZipFile)
        command = commands.append('<MSG><Exec workRequest="storeData(File={0},QGROUP=__BERecord__,Feed=BERecord)" /><GzipCompressedMsg fname="BERecord" /></MSG>')
        bit.sendFile(files, commands, 1, 0)
        os.remove(gZipFile)
        k = 0
    
    os.remove("./.temp/BERecord.xml")
    