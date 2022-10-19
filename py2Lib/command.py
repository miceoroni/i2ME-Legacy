import bit
import os
import shutil
import math
import time
from datetime import datetime

def restartI2Service(headendIds):
    
    HeadendList = ''
    
    for x in headendIds:
        HeadendList += ('<HeadendId>' + x + '</HeadendId>')
    bit.sendCommand('<MSG><Exec workRequest="restartI2Service(File={0},CommandId=0000)" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>I2MSG', 1)
    #print('<MSG><Exec workRequest="restartI2Service(File={0},CommandId=0000)" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>')

def rebootI2(headendIds):
    
    HeadendList = ''
    
    for x in headendIds:
        HeadendList += ('<HeadendId>' + x + '</HeadendId>')
    
    commands = []
    command = '<MSG><Exec workRequest="rebootStar(File={0},CommandId=GOFUCK_YOURSELF)" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>'
    commands.append(command)
    bit.sendCommand(commands, 1)

def clearStarBundle(headendIds, btype):
    
    HeadendList = ''
    
    for x in headendIds:
        HeadendList += ('<HeadendId>' + x + '</HeadendId>')
    
    commands = []
    command = '<MSG><Exec workRequest="clearStarBundle(File={0},BundleType=' + btype + ')" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>'
    commands.append(command)
    bit.sendCommand(commands, 1)

def changePasswords(PasswordFile, headendIds):
    HeadendList = ''
    files = []
    files.append(PasswordFile)
    commands = []
    numSegs = 1
    if headendIds != None:
        for x in headendIds:
            HeadendList += ('<HeadendId>' + x + '</HeadendId>')
            command = '<MSG><Exec workRequest="changePassword(File={0},CommandId=GOFUCK_YOURSELF)" /><GzipCompressedMsg fname="passwords2.i2m" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>'
            commands.append(command)
            bit.sendFile(files, commands, numSegs, 0)
    else:
        command = '<MSG><Exec workRequest="changePassword(File={0},CommandId=GOFUCK_YOURSELF)" /><GzipCompressedMsg fname="passwords2.i2m" /></MSG>'
        commands.append(command)
        bit.sendFile(files, commands, numSegs, 0)
    os.remove(PasswordFile)

def sendMaintCommand(File, headendIds):
    HeadendList = ''
    files = []
    files.append(File)
    commands = []
    numSegs = 1
    if headendIds != None:
        for x in headendIds:
            HeadendList += ('<HeadendId>' + x + '</HeadendId>')
            #command = '<MSG><Exec workRequest="changePassword(File={0},CommandId=GOFUCK_YOURSELF)" /><GzipCompressedMsg fname="passwords" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>'
            #command = '<MSG><Exec workRequest="setTsInNic(File={0},CommandId=GOFUCK_YOURSELF)" /><GzipCompressedMsg fname="TSInConfig" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>'
            #command = '<MSG><Exec workRequest="setTsOutNic(File={0},CommandId=GOFUCK_YOURSELF)" /><GzipCompressedMsg fname="TSOutConfig" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>'
            #command = '<MSG><Exec workRequest="setBackChannelNic(File={0},CommandId=GOFUCK_YOURSELF)" /><GzipCompressedMsg fname="BackChannelNicConfig" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>'
            #command = '<MSG><Exec workRequest="setANFConfig(File={0},CommandId=GOFUCK_YOURSELF)" /><GzipCompressedMsg fname="ANFConfig" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>'
            #command = '<MSG><Exec workRequest="setPipelineEncoderConfig(File={0},CommandId=GOFUCK_YOURSELF)" /><GzipCompressedMsg fname="EncoderConfig" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>'
            #command = '<MSG><Exec workRequest="setPipelineDecoderConfig(File={0},CommandId=GOFUCK_YOURSELF)" /><GzipCompressedMsg fname="DecoderConfig" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>'
            
            #I2 HD
            #command = '<MSG><Exec workRequest="setTsiiConfig(File={0},DeviceType=Encoder,CommandId=GOFUCK_YOURSELF)" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>'
            commands.append(command)
            bit.sendFile(files, commands, numSegs, 0)
    else:
        #command = '<MSG><Exec workRequest="changePassword(File={0},CommandId=GOFUCK_YOURSELF)" /><GzipCompressedMsg fname="passwords.i2m" /></MSG>'
        commands.append(command)
        bit.sendFile(files, commands, numSegs, 0)
    os.remove(File)

def loadRunPres(headendIds, Flavor, Logo, Duration, Id):
    HeadendList = ''
    
    for x in headendIds:
        HeadendList += ('<HeadendId>' + x + '</HeadendId>')
    
    if Logo == '':
        command = ['<MSG><Exec workRequest="loadRunPres(File={0},Flavor='+Flavor+',Duration='+Duration+',PresentationId='+Id+')" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>']
        bit.sendCommand(command, 1)
    else:
        command = ['<MSG><Exec workRequest="loadRunPres(File={0},Flavor='+Flavor+',Logo='+Logo+',Duration='+Duration+',PresentationId='+Id+')" /><CheckHeadendId>' + HeadendList + '</CheckHeadendId></MSG>']
        bit.sendCommand(command, 1)

def sendStarBundle(File):
    
    size = os.path.getsize(File)
    if size >= 67550000:
        CHUNK_SIZE = 67550000
        file_number = 1
        fPath = os.path.dirname(File)
        fpToSplit = os.path.splitext(File)
        splitFn = fpToSplit[0].split('\\')
        newFn = splitFn[-1]
        eCount = size / CHUNK_SIZE
        estCount = math.ceil(eCount)
        
        print("File size is greater than 64MB. Will need to split the files for transmission...\n")
        time.sleep(1)
        

        with open(File, "rb") as f:
            chunk = f.read(CHUNK_SIZE)
            while chunk:
                if file_number < 10:
                    fileNum = '0' + str(file_number)
                else:
                    fileNum = file_number
                with open(fPath + '\\split\\' + newFn + '_' + str(fileNum), "wb") as chunk_file:
                    chunk_file.write(chunk)
                print('Successfully split file ' + str(file_number) + ' out of ' + str(estCount) + '\n')
                file_number += 1
                chunk = f.read(CHUNK_SIZE)

        count = file_number - 1
        part = 1

        with open('./.temp/msgId.txt', "r") as f:
            oMsgId = f.read()
            Id = int(oMsgId)
            f.close()

        for x in os.listdir(fPath + '\\split'):
            path = fPath + '\\split\\'
            y = path + x            
            if part != count:     
                print(x)            
                bit.sendFile([y],['<MSG><SplitMsg id="'+str(Id)+'" part="'+str(part)+'" count="'+str(count)+'" /></MSG>'], 1, 0)
                part += 1
                time.sleep(30)
            elif part == count: 
                print(x)
                bit.sendFile([y],['<MSG><SplitMsg id="'+str(Id)+'" part="'+str(part)+'" count="'+str(count)+'" /></MSG>'], 1, 0)
                time.sleep(30)
                bit.sendCommand(['<MSG><Exec workRequest="stageStarBundle(File=C:\\Program Files\\TWC\\i2\\Volatile\\MsgIngester-7787\\' + str(Id) + ')" /></MSG>'], 0)
                for f in os.listdir(path):
                    os.remove(os.path.join(path, f))
    else:
        bit.sendFile([File],['<MSG><Exec workRequest="stageStarBundle(File={0})" /></MSG>'], 1, 0)
    os.remove(File)

def sendUpgrade(File, RelName):
    
    size = os.path.getsize(File)
    if size >= 67550000:
        CHUNK_SIZE = 67550000
        file_number = 1
        fPath = os.path.dirname(File)
        fpToSplit = os.path.splitext(File)
        splitFn = fpToSplit[0].split('\\')
        newFn = splitFn[-1]
        eCount = size / CHUNK_SIZE
        estCount = math.ceil(eCount)
        
        print("File size is greater than 64MB. Will need to split the files for transmission...\n")
        time.sleep(1)
        

        with open(File, "rb") as f:
            chunk = f.read(CHUNK_SIZE)
            while chunk:
                if file_number < 10:
                    fileNum = '0' + str(file_number)
                else:
                    fileNum = file_number
                with open(fPath + '\\split\\' + newFn + '_' + str(fileNum), "wb") as chunk_file:
                    chunk_file.write(chunk)
                print('Successfully split file ' + str(file_number) + ' out of ' + str(estCount) + '\n')
                file_number += 1
                chunk = f.read(CHUNK_SIZE)

        count = file_number - 1
        part = 1

        with open('./.temp/msgId.txt', "r") as f:
            oMsgId = f.read()
            Id = int(oMsgId)
            f.close()

        for x in os.listdir(fPath + '\\split'):
            path = fPath + '\\split\\'
            y = path + x            
            if part != count:     
                print(x)            
                bit.sendFile([y],['<MSG><SplitMsg id="'+str(Id)+'" part="'+str(part)+'" count="'+str(count)+'" /></MSG>'], 1, 0)
                part += 1
                time.sleep(10)
            elif part == count: 
                print(x)
                bit.sendFile([y],['<MSG><SplitMsg id="'+str(Id)+'" part="'+str(part)+'" count="'+str(count)+'" /></MSG>'], 1, 0)
                part += 1
                time.sleep(15)
                bit.sendCommand(['<MSG><Exec workRequest="storeUpgrade(File=C:\\Program Files\\TWC\\i2\\Volatile\\MsgIngester-7787\\' + str(Id) + ',ReleaseName=' + RelName + ')" /></MSG>'], 0)
                for f in os.listdir(path):
                    os.remove(os.path.join(path, f))
    else:
        bit.sendFile([File],['<MSG><Exec workRequest="storeUpgrade(File={0},ReleaseName=' + RelName + ')" /></MSG>'], 1, 0)
    os.remove(File)

def makeStarBundle(Directory, Type, flag, Version, date, sendAfter):
    header = '<StarBundle>\n  <Version>' + Version + '</Version>\n  <ApplyDate>' + date + '</ApplyDate>\n  <Type>' + Type + '</Type>\n  <FileActions>\n'
    with open('./.temp/i2State\\SD\\ChangesetBundle\\MetaData\\manifest.xml', 'w') as ma:
        ma.write(header)
        ma.close()
    
    for (root,dirs,files) in os.walk(Directory, topdown=True):
        for name in files:
            rootDir = root[24:]
            bDest = os.path.join(rootDir,name)
            fDest = os.path.join(root,name)
            shutil.copy(fDest, './.temp/i2State\\SD\\ChangesetBundle')
        for name in files:
            if flag == 'Domestic_Universe':
                flag = 'flags="Domestic_Universe"'
            elif flag == 'Domestic_SD_Universe':
                flag = 'flags="Domestic_SD_Universe"'
            else:
                pass
            with open('./.temp/i2State\\SD\\ChangesetBundle\\MetaData\\manifest.xml', 'a') as mb:
                mb.write('    <Add src="' + name + '" dest="' + bDest + '" ' + flag + ' />\n')
                mb.close()
    closer = '  </FileActions>\n</StarBundle>'
    with open('./.temp/i2State\\SD\\ChangesetBundle\\MetaData\\manifest.xml', 'a') as ma:
        ma.write(closer)
        ma.close()


#restartI2Service(['006833'])

#rebootI2(['006833'])

#clearStarBundle(['006833'], 'Changeset')

#bit.sendCommand(['<MSG><Exec workRequest="cancelPres(File={0},PresentationId=LDL,StartTime=09/28/2022 03:37:30:22)" /></MSG>'], 1)

#loadRunPres(['038488'], 'domestic/ldlE', '', '72000', 'LDL1')

#changePasswords('./.temp/passwords2.gz', ['006833'])

#sendMaintCommand('./.temp/maint\\temp\\passwords',['040500'])

#sendStarBundle("./.temp/Bundle.zip")

#sendUpgrade("./.temp/Upgrades\\wireshark_1.4.6.0.zip", "wireshark_1.4.6.0")

#For splitting
#sendUpgrade("./.temp/ChangesetHD.zip", "PipelineMaint_6.15.1.5714")

#For no split upgrades
#bit.sendFile('./.temp/Upgrades\\vizRequiredFilesForI2_1.2.0.0.zip', '<MSG><Exec workRequest="storeUpgrade(File={0},ReleaseName=vlc_1.1.12.0)" /><CheckHeadendId><HeadendId>040500</HeadendId></CheckHeadendId></MSG>I2MSG', 0)

#For split upgrades
#bit.sendFile('./.temp/split\\ChangesetHD_04', '<MSG><SplitMsg id="410059811" part="4" count="69" /></MSG>I2MSG', 0)

#Command for split upgrades

#commands = []
#command = '<MSG><Exec workRequest="storeUpgrade(File=C:/Program Files/TWC/i2/Volatile/MsgIngester-7787/410059791,ReleaseName=tts_1.0.0.1)" /></MSG>'

#commands.append(command)
#bit.sendCommand(commands, 1, 0)

#bit.sendFile(['./.temp/Alert.gz'], ['<MSG><Exec workRequest="storePriorityData(File={0},QGROUP=__BEUrgent__,Feed=BEUrgent)" /><GzipCompressedMsg fname="Alert.i2m" /></MSG>'], 1, 0)
'''
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=7zip_9.20.0.0)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=agentRansack_2010.03.29.47911)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=cirrusDriver_6.12.0.5645)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=cirrusFirmware_6.15.0.5692)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=dotNetFx40_Full_x86_x64)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=fileZilla_3.4.0.0)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=i2_7.4.5-release_81535)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=i2PluginRuntime_7.4.1-release_19905)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=i2Shell_6.3.0-release_18031)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=notepad_5.9.0.0)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=vizEngine_2.8.5.2988002)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=vizRequiredFilesForI2_1.2.0.0)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=vlc_1.1.11.0)" /></MSG>'], 0)
bit.sendCommand(['<MSG><Exec workRequest="stageUpgrade(File={0},InstallImmediately=False,ReleaseName=wireshark_1.4.6.0)" /></MSG>'], 0)
'''
#bit.sendCommand(['<MSG><Exec workRequest="cancelPres(File={0},PresentationId=LDL,StartTime=09/17/2022 02:32:40:00)" /><CheckHeadendId><HeadendId>006833</HeadendId></CheckHeadendId></MSG>'], 1)
#bit.sendCommand('./.temp/Upgrades\\split\\PipelineMaint_6.15.1.5714_03', '<MSG><Exec workRequest="storeUpgrade(File=C:/Program Files/TWC/i2/Volatile/MsgIngester-7787/410059604,ReleaseName=PipelineMaint_6.15.1.5714)" /></MSG>I2MSG', 0)




#bit.sendCommand(['<MSG><Exec workRequest="stageStarBundle(File=C:\\Program Files\\TWC\\i2\\Volatile\\MsgIngester-7787\\410069442)" /></MSG>'], 0)

#bit.sendCommand(['<MSG><Exec workRequest="loadPres(File={0},Flavor=domestic/ldlI,Duration=72000,PresentationId=ldl)" /></MSG>'], 1)

#bit.sendCommand(['<MSG><Exec workRequest="cancelPres(File={0},PresentationId=LDL,StartTime=09/25/2022 04:01:30:22)" /></MSG>'], 1)

#bit.sendCommand(['<MSG><Exec workRequest="runPres(File={0},PresentationId=ldl,StartTime=09/17/2022 17:03:35:00)" /></MSG>'], 1)

#makeStarBundle('./.temp/i2State\\SD\\Changeset\\audio\\domesticSD\\vocalLocal\\Cantore', 'Changeset', 'Domestic_SD_Universe', '63702614401035937', '09/19/2022', 0)

