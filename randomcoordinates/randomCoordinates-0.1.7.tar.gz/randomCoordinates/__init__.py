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

def debug(decimals=2):
    print("DD")
    print("Latitude("+str(decimals)+"):",Latitude(decimals))
    print("Longitude("+str(decimals)+"):",Longitude(decimals))
    print("DD("+str(decimals)+"):",DD(decimals))
    print("DDstring("+str(decimals)+"2):",DDstring(decimals))
    
    print("\nDDM/DMM LAT")
    print("DDMLatitude("+str(decimals)+"):",DDMLatitude(decimals))
    print("DMMLatitude("+str(decimals)+"):",DMMLatitude(decimals))
    print("DDMLatitudeString("+str(decimals)+"):",DDMLatitudeString(decimals))
    print("DMMLatitudeString("+str(decimals)+"):",DMMLatitudeString(decimals))

    print("\nDDM/DMM LON")
    print("DDMLongitude("+str(decimals)+"):",DDMLongitude(decimals))
    print("DMMLongitude("+str(decimals)+"):",DMMLongitude(decimals))
    print("DDMLongitudeString("+str(decimals)+"):",DDMLongitudeString(decimals))
    print("DMMLongitudeString("+str(decimals)+"):",DMMLongitudeString(decimals))
    
    print("\nDDM/DMM")
    print("DDM("+str(decimals)+"):",DDM(decimals))
    print("DMM("+str(decimals)+"):",DMM(decimals))
    print("DDMstring("+str(decimals)+"):",DDMstring(decimals))
    print("DMMstring("+str(decimals)+"):",DMMstring(decimals))

    print("\nDMS LAT")
    print("DMSLatitude("+str(decimals)+"):",DMSLatitude(decimals))
    print("DMSLatitudeString("+str(decimals)+"):",DMSLatitudeString(decimals))

    print("\nDMS LON")
    print("DMSLongitude("+str(decimals)+"):",DMSLongitude(decimals))
    print("DMSLongitudeString("+str(decimals)+"):",DMSLongitudeString(decimals))

    print("\nDMS")
    print("DMS("+str(decimals)+"):",DMS(decimals))
    print("DMSstring("+str(decimals)+"):",DMSstring(decimals))

def help():
    print("""Do .list() to have a list of all the functions.
To choose the amount of decimals insert like below,
                        ↓
randomCoordinates.debug( )
And some of the functions can output multiple outputs (shown in list).""")

def list():
    print("""This is a list of all the functions,

Decimal Degrees (DD)
.Latitude()            -outputs latitude
.Longitude()           -outputs longitude
.DD()                  -outputs latitude and longatude into 2 varibles "a,b = .DD()"
.DDstring()            -outputs latitude and longatude into 1 varible

Degrees Decimal Minutes Latitude (DDM/DMM)
.DDMLatitude()         -outputs latitude into 2 varibles in the format of (Degrees Decimal Minutes)
.DMMLatitude()         -same as above
.DDMLatitudeString()   -outputs latitude into 1 varible in the format of (Degrees Decimal Minutes)
.DMMLatitudeString()   -same as above

Degrees Decimal Minutes Longatude (DDM/DMM)
.DDMLongatude()        -outputs longitude into 2 varibles in the format of (Degrees Decimal Minutes)
.DMMLongatude()        -same as above
.DDMLongatudeString()  -outputs longitude into 1 varible in the format of (Degrees Decimal Minutes)
.DMMLongatudeString()  -same as above

Degrees Decimal Minutes (DDM/DMM)
.DDM()                 -outputs latitude and longatude into 2 varibles in the format of (Degrees Decimal Minutes)
.DMM()                 -same as above
.DDMstring()           -outputs latitude and longatude into 1 varible in the format of (Degrees Decimal Minutes)
.DMMstring()           -same as above

Degrees Minutes Seconds Latitude (DMS)
.DMSLatitude()         -outputs latitude into 3 varibles in the format of (Degrees Minutes Seconds)
.DMSLatitudeString()   -outputs latitude into 1 varible in the format of (Degrees Minutes Seconds)

Degrees Minutes Seconds Longatude (DMS)
.DMSLongatude()        -outputs longatude into 3 varibles in the format of (Degrees Minutes Seconds)
.DMSLongatudeString()  -outputs longatude into 1 varible in the format of (Degrees Minutes Seconds)

Degrees Minutes Seconds (DMS)
.DMS()                 -outputs latitude and longatude into 2 varibles in the format of (Degrees Minutes Seconds)
.DMSstring()           -outputs latitude and longatude into 1 varible in the format of (Degrees Minutes Seconds)

Help And Debug
.help()                -some basic infomation about this library
.list()                -list out every function and basic infomation about them
.debug()               -prints out every funtion (for debug testing)""")
