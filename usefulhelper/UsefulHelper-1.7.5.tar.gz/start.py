import os


with open('/home/pi/.bashrc', 'r+') as path:
    path.seek(0, 2)
    path.write('# UsefulHelper\n')
    path.write("alias UsefulHelper='python /home/pi/PycharmProjects/UsefulHelper/UsefulHelper/cli.py'\n")
os.system('source ~/.bashrc')
