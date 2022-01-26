from zumidashboard import zumi, screen, StoppableThread
import zumidashboard.sounds as sounds
import zumidashboard.scripts as scripts
import time
import subprocess


class CheckInternetThread(StoppableThread):
    def __init__(self, info):
        StoppableThread.__init__(self)
        self.info = info

    def run(self):
        # if app.checked_internet:
        #    return
        self.info['need_to_update'] = False
        self.info['checked_internet'] = True
        connected, ssid = scripts.check_wifi()
        if not connected:
            print('Not connected to WiFi')
            self.info['internet_info'] = False
            return

        time.sleep(3)

        self.info['internet_info'] = scripts.check_internet(
            self.info['language'], ssid)

        if self.info['internet_info']["online_status"] == "captive":
            print('app.py: emit check internet captive portal')
            #log('app.py : emit check internet captive portal')
        elif self.info['internet_info']["can_update_dashboard"] or self.info['internet_info']["can_update_content"]:
            self.info['need_to_update'] = True
            print('app.py: need update')
            #log('app.py : need update')


class ConnectWifiThread(StoppableThread):
    # def __init__(self, ssid, password, isHiddenNetwork, isEnterprise):
    def __init__(self, ssid, username, password, isHiddenNetwork):
        StoppableThread.__init__(self)
        self.ssid = ssid
        self.username = username
        self.password = password
        self.isHiddenNetwork = isHiddenNetwork
        # self.isEnterprise = isEnterprise

    def run(self):
        print('app.py : connecting wifi start')
        # log_info('app.py : connecting wifi start')

        print(str(type(self.ssid)) + self.ssid)
        # scripts.add_wifi(self.ssid, self.password, self.isHiddenNetwork, self.isEnterprise)
        scripts.add_wifi(self.ssid, self.username,
                         self.password, self.isHiddenNetwork)
        print("personality start")
        screen.draw_image_by_name("tryingtoconnect")
        sounds.try_calibrate_sound(zumi)
        sounds.try_calibrate_sound(zumi)
        print("personality done")
        # log_info('app.py : connecting wifi:' + self.ssid + ' end')
        print('app.py : connecting wifi end')


def activate_offline_mode():
    screen.draw_text_center("Starting offline mode")
    subprocess.Popen(['sudo', 'killall', 'wpa_supplicant'])
    time.sleep(2)
