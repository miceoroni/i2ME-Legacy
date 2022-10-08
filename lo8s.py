import py2Lib.bit as bit
import time
from datetime import datetime,timedelta
import random

theNow = datetime.now()
    
currentHour = theNow.strftime('%H')

def runLo8s(flavor, duration, LDL, logo = None, LDLColor = None, EmergencyLFCancel = None):

    Id = ''.join(random.choice('ABCDEF0123456789') for i in range(16))
    
    nowUTC = datetime.utcnow()
    
    now = datetime.now()
    
    currentHour = nowUTC.strftime('%H')
    
    friendlyRunTime = now + timedelta(seconds=30)
    
    runTime = nowUTC + timedelta(seconds=30)
    
    runTimeLDL = nowUTC + timedelta(seconds=30)
    
    ldlCancelTime = runTimeLDL.strftime('%m/%d/%Y %H:%M:%S'+':02')
    
    lo8sRunTime = runTime.strftime('%m/%d/%Y %H:%M:%S'+':00')
    
    friendlyLo8sRunTime = friendlyRunTime.strftime('%m/%d/%Y %I:%M:%S %p')
    
    if flavor == 'Z':
        nextLDLRunTime = runTime + timedelta(seconds=91)
    else:
        nextLDLRunTime = runTime + timedelta(seconds=65)
    
    nextLDLRun = nextLDLRunTime.strftime('%m/%d/%Y %H:%M:%S'+':02')
    
    if duration == '60':
        duration = '1800'
    elif duration == '65':
        duration = '1950'
    elif duration == '90':
        duration = '2700'
    elif duration == '120':
        duration = '3600'
    else:
        print('Invalid Duration specified. Please specifiy length of the local forecast in seconds. 60 for 1 minute, 65 for 1 minute 5 seconds, 90 for 1 minute 30 seconds, 120 for 2 minutes.\n\nScript will now terminate...')
        exit()
    nextLDLRun = nextLDLRunTime.strftime('%m/%d/%Y %H:%M:%S'+':02')
    
    if EmergencyLFCancel == 1:
        print('Emergency Local On The 8s Kill Switch is Activated. No Local On The 8s Will Air. Maybe b3atdropp3r Hacked An i2 Again???\n' + friendlyLo8sRunTime) 
        time.sleep(27)
    elif logo != '':
        print('Sending Load Command To All Stars. The Local On The 8s is expected to start at ' + friendlyLo8sRunTime + ' ...')
        bit.sendCommand(['<MSG><Exec workRequest="loadPres(File={0},VideoBehind=000,Logo=domesticAds/tag'+ logo +',Flavor=domestic/'+flavor+',Duration='+duration+',PresentationId='+Id+')" /></MSG>'], 1)
        time.sleep(27)
    else:
        print('Sending Load Command To All Stars. The Local On The 8s is expected to start at ' + friendlyLo8sRunTime + ' ...')
        bit.sendCommand(['<MSG><Exec workRequest="loadPres(File={0},VideoBehind=000,Flavor=domestic/'+flavor+',Duration='+duration+',PresentationId='+Id+')" /></MSG>'], 1)
        time.sleep(27)
    #Cancel LDL
    print('\nCanceling LDL...')
    bit.sendCommand(['<MSG><Exec workRequest="cancelPres(File={0},PresentationId=LDL,StartTime='+ldlCancelTime+')" /></MSG>'], 1)
    #time.sleep(1)
    
    if EmergencyLFCancel == 1:
        print('Not Airing Local On The 8s Due To Kill Switch Activated. Will Reload LDL After National DBS Forecast Finishes...')
        time.sleep(53)
    else:
        #Run Local On The 8s
        print('\nSending The Run Command. Stand By For Your Local Forecast...')
        bit.sendCommand(['<MSG><Exec workRequest="runPres(File={0},PresentationId='+Id+',StartTime='+lo8sRunTime+')" /></MSG>'], 1)
        time.sleep(53)

    if EmergencyLFCancel == 1:
        color = None
        if LDLColor == 0:
            color = 'E'
        elif LDLColor == 1:
            color = 'F'
        else:
            color = 'E'
        print("\nGetting The LDL Ready So It'll Cue After The National DBS Local Forecast")
        bit.sendCommand(['<MSG><Exec workRequest="loadPres(File={0},Flavor=domestic/ldl'+color+',Duration=72000,PresentationId=LDL1)" /></MSG>'], 1)
        time.sleep(10)
        print("\nSending The Run Command For The LDL...")
        bit.sendCommand(['<MSG><Exec workRequest="runPres(File={0},PresentationId=LDL1,StartTime='+nextLDLRun+')" /></MSG>'], 1)
    elif LDL == 1:
        color = None
        if LDLColor == 0:
            color = 'E'
        elif LDLColor == 1:
            color = 'F'
        else:
            color = 'E'
        #Load LDL
        print("\nGetting The LDL Ready So It'll Cue After This Local Forecast...")
        bit.sendCommand(['<MSG><Exec workRequest="loadPres(File={0},Flavor=domestic/ldl'+color+',PresentationId=LDL1)" /></MSG>'], 1)
        time.sleep(10)
        #Run LDL
        print('''\nSending The Run Command For The LDL. As Dave Schwartz Would Say... "That's a Wrap!"''')
        bit.sendCommand(['<MSG><Exec workRequest="runPres(File={0},PresentationId=LDL1,StartTime='+nextLDLRun+')" /></MSG>'], 1)
    else:
        time.sleep(10)
        print('''That's It Folks. As Dave Schwartz Would Say... "That's a Wrap!"''')

BG = ['3094', '3095', '3103', '3115', '3093']

#if currentHour == '22' or currentHour == '23' or currentHour == '00' or currentHour == '06' or currentHour == '07' or currentHour == '08' or currentHour == '09' or currentHour == '10' or currentHour == '11' or currentHour == '12' or currentHour == '13' or currentHour == '14' or currentHour == '15' or currentHour == '16' or currentHour == '17' or currentHour == '18' or currentHour == '19' or currentHour == '20' or currentHour == '21':
branded = random.choice(BG)
#else:
    #branded = ''

#Flavor, Duration, Air LDL After Forecast (1 For Yes or 0 For No), Logo(Optional), LDL Color Mode (Leave blank for normal or 1 for Severe Mode), Emergency Local On The 8s Kill Switch (1 For Kill or leave blank for normal)
runLo8s('V2', '65', 1, branded, 1) #5053 Jonas
#V for Normal Black Logo
#V2 for Red Logo

