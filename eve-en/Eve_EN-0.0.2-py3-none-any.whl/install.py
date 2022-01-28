import os

user = os.path.expanduser('~')
a = f"{user}\\AppData\\Roaming\\Python\\Python310\\site-packages\\EveEN\\_portaudio.cp310-win_amd64.pyd"
b = f"{user}\\AppData\\Roaming\\Python\\Python310\\site-packages\\EveEN\\pyaudio.py"
c = f"{user}\\AppData\\Roaming\\Python\\Python310\\site-packages\\"

try:
    import pyaudio
except ImportError:
    os.system(f"copy  {a} {c}")
    os.system(f"copy  {b} {c}")
