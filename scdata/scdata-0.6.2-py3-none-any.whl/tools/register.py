#!/usr/bin/python

from traceback import print_exc
import sys, time, os
from backup import *
import shutil

sys.path.append("./tools")

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def oneLine(msg):
    enablePrint()
    sys.stdout.write(msg)
    sys.stdout.flush()
    if not verbose: blockPrint()

def enablePrint():
    sys.stdout = sys.__stdout__

if '-h' in sys.argv or '--help' in sys.argv or '-help' in sys.argv:
    print('USAGE:\n\nresgister.py [options] action[s]')
    print('\noptions: -v: verbose; -t: test device')
    print('actions: register, inventory')
    print('register options: -n platform_name -i kit_blueprint_id (default: 26)')
    print('inventory -d "description" --with-test [y/n] (default: n)')
    print('-p port [-f]: specify a port instead of scanning')
    print('-f: option ignores serial device description (must contain Smartcitizen otherwise)')
    sys.exit()

import sck
kit = sck.sck(to_register = True)

force = False
port = None
if '-p' in sys.argv:
    port = sys.argv[sys.argv.index('-p')+1]
    if '-f' in sys.argv: force = True
elif '-f' in sys.argv: ERROR('No force action if port is not specified'); sys.exit()
if not kit.begin(port=port, force=force): sys.exit()

verbose = False
blockPrint()
if '-v' in sys.argv:
    verbose = True
    enablePrint()

if 'register' in sys.argv:
    kit.getInfo()

    if '-n' not in sys.argv:
        kit.platform_name = 'test #'
    else:
        kit.platform_name = sys.argv[sys.argv.index('-n')+1]

    if '-i' in sys.argv:
        try:
            bid = int(sys.argv[sys.argv.index('-i')+1])
        except:
            enablePrint()
            print('Failed parsing blueprint ID, please try again.')
            sys.exit()
        kit.blueprint_id = bid

    if '-t' in sys.argv:
        print ('Setting test device')
        kit.is_test = True

    import options
    if options.mac:
        kit.platform_name = kit.platform_name + ' #' + kit.esp_macAddress[-5:].replace(':', '')

    kit.register()

    enablePrint()
    print("\r\nSerial number: " + kit.sam_serialNum)
    print("Mac address: " + kit.esp_macAddress)
    print("Device token: " + kit.token)
    print("Platform kit name: " + kit.platform_name)
    print("Platform page: " + kit.platform_url)

if 'inventory' in sys.argv:
    try:
        from secret import inventory_path
    except:
        print ('No inventory path defined, using inventory/ folder')
        inventory_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'inventory')
        pass

    print (f'Using inventory in: {inventory_path}')
    kit.description = sys.argv[sys.argv.index('-d')+1]
    kit.getInfo()

    if '--with-test' in sys.argv: tested = 'y'
    else: tested = 'n'

    if not hasattr(kit, 'token'):
        kit.token = ''
    if not hasattr(kit, 'platform_name'):
        kit.platform_name = ''
    if not hasattr(kit, 'platform_url'):
        kit.platform_url = ''

    s3_inv_path = "inventory/deliveries"
    local_inv_name = "inventory.csv"
    if not os.path.exists(inventory_path): os.makedirs(inventory_path)

    sync = None
    try:
        from boto.s3.connection import S3Connection
    except ModuleNotFoundError:
        boto_avail = False
        pass
    else:
        boto_avail = True

    if boto_avail:
        # Try to download file from S3
        sync = S3handler()
        sync.download(os.path.join(inventory_path, local_inv_name), os.path.join(s3_inv_path, local_inv_name))
        # Open the file
        print ('File from S3 synced correctly')
        csvFile = open(os.path.join(inventory_path, local_inv_name), "a")
    else:
        # Keep things local
        print_exc()
        print('Problem downloading file from S3, using local file')

        if os.path.exists(os.path.join(inventory_path, local_inv_name)):
            shutil.copyfile(os.path.join(inventory_path, local_inv_name), inventory_path+".BAK")
            csvFile = open(os.path.join(inventory_path, local_inv_name), "a")
        else:
            csvFile = open(os.path.join(inventory_path, local_inv_name), "w")
            csvFile.write("time,serial,mac,sam_firmVer,esp_firmVer,description,token,platform_name,platform_url,tested,validated,min_validation_date,max_validation_date,replacement,test,destination,batch\n")
        pass

    print (f'Writing into file for Kit: {kit.esp_macAddress}')
    csvFile.write(time.strftime("%Y-%m-%dT%H:%M:%SZ,", time.gmtime()))
    csvFile.write(kit.sam_serialNum + ',' + kit.esp_macAddress + ',' + kit.sam_firmVer + ',' + kit.esp_firmVer + ',' + kit.description + ',' + kit.token + ',' + kit.platform_name + ',' + kit.platform_url + ',' + tested + ',' + ',' + ',' +',' + ',' +',' + ',' +'\n')
    csvFile.close()

    # Put the file in S3
    if sync is not None:
        resp = sync.upload(os.path.join(inventory_path, local_inv_name), os.path.join(s3_inv_path, local_inv_name))

        if resp is None: print ('No response, review bucket')
        else: print ('Success!')
