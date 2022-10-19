import socket
import sys
import os
import struct
import binascii
import math
import time
import logging,coloredlogs

l = logging.getLogger(__name__)
coloredlogs.install()

MCAST_GRP = '224.1.1.77'
MCAST_IF = '127.0.0.1'
BUF_SIZE = 1396

MULTICAST_TTL = 2

conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
conn.setsockopt(socket.SOL_IP,socket.IP_ADD_MEMBERSHIP,socket.inet_aton(MCAST_GRP)+socket.inet_aton(MCAST_IF))

test = b"This is a test"

def sendFile(files, commands, numSgmts, Pri):
    if Pri == 0:
        MCAST_PORT = 7787
    elif Pri == 1:
        MCAST_PORT = 7788
    else:
        l.critical("Invalid Priority Flag. 0 = Routine Message        1 = High Priority Message\n\nScript will now terminate...")
        exit()
    #Get the next message ID
    with open('./.temp/msgId.txt', "r") as f:
        oMsgId = f.read()
        msgNum = int(oMsgId)
        f.close()
    
    nMsgNum = msgNum + 1    
    h = open('./.temp/msgId.txt', "w")
    h.write(str(nMsgNum))
    h.close()
    segnmNum = 0
    if Pri == 0:
        l.info("Sending Routine Msg-" + str(msgNum) + " on UDP " + MCAST_GRP + " " + str(MCAST_PORT) + "....")
    elif Pri == 1:
        l.info("Sending High Priority Msg-" + str(msgNum) + " on UDP " + MCAST_GRP + " " + str(MCAST_PORT) + "....")
    startFlag = False

    for x, y in zip(files, commands):
        size = os.path.getsize(x)
        check = size - BUF_SIZE
        pToBeSent = size / 1405
        packRounded = math.ceil(pToBeSent) + 1
        numSegments = numSgmts + 3
        total_sent = 0
        payloadLength = 0
        packet_count = 1
        j = 0
        pc = packet_count.to_bytes(1, byteorder='big')
        i = 0
        encode1 = bytes(y + 'I2MSG', 'UTF-8')
        commandLength = len(y)
        encode2 = commandLength.to_bytes(4, byteorder='little')
        theCommand = b"".join([encode1, encode2])
        char = ''
        new_file = open(x, "ab")
        new_file.write(theCommand) # Append command to end of the file
        new_file.close()
        new_size = os.path.getsize(x)

        if startFlag == False:
            #Our 34 byte beginning packet
            p1 = struct.pack(">BHHHIIBBBBBBBIBIBBB", 18, 1, 0 , 16, msgNum, 0, segnmNum, 0, 0, 8, numSegments, 3, 0, 0, 8, packRounded, 0, 0, 0)
            conn.sendto(p1, (MCAST_GRP, MCAST_PORT))
            startFlag = True
        with open(x,"rb") as message:
            message.seek(0)
            data = message.read(BUF_SIZE)
            while data:
                packetHeader = struct.pack(">BHHHIIBBB", 18, 1, 0, 1405, msgNum, packet_count, 0, 0, 0)
                fec = struct.pack("<IBI", packet_count, 0, new_size)
                if len(data) < BUF_SIZE:
                    nullCharacterLen = BUF_SIZE - len(data)
                    char = ''
                    while(i < nullCharacterLen):
                        char += '00'
                        i = i+1
                    theNull = bytes.fromhex(char)
                    conn.sendto(packetHeader + fec + data + theNull, (MCAST_GRP, MCAST_PORT))
                else:
                    conn.sendto(packetHeader + fec + data, (MCAST_GRP, MCAST_PORT))
                l.debug(packet_count)
                packet_count += 1
                j += 1
            
                #Rate Limit UDP Packets To Prevent Packet Overflow On Transport Stream.
                if j == 1000: #Number of packets to be sent before pausing
                    time.sleep(2) #Pause for this number of seconds
                    j = 0
                    data = message.read(BUF_SIZE)     
                else:
                    data = message.read(BUF_SIZE)
        segnmNum += 1

    # OUR TEST MESSAGE BLOCK
    #-------------------------------------------------------------------------------------------------------
    w = 3
    while w <= 3 and w != 0:
        p3 = struct.pack(">BHHHIIBBBBBBBI", 18, 1, 1, 8, msgNum, 0, segnmNum, 0, 0, 8, 0, 0, 0, 67108864)
        p4 = struct.pack(">BHHHIIBBB", 18, 1, 1, 14, msgNum, 1, segnmNum, 0, 0) + test
        conn.sendto(p3, (MCAST_GRP, MCAST_PORT))
        conn.sendto(p4, (MCAST_GRP, MCAST_PORT))
        segnmNum += 1
        w -= 1
    #-------------------------------------------------------------------------------------------------------
def sendCommand(command, Pri, msgNum = None):
    if Pri == 0:
        MCAST_PORT = 7787
    elif Pri == 1:
        MCAST_PORT = 7788
    else:
        l.critical("Invalid Priority Flag. 0 = Routine Message        1 = High Priority Message\n\nScript will now terminate...")
        exit()
    #Get the next message ID
    with open('./.temp/msgId.txt', "r") as f:
        oMsgId = f.read()
        msgNum = int(oMsgId)
        f.close()
    
    nMsgNum = msgNum + 1    
    h = open('./.temp/msgId.txt', "w")
    h.write(str(nMsgNum))
    h.close()
    segnmNum = 0
    if Pri == 0:
        l.info("Sending Routine Msg-" + str(msgNum) + " on UDP " + MCAST_GRP + " " + str(MCAST_PORT) + "....")
    elif Pri == 1:
        l.info("Sending High Priority Msg-" + str(msgNum) + " on UDP " + MCAST_GRP + " " + str(MCAST_PORT) + "....")
    startFlag = False

    for x in command:
        bx = bytes(x, 'utf-8')
        with open('./.temp/command', 'wb') as c:
            c.write(bx)
            c.close()
        size = os.path.getsize('./.temp/command')
        encode1 = bytes('I2MSG', 'UTF-8')
        commandLength = size
        encode2 = commandLength.to_bytes(4, byteorder='little')
        theCommand = b"".join([encode1, encode2])
        with open('./.temp/command', 'ab') as d:
            d.write(theCommand)
            d.close()
        check = size - BUF_SIZE
        pToBeSent = size / 1405
        packRounded = math.ceil(pToBeSent) + 1
        numSegments = 4
        total_sent = 0
        payloadLength = 0
        packet_count = 1
        j = 0
        pc = packet_count.to_bytes(4, byteorder='little')
        i = 0
        char = ''
        new_size = os.path.getsize('./.temp/command')

        if startFlag == False:
            #Our 34 byte beginning packet
            p1 = struct.pack(">BHHHIIBBBBBBBIBIBBB", 18, 1, 0 , 16, msgNum, 0, segnmNum, 0, 0, 8, numSegments, 3, 0, 0, 8, packRounded, 0, 0, 0)
            conn.sendto(p1, (MCAST_GRP, MCAST_PORT))
            startFlag = True
        with open('./.temp/Command',"rb") as message:
            message.seek(0)
            data = message.read(BUF_SIZE)
            while data:
                packetHeader = struct.pack(">BHHHIIBBB", 18, 1, 0, 1405, msgNum, packet_count, 0, 0, 0)
                fec = struct.pack("<IBI", packet_count, 0, new_size)
                if len(data) < BUF_SIZE:
                    nullCharacterLen = BUF_SIZE - len(data)
                    char = ''
                    while(i < nullCharacterLen):
                        char += '00'
                        i = i+1
                    theNull = bytes.fromhex(char)
                    conn.sendto(packetHeader + fec + data + theNull, (MCAST_GRP, MCAST_PORT))
                else:
                    conn.sendto(packetHeader + fec + data, (MCAST_GRP, MCAST_PORT))
                l.debug(packet_count)
                packet_count += 1
                j += 1
            
                #Rate limit UDP Packets to prevent Packet Overflow on i2 machine.
                if j == 1000: #Number of packets to be sent before pausing
                    time.sleep(10) #Pause for this number of seconds
                    j = 0
                    data = message.read(BUF_SIZE)     
                else:
                    data = message.read(BUF_SIZE)
        segnmNum += 1

    # OUR TEST MESSAGE BLOCK
    #-------------------------------------------------------------------------------------------------------
    w = 3
    while w <= 3 and w != 0:
        p3 = struct.pack(">BHHHIIBBBBBBBI", 18, 1, 1, 8, msgNum, 0, segnmNum, 0, 0, 8, 0, 0, 0, 67108864)
        p4 = struct.pack(">BHHHIIBBB", 18, 1, 1, 14, msgNum, 1, segnmNum, 0, 0) + test
        conn.sendto(p3, (MCAST_GRP, MCAST_PORT))
        conn.sendto(p4, (MCAST_GRP, MCAST_PORT))
        segnmNum += 1
        w -= 1
    #-------------------------------------------------------------------------------------------------------


#Send Current Observations
#sendFile("./.temp/CurrentObservations.i2m.gz", '<MSG><Exec workRequest="storeData(File={0},QGROUP=__CurrentObservations__,Feed=CurrentObservations)" /><GzipCompressedMsg fname="CurrentObservations.i2m" /></MSG>I2MSG', 0)
#time.sleep(10)
#Send Hourly Forecast
#sendFile("./.temp/HourlyForecast.i2m.gz", '<MSG><Exec workRequest="storeData(File={0},QGROUP=__HourlyForecast__,Feed=HourlyForecast)" /><GzipCompressedMsg fname="HourlyForecast.i2m" /></MSG>I2MSG', 0)
#time.sleep(10)
#Send Daily Forecast
#sendFile("./.temp/DailyForecast.i2m.gz", '<MSG><Exec workRequest="storeData(File={0},QGROUP=__DailyForecast__,Feed=DailyForecast)" /><GzipCompressedMsg fname="DailyForecast.i2m" /></MSG>I2MSG', 0)

#Send radar image
#sendFile("./.temp/radar.i2m", '<MSG><Exec workRequest="storePriorityImage(File={0},FileExtension=.tiff,IssueTime=08/28/2022 03:00:00,Location=US,ImageType=Radar)" /></MSG>I2MSG', 0)

#Load Local On The 8s
#sendCommand('<MSG><Exec workRequest="loadPres(File={0},VideoBehind=000,Logo=domesticAds/tag3352,Flavor=domestic/V,Duration=1950,PresentationId=3E396FFF95A00067)" /></MSG>I2MSG', 1)
#time.sleep(25)
#Cancel LDL
#sendCommand('<MSG><Exec workRequest="cancelPres(File={0},PresentationId=LDL,StartTime=08/29/2022 00:20:55:02)" /></MSG>I2MSG', 1)
#time.sleep(1)
#Run Local On The 8s
#sendCommand('<MSG><Exec workRequest="runPres(File={0},PresentationId=3E396FFF95A00067,StartTime=08/29/2022 00:20:55:00)" /></MSG>I2MSG', 1)
#time.sleep(35)
#Load LDL
#sendCommand('<MSG><Exec workRequest="loadPres(File={0},Flavor=domestic/ldlE,PresentationId=LDL1)" /></MSG>I2MSG', 1)
#time.sleep(10)
#Run LDL
#sendCommand('<MSG><Exec workRequest="runPres(File={0},PresentationId=LDL1,StartTime=08/29/2022 00:22:00:02)" /></MSG>I2MSG', 1)

#Heartbeat Command
#sendCommand('<MSG><Exec workRequest="heartbeat(File={0},Time=08/28/2022 02:29:00.234)" /></MSG>I2MSG', 1)

#Misc commands
#sendCommand('<MSG><Exec workRequest="loadRunPres(File={0},Flavor=domestic/ldlE,PresentationId=LDL1)" /><CheckHeadendId><HeadendId>040500</HeadendId></CheckHeadendId></MSG>I2MSG', 1)

#sendCommand('<MSG><Exec workRequest="cancelPres(File={0},PresentationId=LDL1,StartTime=08/28/2022 15:00:00:00)" /><CheckHeadendId><HeadendId>040500</HeadendId></CheckHeadendId></MSG>I2MSG', 1)
#Restart Command
#sendCommand('<MSG><Exec workRequest="restartI2Service(File={0},CommandId=0000)" /><CheckHeadendId><HeadendId>040500</HeadendId></CheckHeadendId></MSG>I2MSG', 1)

#Set ANF Mode
#sendFile("./.temp/ANFOn.i2m",'<MSG><Exec workRequest="setANFDisplay(File={0},CommandId=0000)" /><CheckHeadendId><HeadendId>040500</HeadendId><HeadendId>040449</HeadendId><HeadendId>030025</HeadendId></CheckHeadendId></MSG>I2MSG', 1)

#SendBundle
#sendFile("./.temp/Bundles.zip",'<MSG><Exec workRequest="stageStarBundle(File={0})" /></MSG>I2MSG', 0)

#Send Upgrade
#sendFile("./.temp/Upgrades/maintenance_1.0.0.50.zip",'<MSG><Exec workRequest="storeUpgrade(File={0},ReleaseName=maintenance_1.0.0.50)" /></MSG>I2MSG', 0)

#Stage Upgrade
#sendCommand('<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=maintenance_1.0.0.50)" /></MSG>I2MSG', 0)

#Change Passwords
#sendFile("./.temp/passwords.i2m",'<MSG><Exec workRequest="changePassword(File={0},CommandId=0000)" /></MSG>I2MSG', 0)