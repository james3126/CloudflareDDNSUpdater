# CloudflareDDNSUpdater
A simple tool to update your Cloudflare DDNS automatically.

## YOU MUST HAVE PYTHON3.5 OR GREATER.

#### This repo is currently under LOTS of active development. Please either keep ontop of updates, or star the repo and come back in a few days time once a full release has been made (I expect bugs at the moment, and keep applying fixes constantly. Feel free to inform me of any you find)

## HOW TO USE
1. [Download this script](https://github.com/james3126/CloudflareDDNSUpdater/archive/master.zip)

2. Install requirements for this script by either (Soon To Be Legacy)
   - Running `pip install -r requirements.txt`
   - Running the `EzReqInstaller.py` script by either
      - Double clicking on `EzReqInstaller.py`
      - Running `python3 EzReqInstaller.py` via command line
      
3. Run the script via
   - Double clicking on the file
   - Running `python3 CloudflareDDNSUpdater.py` via command line
   
4. It should close. You can now locate the config.ini file, and place your details in:
   - `auto_fetch_time_in_minutes =` | How often the script will run (You should not need to make this any shorter)
      - Default `5`
   - `remote_check =` | A remote servers IP to ping, to ensure the local machine is connected to the internet (Leave this as default as it's pinging cloudflares DNS, and will make sure both you and cloudflare are online)
      - Default `1.1.1.1`
   - `api_key =` | Your Cloudflare API key. Can be found at: Cloudflare -> My Profile -> API Keys -> Global API Key -> View. (KEEP THIS SAFE! DO NOT SHARE)
   - `email =` | Your E-Mail that is registered to your Cloudflare account
   - `web_address =` | Should be your standard domain name E.G, 'jammyworld.com' (ADVANCED: Can be the name of any A-Name record)   

5. (OPTIONAL) Open up `CloudflareDDNSUpdater.py` and edit the following lines to your liking
   - `PROXIED_OVERRIDE =` | Chooses wether to override your current Cloudflare record proxied state (Goes through Cloudflare servers). True will force enable, False will force disable, None will leave as your current state and wont override.
      - Default `None`
   - `DEBUG =` | Turns on a verbose logging. Not useful unless you're me, or editing the code.
      - Default `False`

6. Run the script via
   - Double clicking on the file
   - Running `python3 CloudflareDDNSUpdater.py` via command line


#### Future updates
- [x] Config file to reduce copying over details with each update
- [ ] Update notifier at script run
- [ ] Auto-update via git grabbing
- [ ] Allow mulitple A name records
- [ ] Allow multiple types of records
- [ ] GUI for novice or users who want one
