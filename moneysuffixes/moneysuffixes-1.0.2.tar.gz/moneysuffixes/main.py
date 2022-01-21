from ssl import ALERT_DESCRIPTION_ACCESS_DENIED
import subprocess

class Money:
    def shorten(input):
        result = subprocess.check_output(['./runner.exe', '-l', 'test', '-e', f'shorten({input})'])    
        return result.decode().replace("\n","")