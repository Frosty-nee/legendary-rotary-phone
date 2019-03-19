#! python3

import sys
import webbrowser

from datetime import datetime, timedelta
import base64
import requests
import sqlite3
import json
import toml


def fetch_system_data():
    r = requests.get('https://esi.evetech.net/latest/fw/systems/?datasource=tranquility')
    return r.json()

def get_auth_token():
    request_url = 'https://login.eveonline.com/oauth/authorize?response_type=code&redirect_uri=https://localhost/oauth-callback&client_id=3cb60c8043f243568073d6a1fe2594bb&scope=esi-location.read_location.v1%20esi-ui.write_waypoint.v1'
    #webbrowser.open(request_url)
    callback_url = input("copy paste the full callback url here:\n")
    authorization_token = callback_url.split('code=')[1]
    return authorization_token

def get_access_token(auth_code=None):
    if auth_code != None:
        request_url = 'https://login.eveonline.com/oauth/token'
        headers = {'Authorization': b'Basic ' + base64.b64encode(bytes(config['client_id'] + ':' + config['secret_key'], 'utf-8')), 'Content-Type': 'application/json'}
        data = {'grant_type': 'authorization_code', 'code': auth_code}
        r = requests.post(request_url, headers=headers, json=data)
        js = r.json()
        config['access_token'] = js['access_token']
        config['refresh_token']= js['refresh_token']
        config['access_token_expiry'] = datetime.utcnow() + timedelta(seconds=js['expires_in'])
        write_config(config)
        return
    if datetime.utcnow() > config['access_token_expiry']:
        print('access token expired, refreshing')



def get_config():
    try:
        with open('config.toml') as f:
            config = toml.loads(f.read())
            if 'client_id' not in config.keys():
                config['client_id'] = input('enter the application client id\n')
            if 'secret_key' not in config.keys():
                config['secret_key'] = input('enter the application secret key\n')
            write_config(config)
            return config
    except FileNotFoundError:
        print("config file doesn't exist, creating default configuration file")
        write_config({'default_faction':0})
        return get_config()


def write_config(config_dict):
    with open('config.toml', 'w') as f:
        toml.dump(config_dict, f)



if __name__ == '__main__':
    config = get_config()
    if 'access_token' in config.keys():
        get_access_token()
    else:
        get_access_token(get_auth_token())
    conn = sqlite3.connect('sqlite-latest.sqlite')
    curs = conn.cursor()
    factions = {'caldari': 500001, 'minmatar': 500002, 'amarr': 500003, 'gallente': 500004}
    faction_NPC_corp = {500001: 1000180, 500002: 1000182, 500004: 1000181, 500003: 1000179}
    if config['default_faction'] == 0:
        mission_group = input("FW faction to run missions for: ").lower()
        if mission_group in factions.keys():
            faction = factions[mission_group]
            corp = faction_NPC_corp[faction]
            set_default = input('set this as the default faction?[Y/n]: ').lower()
            if set_default == 'y' or set_default == '':
                config['default_faction'] = factions[mission_group]
                write_config(config)
        else: 
            print("faction not found")
            sys.exit()
    else: 
        faction = config['default_faction']
        corp = faction_NPC_corp[faction]

    curs.execute('''SELECT stationID, solarSystemID, security FROM staStations where corporationID = ?''', (corp, ))
    station_list = curs.fetchall()
    system_data = fetch_system_data()
    owned_systems = []
    for system in system_data:
        if system['occupier_faction_id'] == faction:
            owned_systems.append(system['solar_system_id'])
    available_mission_stations = []
    for station in station_list: 
        if station[1] in owned_systems or station[2] >= 0.50:
            available_mission_stations.append(station[0])

