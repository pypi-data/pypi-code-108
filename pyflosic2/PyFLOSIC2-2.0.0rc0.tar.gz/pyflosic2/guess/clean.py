import os

delete = [
    'pyflosic2.log',
    'fodMC.out',
    'Kr.xyz',
    'FB_GUESS_COM.xyz',
    'GUI.log',
    'PyFLOSIC_dev_CMD.log',
    'fodMC_GUESS.xyz',
    'CMD.log',
    'RFODMC.log',
    'UFODMC.log']
for d in delete:
    try:
        os.remove(d)
        print("File Removed!")
    except BaseException:
        'Nothing'
