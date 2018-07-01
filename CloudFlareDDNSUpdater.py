import requests
import json
import time
import sys
import os

# Fill out your information here!
API_KEY = ""
EMAIL = ""
WEB_ADDRESS = ""

# Only enable if you are debugging. This is verbose and dumps lots of information that you dont normally need
DEBUG = True

# First, get the DNS records ID
# GET_DNS_RECORD_ID_URL = "https://api.cloudflare.com/client/v4/zones/"+str(ZONE_ID)+"/dns_records?type=A&name="+str(WEB_ADDRESS)+"&page=1&per_page=20&order=type&direction=desc&match=all"

def get_current_ip():
    CURRENT_IP = requests.get('https://api.ipify.org').text

    if DEBUG:
        print("DEBUG: getting the current ip using ipify.org api")
        print("\nDEBUG: IP found: "+str(CURRENT_IP))
        
    return CURRENT_IP

def get_zone_id(WEB_ADDRESS, EMAIL, API_KEY):
    GET_ZONE_ID_URL = "https://api.cloudflare.com/client/v4/zones?name="+str(WEB_ADDRESS)+"&status=active&page=1&per_page=20&order=status&direction=desc&match=all"
    headers = {"X-Auth-Email": str(EMAIL),
               "X-Auth-Key": str(API_KEY),
               "Content-Type": "application/json"}

    r = requests.get(GET_ZONE_ID_URL, headers=headers)

    if DEBUG:
        print("DEBUG: getting the zone ID from CloudFlare")
        print("\nDEBUG: GET request being sent to: "+GET_ZONE_ID_URL)
        print("\nDEBUG: GET request headers:\n\t'X-Auth-Email': "+str(EMAIL)+"\n\t'X-Auth-Key': "+str(API_KEY)+"\n\t'Content-Type': 'application/json'")
        print("\nDEBUG: status code:", r.status_code)
        print("\nDEBUG: encoding:", r.encoding)
        print("\nDEBUG: text:", r.text)
        print("\nDEBUG: json:", r.json())

    JSON_RESPONSE = r.json()
    if 'result' in JSON_RESPONSE:
        ZONE_ID = str(JSON_RESPONSE['result'][0]['id'])
        if DEBUG:
            print("\nDEBUG: Zone ID has been found. It is: "+ZONE_ID)

        return ZONE_ID

def check_for_change(ZONE_ID, WEB_ADDRESS, CURRENT_IP, OLD_IP, EMAIL, API_KEY):
    CHECK_A_NAME_RECORD_CHANGE_URL = "https://api.cloudflare.com/client/v4/zones/"+str(ZONE_ID)+"/dns_records?type=A&name="+str(WEB_ADDRESS)+"&content="+str(CURRENT_IP)+"&page=1&per_page=20&order=type&direction=desc&match=all"    
    headers = {"X-Auth-Email": str(EMAIL),
               "X-Auth-Key": str(API_KEY),
               "Content-Type": "application/json"}

    r = requests.get(CHECK_A_NAME_RECORD_CHANGE_URL, headers=headers)

    if DEBUG:
        print("\n\nDEBUG: checking for a change in IP")
        print("\nDEBUG: GET request being sent to: "+CHECK_A_NAME_RECORD_CHANGE_URL)
        print("\nDEBUG: GET request headers:\n\t'X-Auth-Email': "+str(EMAIL)+"\n\t'X-Auth-Key': "+str(API_KEY)+"\n\t'Content-Type': 'application/json'")
        print("\nDEBUG: status code:", r.status_code)
        print("\nDEBUG: encoding:", r.encoding)
        print("\nDEBUG: text:", r.text)
        print("\nDEBUG: json:", r.json())
        print("\n")

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

def get_identifier(ZONE_ID, EMAIL, API_KEY):
    GET_IDENTIFIER_URL = "https://api.cloudflare.com/client/v4/zones/"+str(ZONE_ID)+"/dns_records?type=A&name="+str(WEB_ADDRESS)
    headers = {"X-Auth-Email": str(EMAIL),
               "X-Auth-Key": str(API_KEY),
               "Content-Type": "application/json"}

    r = requests.get(GET_IDENTIFIER_URL, headers=headers)

    if DEBUG: 
        print("\n\nDEBUG: checking for a change in IP")
        print("\nDEBUG: GET request being sent to: "+GET_IDENTIFIER_URL)
        print("\nDEBUG: GET request headers:\n\t'X-Auth-Email': "+str(EMAIL)+"\n\t'X-Auth-Key': "+str(API_KEY)+"\n\t'Content-Type': 'application/json'")
        print("\nDEBUG: status code:", r.status_code)
        print("\nDEBUG: encoding:", r.encoding)
        print("\nDEBUG: text:", r.text)
        print("\nDEBUG: json:", r.json())
        print("\n")

    JSON_RESPONSE = r.json()
    if 'result' in JSON_RESPONSE:
        IDENTIFIER = str(JSON_RESPONSE['result'][0]['id'])
        if DEBUG:
            print("\nDEBUG: Identifier has been found. It is: "+IDENTIFIER)

        return IDENTIFIER
    else:
        print("There is likely a problem with your details. Please double check. If the problem persists, contact me and I'll do my best to help!")
        sys.exit(0)

#ONLY FOR UPDATING
def update_record(ZONE_ID, WEB_ADDRESS, CURRENT_IP, EMAIL, API_KEY, IDENTIFIER):
    UPDATE_A_NAME_RECORD_URL = 'https://api.cloudflare.com/client/v4/zones/'+str(ZONE_ID)+'/dns_records/'+str(IDENTIFIER)

    payload = {'type': 'A','name': WEB_ADDRESS,'content': CURRENT_IP,'ttl': 1,'proxied': False}

    headers = {"X-Auth-Email": str(EMAIL),
               "X-Auth-Key": str(API_KEY),
               "Content-Type": "application/json"}

    r = requests.put(UPDATE_A_NAME_RECORD_URL, data=json.dumps(payload), headers=headers)

    if DEBUG:
        print("\n\nDEBUG: updating the stored A NAME record at CloudFlare")
        print("\nDEBUG: GET request being sent to: "+UPDATE_A_NAME_RECORD_URL)
        print("{\n\t'type': 'A',\n\t'name': '"+WEB_ADDRESS+"',\n\t'content': '"+CURRENT_IP+"',\n\t'ttl': 1,\n\t'proxied': false\n}")        
        print("\nDEBUG: GET request headers:\n\t'X-Auth-Email': "+str(EMAIL)+"\n\t'X-Auth-Key': "+str(API_KEY)+"\n\t'Content-Type': 'application/json'")
        print("\nDEBUG: status code:", r.status_code)
        print("\nDEBUG: encoding:", r.encoding)
        print("\nDEBUG: text:", r.text)
        print("\nDEBUG: json:", r.json())

    if str(r.status_code) == "200":
        print("Update completed successfully")
    else:
        print("There has been an error. If the problem persists, contact me and I'll do my best to help!")
        sys.exit(0)

# -- BEGINING OF PROGRAM --

CURRENT_IP = get_current_ip()
#CURRENT_IP = '10.100.1.10'
OLD_IP = CURRENT_IP # Move to outside of loop. Only update after run

ZONE_ID = get_zone_id(WEB_ADDRESS, EMAIL, API_KEY)
IDENTIFIER = get_identifier(ZONE_ID, EMAIL, API_KEY)

while True:
    UPDATE_NEEDED = check_for_change(ZONE_ID, WEB_ADDRESS, CURRENT_IP, OLD_IP, EMAIL, API_KEY)

    if UPDATE_NEEDED:
        update_record(ZONE_ID, WEB_ADDRESS, CURRENT_IP, EMAIL, API_KEY, IDENTIFIER)

    time.sleep(120)




responses = {200: 'OK',304: 'Not Modified',400: 'Bad Request',401: 'Unauthorized',403: 'Forbidden',405: 'Method Not Allowed',415: 'Unsupported Media Type',429: 'Too many requests'}
