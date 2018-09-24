# HTTP GET/PUT module without 'requests' - James Kerley 2018
import urllib.request
import urllib3
from urllib.parse import urlencode
urllib3.disable_warnings()
import json

class request:
    def get(url, headers=None, jsonOut=False):
        if headers != None:
            req = urllib.request.Request(url, headers=headers)
        else:
            req = urllib.request.Request(url)
        raw_response = urllib.request.urlopen(req)
        response = raw_response.read().decode('utf-8')
        if jsonOut:
            json_obj = json.loads(response)
            return json_obj
        else:
            return response

    def put(url, data, headers=None):
        if headers != None:
            http = urllib3.PoolManager()
            encoded_body = json.dumps(data)

            r=http.request("PUT",url,headers=headers,body=encoded_body)
            x=json.loads(r.data.decode("utf-8"))

            return x['success']
