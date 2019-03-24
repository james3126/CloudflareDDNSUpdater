# Class for each record

from reqs import request
import subprocess
import json
import sys
#from debugging import debugComment
#from debugging import unpackDict
from debugging import *

class CDNSU:
    """Main CF DNS Updater class!"""
    #Reqs:
    # Init for vars (windows OS, remote checking ip, your web address, your email, your api key)
    # Check for online
    # Getting the current IP
    # Getting zone ID
    # Getting identifier, old ip and proxied state
    # Check if gotten IP matches CF one
    # Update the record

    #Req vars:
    # REQUIRED INIT Api Key
    # REQUIRED LATE Current Ip
    # OPTIONAL INIT Debug
    # REQUIRED INIT Email
    # OPTIONAL INIT Fetch Frequency
    # DEFAULT  INIT Headers
    # REQUIRED LATE Identifier
    # REQUIRED LATE Old Ip
    # OPTIONAL INIT Ping IP
    # OPTIONAL INIT Change Proxied State
    # OPTIONAL INIT New Proxied State
    # REQUIRED INIT Web Address
    # REQUIRED INIT Windows
    # REQUIRED LATE Zone ID
    def __init__(self, apiKey, email, webAddress, windows, changePxy=False, newPxyState=None, pingIp='1.1.1.1', freq=2, debug=False):
        self.apiKey     = apiKey
        self.changePxy  = changePxy
        #self.newPxyState= newPxyState
        #self.oldPxyState= ''
        self.proxied    = newPxyState
        self.currentIp  = ''
        self.debug      = debug
        self.email      = email
        self.freq       = freq
        self.identifier = ''
        self.online     = False
        self.oldIp      = ''
        self.pingIp     = pingIp
        self.updateReq  = False
        self.webAddress = webAddress
        self.windows    = windows
        self.zoneId     = ''

        self.headers = {'X-Auth-Email'  : str(self.email),
                        'X-Auth-Key'    : str(self.apiKey),
                        'Content-Type'  : 'application/json'}

        if ((self.changePxy) and (self.proxied == None)):
            print("If you enable manuaal changing of the proxy state, you must also set whether to use CF proxying")
            sys.exit(0)

    def isOnline(self):
        """Check if client can connect to CloudFlare servers"""

        # debugComment('checking if online')
        try:
            tryPing = subprocess.Popen("ping -{} 1 {}".format('n' if self.windows else 'cc', self.pingIp), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            pingResponse = tryPing.wait()
        except Exception as error:
            # debugComment('online status: {}'.format(pingResponse))
            print('online status: {}'.format(pingResponse))
            self.online = False
            return False
        if pingResponse != 0:
            # debugComment('online status: {}'.format(pingResponse))
            print('online status: {}'.format(pingResponse))
            self.online = False
            return False

        #debugComment('online status: {}'.format(pingResponse))
        print('online status: {}'.format(pingResponse))
        self.online = True
        return True

    # CAN PROBABLY REMOVE THIS, AND PUT IT INTO THE PROGRAM AS CHECKING FOR THIS FOR EACH THING ISNT GOOD
    def getIp(self):
        """Get the clients current external IP"""
        
        # debugComment('getting the current ip using ipify.org api')
        self.currentIp = request.get('https://api.ipify.org')
        # debugComment('IP found: {}'.format(self.currentIp))

        return self.currentIp

    def getZoneId(self):
        """Get the zone ID from CloudFlare"""

        url = 'https://api.cloudflare.com/client/v4/zones?name={}&status=active&page=1&per_page=20&order=status&direction=desc&match=all'.format(self.webAddress)

        jsonResponse = request.get(url, headers=self.headers, jsonOut=True)

        debugComment('getting the zone ID from CloudFlare')
        debugComment('GET request being sent to: {}'.format(url))
        debugComment('GET headers being sent: {}'.format(unpackDict(self.headers)))

        if 'result' in jsonResponse:
            self.zoneId = str(jsonResponse['result'][0]['id'])
            debugComment('zone ID has been found. It is: {}'.format(self.zoneId))

            return self.zoneId
        
    def getIdOldipPrxstate(self):
        """Get the ID, Old IP and Proxied State from CloudFlare"""

        # NEED TO ADD THE ABILITY TO SELECT THE RECORD TYPE. NOT JUST A TYPE?
        url = 'https://api.cloudflare.com/client/v4/zones/{}/dns_records?type=A&name={}'.format(self.zoneId,self.webAddress)
        jsonResponse = request.get(url, headers=self.headers, jsonOut=True)
        
        # debugComment("checking for a change in IP")
        # debugComment("GET request being sent to: {}".format(url))
        # debugComment("GET headers being sent: {}".format(unpack_dict(self.headers)))

        if 'result' in jsonResponse:
            self.identifier = str(jsonResponse['result'][0]['id'])
            self.oldIp      = str(jsonResponse['result'][0]['content'])
            proxied         = str(jsonResponse['result'][0]['proxied'])

            # debugComment('identifier has been found. It is: {}'.format(self.identifier))
            # debugComment('fetched old IP. It is: {}'.format(self.oldIp))
            # debugComment('fetched proxied state: {}'.format(self.proxied)

            if proxied.lower() == 'true':
                #self.oldPxyState = True
                self.proxied = True
            else:
                #self.oldPxyState = False
                self.proxied = False

            #return self.identifier, self.oldIp, self.oldPxyState
            return self.identifier, self.oldIp, self.proxied
        else:
            print('There is likely a problem with your details. Please double check. If the problem persists, contact me and I\'ll do my best to help!')
            sys.exit(0)

    def chkForChanges(self):
        """Check client IP against CloudFlare servers stored IP"""

        url = 'https://api.cloudflare.com/client/v4/zones/{}/dns_records?type=A&name={}&content={}&page=1&per_page=20&order=type&direction=desc&match=all'.format(self.zoneId,self.webAddress,self.currentIp)
        jsonResponse = request.get(url, headers=self.headers, jsonOut=True)

        # debugComment('checking for a change in IP')
        # debugComment('GET request being sent to: {}'.format(url))
        # debugComment('GET headers being sent: {}'.format(unpackDict(self.headers)))

        if 'result_info' in jsonResponse:
            matches = str(jsonResponse['result_info']['count'])
            # debugComment('matches found: {}'.format(matches))

            if matches == '1':
                print('Check completed, no updated needed! (Current IP: {})'.format(self.currentIp))
                self.updateReq = False
            else:
                print('Check completed, update required! (Old IP: {}, New IP: {})'.format(self.oldIp, self.currentIp))
                self.updateReq = True

            return self.updateReq

        else:
            print('There is likely a problem with your details. Please double check. If the problem persists, contact me and I\'ll do my best to help!')
            sys.exit(0)

    def updateRecord(self):
        """Update the record on CloudFlares servers"""

        url = 'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(self.zoneId,self.identifier)
        payload = {'type'   : 'A',
                   'name'   : self.webAddress,
                   'content': self.currentIp,
                   'ttl'    : 1,
                   #'proxied': bool(self.newPxyState)}
                   'proxied': bool(self.proxied)}
    
        r_status, r_reason = request.put(url, data=payload, headers=self.headers)

        # debugComment('updating the stored A NAME record at CloudFlare')
        # debugComment('GET request being sent to: {}'.format(url))
        # debugComment('PAYLOAD being sent: {}'.format(unpackDict(payload)))
        # debugComment('GET headers being sent: {}'.format(unpackDict(self.headers)))

        if str(r_status) == '200':
            print('Update completed successfully')
        else:
            print('Record update failed with the following reason:\n'.format(r_reason))
            sys.exit(0)
