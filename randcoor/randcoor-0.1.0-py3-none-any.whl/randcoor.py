from random import uniform, choice
from math import *

def randCoor():
    """Returns a random position"""
    lat, lon = uniform(-90, 90), uniform(-180, 180)
    return (-lat if lat==-90 else lat, lon if lon==-180 else lon)

def randCoorByDist(position, distanceMax, distanceMin=0):
    """Returns a random position that is situated between distanceMin km and distanceMax km from position"""
    deg100 = 0.8993216059187302 # Value such that the distance between (0,0) and (0,deg100) is 100km
    randDist = uniform(distanceMin, distanceMax)
    randAngle = uniform(0, 360)
    lat, lon = randDist*cos(radians(randAngle)), randDist*sin(radians(randAngle))
    lat, lon = position[0]+deg100/100*lat, position[1]+deg100/100*lon
    if abs(lat)>90:
        if lat>0:
            lat=-lat+180
        else:
            lat=-lat-180
    if abs(lon)>180:
        lon = (lon+180)%360-180
    return (lat, lon)

def randCoorByRule(rule, limit=None, showError=False):
    """
    Returns a random position that satisfies the function rule(lat, lon) with try-and-error
    unless the algorithm has tried limit times, and in that case show an error if showError
    """
    lenErr = iter(int, 1)
    if limit:
        lenErr = range(limit)
    for x in lenErr:
        lat, lon = randCoor()
        if rule(lat, lon):
            return (lat, lon)
    if showError:
        raise Exception('No randomly generated values satisfied the given condition')    

def calcDist(*coordinates):
    """Calculates the distance between positions entered as parameters or contained in an iterable"""
    if len(coordinates) == 1:
        coordinates = coordinates[0]
    n = 0
    for x in range(len(coordinates)-1):
        c1, c2 = coordinates[x], coordinates[x+1]
        latDif = radians(c2[0]-c1[0])/2
        lonDif = radians(c2[1]-c1[1])/2
        lat1 = radians(c1[0])
        lat2 = radians(c2[0])
        a = sin(latDif) * sin(latDif) + sin(lonDif) * sin(lonDif) * cos(lat1) * cos(lat2)
        n += 12742 * asin(sqrt(a))
    return n
