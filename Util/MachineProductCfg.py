import json
import sys
import xmltodict


# Open the MachineProductCfg.xml file in the root directory
try:
    with open("MachineProductCfg.xml", mode = 'r', encoding= 'utf-8') as MPCxml:
        MPCdict = xmltodict.parse(MPCxml.read())
        MPCdump = json.dumps(MPCdict)
        data = json.loads(MPCdump)
except Exception as e:
    print(e)
    sys.exit("There was an error opening your MachineProductCfg.xml. Is the file in the root folder?")
    

def getPrimaryLocations():
    """ Returns all of the primary locations in the MachineProductCfg """
    locationIds = []
    # iterate on the json data and grab anything that has PrimaryLocation.
    # Also needs to return anything in the Regional area.
    for i in data['Config']['ConfigDef']['ConfigItems']['ConfigItem']:
        if "PrimaryLocation" in i['@key'] and i['@value'] != "":
            # Split the string up
            locationIds.append(i['@value'].split("_")[2])

        if "NearbyLocation" in i['@key'] and i['@value'] != "":
            locationIds.append(i['@value'].split("_")[2])

    return locationIds

def getMetroCities():
    """ Returns all Metro Map locations in the MPC """
    locationIds = []

    for i in data['Config']['ConfigDef']['ConfigItems']['ConfigItem']:
        if 'MetroMapCity' in i['@key'] and i['@value'] != "":
            locationIds.append(i['@value'].split("_")[2])

    return locationIds

def getTideStations():
    """ Returns all of the tide stations present in the MachineProductCfg """
    stations = []
    for i in data['Config']['ConfigDef']['ConfigItems']['ConfigItem']:
        if "TideStation" in i['@key'] and i['@value'] != "":
            stations.append(i['@value'].split("_")[2])

    return stations

def getAirportCodes():
    """ Returns all of the airport identifiers present in the MachineProductCfg """
    airports = [
        'ATL',
        'LAX',
        'ORD',
        'DFW',
        'JFK',
        'DEN',
        'SFO',
        'CLT',
        'LAS',
        'PHX',
        'IAH',
        'MIA',
        'SEA',
        'EWR',
        'MCO',
        'MSP',
        'DTW',
        'BOS',
        'PHL',
        'LGA',
        'FLL',
        'BWI',
        'IAD',
        'MDW',
        'SLC',
        'DCA',
        'HNL',
        'SAN',
        'TPA',
        'PDX',
        'STL',
        'HOU',
        'BNA',
        'AUS',
        'OAK',
        'MSY',
        'RDU',
        'SJC',
        'SNA',
        'DAL',
        'SMF',
        'SAT',
        'RSW',
        'PIT',
        'CLE',
        'IND',
        'MKE',
        'CMH',
        'OGG',
        'PBI',
        'BDL',
        'CVG',
        'JAX',
        'ANC',
        'BUF',
        'ABQ',
        'ONT',
        'OMA',
        'BUR',
        'OKC',
        'MEM',
        'PVD',
        'RIC',
        'SDF',
        'RNO',
        'TUS',
        'CHS',
        'ORF',
        'PWM',
        'GRR',
        'BHM',
        'LIT',
        'DSM',
        'FAR',
        'FSD',
        'ICT',
        'LBB',
        'BIL',
        'BOI',
        'GEG'
    ]
    for i in data['Config']['ConfigDef']['ConfigItems']['ConfigItem']:
        if "Airport" in i['@key'] and i['@value'] != "" and not i['@value'] in airports:
            # Split the string up
            airports.append(i['@value'].split("_")[2])

    return airports

def getAlertZones():
    """ Returns a list of zones present in the MachineProductCfg """
    zones = []
    for i in data['Config']['ConfigDef']['ConfigItems']['ConfigItem']:
        if i['@key'] == "primaryZone" and i['@value'] != "":
            zones.append(i['@value'])   # This should only be one value

        if i['@key'] == "secondaryZones" and i['@value'] != "":
            for x in i['@value'].split(','):
                zones.append(x)

        if i['@key'] == 'primaryCounty' and i['@value'] != "":
            zones.append(i['@value'])
 
        if i['@key'] == "secondaryCounties" and i['@value'] != "":
            for x in i['@value'].split(','):
                zones.append(x)

    return zones