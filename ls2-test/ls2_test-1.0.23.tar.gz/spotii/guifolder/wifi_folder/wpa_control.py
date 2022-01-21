import os, sys, inspect

import time
import subprocess
import re



keytype = ['Open', 'WPA', 'WPA-Personal', 'WPA2', 'WPA2-Personal', 'Unknown']
##[['BELL710', 'WPA2-Personal', '53%'], ['UCS', 'WPA2-Personal', '57%'],...]
def getList_linux():

    response = subprocess.check_output(["wpa_cli -iwlan0 scan"],shell=True)
    print('scan', response)

    response=''
    for i in range(50):
        response = subprocess.check_output(["wpa_cli -iwlan0 scan_results"],shell=True)
    #print(response)
        response = response.decode("ascii")
    #print(response)    
        response = response.split('\n')
        if len(response)>1 and len(response[1])!=0:
            print('got scan results')
            break;
        print(i)
        time.sleep(0.1)
    simple=[]
    network=[]
    for each in response[1:]:
        item = each.split('\t')
        if len(item)!=5:
            continue
        
        network.append(item[4])
        firstKey=item[3][item[3].find("[")+1:item[3].find("]")]
        if firstKey == 'ESS':
            network.append('Open')
        else:
            network.append('WPA-Personal')
            

        signal = int(item[2])
        if(signal <= -100):
            quality = 0
        elif(signal >= -50):
            quality = 100
        else:
            quality = 2 * (signal + 100);

        network.append(str(quality))
        new =network.copy()
        network.clear()
        if new not in simple:
            simple.append(new)
    print(simple)
    return simple

def connected(interface):
    try:
        command = 'ifconfig '+interface
        response = subprocess.check_output([command],shell=True)
        response = response.decode("ascii")
        r_list   = response.split('\n')
        
        if 'inet ' in r_list[1]:
            return True
        return False
    except Exception as e:
        print(e)
        return False
    
def getProfileList():
    response = subprocess.check_output(["wpa_cli -iwlan0 list_network"],shell=True)
    #print(response)
    response = response.decode("ascii")
    #print(response.split('\n'))
    response = response.split('\n')
    simple=[]
    for each in response:
        item = each.split('\t')
        #print(item)
        if item[0].isdigit():
            #print (item[1])
            simple.append([item[1],item[3]])
    return simple

def gotIndex(ssid):
    p_list = getProfileList()
    try:
        index = 0
        for each in p_list:
            if ssid == each[0]:
                return index
            index += 1
        return None
    except Exception as e:
        print(e)
        return None
        
def deleteProfile(ssid):
    index = gotIndex(ssid)
    if index != None:
        cmd = 'wpa_cli -iwlan0 remove_network '+str(index)
        response = subprocess.check_output([cmd],shell=True)

def disableProfile(index):
    cmd = 'wpa_cli -iwlan0 disable_network '+str(index)
    response = subprocess.check_output([cmd],shell=True)
    print('disable network', index, response)
    
def enableProfile(index):
    cmd = 'wpa_cli -iwlan0 enable_network '+str(index)
    response = subprocess.check_output([cmd],shell=True)
    print('enable network', index, response)
    p_list = getProfileList()
    current = 0
    for each in p_list:
        if current != index and each[1] != '[DISABLED]':
            disableProfile(current)
        current += 1

def addProfile(ssid,key=None):  ##key:    None-- don't change setting, ''-- no key,  others-- key
    index = gotIndex(ssid)
    if key == None:
        return index
    
    if index ==None:        
        response = subprocess.check_output(["wpa_cli -iwlan0 add_network"],shell=True)
        index=int(response.decode("ascii"))
        #print(index)
    cmd = 'wpa_cli -iwlan0 set_network '+str(index)+' ssid \"\\\"'+ssid+'\\\"\"'
    print(cmd)
    subprocess.check_output([cmd],shell=True)
    if(key!=''):
        cmd = 'wpa_cli -iwlan0 set_network '+str(index)+' psk \"\\\"'+key+'\\\"\"'
        subprocess.check_output([cmd],shell=True)
        cmd = 'wpa_cli -iwlan0 set_network '+str(index)+' key_mgmt '+'WPA-PSK'
        subprocess.check_output([cmd],shell=True)
    else:
        cmd = 'wpa_cli -iwlan0 set_network '+str(index)+' key_mgmt '+'NONE'
        subprocess.check_output([cmd],shell=True)
    return index
    
def saveProfile():
    response = subprocess.check_output(["wpa_cli -iwlan0 save"],shell=True)
    print('save profile')
    
    
def killSupplicant(timeout):
    try:
        subprocess.check_output(["sudo killall wpa_supplicant"],shell=True)
        t_0 = time.time()
        while True:
            if not connected('wlan0'):
                return True           
            if time.time() - t_0 > timeout:
                return False
            time.sleep(0.2)
            print(".", end="")        
    except Exception as e:
        print(e)
        return False

def connect_wifi_linux(ssid, key, timeout):  #key:   None--Try to connect with previous setting, ''--No key, others--key
        
    index=addProfile(ssid,key)
    if index ==None :
        return False
    enableProfile(index)
    saveProfile()
    killSupplicant(5)
    time.sleep(2)
    try:
        subprocess.check_output(["sudo wpa_supplicant -Dnl80211 -iwlan0 -c/etc/wpa_supplicant/wpa_supplicant.conf -B"],shell=True)
    except Exception as e:
        print(e)
    
    t_0 = time.time()
    while True:
        if connected('wlan0'):
            return True           
        if time.time() - t_0 > timeout:
            return False
        time.sleep(0.5)
        print(".", end="")
    return True
   ###
    
if __name__ == "__main__":
    #ifconfigStatus('wlan0')
    #killSupplicant(5)
    
    #connect_wifi_linux('TP-Link_LP24','DaReLoVe501',15)
    #connect_wifi_linux('TP-Link_LP24','DaReLoVe501',15)
    #addProfile('TP-Link_LP24','DaReLoVe501')
    #saveProfile()
#    deleteProfile('TP-Link_LP24')
#    saveProfile()
#     print(getProfileList())
#     disableProfile(3)
#     saveProfile()

    getList_linux()

