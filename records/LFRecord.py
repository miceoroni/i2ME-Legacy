import sqlite3

# Make a connection to the LFRecord database
con = sqlite3.connect("records/LFRecord.db")
cur = con.cursor()


def getZip(locId: str):
    """ Returns the zip code for a given location """
    COMMAND = (f"SELECT zip2locId FROM lfrecord WHERE locId='{locId}'")
    cur.execute(COMMAND)
    return cur.fetchone()[0]

def getCoopId(locId: str):
    """ Returns the TWC co-op ID for a given location """
    COMMAND = (f"SELECT coopId FROM lfrecord WHERE locId='{locId}'")
    cur.execute(COMMAND)
    return cur.fetchone()[0]

def getEpaId(locId: str):
    """ Return the Air Quality station id for a given location. """
    COMMAND = (f"SELECT epaId FROM lfrecord WHERE locId='{locId}'")
    cur.execute(COMMAND)
    return cur.fetchone()[0]

def getPollenInfo(locId: str):
    """ Return the Pollen forecast id for a given location. """
    COMMAND = (f"SELECT pllnId FROM lfrecord WHERE locId='{locId}'")
    cur.execute(COMMAND)
    return cur.fetchone()[0]

def getLatLong(locId: str):
    """ Return the Pollen forecast id for a given location. """
    COMMAND = (f"SELECT lat,long FROM lfrecord WHERE locId='{locId}'")
    cur.execute(COMMAND)
    fetched = cur.fetchone()
    return fetched[0] + "/" + fetched[1]

def getLocationInfo(locId: str):
    pass

print(getCoopId('USAZ0278'))
print(getZip('USAZ0278'))
print(getLatLong('USAZ0278'))