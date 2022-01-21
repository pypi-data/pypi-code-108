import subprocess

def shorten(input):
    result = subprocess.check_output(['./runner.exe', '-l', 'test', '-e', f'shorten({input})'])    
    return result.decode().replace("\n","")

print(shorten(1000000))