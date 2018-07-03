# CloudflareDDNSUpdater
A simple tool to update your Cloudflare DDNS automatically.

## YOU MUST HAVE PYTHON3.5 OR GREATER, AND HAVE REQUESTS MODULE (This will be fixed at a later date)

## HOW TO USE
1. [Download this script](https://github.com/james3126/CloudflareDDNSUpdater/archive/master.zip)
2. Open the `CloudflareDDNSUpdater.py` file
3. Edit the following lines
```
API_KEY = ""
EMAIL = ""
WEB_ADDRESS = ""
```
4. (OPTIONAL) Edit the following lines
```
AUTO_FETCH_TIME_IN_MINUTES = 2
PROXIED_OVERRIDE = None
DEBUG = False
```
5. Install requirements for this script by either
   - Running `pip install -requirements.txt`
   - Running the `EzReqInstaller.py` script by either
      - Double clicking on `EzReqInstaller.py`
      - Running `python3 EzReqInstaller.py` via command line
6. Run the script via
   - Double clicking on the file
   - Running `python3 CloudflareDDNSUpdater.py` via command line
