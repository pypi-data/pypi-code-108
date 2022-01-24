import requests

TOKEN = requests.get('https://public-keys.teamtv.nl/app.teamtv.nl.pub').content
