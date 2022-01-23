## -*- coding: utf-8 -*-
import sys
import os
import socket

# RENOMER CETTE VARIABLE AVEC LE NOM DU DOSSIER QUI CONTIENT VOTRE PROJET
ROOT_DIRECTORY = "noyau_devII_2TM2"
COMMAND_LIST = ["/help", "/weather", "/itinerary", "/resto", "/cine", "/news", "/opinion"]

# Link open street service
headers = {'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8', }
open_street_link = 'https://api.openrouteservice.org/v2/directions/driving-car?api_key' \
                   '=5b3ce3597851110001cf62481288a0a3b2fe4b43a2d8a701aaaa3436 '

# Directory containing
ROOT_DIR = ""
if sys.platform == "win32":
    if ROOT_DIRECTORY in sys.path[0].split('\\'):
        index_root = sys.path[0].split('\\').index(ROOT_DIRECTORY)
        ROOT_DIR = "\\".join(sys.path[0].split("\\")[:index_root + 1])
        MODULE_DIR = os.path.join(ROOT_DIR, "src")
    else:
        ROOT_DIR = "\\".join(sys.path[-1].split("\\")[:])
        MODULE_DIR = ROOT_DIR

    HELP_FILE = os.path.join(MODULE_DIR, "Bot\\help.txt")
    CERTIFICATE_FILE = os.path.join(MODULE_DIR, "Bot\\db_key.pem")
    try:
        with open(HELP_FILE) as fd:
            pass
    except FileNotFoundError:
        HELP_FILE = os.path.join(sys.path[0], "src\\Bot\\help.txt")
        CERTIFICATE_FILE = os.path.join(MODULE_DIR, "src\\Bot\\db_key.pem")

if sys.platform == "linux":
    if ROOT_DIRECTORY in sys.path[0].split('/'):
        index_root = sys.path[0].split('/').index(ROOT_DIRECTORY)
        ROOT_DIR = "/".join(sys.path[0].split("/")[:index_root + 1])
        MODULE_DIR = os.path.join(ROOT_DIR, "src")
    else:
        ROOT_DIR = "/".join(sys.path[-1].split("/")[:])
        MODULE_DIR = ROOT_DIR

    HELP_FILE = os.path.join(MODULE_DIR, "Bot/help.txt")
    CERTIFICATE_FILE = os.path.join(MODULE_DIR, "Bot/db_key.pem")
    try:
        with open(HELP_FILE) as fd:
            pass
    except FileNotFoundError:
        HELP_FILE = os.path.join(sys.path[0], "src/Bot/help.txt")
        CERTIFICATE_FILE = os.path.join(MODULE_DIR, "src/Bot/db_key.pem")


# Link nominatim openstreetmap
def itinerary_link(address):
    return 'https://nominatim.openstreetmap.org/search/' + address + '?format=json'


def weather_stack(param):
    return f"http://api.weatherstack.com/current?access_key=4c53b8fcf4818536539b668a0247408c&query={param}"


def news_link():
    return f"http://api.mediastack.com/v1/news?access_key=4a9e07d9cfd75c8d73c70f90ed4846f5"


def cine_link(address):
    return f"https://nominatim.openstreetmap.org/search?osmtype=N&addressdetails=1&q=cinema+{address}&format=json"


def resto_link(address):
    return f"https://nominatim.openstreetmap.org/search?osmtype=N&addressdetails=1&q=restaurant+{address}&format=json"


def check_conection_defaullt():
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return False
    except socket.error:
        return True


def check_conection():
    try:
        # if we resolve the hostname urllib.urlopen() -- fonctionne aussi
        host = socket.gethostbyname("www.google.com")

        socket.create_connection((host, 80), 2)
        return False
    except socket.error:
        return True
