# HTTP GET module without 'requests' - James Kerley 2018
import urllib.request
import json

class request:
    def get_request(url, headers=None, json=False):
        if headers != None:
            req = urllib.request.Request(url)
        else:
            req = urllib.request.Request(url, headers)
        raw_response = urllib.request.urlopen(req)
        reponse = raw_response.read().decode('utf-8')
        if json:
            json_obj = json.loads(response)
            return json_obj
        else:
            return reponse
