# CloudFlare DNS record updater v1.0 - James Kerley 2018
import requests
import json
import time
import sys
import os

# Fill out your information here!
API_KEY = "" # Your Cloudflare API key -> Cloudflare -> My Profile -> API Keys -> Global API Key -> View (KEEP THIS SAFE! DO NOT SHARE)
EMAIL = "" # Your E-Mail registered to your Cloudflare account
WEB_ADDRESS = "" # Should be your standard domain name E.G, 'jammyworld.com' -> ADVANCED: Can be the name of any A-Name record!
AUTO_FETCH_TIME_IN_MINUTES = 2 # Default 2 minutes (120 seconds)

# Only enable if you are debugging. This is verbose and dumps lots of information that you dont normally need
DEBUG = False # True/False -> Default False

# ---- You DONT need to touch anything below here for normal operation ----

# Function for the closely repeated REQUESTS DEBUG comments
def debug_comment_r(r):
    print("\nDEBUG: status code:", r.status_code)
    print("\nDEBUG: encoding:", r.encoding)
    print("\nDEBUG: text:", r.text)
    print("\nDEBUG: json:", r.json())

# Function for custom DEBUG comments
def debug_comment(e):
    print("\nDEBUG: "+str(e))

# Function to print out a dict in a pretty way for DEBUG
def unpack_dict(dic):
    for key, value in sorted(HEADERS.items(), key=lambda x: x[0]):
        return "{} : {}".format(key, value)

# Function to get the current external IP
def get_current_ip():
    CURRENT_IP = requests.get('https://api.ipify.org').text

    if DEBUG:
        debug_comment("getting the current ip using ipify.org api")
        debug_comment("IP found: "+str(CURRENT_IP))
        
    return CURRENT_IP

# Function to get the CloudFlare DNS Zone ID
def get_zone_id(WEB_ADDRESS, EMAIL, API_KEY, HEADERS):
    GET_ZONE_ID_URL = "https://api.cloudflare.com/client/v4/zones?name="+str(WEB_ADDRESS)+"&status=active&page=1&per_page=20&order=status&direction=desc&match=all"

    r = requests.get(GET_ZONE_ID_URL, headers=HEADERS)

    if DEBUG:
        debug_comment("getting the zone ID from CloudFlare")
        debug_comment("GET request being sent to: "+GET_ZONE_ID_URL)
        debug_comment("GET headers being sent: "+unpack_dict(HEADERS))
        debug_comment_r(r)

    JSON_RESPONSE = r.json()
    if 'result' in JSON_RESPONSE:
        ZONE_ID = str(JSON_RESPONSE['result'][0]['id'])
        if DEBUG:
            debug_comment("Zone ID has been found. It is: "+ZONE_ID)

        return ZONE_ID

# Function to get the CloudFlare DNS Zone A-Name record ID
def get_identifier_and_old_ip(ZONE_ID, EMAIL, API_KEY, HEADERS):
    GET_IDENTIFIER_URL = "https://api.cloudflare.com/client/v4/zones/"+str(ZONE_ID)+"/dns_records?type=A&name="+str(WEB_ADDRESS)

    r = requests.get(GET_IDENTIFIER_URL, headers=HEADERS)

    if DEBUG: 
        debug_comment("checking for a change in IP")
        debug_comment("GET request being sent to: "+GET_IDENTIFIER_URL)
        debug_comment("GET headers being sent: "+unpack_dict(HEADERS))
        debug_comment_r(r)

    JSON_RESPONSE = r.json()
    if 'result' in JSON_RESPONSE:
        IDENTIFIER = str(JSON_RESPONSE['result'][0]['id'])
        OLD_IP = str(JSON_RESPONSE['result'][0]['content'])
        if DEBUG:
            debug_comment("Identifier has been found. It is: "+IDENTIFIER)
            debug_comment("Fetched the old IP. It is: "+OLD_IP)
            
        return IDENTIFIER, OLD_IP
    else:
        print("There is likely a problem with your details. Please double check. If the problem persists, contact me and I'll do my best to help!")
        sys.exit(0)

# Function to check for a different current external IP, than the one currently stored in the CloudFlare DNS A-Name record
def check_for_change(ZONE_ID, WEB_ADDRESS, CURRENT_IP, OLD_IP, EMAIL, API_KEY, HEADERS):
    CHECK_A_NAME_RECORD_CHANGE_URL = "https://api.cloudflare.com/client/v4/zones/"+str(ZONE_ID)+"/dns_records?type=A&name="+str(WEB_ADDRESS)+"&content="+str(CURRENT_IP)+"&page=1&per_page=20&order=type&direction=desc&match=all"

    r = requests.get(CHECK_A_NAME_RECORD_CHANGE_URL, headers=HEADERS)

    if DEBUG:
        debug_comment("checking for a change in IP")
        debug_comment("GET request being sent to: "+CHECK_A_NAME_RECORD_CHANGE_URL)
        debug_comment("GET headers being sent: "+unpack_dict(HEADERS))
        debug_comment_r(r)

    JSON_RESPONSE = r.json()
    if 'result_info' in JSON_RESPONSE:
        MATCHES_FOUND = str(JSON_RESPONSE['result_info']['count'])
        if DEBUG:
            print('Matches found: '+MATCHES_FOUND)

        if MATCHES_FOUND == '1':
            print("Check completed, no update needed! (Current IP: "+CURRENT_IP+")")
            UPDATE_NEEDED = False
        else:
            print("Check completed, update reqired! (Old IP: "+OLD_IP+", New IP: "+CURRENT_IP+")")
            UPDATE_NEEDED = True

        return UPDATE_NEEDED

    else:
        print("There is likely a problem with your details. Please double check. If the problem persists, contact me and I'll do my best to help")
        sys.exit(0)


# Function to update the CloudFlare DNS A-Name record to the new external IP
def update_record(ZONE_ID, WEB_ADDRESS, CURRENT_IP, EMAIL, API_KEY, IDENTIFIER, HEADERS):
    UPDATE_A_NAME_RECORD_URL = 'https://api.cloudflare.com/client/v4/zones/'+str(ZONE_ID)+'/dns_records/'+str(IDENTIFIER)

    PAYLOAD = {'type': 'A','name': WEB_ADDRESS,'content': CURRENT_IP,'ttl': 1,'proxied': False}

    r = requests.put(UPDATE_A_NAME_RECORD_URL, data=json.dumps(PAYLOAD), headers=HEADERS)

    if DEBUG:
        debug_comment("updating the stored A NAME record at CloudFlare")
        debug_comment("GET request being sent to: "+UPDATE_A_NAME_RECORD_URL)
        debug_comment("GET headers being sent: "+unpack_dict(payload))        
        debug_comment("GET headers being sent: "+unpack_dict(HEADERS))
        debug_comment_r(r)

    if str(r.status_code) == "200":
        print("Update completed successfully")
    else:
        print("There has been an error. If the problem persists, contact me and I'll do my best to help!")
        sys.exit(0)

# Vars that need to be run once, or a first time outside of the loop.
CURRENT_IP = get_current_ip()
HEADERS = {"X-Auth-Email": str(EMAIL),
           "X-Auth-Key": str(API_KEY),
           "Content-Type": "application/json"}

ZONE_ID = get_zone_id(WEB_ADDRESS, EMAIL, API_KEY, HEADERS)
IDENTIFIER, OLD_IP = get_identifier_and_old_ip(ZONE_ID, EMAIL, API_KEY, HEADERS)

# Main loop to run, checking for updated and, if needed, updating the CloudFlare DNS A-Name record. Then sleeping for 2 minutes.
while True:
    OLD_IP = CURRENT_IP
    CURRENT_IP = get_current_ip()
    UPDATE_NEEDED = check_for_change(ZONE_ID, WEB_ADDRESS, CURRENT_IP, OLD_IP, EMAIL, API_KEY, HEADERS)

    if UPDATE_NEEDED:
        update_record(ZONE_ID, WEB_ADDRESS, CURRENT_IP, EMAIL, API_KEY, IDENTIFIER, HEADERS)

    time.sleep(round((AUTO_FETCH_TIME_IN_MINUTES*60),1))
