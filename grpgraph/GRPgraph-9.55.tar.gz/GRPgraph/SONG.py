import pyttsx3

class PY_tolk:
    def __init__(self,voise,volume):
        self.cal = pyttsx3.init()
        self.cal.setProperty('rate',voise)
        self.cal.setProperty('volume',volume)
    
    def caling(self,text=''):
        self.cal.say(text)
    def End_cal(self):
        self.cal.runAndWait()
    

