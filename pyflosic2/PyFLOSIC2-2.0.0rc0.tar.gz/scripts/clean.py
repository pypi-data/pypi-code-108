import os

delete = [
    'fodopt.xyz',
    'pyflosic2.log',
    'UFLOSIC.log',
    'RFLOSIC.log',
    'FB_GUESS_COM.xyz',
    'atoms.xyz',
    'system',
    'CMD.log']
for d in delete:
    try:
        os.remove(d)
        print("File Removed!")
    except BaseException:
        'Nothing'
