import py2Lib.bit as bit
from time import sleep
from datetime import datetime, timedelta
from  random import choice

def runLo8s(flavor, duration, LDL, logo = None, LDLColor = None, EmergencyLFCancel = None):
    Id = ''.join(random.choice('ABCDEF0123456789') for i in range(16))
    nowUTC = datetime.utcnow()
    now = datetime.now()
    friendlyRunTime = now + timedelta(seconds=30).strftime('%m/%d/%Y %I:%M:%S %p')
    runTime = nowUTC + timedelta(seconds=30)
    ldlCancelTime = runTime.strftime('%m/%d/%Y %H:%M:%S:02')
    lo8sRunTime = runTime.strftime('%m/%d/%Y %H:%M:%S:00')
    if flavor == 'Z':
        nextLDLRunTime = runTime + timedelta(seconds=91)
    else:
        nextLDLRunTime = runTime + timedelta(seconds=65)
    nextLDLRun = nextLDLRunTime.strftime('%m/%d/%Y %H:%M:%S:02')
    if duration == '60':
        duration = '1800'
    elif duration == '65':
        duration = '1950'
    elif duration == '90':
        duration = '2700'
    elif duration == '120':
        duration = '3600'
    else:
        print('Invalid Duration specified. Please specifiy length of the local forecast in seconds.\n60 for 1 minute, 65 for 1 minute 5 seconds, 90 for 1 minute 30 seconds, 120 for 2 minutes.\n\nScript will now terminate...')
        exit()
    if EmergencyLFCancel == 1:
        print(f'Emergency Local On The 8s Kill Switch is Activated. No Local On The 8s Will Air. Maybe b3atdropp3r Hacked An i2 Again???\n{friendlyLo8sRunTime}') 
        sleep(27)
    elif logo != '':
        print(f'Sending Load Command To All Stars. The Local On The 8s is expected to start at {friendlyLo8sRunTime} ...')
        bit.sendCommand([f'<MSG><Exec workRequest="loadPres(File={0},VideoBehind=000,Logo=domesticAds/TAG{logo},Flavor=domestic/{flavor},Duration={duration},PresentationId={Id})" /></MSG>'], 1)
        sleep(27)
    else:
        print(f'Sending Load Command To All Stars. The Local On The 8s is expected to start at {friendlyLo8sRunTime} ...')
        bit.sendCommand([f'<MSG><Exec workRequest="loadPres(File={0},VideoBehind=000,Flavor=domestic/{flavor},Duration={duration},PresentationId={Id})" /></MSG>'], 1)
        sleep(27)
    print('\nCanceling LDL...')
    bit.sendCommand([f'<MSG><Exec workRequest="cancelPres(File={0},PresentationId=LDL,StartTime={ldlCancelTime})" /></MSG>'], 1)
    
    if EmergencyLFCancel == 1:
        print('Not Airing Local On The 8s Due To Kill Switch Activated. Will Reload LDL After National DBS Forecast Finishes...')
        sleep(53)
    else:
        print('\nSending The Run Command. Stand By For Your Local Forecast...')
        bit.sendCommand([f'<MSG><Exec workRequest="runPres(File={0},PresentationId={Id},StartTime={lo8sRunTime})" /></MSG>'], 1)
        sleep(53)

    if EmergencyLFCancel == 1:
        print("\nGetting The LDL Ready So It'll Cue After The National DBS Local Forecast")
        bit.sendCommand([f'<MSG><Exec workRequest="loadPres(File={0},Flavor=domestic/ldl{LDLColor},Duration=72000,PresentationId=LDL1)" /></MSG>'], 1)
        time.sleep(10)
        print("\nSending The Run Command For The LDL...")
        bit.sendCommand([f'<MSG><Exec workRequest="runPres(File={0},PresentationId=LDL1,StartTime={nextLDLRun})" /></MSG>'], 1)
    elif LDL == 1:
        print("\nGetting The LDL Ready So It'll Cue After This Local Forecast...")
        bit.sendCommand([f'<MSG><Exec workRequest="loadPres(File={0},Flavor=domestic/ldl{LDLColor},PresentationId=LDL1)" /></MSG>'], 1)
        time.sleep(10)
        print('\nSending The Run Command For The LDL. As Dave Schwartz Would Say... "That\'s a Wrap!"')
        bit.sendCommand([f'<MSG><Exec workRequest="runPres(File={0},PresentationId=LDL1,StartTime={nextLDLRun})" /></MSG>'], 1)
    else:
        time.sleep(10)
        print('That\'s It Folks. As Dave Schwartz Would Say... "That\'s a Wrap!"')

#----- SET BACKGROUNDS HERE ----------------------#
BGCatastrophic = ['3094', '3095', '3103', '3115']
BGStorm = []
BGAlert = ['3094', '3095', '3103', '3115']
#BGNight = ['3091', '3092', '3102', '3114', '3191']
BGNorm = ['3091', '3092', '3102', '3114']

#------ BG RULES SECTION ------------------------#

if BGCatastrophic:
    brandedCatastrophic = random.choice(BGCatastrophic)
else:
    brandedCatastrophic = ''
if BGStorm:
    brandedStorm = random.choice(BGStorm)
else:
    brandedStorm = ''
if BGAlert:
    brandedAlert = random.choice(BGAlert)
else:
    brandedAlert = ''

if BGNorm:
    brandedNormal = random.choice(BGNorm)
else:
    brandedNormal = ''
#----------------------------------------------

while True:
    mode = input('Please specify mode.\n0  -  "Unbranded"\n1  -  "Normal"\n2  -  "Alert"\n3  -  "Storm Mode"\n4  -  "Catastrophic"\n5  -  "Tag"\n9  -  Exit LOT8\n==>')
    if mode == '0':
        runLo8s('V', '65', 1, '', 'E')
    elif mode == '1':
        runLo8s('V', '65', 1, brandedNormal, 'E')
    elif mode == '2':
        runLo8s('V', '65', 1, brandedAlert, 'E')
    elif mode == '3':
        runLo8s('V1', '65', 1, brandedStorm, 'STORM')
    elif mode == '4':
        runLo8s('V2', '65', 1, brandedCatastrophic, 'F')
    elif mode == '5':
        ad = input('Please specify Tag Number.\n==>')
        flavor = input("Flavor Overide? Default is 'V'.\nEnter flavor letter, or press enter to bypass.\n==>")
        if flavor == '':
            runLo8s('V', '65', 1, ad, 'E')
        else:
            runLo8s(flavor, '65', 1, ad, 'E')
    elif mode == '9':
        print("\n\nGoodbye.\n\n")
        exit()
    else:
        print("Not a valid selection.\n\n")
        time.sleep(1)
