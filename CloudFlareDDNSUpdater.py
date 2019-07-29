# Cloudflare DNS record updater v1.16 - James Kerley 2018
# Huge amount of bug fixes
import sys
if sys.version_info < (3, 0):
    print("Please run this program with Python 3 or above")
from reqs import request
import configparser
import subprocess
import argparse
import platform
import time
import os

DEBUG = False # Verbose debug output, dumping lots of useless information for normal operation. | Default: False
PROXIED_OVERRIDE = None # This will allow you to override your Cloudflare record proxy configuration. Change this to True (Force enable proxy) or False (Force disable proxy) or None (Keep current setting) | Default: None
SINGLE_RUN = False # This will enable you to run more easily as a cron job. | Default: False

# ---- You DONT need to touch anything below here for normal operation ----
VERSION = '1.16'

# Function for DEBUG comments
def debug_comment(e):
    if DEBUG:
        print("\nDEBUG: {}".format(e))

# Function to print out a dict in a pretty way for DEBUG
def unpack_dict(dic):
    for key, value in sorted(HEADERS.items(), key=lambda x: x[0]):
        
        return "{} : {}".format(key, value)

# Function to check for all required details entered
def details_exist(VARS):
    debug_comment("checking for all vars set")

    for VAR in VARS:
        debug_comment("checking var '{}' exists".format(VAR))

        if VAR in globals():
            debug_comment("checking {} is set".format(VAR))
            if bool(globals()[VAR]):
                pass
            elif VAR == 'DEBUG':
                pass
            else:
                print("You haven't set {}".format(VAR))
                sys.exit(0)
        else:
            print("You have removed {}".format(VAR))
            sys.exit(0)

# Function to decide if OS is windows or not
def is_windows():
    debug_comment("finding out OS...")
        
    PLATFORM = platform.system().lower()
    WINDOWS = bool(PLATFORM == "windows")

    debug_comment("found OS: {}".format(PLATFORM))
    debug_comment("is windows: {}".format(WINDOWS))

    return WINDOWS

# Function to ping CloudFlare to first ensure both the local and remote machines are available over the internet
def is_online(REMOTE_IP):
    debug_comment("checking if online")
    WINDOWS = is_windows()
    try:
        #OUTPUT = subprocess.check_output("ping -{} 1 {}".format('n' if WINDOWS else 'c', REMOTE_IP), shell=True)
        TRY_PING = subprocess.Popen("ping -{} 1 {}".format('n' if WINDOWS else 'c', REMOTE_IP), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        OUTPUT = TRY_PING.wait()
    except Exception as error:
        debug_comment("online status: {}".format(OUTPUT))
        return False
    if OUTPUT != 0:
        debug_comment("online status: {}".format(OUTPUT))
        
        return False
    debug_comment("online status: {}".format(OUTPUT))
    
    return True

# Function to get the current external IP
def get_current_ip():
    CURRENT_IP = request.get("https://api.ipify.org")

    debug_comment("getting the current ip using ipify.org api")
    debug_comment("IP found: {}".format(CURRENT_IP))
        
    return CURRENT_IP

# Function to get the CloudFlare DNS Zone ID
def get_zone_id(WEB_ADDRESS, EMAIL, API_KEY, HEADERS):
    GET_ZONE_ID_URL = "https://api.cloudflare.com/client/v4/zones?name={}&status=active&page=1&per_page=20&order=status&direction=desc&match=all".format(WEB_ADDRESS)

    JSON_RESPONSE = request.get(GET_ZONE_ID_URL, headers=HEADERS, jsonOut=True)

    debug_comment("getting the zone ID from CloudFlare")
    debug_comment("GET request being sent to: {}".format(GET_ZONE_ID_URL))
    debug_comment("GET headers being sent: {}".format(unpack_dict(HEADERS)))

    if 'result' in JSON_RESPONSE:
        ZONE_ID = str(JSON_RESPONSE['result'][0]['id'])
        debug_comment("Zone ID has been found. It is: {}".format(ZONE_ID))
        
        return ZONE_ID

# Function to get the CloudFlare DNS Zone A-Name record ID
def get_identifier_oldip_proxiedstate(ZONE_ID, EMAIL, API_KEY, HEADERS):
    GET_IDENTIFIER_URL = "https://api.cloudflare.com/client/v4/zones/{}/dns_records?type=A&name={}".format(ZONE_ID, WEB_ADDRESS)

    JSON_RESPONSE = request.get(GET_IDENTIFIER_URL, headers=HEADERS, jsonOut=True)

    debug_comment("checking for a change in IP")
    debug_comment("GET request being sent to: {}".format(GET_IDENTIFIER_URL))
    debug_comment("GET headers being sent: {}".format(unpack_dict(HEADERS)))

    if 'result' in JSON_RESPONSE:
        IDENTIFIER = str(JSON_RESPONSE['result'][0]['id'])
        OLD_IP = str(JSON_RESPONSE['result'][0]['content'])
        PROXIED = str(JSON_RESPONSE['result'][0]['proxied'])
        
        debug_comment("Identifier has been found. It is: {}".format(IDENTIFIER))
        debug_comment("Fetched the old IP. It is: {}".format(OLD_IP))
        debug_comment("Fetched whether to proxy or not: {}".format(PROXIED))

        if PROXIED == 'true' or PROXIED == 'True':
            PROXIED = True
        else:
            PROXIED = False
            
        return IDENTIFIER, OLD_IP, PROXIED
    else:
        print("There is likely a problem with your details. Please double check. If the problem persists, contact me and I'll do my best to help!")
        sys.exit(0)

# Function to check for a different current external IP, than the one currently stored in the CloudFlare DNS A-Name record
def check_for_change(ZONE_ID, WEB_ADDRESS, CURRENT_IP, OLD_IP, EMAIL, API_KEY, HEADERS):
    CHECK_A_NAME_RECORD_CHANGE_URL = "https://api.cloudflare.com/client/v4/zones/{}/dns_records?type=A&name={}&content={}&page=1&per_page=20&order=type&direction=desc&match=all".format(ZONE_ID, WEB_ADDRESS, CURRENT_IP)

    JSON_RESPONSE = request.get(CHECK_A_NAME_RECORD_CHANGE_URL, headers=HEADERS, jsonOut=True)

    debug_comment("checking for a change in IP")
    debug_comment("GET request being sent to: {}".format(CHECK_A_NAME_RECORD_CHANGE_URL))
    debug_comment("GET headers being sent: {}".format(unpack_dict(HEADERS)))
    
    if 'result_info' in JSON_RESPONSE:
        MATCHES_FOUND = str(JSON_RESPONSE['result_info']['count'])
        debug_comment('Matches found: {}'.format(MATCHES_FOUND))

        if MATCHES_FOUND == '1':
            print("Check completed, no update needed! (Current IP: {})".format(CURRENT_IP))
            UPDATE_NEEDED = False
        else:
            print("Check completed, update reqired! (Old IP: {}, New IP: {})".format(OLD_IP, CURRENT_IP))
            UPDATE_NEEDED = True

        return UPDATE_NEEDED

    else:
        print("There is likely a problem with your details. Please double check. If the problem persists, contact me and I'll do my best to help")
        sys.exit(0)

# Function to update the CloudFlare DNS A-Name record to the new external IP
def update_record(ZONE_ID, WEB_ADDRESS, CURRENT_IP, EMAIL, API_KEY, IDENTIFIER, HEADERS, PROXIED):
    UPDATE_A_NAME_RECORD_URL = "https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}".format(ZONE_ID, IDENTIFIER)

    PAYLOAD = {'type': 'A','name': WEB_ADDRESS,'content': CURRENT_IP,'ttl': 1,'proxied': bool(PROXIED)}

    r_status, r_reason = request.put(UPDATE_A_NAME_RECORD_URL, data=PAYLOAD, headers=HEADERS)

    debug_comment("updating the stored A NAME record at CloudFlare")
    debug_comment("GET request being sent to: {}".format(UPDATE_A_NAME_RECORD_URL))
    debug_comment("GET headers being sent: {}".format(unpack_dict(PAYLOAD)))
    debug_comment("GET headers being sent: {}".format(unpack_dict(HEADERS)))

    

    if str(r_status) == "200":
        print("Update completed successfully")
    else:
        print("Record update failed with following reason:\n{}".format(r_reason))
        sys.exit(0)

# ********* MAIN PROGRAM ***********
VAR_LIST = ['API_KEY','EMAIL','WEB_ADDRESS','FETCH_FREQUENCY','REMOTE_CHECK','DEBUG']
REQ_VARS = VAR_LIST[0:3]
MISS_VAR = []

# Setup argparser
config = configparser.ConfigParser()
parser = argparse.ArgumentParser(description='Cloudflare DDNS updater!', conflict_handler='resolve')
parser.add_argument('--key', '-k', type=str, action="store", dest="API_KEY", help="This is your Cloudflare API key. Can be found at:\nCloudflare -> My Profile -> API Keys -> Global API Key -> View.\n(KEEP THIS SAFE! DO NOT SHARE!)", required=False)
parser.add_argument('--email', '-e', type=str, action="store", dest="EMAIL", help="This is the email associated to the cloudflare account that your domain is registered too", required=False)
parser.add_argument('--address', '-a', type=str, action="store", dest="WEB_ADDRESS", help="This is the standard domain name that your record is associated too. EG: jammyworld.com", required=False)
parser.add_argument('--freq', '-f', type=int, action="store", dest="FETCH_FREQUENCY", default=5, help="This is the time in minutes that the scipt will pause between each check\nDEFAULT: 5", required=False)
parser.add_argument('--remote', '-r', type=str, action="store", dest="REMOTE_CHECK", default='1.1.1.1', help="This is a remote IP that will be pinged to ensure you're online.\nDEFAULT: 1.1.1.1", required=False)
parser.add_argument('--proxy', '-p', type=bool, action="store", dest="PROXY_OVERRIDE", help="This will push an override to your current Cloudflare proxied state.\nTrue - Force proxied state on\nFalse - Force proxied state off\nDEFAULT: None", required=False)
parser.add_argument('--debug', '-d', type=bool, action="store", dest="DEBUG", default=False, help="This will enable or disable a verbose logging output.\nTrue - On\nFalse - Off\nDEFAULT: False", required=False)
parser.add_argument('--single', '-s', type=bool, action="store", dest="SINGLE_RUN", default=True, help="This will only run the program once, perfect for cron jobs with command line useage.\nDEFAULT: True", required=False)

# Get any results and dump to vars
parsedArgs = parser.parse_args()
argVars = vars(parsedArgs)
debug_comment(argVars)

debug_comment("checking for required parsed args!")
for req in REQ_VARS:
    debug_comment("checking for parsed {}".format(req))
    #if req not in argVars:
    if argVars[req] == None: # Check for each variable having data
        debug_comment("{} not found in parsed args".format(req)) 
        MISS_VAR.append(req) #Note down a missing variable
if (len(MISS_VAR) < len(REQ_VARS)) and (len(MISS_VAR) != 0):
    debug_comment("Missing vars found {}. But still parsed args".format(MISS_VAR))
    for miss in MISS_VAR:
        print("Missing {} args".format(miss))
    sys.exit(0)
elif len(MISS_VAR) == 0:
    debug_comment("no missing vars. Choosing parsed args over config.ini")
    if not DEBUG: # Simple check to see if script has DEBUG = True, and dont allow the default of parser to override this, due to the point in the program this is set.
        DEBUG = argVars['DEBUG']
    del argVars['DEBUG']
    
    globals().update(argVars)
else:
    debug_comment("no parsed args found. Trying for ini file")
    try:
        debug_comment("trying to open the config.ini")
        open('config.ini', 'r')
    except FileNotFoundError:
        debug_comment("config file was not found. Setting up new file")
        print("Creating config file...")
        config['settings'] = {'FETCH_FREQUENCY' : 5,
                              'REMOTE_CHECK': '1.1.1.1'}
                              #'PROXIED_OVERRIDE': None} NEEDS WORK
        config['account'] = {'API_KEY': '',
                             'EMAIL': '',
                             'WEB_ADDRESS': ''}

        debug_comment("writing the file")
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        print("Your config file wasn't found, a new one has been created. Find the file and add your info.\nThis should only ever have to be done once!")
        sys.exit(0)
    else:
        debug_comment("config file found. Opening, reading, and setting variables")
        config.read('config.ini')
        try:
            FETCH_FREQUENCY = int(config['settings']['FETCH_FREQUENCY'])
            #PROXIED_OVERRIDE = config['settings']['PROXIED_OVERRIDE'] NEEDS WORK. Need to store a bool AND none
            REMOTE_CHECK = str(config['settings']['REMOTE_CHECK'])
            
            WEB_ADDRESS = str(config['account']['WEB_ADDRESS'])
            API_KEY = str(config['account']['API_KEY'])
            EMAIL = str(config['account']['EMAIL'])
        except KeyError as K_E:
            K_E = str(K_E).lower()
            print("You have damaged your config.ini file, and the {} variable could not be found.\n\nPlease either delete the config.ini file and re-run the program, or manually add it back".format(K_E))
            sys.exit(0)

details_exist(VAR_LIST)
debug_comment("Single run: {}".format(SINGLE_RUN))

if not is_online(REMOTE_CHECK):
    print("Please ensure you are connected to the internet, and have access to cloudflares servers")
    sys.exit(0)

# Vars that need to be run once, or a first time outside of the loop.
CURRENT_IP = get_current_ip()
HEADERS = {"X-Auth-Email": str(EMAIL),
           "X-Auth-Key": str(API_KEY),
           "Content-Type": "application/json"}

ZONE_ID = get_zone_id(WEB_ADDRESS, EMAIL, API_KEY, HEADERS)
IDENTIFIER, OLD_IP, PROXIED = get_identifier_oldip_proxiedstate(ZONE_ID, EMAIL, API_KEY, HEADERS)

if PROXIED_OVERRIDE != None:
    PROXIED = PROXIED_OVERRIDE
    debug_comment("PROXIED has been overridden and set to: {}".format(PROXIED))

# Main loop to run, checking for updated and, if needed, updating the CloudFlare DNS A-Name record. Then sleeping for 2 minutes.
while True:
    if is_online(REMOTE_CHECK):
        OLD_IP = CURRENT_IP
        CURRENT_IP = get_current_ip()
        UPDATE_NEEDED = check_for_change(ZONE_ID, WEB_ADDRESS, CURRENT_IP, OLD_IP, EMAIL, API_KEY, HEADERS)

        if UPDATE_NEEDED:
            update_record(ZONE_ID, WEB_ADDRESS, CURRENT_IP, EMAIL, API_KEY, IDENTIFIER, HEADERS, PROXIED) #HERE

    else:
        print("Not online currently. Awaiting for connection to cloudflare servers to resume...")
    if not SINGLE_RUN:
        #time.sleep(round((FETCH_FREQUENCY*60),None))
        time.sleep(int(FETCH_FREQUENCY*60))
    else:
        break
sys.exit(0)
