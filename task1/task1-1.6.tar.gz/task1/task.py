"""Contains all the necessary code to run various features like searching in net,running files,etc"""
import datetime
import difflib
import json
import os
import random
import subprocess
import webbrowser
from pathlib import Path

from talk1.talk1 import talk
import platform

if platform.system() == 'Windows':
    homedir = os.environ["USERPROFILE"]
else: homedir = os.path.expanduser('~')

# .....Time and Greeting............
greeting = lambda nam: talk(f"Good morning {nam}") if datetime.datetime.now().hour < 12 else talk(f"Good evening {nam}")
tell_time = lambda: talk(f"It is {datetime.datetime.now().hour} {datetime.datetime.now().minute}")  # To tell the current time

# ...........Programmes..........................
programdata = json.load(open(os.path.abspath(__file__)[:-7] + "programs.json"))
getprogramnames = lambda: programdata.keys()  # To get the names of all the programs supported by Elsa


def programopener(prgramname) -> None:
    """To open the program"""
    try:
        os.system(programdata[prgramname[0]])
        talk(f"Opening {prgramname}")
    except Exception as e:
        print(e, "Sorry i could not do what you requested. Try again later")
        talk("Sorry, could not open the program")


# .........browser and net related................
def web(searchword) -> None:
    """To open the web browser along with the search results"""
    try:
        webbrowser.open(("https://www.google.com/search?client=firefox-b-d&q=" + searchword), new = 1)  # Works best in firefox
        talk(f"This is what I found for {searchword}")
    except:
        webbrowser.open(searchword, new = 1)
        print("Sorry i could not do what you requested Try again later")


def youtube(srch) -> None:
    """To open the youtube search results"""
    webbrowser.open(f"https://www.youtube.com/results?search_query={srch}")
    talk('Here is what you requested')


# .............folders......................
def commonFolder(foldername) -> None:
    """To open the common folders"""
    try:
        os.startfile(Path(os.path.join(os.path.join(homedir), foldername)))
        talk('Here is what you requested')
    except: talk(f"Sorry, could not open the {foldername} folder")


download, desktop, musicFolder = lambda: commonFolder('Downloads'), lambda: commonFolder('Desktop'), lambda: commonFolder('Music')


def joke() -> None:
    """To tell a joke"""
    try:
        jokeslist = ["My friend was explaining electricity to me, but I was like, wat ?",
                     "I failed math so many times at school, I can’t even count",
                     "Never trust atoms; they make up everything",
                     "The future, the present, and the past walk into a bar. Things got a little tense"]
        jokeselected = random.choice(jokeslist)
        talk(jokeselected)
    except: talk("Give me time to think. please try again")


# ...........shutdown,restart and log off.....
def turnoff(arg) -> None:
    """To shutdown the computer"""
    try:
        # /s is for shutdown ,/t is for timeout and 5 is the delay time
        # /r is for restart ,/t is for timeout and 5 is the delay time
        talk("Shutting down your computer in 5 seconds. Bye bye")
        subprocess.call(["shutdown", arg, "/t", "5"])
    except: talk("Sorry.Something went wrong")


shutdown, restart = lambda: turnoff('\s'), lambda: turnoff('\r')
webdict = json.load(open(os.path.abspath(__file__)[:-7] + "weblist.json"))
websitelist = tuple(web for web in webdict)


# ......websites..............
def websiteopen(website) -> None:
    """To open the website"""
    try:
        approx_match = difflib.get_close_matches(website, websitelist, cutoff = 0.7, n = 1)
        print(f"Approximated {website} to {approx_match[0]}")
        webbrowser.open(webdict[approx_match[0]])
        talk(f"opening {approx_match[0]}")
    except: talk(f"Sorry,could not find {website}")
