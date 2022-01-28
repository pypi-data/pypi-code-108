import os
from subprocess import DEVNULL, Popen, check_call
import webbrowser
from EveEN.ENlogo import *
from EveEN.ENall import *
from EveEN.ENweather import *
from EveEN.czy import *
from EveEN.ENweb import *


def Eve():
    cls()
    starter()
    while True:
        Ebreak()
        Evecommends()

def Evecommends():
    i = 0
    for i in range(25):
        print(" ")
        audio = get_audio()
        if len(czy(audio, TIME)):
            if len(czy(audio, IN)):
                city = audio.lower().split(" " + czy(audio, IN)[0] + " ")[1]
                ENtime(city)
                Evecommends()
            ENlocaltime()
            Evecommends()
        if len(czy(audio, what)):
            if len(czy(audio, IS)):
                if len(czy(audio, YOUR)):
                    if len(czy(audio, NAME)):
                        say("My name is Eve")
                        Evecommends()
        if len(czy(audio, temperature)):
            if len(czy(audio, IN)):
                city = audio.lower().split(" " + czy(audio, IN)[0] + " ")[1]
                ENtemperature(city)
                Evecommends()
        if len(czy(audio, stop)):
            if len(czy(audio, application)):
                ENsay("OK, Goodbye")
                exit()
            if len(czy(audio, listening)):
                ENsay("OK, just say Eve if you want to wake me up")
                Ebreak()
                Evecommends()
        if len(czy(audio, open)):
            if len(czy(audio, MUSIC)):
                if len(czy(audio, FOLDER))
            if len(czy(audio, web)):
                if len(czy(audio, browser)):
                    ENsay("OK, the browser opens")
                    webbrowser.get('edge').open("google.com")
                    Evecommends()
            if len(czy(audio, youtube)):
                ENsay("OK, the youtube opens")
                webbrowser.get('edge').open("youtube.com")
                Evecommends()
            if len(czy(audio, netflix)):
                ENsay("OK, the netflix opens")
                webbrowser.get('edge').open("netflix.com")
                Evecommends()
            if len(czy(audio, twitch)):
                ENsay("OK, the twitch opens")
                webbrowser.get('edge').open("twitch.com")
                Evecommends()
            if len(czy(audio, TEAMS)):
                ENsay("OK, the teams open")
                webbrowser.get('edge').open("https://teams.microsoft.com/go#")
                Evecommends()
            if len(czy(audio, FACEBOOK)):
                ENsay("OK, the facebook open")
                webbrowser.get('edge').open("facebook.com")
                Evecommends()
            if len(czy(audio, MESSENGER)):
                ENsay("OK, the message open")
                webbrowser.get('edge').open("http://messenger.com/")
                Evecommends()
    ENsay("I'm going to sleep. You can wake me up saying Eve")
    Ebreak()
    Evecommends()







################################################################################\

#if len(czy(audio, )):

################################################################################\ms

folder = ['folder']
MUSIC = ["music"]
MESSENGER = ["messenger"]
FACEBOOK = ["facebook"]
TEAMS = ["teams"]
TIME = ["time"]
stop = ["stop"]
what = ["what"]
IS = ["is"]
YOUR = ["your"]
NAME = ["name"]
listening= ["listening"]
open = ["open"]
web = ["web"]
browser = ["browser"]
youtube = ["youtube"]
application = ["application", "app"]
netflix = ["netflix"]
twitch = ["twitch"]
temperature = ["temperature"]
IN = ["in"]

################################################################################


webbrowser.register('edge',
	None,
	webbrowser.BackgroundBrowser("C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"))
