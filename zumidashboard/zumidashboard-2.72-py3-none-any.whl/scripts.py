import re
import os
from time import sleep
import subprocess


# def add_wifi(ssid, password, isHiddenNetwork, isEnterprise):
def add_wifi(ssid, username, password, isHiddenNetwork):
    #ssid = ssid.encode('utf-8').hex().upper()
    MyOut3 = subprocess.Popen(['sudo', 'ifdown', '--force', 'wlan0'])
    MyOut3.wait()
    print('ifdown wlan0')
    MyOut2 = subprocess.Popen(['sudo', 'killall', 'dhclient'])
    print('scripts.py : add_wifi start')
    print('scripts.py : copying wpa_supplicant.conf')
    MyOut = subprocess.Popen(['sudo', 'cp', '/usr/local/lib/python3.5/dist-packages/zumidashboard/wpa_supplicant.conf',
                              '/etc/wpa_supplicant/wpa_supplicant.conf'])
    MyOut.wait()
    print('scripts.py : copyed wpa_supplicant.conf')

    if username:
        identity = username
        password = password
        file = open("/etc/wpa_supplicant/wpa_supplicant.conf", "a")
        file.write("\nnetwork={")
        file.write("\nssid=\"" + ssid + "\"")
        if isHiddenNetwork:
            file.write("\nscan_ssid=1")
        file.write("\nkey_mgmt=WPA-EAP")
        file.write("\nid_str=\"AP1\"")
        file.write("\npriority=100")
        file.write("\nidentity=\"{}\"".format(identity))
        file.write("\npassword=\"{}\"".format(password))
        file.write("\neap=PEAP")
        file.write("\nphase1=\"peaplabel=0\"")
        file.write("\nphase2=\"auth=MSCHAPV2\"")
        file.write("\n}")
        file.close()

    elif not password:
        print('no password')
        file = open("/etc/wpa_supplicant/wpa_supplicant.conf", "a")
        file.write("\nnetwork={")
        file.write("\nssid=\"" + ssid + "\"")
        if isHiddenNetwork:
            file.write("\nscan_ssid=1")
        file.write("\nkey_mgmt=NONE")
        file.write("\nid_str=\"AP1\"")
        file.write("\npriority=100")
        file.write("\n}")
        file.close()

    else:
        MyOut2 = subprocess.Popen(['wpa_passphrase', ssid, password],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        stdout, stderr = MyOut2.communicate()
        raw_psk = str(stdout[-67:][:-3], 'utf-8')
        wpa_psk = "\npsk="+raw_psk
        print(stderr)
        if len(stdout) == 0:
            pass

        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as file:
            file.write("\nnetwork={")

            file.write("\nssid=\"" + ssid + "\"")
            if isHiddenNetwork:
                file.write("\nscan_ssid=1")
            file.write(wpa_psk)
            file.write("\nid_str=\"AP1\"")
            file.write("\npriority=100")
            file.write("\nkey_mgmt=WPA-PSK")
            file.write("\n}")
            file.close()
    print('added wifi information to wpa_supplicant')
    sleep(3)
    print('force all rogue wpa_supplicant ...')

    print('kill all wpa_supplicant')
    MyOut2 = subprocess.Popen(
        ['sudo', 'systemctl', 'restart', 'zumi_wifi_setup.service'])
    sleep(6)
    print('dhclient end')
    print('getting an ip address')
    print('scripts.py : add_wifi end')


def kill_supplicant():
    myCmd = 'sudo killall -9 wpa_supplicant'
    os.system(myCmd)
    print('finish kill all wpa_supplicant')


def OSinfo(runthis):
    try:
        osstdout = subprocess.check_call(runthis.split())
    except (subprocess.CalledProcessError) as err:
        return 1
    return osstdout


def get_wlan_ip():
    print('scripts.py : check_wifi start')
    cmd = "ifconfig wlan0 | awk '$1 ~ /^inet/ {print $2}'"
    cmd += "| awk '$1 ~/^[1-9]/ {print $0}'"
    ip_addr = os.popen(cmd).read()
    print(ip_addr.split('\n'))
    return ip_addr.split('\n')[0]


def check_wifi():
    print('scripts.py : check_wifi start')
    ssid = os.popen("sudo iwconfig wlan0 | grep 'ESSID' \
                    | awk -F\\\" '{print$2}'").read().replace("\n", "")
    print(ssid)

    numbers = re.findall('\\\\x[0-9a-fA-F][0-9a-fA-F]', ssid)

    # if character has unicode(UTF-8)
    if len(numbers) > 0:
        byte_string = b''
        for n in numbers:
            sp = ssid.split(n, 1)
            if sp[0] != '':
                byte_string += sp[0].encode('utf-8')
            ssid = sp[1]
            byte_string += string_to_hex(n).to_bytes(1, byteorder='big')
        byte_string += ssid.encode('utf-8')
        print(byte_string.decode())
        ssid = byte_string.decode()

    if len(ssid) <= 1:
        MyOut2 = subprocess.Popen(['sudo', 'killall', 'dhclient'])

        return False, "None"
    return True, ssid
    print('scripts.py : check_wifi end')


def check_internet(language, ssid):
    os.popen('sudo echo "nameserver 8.8.8.8">/etc/resolv.conf')

    # testing captive portal
    # return {"online_status": "captive", "network_name": ssid}

    print("checking captive portal")
    if check_captive_portal():
        print('captive portal')
        return {"online_status": "captive", "network_name": ssid}
    print("checking dashboard")
    can_update_dashboard, latest_dashboard, online_status = check_dashboard_update()
    print("checking content")
    try:
        can_update_content = check_content_update(language)
    except:
        can_update_content = False
    try:
        ip_addr = get_wlan_ip()
    except:
        ip_addr = ''
    return {"can_update_dashboard": can_update_dashboard, "can_update_content": can_update_content,
            "latest_dashboard_version": latest_dashboard, "online_status": online_status, "network_name": ssid,
            "ip_addr": ip_addr}


def check_captive_portal():
    os.popen('sudo echo "nameserver 8.8.8.8">/etc/resolv.conf')
    output = ""
    cnt = 0
    while cnt < 3:
        cnt += 1
        output = os.popen(
            'curl --write-out %{http_code} --silent --output /dev/null www.appleiphonecell.com').read()
        print(output)
        if "302" in output or "307" in output:
            return True
        if "000" in output:
            if cnt == 2:
                subprocess.Popen(['sudo', 'systemctl', 'restart', 'zumi_wifi_setup.service'])
                sleep(2)
                return True
        #if "200" in output:
        #    return False
    return False


def check_content_update(language):
    cnt = 0
    latest_content = ''
    while len(latest_content) < 2 and cnt < 3:
        if language == "ko":
            url = "https://raw.githubusercontent.com/robolink-korea/zumi_kor_lesson/master/README.md"
        elif language == "hu":
            url = "https://raw.githubusercontent.com/RobolinkInc/Zumi_Content_Hungarian/master/README.md"
        elif language == "zh":
            url = "https://raw.githubusercontent.com/RobolinkInc/Zumi_Content_Chinese/master/README.md"
        else:
            url = "https://raw.githubusercontent.com/RobolinkInc/Zumi_Content/master/README.md"
        try:
            latest_content = os.popen(
                "curl -m 12 --fail {}".format(url)).read().split()[0]
            cnt += 1
        except:
            latest_content = None
    print(latest_content)
    try:
        current_content = open(
            '/home/pi/Dashboard/Zumi_Content_' + language + '/README.md').readline().split()[0]
    except:
        current_content = None
    finally:
        if current_content is None:
            return "No_content"
        elif latest_content is None:
            return False
        else:
            return current_content != latest_content


def check_content_missing(language):
    try:
        content_path = '/home/pi/Dashboard/Zumi_Content_' + language + '/'
        check_if_master_folder_exists = os.path.isdir(content_path)
        check_if_readme_exists = os.path.exists(content_path + "README.md")
        check_if_lesson_folder_exists = os.path.isdir(content_path + 'Lesson/')
        check_if_lessons_exist = True if len(
            os.listdir(content_path + 'Lesson/')) > 0 else False

        current_content = open(
            '/home/pi/Dashboard/Zumi_Content_' + language + '/README.md').readline().split()[0]

        result = check_if_master_folder_exists and check_if_readme_exists and check_if_lesson_folder_exists and check_if_lessons_exist
        return not result
    except Exception as e:
        print(e)
        return True


def check_user_content_missing(usr, language):
    try:
        current_content = open('/home/pi/Dashboard/user/' + usr +
                               '/Zumi_Content_' + language + '/README.md').readline().split()[0]
        return False
    except:
        return True


def check_dashboard_update():
    cnt = 0
    latest_dashboard = ''
    url = 'https://raw.githubusercontent.com/RobolinkInc/zumi-version/master/version.txt'
    while len(latest_dashboard) < 2 and cnt < 3:
        latest_dashboard = os.popen('curl -m 12 --fail {}'.format(url)).read()
        cnt += 1
    print(latest_dashboard)
    try:
        import json
        lib = "/usr/local/lib/python3.5/dist-packages/zumidashboard"
        with open(lib + '/dashboard/data.json') as version:
            data = json.load(version)
            current_dashboard = data["libVersion"]
    except:
        current_dashboard = None
    online_status = "zumidashboard" in latest_dashboard
    if online_status:
        latest_dashboard = re.findall('[0-9]+.[0-9]+', latest_dashboard)[0]
    else:
        latest_dashboard = current_dashboard
    return current_dashboard != latest_dashboard, latest_dashboard, online_status


def shutdown_ap():
    print('shutting down AP mode')
    subprocess.Popen(['sudo', 'ifdown', '--force', 'ap0'])


def get_ssid_list():
    MyOut = subprocess.Popen(['sudo', 'sh', os.path.dirname(os.path.abspath(__file__)) + '/shell_scripts/scan-ssid.sh', '.'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    stdout, stderr = MyOut.communicate()
    string = stdout.decode()
    numbers = re.findall('\\\\x[0-9a-fA-F][0-9a-fA-F]', string)

    # if character has unicode(UTF-8)
    if len(numbers) > 0:
        byte_string = b''
        for n in numbers:
            sp = string.split(n, 1)
            if sp[0] != '':
                byte_string += sp[0].encode('utf-8')
            string = sp[1]
            byte_string += string_to_hex(n).to_bytes(1, byteorder='big')
        byte_string += string.encode('utf-8')
        print(byte_string.decode())
        string = byte_string.decode()
    else:
        print(stdout.decode())
        string = stdout.decode()

    string = string.replace('\t', '')
    string = string.replace('\n', '')
    result = list()
    ssid_list = list()
    ssid_with_pw = string.split("SSID: ")[1:-1]
    for item in ssid_with_pw:
        split_item = item.split("*")
        if len(split_item) == 1:
            psk_type = False
            is_enterprise = False
        else:
            if "PSK" in split_item[1]:
                psk_type = True
                is_enterprise = False
            else:
                psk_type = True
                is_enterprise = {"eap_auth": "PEAP", "peap_ver": 0,
                                 "inner_authentication": "MSCHAPv2"}
            if split_item[0][-1] == " ":
                split_item[0] = split_item[0][:-1]
        if split_item[0] not in ssid_list:
            result.append(
                {"network_name": split_item[0], "need_pwd": psk_type, "enterprise": is_enterprise})
            ssid_list.append(split_item[0])

    return result  # ssid_list, pw_list


def string_to_hex(str):
    if len(str) != 4:
        return str
    elif str[:2] != '\\x':
        return str
    else:
        f = char_to_hexnumber(str[2])
        s = char_to_hexnumber(str[3])
        if f is not None and s is not None:
            return f*16+s
        else:
            return str


def char_to_hexnumber(ch):
    if re.match('[0-9]', ch):
        return int(ch)
    elif re.match('[a-f]', ch):
        return ord(ch)-87
    elif re.match('[A-F]', ch):
        return ord(ch)-55
    elif True:
        return None


def ap_connected_ip():
    result = os.popen("arp -a").read()
    result = re.findall("(192.168.10.[^)]*)", result)
    return result


def shutdown():
    subprocess.call(["sudo", "shutdown", "now"])


def is_device_connected():
    if ap_connected_ip().__len__() == 0:
        return False
    return True


if __name__ == '__main__':
    print(get_wlan_ip())
