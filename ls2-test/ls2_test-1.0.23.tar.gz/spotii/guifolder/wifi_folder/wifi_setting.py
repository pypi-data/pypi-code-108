##from wifi import Cell, Scheme
##print (list(Cell.all('wlan0')))

import ctypes
import os, sys, inspect
import time
if sys.platform in ["win32", "linux"]:
    import pywifi
    from pywifi import const
import subprocess
import re

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
import wpa_control

def main(ssid, psk, timeout):
    print("Wifi connecting: SSID {0} ".format(ssid))
    if ssid == get_current_wifi():
        print("Wifi already connected to {0}".format(ssid))
        return
    connect_wifi(ssid, psk, int(timeout))

    
    
def create_wifi_interface():
    print("Creating wifi interface")
    wifi = pywifi.PyWiFi()
    return wifi.interfaces()[0]


def disconnect_wifi(timeout, interface):
    print("Disconnect wifi")
    interface.disconnect()
    t_0 = time.time()
    while not (interface.status() in [const.IFACE_DISCONNECTED,
                                      const.IFACE_INACTIVE]):
        if time.time() - t_0 > timeout:
            raise TimeoutError
        time.sleep(0.1)
        print(".", end="")
    print("Disconnect wifi succes!")


# def connect_wifi(ssid, psk, timeout):
#     print("Connect wifi for {0}".format(sys.platform))
#     interface = create_wifi_interface()
#     disconnect_wifi(timeout, interface)
#     profile = pywifi.Profile()
#     profile.ssid = ssid
#     profile.auth = const.AUTH_ALG_OPEN
#     profile.akm.append(const.AKM_TYPE_WPA2PSK)
#     profile.cipher = const.CIPHER_TYPE_CCMP
#     profile.key = psk
#     interface.remove_all_network_profiles()
#     tmp_profile = interface.add_network_profile(profile)
#     interface.connect(tmp_profile)
#     t_0 = time.time()
#     while not (interface.status() == const.IFACE_CONNECTED):
#         if time.time() - t_0 > timeout:
#             raise TimeoutError
#         time.sleep(0.1)
#         print(".", end="")
#     print("\n", "Connect wifi succes!")


def connect_it(timeout, interface, profile):
    interface.connect(profile)
    t_0 = time.time()
    while not (interface.status() == const.IFACE_CONNECTED):
        if time.time() - t_0 > timeout:
            return False
        time.sleep(0.1)
        print(".", end="")
    print("\n", "Connect wifi succes!")
    return True

    
def connect_wifi(ssid, psk, timeout):
    print("Connect wifi for {0}".format(sys.platform))
    interface = create_wifi_interface()
    #disconnect_wifi(timeout, interface)    
    subprocess.check_output(["sudo ifconfig wlan0 down"],shell=True)
    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP    
    profile.key = psk
    tmp_profile = interface.add_network_profile(profile)
    return connect_it(timeout, interface, tmp_profile)

def connect_wifi_immediately(ssid, psk, timeout):
    print("Connect wifi for {0}".format(sys.platform))
    interface = create_wifi_interface()   
    disconnect_wifi(timeout, interface)
    
    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP    
    currentProfiles = interface.network_profiles()
    exist = False
    for each in currentProfiles:
        if profile == each:
            exist = True
            break
    if not exist:
        print('new')
        return False
    return connect_it(timeout, interface, each)

# ##['Enabled', 'Connected', 'Dedicated', 'wlan0']
# ##      0          1           2           3
WIFI_STATUS_CONNECTED    = 'Connected'
WIFI_STATUS_DISCONNECTED = 'Disconnected'
# 
# def wifi_status_change_to(timeout, target):
#     time.sleep(0.01)
#     t_0 = time.time()
#     while True:
#         interface = getInterface_linux()
#         if target == interface[1]:
#             break;
#         if time.time() - t_0 > timeout:
#             return False
#         time.sleep(0.1)
#         print(".", end="")
#     
#     return True
# 
# #sudo wpa_supplicant -Dnl80211 -iwlan0 -c/etc/wpa_supplicant/wpa_supplicant.conf -B
# #sudo wpa_supplicant -Dnl80211 -iwlan0 -c/etc/wpa_supplicant/wpa_supplicant.conf -B
# 
# def connect_wifi_linux(ssid, psk, timeout):
#     print("Connect wifi for {0}".format(sys.platform))
#     
#     subprocess.check_output(["sudo killall wpa_supplicant"],shell=True)
#     
#     if wifi_status_change_to(timeout, WIFI_STATUS_DISCONNECTED):
#         print('wifi is disconnected')
#         command = 'sudo su -c \'wpa_supplicant -Dnl80211 -iwlan0 -B -c <(wpa_passphrase '+ssid+' '+psk+')\'' 
#         subprocess.check_output([command],shell=True)
#         if wifi_status_change_to(timeout, WIFI_STATUS_CONNECTED):
#             print('success to connect')
#         else:
#             print('fail to connect')
#     else:
#         print('failed to disconnect.')
        
        
    

    
        
    
    
def wifi_list(interface):
    ls = interface.scan_results()
    for each in ls:
        print('------------------------------------------')
        print('ssid', each.ssid)
        print('bssid', each.bssid)
        print('id',each.id)
        print('auth',each.auth)
        print('cipher',each.cipher)
        print('key', each.key)
        if(each.signal <= -100):
            quality = 0
        elif(each.signal >= -50):
            quality = 100
        else:
            quality = 2 * (each.signal + 100);

        print('signal', quality)
        print('akm', each.akm)

##def get_current_wifi():
##    print("Get current wifi for {0}".format(sys.platform))
##    ssid = ""
##    if sys.platform == "win32":  # Windows
##        try:
##            ssid = get_current_wifi_windows()
##        except subprocess.CalledProcessError:
##            pass
##    elif sys.platform == "linux":
##        try:
##            ssid = get_current_wifi_linux()
##        except AttributeError:
##            pass
##    else:
##        raise OSError
##    print("Current ssid {0}".format(ssid))
##    return ssid
##
##
##def get_current_wifi_linux():
##    network_information = os.popen('/sbin/iwconfig | grep ESSID').read()
##    ssid = re.search('ESSID:"(.*)"', network_information).group(1)
##    return ssid
##
##
##def get_current_wifi_windows(): #########BUG!!!!!!
##    network_information = str(subprocess.check_output(["netsh", "wlan", "show", "network"]))
##    network_information = network_information.replace('\\r', '')
##    network_information = network_information.replace("b' ", '')
##    network_information = network_information.replace(":", '\n')
##    network_information = network_information.replace("\\n", '\n')
##    network_information = network_information.splitlines()
##    ssid = network_information[6][1:]
##    return ssid




def parsing(results):
    results = results.decode("ascii") # needed in python 3
    #print(results)
    results = results.replace("\r","")
    results = re.sub(' +', ' ', results)

    return results.split("\n")

network=[]
currentIndex=0
def fillIt(mainList, item):
    global currentIndex
    global network
    pair = item.split(':')
    if len(pair)!=2:
        return
    if(currentIndex == 0):
        if pair[0].strip()[:4] == 'SSID':
            network.append(pair[1].strip())
            currentIndex +=1
    elif(currentIndex == 1):
        if 'Authentication' == pair[0].strip():
            network.append(pair[1].strip())
            currentIndex+=1
    elif(currentIndex == 2):
        if 'Signal' == pair[0].strip():
            network.append(pair[1].strip())
            new = network.copy()
            mainList.append(new)
            currentIndex=0
            network.clear()

def getList():
    results = subprocess.check_output(["netsh", "wlan", "show", "network", "mode=Bssid"],shell=True)
    ls = parsing(results)
    simple=[]
    for each in ls:
        fillIt(simple,each)
#    print(simple)
    return simple

# # Define auth key mgmt types.
# AKM_TYPE_NONE = 0
# AKM_TYPE_WPA = 1
# AKM_TYPE_WPAPSK = 2
# AKM_TYPE_WPA2 = 3
# AKM_TYPE_WPA2PSK = 4
# AKM_TYPE_UNKNOWN = 5
keytype = ['Open', 'WPA', 'WPA-Personal', 'WPA2', 'WPA2-Personal', 'Unknown']
##[['BELL710', 'WPA2-Personal', '53%'], ['UCS', 'WPA2-Personal', '57%'],...]
def getList_linux():
    
    interface=create_wifi_interface()
    ls = interface.scan_results()
    #print(ls)
    simple=[]
    network=[]
    for each in ls:
        network.append(each.ssid)

        if len(each.akm) == 0:
            network.append(keytype[0])
        else:
            network.append(keytype[each.akm[0]])
        if(each.signal <= -100):
            quality = 0
        elif(each.signal >= -50):
            quality = 100
        else:
            quality = 2 * (each.signal + 100);

        network.append(str(quality))
        new =network.copy()
        network.clear()
        if new not in simple:
            simple.append(new)
    return simple


def getSsid():
    results = subprocess.check_output(["netsh", "wlan", "show", "interfaces"],shell=True)
    ls = parsing(results)
    for each in ls:
        pair = each.split(':')
        if pair[0].strip() == 'State':
            if pair[1].strip() == 'disconnected' :                
                return None
        elif pair[0].strip() == 'SSID':
            return pair[1].strip()        
    return None

def getSsid_linux():
    results = subprocess.check_output(["iwconfig wlan0"],shell=True)
    ls = parsing(results)
    ssid=ls[0].split('ESSID:')[1].strip(' ')
    if ssid.count('\"') == 2:
        return ssid.strip('\"')
    return None
#     for each in ls:
#         pair = each.split(':')
#         if pair[0].strip() == 'State':
#             if pair[1].strip() == 'disconnected' :                
#                 return None
#         elif pair[0].strip() == 'SSID':
#             return pair[1].strip()        
#     return None


def getInterface():
    results = subprocess.check_output(["netsh", "interface", "show", "interface"],shell=True)
    ls=parsing(results)
    for each in ls:
        subList=each.split(' ')
        if len(subList) == 4:
            if 'Wi-Fi' in subList[3]:
                return subList

## 'wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST> mtu 1500',' inet 192.168.2.247 netmask 255.255.255.0 broadcast 192.168.2.255'
## 'wlan0: flags=4098<BROADCAST,MULTICAST> mtu 1500'
def getInterface_linux():
    results = subprocess.check_output(['ifconfig -a'],shell=True)
    ls=parsing(results)
    for index, each in enumerate(ls):
        if 'wlan' in each:
            break;
    wlan=ls[index:]
#    print(wlan)
    interfaceName = wlan[0].strip(' ').split(':')[0]
#    print(interfaceName)
    interfaceStatus = wlan[0].split('<')[1].split(',')[0]
#    print(interfaceStatus)
    networkStatus = wlan[1].strip(' ').split(' ')[0]
#    print(networkStatus)

    interface=[]
    
    if interfaceStatus == 'UP':
        interface.append('Enabled')
    else:
        interface.append('Disabled')
        
    if 'inet' in networkStatus:
        interface.append(WIFI_STATUS_CONNECTED)
    else:
        interface.append(WIFI_STATUS_DISCONNECTED)
    interface.append('Dedicated')
    interface.append(interfaceName)
    return interface


def admin_permit():
    
    try:
        admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        admin = False        
    if not admin:
        print('admin permit')
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def stopWifi(name):
    admin_permit()
    try:
        results = subprocess.run(["netsh", "interface", "set", "interface",name, "disable"],shell=True)
        print('stop command sent',results)
    except Exception as e:
        print('stopWifi exception',e)

def stopWifi_linux(name):
    try:
#        cmd= 'sudo ifconfig '+name+' down'
        cmd= 'sudo rfkill block wifi'
        results = subprocess.run([cmd],shell=True)
        print('stop command sent',results)
    except Exception as e:
        print('stopWifi exception',e)


def startWifi(name):
    admin_permit()
    try:
        results = subprocess.run(["netsh", "interface", "set", "interface",name, "enable"],shell=True)
        print('start command sent',results)
    except Exception as e:
        print('stopWifi exception',e)

def startWifi_linux(name):
    try:
#        cmd= 'sudo ifconfig '+name+' up'
        cmd= 'sudo rfkill unblock wifi'
        results = subprocess.run([cmd],shell=True)
    except Exception as e:
        print('stopWifi exception',e)

#---------------------------#
def wifiList():
    if sys.platform == 'win32':
        return getList()
    elif sys.platform == 'linux':
        return wpa_control.getList_linux()
    
def wifiSsid():
    if sys.platform == 'win32':
        return getSsid()
    elif sys.platform == 'linux':
        return getSsid_linux()
    
def wifiInterface():
    if sys.platform == 'win32':
        return getInterface()
    elif sys.platform == 'linux':
        return getInterface_linux()

def wifiTurnOn(name):
    if sys.platform == 'win32':
        startWifi(name)
    elif sys.platform == 'linux':
        startWifi_linux(name)
    
def wifiTurnOff(name):
    if sys.platform == 'win32':
        stopWifi(name)
    elif sys.platform == 'linux':
        stopWifi_linux(name)

def wifiConnect(name, key=None):
    if sys.platform == 'win32':
        if key == None:
            return connect_wifi_immediately(name,'',10)
        else:
            return connect_wifi(name,key,10)
    elif sys.platform == 'linux':
        return wpa_control.connect_wifi_linux(name, key, 30)
    


if __name__ == "__main__":
##    print(wifiSsid())

#     wifiList=wifiList()
#     print(wifiList)

##    interface=wifiInterface()
##    print(interface)
##    startWifi(interface[3])

    
    #wifiTurnOn('wlan0')
    #print(wifiInterface())

    
##
##    #print(get_current_wifi())
##    print(wifiSsid())

    #connect_wifi('TP-Link_LP24', 'DaReLoVe501', 10)
    
    #connect_wifi_linux('TP-Link_LP24', 'DaReLoVe501',10)
##    getList()

#     interface=create_wifi_interface()
#     wifi_list(interface)
    
# #!/usr/bin/env python3
# # vim: set fileencoding=utf-8
# 
# """Constants used in pywifi library define here."""
# 
# # Define interface status.
# IFACE_DISCONNECTED = 0
# IFACE_SCANNING = 1
# IFACE_INACTIVE = 2
# IFACE_CONNECTING = 3
# IFACE_CONNECTED = 4
# 
# # Define auth algorithms.
# AUTH_ALG_OPEN = 0
# AUTH_ALG_SHARED = 1
# 
# # Define auth key mgmt types.
# AKM_TYPE_NONE = 0
# AKM_TYPE_WPA = 1
# AKM_TYPE_WPAPSK = 2
# AKM_TYPE_WPA2 = 3
# AKM_TYPE_WPA2PSK = 4
# AKM_TYPE_UNKNOWN = 5
# 
# # Define ciphers.
# CIPHER_TYPE_NONE = 0
# CIPHER_TYPE_WEP = 1
# CIPHER_TYPE_TKIP = 2
# CIPHER_TYPE_CCMP = 3
# CIPHER_TYPE_UNKNOWN = 4
# 
# KEY_TYPE_NETWORKKEY = 0
# KEY_TYPE_PASSPHRASE = 1
# © 2021 GitHub, Inc.
# Terms
# Privacy
# Security
# Status
#
    pass
