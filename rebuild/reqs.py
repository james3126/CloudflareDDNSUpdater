# HTTP GET/PUT module without 'requests' - James Kerley 2019
import urllib.request
import json

class request:
    def get(url, headers=None, jsonOut=False):
        if headers != None:
            req = urllib.request.Request(url, headers=headers)
        else:
            req = urllib.request.Request(url)

        try:
            raw_response = urllib.request.urlopen(req)
        except urllib.request.HTTPError as e:
            print("ERROR: {}\nERROR: It is likely your details are inccorect! Please check and try again!".format(e))
            exit()

        response = raw_response.read().decode('utf-8')
        if jsonOut:
            json_obj = json.loads(response)
            return json_obj
        else:
            return response

    def put(url, data, headers=None):
        if headers != None:
            params = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(url, data=params, headers=headers, method="PUT")

            response = urllib.request.urlopen(req)
            #r = response.read().decode("utf-8")

            return response.status, response.reason
