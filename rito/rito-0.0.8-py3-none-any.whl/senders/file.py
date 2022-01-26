import os

def send_message(file, text):
    with open(file, 'a') as f:
        f.write(f'{text}{os.linesep}')