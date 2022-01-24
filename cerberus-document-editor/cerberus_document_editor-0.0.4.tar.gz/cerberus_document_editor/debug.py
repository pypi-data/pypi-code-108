import os
import datetime

with open('log.txt', 'w') as f:
    print(f"{datetime.datetime.now()}", file=f)

def log(*args):
    if os.getenv('DEBUG'):
        with open('log.txt', 'a') as f:
            print(*args, file=f)