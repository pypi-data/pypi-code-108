import speech_recognition as sr
import os
from EveEN.ENplaysound import  *
import os
from EveEN.ENlogo import *
from gtts import gTTS
from EveEN.czy import *
import os

user = os.path.expanduser('~')
voicefile = f"{user}\\Music\\"
voicefile2 = "C:\\"

def cls():
    import os
    os.system("cls")


def starter():
    logo()
    ENsay("Hello, I'm Eve, if you want to wake me up saying Eve")

def Ebreak():
    while True:
        audio = get_audio()
        if len(czy(audio, EVE)):
            ENsay("Yes sir? I'm Listening")
            break

################################################################################
EVE = ["eve", "eva"]
################################################################################



def ENsay(text):
    tts = gTTS(text=text, lang="en")
    filename = "voice.mp3"
    tts.save(filename)
    print(text)
    playsound(filename)
    os.remove("voice.mp3")

def ENlossay(text):
    import random
    a = random.choice(text)
    ENsay(a)





def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listens...")
        audio = r.listen(source)
        said=""
        try:
            said= r.recognize_google(audio, language="en")
            print("Said: " + said.lower())
        except Exception as e:
            print("Waiting..." + str(e))

    return said.lower()
