import os

delete = [
    'fodopt.xyz',
    'pyflosic2.log',
    'UFLOSIC.log',
    'RFLOSIC.log',
    'FB_GUESS_COM.xyz',
    'atoms.xyz',
    'system',
    'fodMC_GUESS.xyz',
    'CMD.log',
    'system.xyz',
    'UBONDS.log',
    'RBONDS.log']
for d in delete:
    try:
        os.remove(d)
        print("File Removed!")
    except BaseException:
        'Nothing'
