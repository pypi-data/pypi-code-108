"""This package is a text to speech synthesiser"""
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty("voices")  # getting details of current voice
# engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
engine.setProperty("voice", voices[1].id)  # changing index, changes voices. 1 for female
rate = engine.getProperty("rate")  # getting details of current speaking rate
engine.setProperty("rate", 135)  # setting up new voice rate


def talk(speak, var: None | bool = None) -> None:
    """A function for text to speech functionality"""
    try:
        if var is not None: print(speak)
        engine.say(speak)
        engine.runAndWait()
    except: pass
