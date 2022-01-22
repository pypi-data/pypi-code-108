import random

#DD
def Latitude(decimals=2):
    lat = round(random.uniform(-90,90),decimals)
    return lat

def Longitude(decimals=2):
    lon = round(random.uniform(-180,180),decimals)
    return lon

def DD(decimals=2):
    Lat = Latitude(decimals)
    Lon = Longitude(decimals)
    return Lat, Lon

def DDstring(decimals=2):
    DD = str(Latitude(decimals)) + " " + str(Longitude(decimals))
    return DD

#DDM/DMM
def DDMLatitude(decimals=2):
    degrees = random.randint(0,89)
    decimalMinutes = round(random.uniform(0,60),decimals)
    return degrees, decimalMinutes

def DMMLatitude(decimals=2):
    D,DM = DDMLatitude(decimals)
    return D,DM

def DDMLatitudeString(decimals=2):
    D,DM = DDMLatitude(decimals)
    S = str(D)+" "+str(DM)
    return S

def DMMLatitudeString(decimals=2):
    D = DDMLatitudeString(decimals)
    return D

def DDMLongitude(decimals=2):
    degrees = random.randint(0,179)
    decimalMinutes = round(random.uniform(0,60),decimals)
    return degrees, decimalMinutes

def DMMLongitude(decimals=2):
    D,DM = DDMLongitude(decimals)
    return D,DM

def DDMLongitudeString(decimals=2):
    D,DM = DDMLongitude(decimals)
    S = str(D)+" "+str(DM)
    return S

def DMMLongitudeString(decimals=2):
    D = DDMLongitudeString(decimals)
    return D

def DDMstring(decimals=2):
    a = DDMLongitudeString(decimals)+" "+ DDMLatitudeString(decimals)
    return a

def DMMstring(decimals=2):
    D = DDMstring(decimals)
    return D

def DDM(decimals=1):
    lat = str(DDMLatitudeString(decimals))
    lon = str(DDMLongitudeString(decimals))
    return lat, lon

def DMM(decimals=1):
    lat,lon = DDM(decimals)
    return lat, lon
    
#DMS
def DMSLatitude(decimals=1):
    degrees = random.randint(-89,89)
    minutes = random.randint(0,59)
    seconds = round(random.uniform(0,60),decimals)
    return degrees,minutes,seconds

def DMSLongitude(decimals=1):
    degrees = random.randint(-179,179)
    minutes = random.randint(0,59)
    seconds = round(random.uniform(0,60),decimals)
    return degrees,minutes,seconds

def DMSLatitudeString(decimals=1):
    null,minutes,seconds = DMSLatitude(decimals)
    degrees = random.randint(0,89)
    direction = random.randint(0,1)
    if direction == 0:
        NS = "S"
    else:
        NS = "N"
    final = str(degrees) + "°" + str(minutes) + "'" + str(seconds) + '"' + str(NS)
    return final
    
def DMSLongitudeString(decimals=1):
    null,minutes,seconds = DMSLongitude(decimals)
    degrees = random.randint(0,179)
    direction = random.randint(0,1)
    if direction == 0:
        EW = "E"
    else:
        EW = "W"
    final = str(degrees) + "°" + str(minutes) + "'" + str(seconds) + '"' + str(EW)
    return final

def DMS(decimals=1):
    lat = str(DMSLatitudeString(decimals))
    lon = str(DMSLongitudeString(decimals))
    return lat, lon

def DMSstring(decimals=1):
    DNS = DMSLatitudeString(decimals) + " " + DMSLongitudeString(decimals)
    return DNS

def Debug():
    print("DD")
    print("Latitude(2):",Latitude(2))
    print("Longitude(2):",Longitude(2))
    print("DD(2):",DD(2))
    print("DDstring(2):",DDstring(2))
    
    print("\nDDM/DMM LAT")
    print("DDMLatitude(2):",DDMLatitude(2))
    print("DMMLatitude(2):",DMMLatitude(2))
    print("DDMLatitudeString(2):",DDMLatitudeString(2))
    print("DMMLatitudeString(2):",DMMLatitudeString(2))

    print("\nDDM/DMM LON")
    print("DDMLongitude(2):",DDMLongitude(2))
    print("DMMLongitude(2):",DMMLongitude(2))
    print("DDMLongitudeString(2):",DDMLongitudeString(2))
    print("DMMLongitudeString(2):",DMMLongitudeString(2))
    
    print("\nDDM/DMM")
    print("DDM(2):",DDM(2))
    print("DMM(2):",DMM(2))
    print("DDMstring(2):",DDMstring(2))
    print("DMMstring(2):",DMMstring(2))

    print("\nDMS LAT")
    print("DMSLatitude(2):",DMSLatitude(2))
    print("DMSLatitudeString(2):",DMSLatitudeString(2))

    print("\nDMS LON")
    print("DMSLongitude(2):",DMSLongitude(2))
    print("DMSLongitudeString(2):",DMSLongitudeString(2))

    print("\nDMS")
    print("DMS(2):",DMS(2))
    print("DMSstring(2):",DMSstring(2))