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
	factions = {}
	faction_NPC_corp = {'caldari': 1000180, 'minmatar': 1000182, 'gallente': 1000181, 'amarr': 1000179}
	if config.default_faction == 0:
		faction = input("FW faction to run missions for: ").lower()
		if faction in faction_NPC_corp.keys():
			faction = faction_NPC_corp[faction]
		else: 
			print("faction not found")
			sys.exit()
	else: faction = config.default_faction
	curs.execute('''SELECT stationID, solarSystemID FROM staStations where corporationID = ?''', (faction, ))
	station_list = curs.fetchall()
	system_data = fetch_system_data()
	owned_systems = []
	for system in system_data:
		if system['occupier_faction_id'] == faction and system['owner_faction_id'] == faction:
			owned_systems.append(system['solar_system_id'])
	print(owned_systems)
	available_mission_stations = []
	for station in station_list: 
		if station[1] in owned_systems:
			available_mission_stations.append(station[0])
	print(available_mission_stations)

