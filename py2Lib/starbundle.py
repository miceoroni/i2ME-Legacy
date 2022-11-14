import os
import shutil
import random

def makeStarBundle(Directory, Type, flag, Version, date, sendAfter):
    header = '<StarBundle>\n  <Version>' + Version + '</Version>\n  <ApplyDate>' + date + '</ApplyDate>\n  <Type>' + Type + '</Type>\n  <FileActions>\n'
    with open('C:\\Bundle\\MetaData\\manifest.xml', 'w') as ma:
        ma.write(header)
        ma.close()
    
    for (root,dirs,files) in os.walk(Directory, topdown=True):
        num = 0
        for name in files:
            rootDir = None
            if Type == "Managed":
                rootDir= root[22:]
            else:
                rootDir = root[24:]
            bDest = os.path.join(rootDir,name)
            fDest = os.path.join(root,name)
            signature = ''.join(random.choice('abcdef0123456789') for i in range(32))
            splitExt = os.path.splitext(name)
            bName = splitExt[0] + '_' + signature
            shutil.copy(fDest, 'C:\\Bundle\\' + bName)
            if flag == 'Domestic_Universe':
                flag = 'flags="Domestic_Universe"'
            elif flag == 'Domestic_SD_Universe':
                flag = 'flags="Domestic_SD_Universe"'
            else:
                pass
            with open('C:\\Bundle\\MetaData\\manifest.xml', 'a') as mb:
                mb.write('    <Add src="' + bName + '" dest="' + bDest + '" ' + flag + ' />\n')
                mb.close()
            num += 1
    closer = '  </FileActions>\n</StarBundle>'
    with open('C:\\Bundle\\MetaData\\manifest.xml', 'a') as ma:
        ma.write(closer)
        ma.close()
        
        
        


                 #Directory which contains Files to be bundled                        Type                Flags                 Version           Date       SendImmediately(Does not apply to this script)
# makeStarBundle('./.temp/i2State/SD/Managed/Events', 'Managed', 'Domestic_SD_Universe', '637898877227230030', '09/28/2022', 0)