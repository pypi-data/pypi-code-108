import requests
import time
import pygame
import sys
import json
import time

def getCookies():
    cookies = ""
    if len(sys.argv) > 1:
        try:
            cookies = json.loads(sys.argv[1])["cookies"]
        except:
            pass
    return cookies

def jsonLoads(str):
    try:
        return json.loads(str)
    except:
        return None

# Information Transfer Protocol
# Information exchange Protocol

def InfoTransferAndExchange(data):
	time.sleep(0.01)
	jsonStr = json.dumps(data)
	print("#xzeysx#" + jsonStr + "#xzeysx#")


g_gender="male"
g_rate=None
g_pitch=None


def setmode(gender):
    if gender != "male" and gender != "female" and gender != "boy" and gender != "girl":
        raise Exception("gender only boy,girl,male and female")
    if gender == "boy":
        gender = "male"
    elif gender == "girl":
        gender = "female"

    global g_gender
    g_gender = gender



def setspeed(rate):
    if not isinstance(rate, int) and not isinstance(rate, float):
        raise Exception("rate only 0,1 or 2")

    if rate < 0 or rate > 2:
        raise Exception("rate only 0,1 or 2")

    global g_rate
    g_rate = rate


def sethigh():
    global g_pitch
    g_pitch = "high"


def speak(text):
    text = text.strip()
    if text == "":
        raise Exception("text cannot none")


    global g_gender,g_rate,g_pitch
    params = {"text":text,"gender":g_gender,"rate":g_rate,"pitch":g_pitch}
    cookies = getCookies()
    headers = {"Cookie": cookies}
    rep = requests.get("https://code.xueersi.com/api/ai/python_tts/tts", params=params, headers=headers)
    repDic = jsonLoads(rep.text)
    if repDic is None:
        raise Exception("time out")

    if repDic["stat"] != 1:
        raise Exception(repDic["msg"])

    voiceUrl = repDic["data"]["url"]
    duration = repDic["data"]["duration"]

    
    r = requests.get(voiceUrl)
    filename = voiceUrl.split("/")[-1]
    with open(filename, "wb") as f:
        f.write(r.content)
    f.close()

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()



    time.sleep(duration + 1)



def translate(text):
    text = text.strip()
    if text == "":
        return ""


    params = {"text": text}
    cookies = getCookies()
    headers = {"Cookie": cookies}
    rep = requests.get("https://code.xueersi.com/api/ai/python_tts/translate", params=params, headers=headers)
    repDic = jsonLoads(rep.text)
    if repDic is None:
        raise Exception("time out")

    if repDic["stat"] != 1:
        raise Exception(repDic["msg"])



    result = repDic["data"]["text"]
    return result