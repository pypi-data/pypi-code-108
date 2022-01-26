from zumi.zumi import Zumi
from zumi.util.screen import Screen
from zumi.protocol import Note
import os, subprocess, time, signal
from threading import Thread
from PIL import Image, ImageDraw
import numpy as np


def __progress(screen, img, start, end):
    while start != end:
        draw = ImageDraw.Draw(img)
        draw.point([(start + 13, 35), (start + 13, 36), (start + 13, 37)])
        screen.draw_image(img.convert('1'))
        start += 1


def __finished_updating(_internal_zumi, _screen):
    # TODO need to change this part more clear
    # img = _screen.path_to_image('/usr/local/lib/python3.5/dist-packages/zumi/util/images/happy1.ppm')
    # time.sleep(.5)
    # _screen.draw_text(text, x=10, y=5, image=img.convert('1'), font_size=12, clear=False)

    tempo = 60
    time.sleep(0.5)
    _internal_zumi.play_note(41, tempo)
    _internal_zumi.play_note(43, tempo)
    _internal_zumi.play_note(45, tempo)
    time.sleep(1)
    f = open("/home/pi/Dashboard/upate/justUpdated", "w")
    f.write("Just updated")
    f.close()


class UpdaterThread(Thread):
    def __init__(self, language=None):
        Thread.__init__(self)
        self.kill_flag = False
        self.process = None
        self._language = language
        self.success = True
        if self._language == 'ko':
            self.git_url = 'git clone https://github.com/robolink-korea/zumi_kor_lesson.git '
        elif self._language == 'hu':
            self.git_url = 'git clone https://github.com/RobolinkInc/Zumi_Content_Hungarian.git '
        elif self._language == 'zh':
            self.git_url = 'git clone https://github.com/RobolinkInc/Zumi_Content_Chinese.git '
        else:
            self.git_url = 'git clone https://github.com/RobolinkInc/Zumi_Content.git '

    def run(self):
        self.process = subprocess.Popen(self.git_url + '/home/pi/Dashboard/content_temp',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, preexec_fn=os.setsid)
        print("start clone")
        try:
            while self.process.poll() is None:
                time.sleep(1)
        except:
            print("Couldn't update, please try again")
            self.success = False
        print("git clone done")
        try:
            for line in self.process.stdout:
                print(line.decode(), end='')
                if 'fatal: ' in line.decode():
                    print("found fatal")
                    self.success = False
                print(self.success)
        except:
            print("process killed")
            self.success = False
        time.sleep(2)

    def kill(self):
        if self.process.poll() is None:
            self.process.kill()
            self.process.stdout.close()


def __kill_updater(proc, timeout):
    print("timeout!")
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    timeout["value"] = True


def update_version(_zumi, _screen, v=None):
    if v is None:
        _screen.draw_text_center("didn't get the version number try again")
        return False
    p = subprocess.Popen('sudo pip3 install zumidashboard=={}'.format(v),
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    img_arr = np.asarray(Image.open('/usr/local/lib/python3.5/dist-packages/zumi/util/images/blankbar.ppm'))
    img = Image.fromarray(img_arr.astype('uint8'))

    _screen.draw_text("I'm updating", x=31, y=8, image=img.convert('1'), font_size=12, clear=False)
    img = _screen.screen_image.convert('RGB')

    updater_thread = Thread(target=__progress, args=(_screen,img, 0, 51))
    updater_thread.start()

    try:
        while p.poll() is None:
            line = p.stdout.readline().decode()
            print(line)

            if 'Error' in line:
                updater_thread.join()
                _screen.draw_text_center("Couldn't update, please try again")
                time.sleep(1)
                _zumi.play_note(Note.A5, 100)
                _zumi.play_note(Note.F5, 2 * 100)
                time.sleep(7)
                return False

            if 'Collecting' in line:
                updater_thread.join()
                updater_thread = Thread(target=__progress, args=(_screen, img, 51, 88))
                updater_thread.start()

            elif 'Installing collected packages' in line:
                updater_thread.join()
                updater_thread = Thread(target=__progress, args=(_screen, img, 88, 96))
                updater_thread.start()

            elif 'Successfully installed' in line:
                updater_thread.join()
                updater_thread = Thread(target=__progress, args=(_screen, img, 96, 101))
                updater_thread.start()

        updater_thread.join()

        time.sleep(1)
        img = _screen.path_to_image('/usr/local/lib/python3.5/dist-packages/zumi/util/images/happy1.ppm')
        time.sleep(.5)
        _screen.draw_text("I'm updated!", x=32, y=5, image=img.convert('1'), font_size=12, clear=False)
        __finished_updating(_zumi, _screen)
        time.sleep(2)

    except Exception as e:
        updater_thread.join()
        _screen.draw_text_center("Zumi already up-to-date")
        print(e)
    return True


def update_content(_zumi, _screen, _language='en'):
    print("new updater content")
    img = Image.open('/usr/local/lib/python3.5/dist-packages/zumi/util/images/blankbar.ppm')
    img = Image.fromarray(np.asarray(img).astype('uint8'))
    _screen.draw_text("Getting latest lessons", x=5, y=8, image=img.convert('1'), font_size=12, clear=False)
    img = _screen.screen_image.convert('RGB')
    print("setting done")
    content_updater_thread = UpdaterThread(_language)
    progress_bar_thread = Thread(target=__progress, args=(_screen, img, 0, 71))
    progress_bar_thread.start()
    content_updater_thread.start()
    st_time = time.time()
    time.sleep(1)

    while content_updater_thread.is_alive():
        if time.time() - st_time > 30:
            print("checking internet")
            if not _check_internet():
                print("fail to get info from internet")
                content_updater_thread.kill()
                break
            st_time = time.time()
            time.sleep(2)
    print("joining updater")
    content_updater_thread.join()
    print("joining progress bar")
    progress_bar_thread.join()
    print("update {}".format(content_updater_thread.success))
    time.sleep(1)

    if content_updater_thread.success:
        progress_bar_thread = Thread(target=__progress, args=(_screen, img, 67, 101))
        progress_bar_thread.start()
        _change_to_log_folder(_language)
        temp = subprocess.Popen("sudo mv /home/pi/Dashboard/content_temp /home/pi/Dashboard/Zumi_Content_" + _language,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        temp.communicate()
        temp = subprocess.Popen("sudo chown -R pi " + "/home/pi/Dashboard/Zumi_Content_" + _language,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        temp.communicate()
        progress_bar_thread.join()
        time.sleep(1)
        updated_version = open('/home/pi/Dashboard/Zumi_Content_{}/README.md'.format(_language)).readline().split()[0]
        # __finished_updating(_zumi, _screen, "Updated to v{} !".format(updated_version))
        _screen.draw_text_center("Got the latest lessons!")
        tempo = 60
        time.sleep(0.5)
        _zumi.play_note(41, tempo)
        _zumi.play_note(43, tempo)
        _zumi.play_note(45, tempo)
        time.sleep(2)
    else:
        _screen.draw_text_center("Couldn't update, please try again")
        time.sleep(1)
        _zumi.play_note(Note.A5, 100)
        _zumi.play_note(Note.F5, 2 * 100)
        time.sleep(4)
        temp = subprocess.Popen("sudo rm -rf /home/pi/Dashboard/content_temp",
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        temp.communicate()


def _check_internet():
    cnt = 0
    latest_dashboard = ''
    url = 'https://raw.githubusercontent.com/RobolinkInc/zumi-version/master/version.txt'
    while len(latest_dashboard) < 2 and cnt < 2:
        latest_dashboard = os.popen('curl -m 12 --fail {}'.format(url)).read()
        cnt += 1
    return "zumidashboard" in latest_dashboard


def _roll_back_folder(_screen, _zumi, log_folder, path, language):
    if log_folder is not None:
        print("revert folder")
        subprocess.Popen("sudo rm -rf /home/pi/Dashboard/Zumi_Content_"+language,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        time.sleep(1)
        subprocess.Popen('mv ' + log_folder + " " + path + "Zumi_Content_"+language,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        time.sleep(2)
        subprocess.Popen("sudo chown -R pi " + path + "Zumi_Content_"+language,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    _screen.draw_text_center("Couldn't update, please try again")
    time.sleep(1)
    _zumi.play_note(Note.A5, 100)
    _zumi.play_note(Note.F5, 2 * 100)
    time.sleep(7)


def _change_to_log_folder(language, path='/home/pi/Dashboard/'):
    if not os.path.isdir("{}content_history".format(path)):
        os.mkdir("{}content_history".format(path))

    current = None
    try:
        if os.path.isdir(path+'Zumi_Content_{}'.format(language)):
            current = open(path+'Zumi_Content_{}/README.md'.format(language)).readline().split()[0]
        else:
            return current
    except FileNotFoundError:
        current = '0.0'

    folder_name = 'content_history/log_v{}_content_{}'.format(str(current), language)
    log_folder = path + folder_name
    cnt = 1
    while os.path.isdir(log_folder):
        log_folder = path + folder_name + '_{}'.format(cnt)
        cnt += 1
    subprocess.Popen('mv ' + path + 'Zumi_Content_{} '.format(language) + log_folder,
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    time.sleep(2)
    subprocess.Popen("sudo chown -R pi " + log_folder,
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    print("change name : {}".format(log_folder))
    return log_folder


def restart_threads(_zumi, _screen):
    Thread(target=restart_app, args=()).start()
    Thread(target=go_to_zumi_dashboard_msg, args=(_zumi, _screen)).start()


def restart_app():
    subprocess.run(["sudo systemctl restart zumidashboard.service"], shell=True)


def go_to_zumi_dashboard_msg(_zumi, _screen):
    lib_dir = os.path.dirname(os.path.abspath(__file__))
    _screen.draw_text_center("Dashboard restarting...")
    while True:
        p = subprocess.Popen(
            ['sudo', 'bash', lib_dir + '/shell_scripts/check_port.sh', '80'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        stdout, stderr = p.communicate()
        p.wait()
        if len(stdout) > 1:
            print("server(port 80) is not ready")
        else:
            print("server(port 80) is ready")
            tempo = 60
            _zumi.play_note(41, tempo)
            _zumi.play_note(43, tempo)
            _zumi.play_note(45, tempo)
            break
        time.sleep(2)
    _screen.draw_text_center("Go to \"zumidashboard.ai\" in your browser")


def check_user_content(base_dir_path, usr_dir_path, language):
    try:
        base = open(base_dir_path + 'Zumi_Content_{}/README.md'.format(language)).readline().split()[0]
    except:
        return True
    try:
        usr_version = open(usr_dir_path+'Zumi_Content_{}/README.md'.format(language)).readline().split()[0]
    except:
        return True

    if usr_version != base:
        return True
    else:
        return False


def copy_content(base_dir_path, usr_dir_path, language):
    _change_to_log_folder(language, usr_dir_path)
    p = subprocess.Popen(['cp', '-r', base_dir_path + 'Zumi_Content_' + language, usr_dir_path])
    stdout, stderr = p.communicate()
    print("done copy")
    time.sleep(2)
    p = subprocess.Popen("sudo chown -R pi:pi " + usr_dir_path + 'Zumi_Content_'+language,
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    stdout, stderr = p.communicate()
    print("done change permition")


def update_develop_version(_zumi, _screen):
    option = '--upgrade'
    git_url = 'https://develop:ehhwu3qQn5Es5aJVuFS9@gitlab.com/robolink-team/Flask-AP.git@develop#egg=zumidashboard'
    p = subprocess.Popen('sudo pip3 install {} git+{}'.format(option, git_url),
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    img_arr = np.asarray(Image.open('/usr/local/lib/python3.5/dist-packages/zumi/util/images/blankbar.ppm'))
    img = Image.fromarray(img_arr.astype('uint8'))

    _screen.draw_text("Updating from git", x=9, y=8, image=img.convert('1'), font_size=12, clear=False)
    img = _screen.screen_image.convert('RGB')

    updater_thread = Thread(target=__progress, args=(_screen,img, 0, 21))
    updater_thread.start()

    try:
        while p.poll() is None:
            line = p.stdout.readline().decode()
            print(line)

            if 'Error' in line:
                updater_thread.join()
                _screen.draw_text_center("Couldn't update, please try again")
                time.sleep(1)
                _zumi.play_note(Note.A5, 100)
                _zumi.play_note(Note.F5, 2 * 100)
                time.sleep(7)
                return False

            if 'Cloning' in line:
                updater_thread.join()
                updater_thread = Thread(target=__progress, args=(_screen, img, 21, 88))
                updater_thread.start()

            elif 'Installing collected packages' in line:
                updater_thread.join()
                updater_thread = Thread(target=__progress, args=(_screen, img, 88, 96))
                updater_thread.start()

            elif 'Successfully installed' in line:
                updater_thread.join()
                updater_thread = Thread(target=__progress, args=(_screen, img, 96, 101))
                updater_thread.start()
                version_info = line.split('-')[-1]

        print(version_info)
        updater_thread.join()

        time.sleep(1)
        img = _screen.path_to_image('/usr/local/lib/python3.5/dist-packages/zumi/util/images/happy1.ppm')
        time.sleep(.5)
        _screen.draw_text("I'm updated!", x=24, y=5, image=img.convert('1'), font_size=12, clear=False)
        __finished_updating(_zumi, _screen)
        _screen.draw_text_center("Dashboard updated to v" + str(version_info), font_size=15)

    except Exception as e:
        updater_thread.join()
        _screen.draw_text_center("Couldn't update, please try again")
        time.sleep(1)
        _zumi.play_note(Note.A5, 100)
        _zumi.play_note(Note.F5, 2 * 100)
        time.sleep(7)
        return False
    return True


def update_eveything_pipeline(_zumi, _screen, v, language='en'):
    update_success = update_version(_zumi, _screen, v)
    time.sleep(2)
    if update_success:
        update_content(_zumi, _screen, language)
    restart_threads(_zumi, _screen)


def update_dashboard_pipeline(_zumi, _screen, v):
    update_version(_zumi, _screen, v)
    time.sleep(2)
    restart_threads(_zumi, _screen)


def update_develop_pipeline(_zumi, _screen):
    update_develop_version(_zumi, _screen)
    time.sleep(2)
    restart_threads(_zumi, _screen)


def run_develop():
    zumi = Zumi()
    screen = Screen(clear=False)
    update_develop_pipeline(zumi, screen)


def run(v=None):
    zumi = Zumi()
    screen = Screen(clear=False)
    update_dashboard_pipeline(zumi, screen, v)


def run_everything(v=None, language='en'):
    zumi = Zumi()
    screen = Screen(clear=False)
    update_eveything_pipeline(zumi, screen, v, language)


if __name__ == '__main__':
    import sys
    lib_dir = os.path.dirname(os.path.abspath(__file__))
    p = subprocess.Popen(
        ['sudo', 'bash', lib_dir+'/shell_scripts/check_port.sh', '80'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    p.wait()
    if len(stdout) > 1:
        print("server(port 80) is not ready")
    else:
        print("server(port 80) is ready")
        p = subprocess.Popen(['sudo', 'systemctl', 'stop', 'zumidashboard.service'])

    if sys.argv[1] == "develop":
        run_develop()
    elif sys.argv[2] == "None":
        run(sys.argv[1])
    else:
        run_everything(sys.argv[1], sys.argv[2])
