# CloudFlare DDNS Updater MAIN

from CDNSUpdater import CDNSU
import platform
import sys

debugComment = lambda x: print(f'DEBUG: {x}') 

DEBUG=True

def is_windows():
    # debugComment('finding out OS...')

    platformName = platform.system().lower()
    windows = bool(platformName == 'windows')

    debugComment('found OS: {}'.format(platformName))
    debugComment('is windows: {}'.format(windows))

    return windows

apiKey = '111111'
email = 'e@b.c'
webAddress = 'e.com'

RecordUpdater = CDNSU(apiKey,email,webAddress,is_windows())

#if not RecordUpdater.isOnline():
#    print('Please ensure you are connected to the internet, and have access to CloudFlare\'s servers')
#    sys.exit(0)
print(f'Online: {RecordUpdater.isOnline()}')

print(RecordUpdater.getIp())
print(RecordUpdater.getZoneId())
print(RecordUpdater.getIdOldipPrxstate())

firstRun=True

if RecordUpdater.isOnline():
    if not firstRun:
        firstRun = False
        RecordUpdater.oldIp = RecordUpdater.currentIp
    RecordUpdater.getIp()

    if RecordUpdater.chkForChanges():
        RecordUpdater.updateRecord()

else:
    print("Not online currently! Waiting for reconnection...")

sys.exit(0)
