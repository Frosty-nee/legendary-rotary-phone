#! python

import sys

import requests
import sqlite3
import json

import config

def fetch_system_data():
	r = requests.get('https://esi.evetech.net/latest/fw/systems/?datasource=tranquility')
	return r.json()

if __name__ == '__main__':
	conn = sqlite3.connect('sqlite-latest.sqlite')
	curs = conn.cursor()
        factions = {'caldari': 500001, 'minmatar': 500002, 'amarr': 500003, 'gallente': 500004}
	faction_NPC_corp = {500001: 1000180, 500002: 1000182, 500004: 1000181, 500003: 1000179}
	if config.default_faction == 0:
		mission_group = input("FW faction to run missions for: ").lower()
		if mission_group in faction_NPC_corp.keys():
                        faction = factions[mission_group]
			corp = faction_NPC_corp[faction]
		else: 
			print("faction not found")
			sys.exit()
	else: 
            faction = config.default_faction
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
        print(available_mission_stations)

