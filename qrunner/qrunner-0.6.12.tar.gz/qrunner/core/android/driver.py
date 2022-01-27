import os
import time
import allure
import uiautomator2 as u2
from qrunner.utils.config import conf
from qrunner.utils.log import logger


class AndroidDriver(object):
    _instance = {}

    def __new__(cls, serial_no=None):
        if not serial_no:
            serial_no = conf.get_name('app', 'serial_no')
        if serial_no not in cls._instance:
            cls._instance[serial_no] = super().__new__(cls)
        return cls._instance[serial_no]

    def __init__(self, serial_no=None):
        if not serial_no:
            self.serial_no = conf.get_name('app', 'serial_no')
        self.serial_no = serial_no
        self.pkg_name = conf.get_name('app', 'pkg_name')

        logger.info(f'启动 android driver for {self.serial_no}')
        self.d = u2.connect(self.serial_no)
        self.session = None

    @classmethod
    def get_instance(cls, serial_no=None):
        """Create singleton"""
        if serial_no not in cls._instance:
            logger.info(f'[{serial_no}] Create android driver singleton')
            return AndroidDriver(serial_no)
        return AndroidDriver._instance[serial_no]

    # @classmethod
    # def get_remote_instance(cls, server_url, token):
    #     device = Device(server_url, token)
    #     d = u2.connect(device.get_device())
    #     return d, device

    def uninstall_app(self, pkg_name=None):
        if not pkg_name:
            pkg_name = self.pkg_name
        logger.info(f'卸载应用: {pkg_name}')
        self.d.app_uninstall(pkg_name)

    def install_app(self, apk_path, is_new=False):
        if is_new:
            self.uninstall_app(self.pkg_name)
        logger.info(f'安装应用: {apk_path}')
        self.d.app_install(apk_path)

    def start_app(self, pkg_name=None):
        if not pkg_name:
            pkg_name = self.pkg_name
        logger.info(f'启动应用: {pkg_name}')
        self.d.app_start(pkg_name)

    def stop_app(self, pkg_name=None):
        if not pkg_name:
            pkg_name = self.pkg_name
        logger.info(f'退出应用: {pkg_name}')
        self.d.app_stop(pkg_name)

    def stop_all_app(self):
        logger.info(f'退出所有应用')
        self.d.app_stop_all()

    def stop_app_list(self, app_list: list):
        logger.info(f'退出多个应用: {app_list}')
        self.d.app_stop_all(excludes=app_list)

    def force_start_app(self, pkg_name=None):
        if not pkg_name:
            pkg_name = self.pkg_name
        logger.info(f'强制启动应用: {pkg_name}')
        self.d.app_start(pkg_name, stop=True)

    def clear_app(self, pkg_name=None):
        if not pkg_name:
            pkg_name = self.pkg_name
        logger.info(f'清除应用缓存: {pkg_name}')
        self.d.app_clear(pkg_name)

    def get_driver_info(self):
        logger.info(f'获取连接信息')
        return self.d.info

    def get_app_info(self, pkg_name=None):
        if not pkg_name:
            pkg_name = self.pkg_name
        logger.info(f'获取指定应用信息: {pkg_name}')
        info = self.d.app_info(pkg_name)
        logger.info(info)
        return info

    def get_current_app(self):
        logger.info(f'获取当前应用信息')
        return self.d.app_current()

    def save_app_icon(self, pkg_name=None):
        if not pkg_name:
            pkg_name = self.pkg_name
        logger.info(f'获取应用icon并保存到当前目录')
        img = self.d.app_icon(pkg_name)
        img.save(f'{pkg_name}-icon.png')

    def get_running_apps(self):
        logger.info(f'获取所有正在运行的应用')
        app_list = self.d.app_list_running()
        logger.info(app_list)
        return app_list

    def get_app_list(self):
        logger.info(f'获取所有已安装的应用')
        app_list = self.d.app_list()
        logger.info(app_list)
        return app_list

    def wait_app_running(self, pkg_name=None, front=True, timeout=20):
        """
        等待应用运行
        @param pkg_name: 应用包名
        @param front: 是否前台运行
        @param timeout: 等待时间
        @return: 应用pid
        """
        if not pkg_name:
            pkg_name = self.pkg_name
        pid = self.d.app_wait(pkg_name, front=front, timeout=timeout)
        if not pid:
            logger.info(f'{pkg_name} is not running')
        else:
            logger.info(f'{pkg_name} pid is {pid}')
        return pid

    def wait_activity(self, activity_name, timeout=10):
        """
        等待activity运行
        @param activity_name: activity名称，.ApiDemos
        @param timeout: 超时时间
        @return: True or False
        """
        logger.info(f'等待activity {activity_name}')
        flag = self.d.wait_activity(activity_name, timeout=timeout)
        logger.info(flag)
        return flag

    def push(self, src_path, target_path, mode=None):
        """
        把电脑本地文件上传到手机上
        @param src_path: 电脑本地文件，foo.txt
        @param target_path: 手机目录，/sdcard/
        @param mode: 需要修改的权限，0o755
        @return:
        """
        logger.info(f'把{src_path} push到手机 {target_path}目录')
        if mode is not None:
            self.d.push(src_path, target_path)
        else:
            self.d.push(src_path, target_path, mode=mode)

    def pull(self, src_path, target_path):
        """
        把手机上的文件下载到电脑
        @param src_path: 手机文件，/sdcard/tmp.txt
        @param target_path: 电脑目录，tmp.txt
        @return:
        """
        logger.info(f'{src_path} pull到电脑 {target_path}目录')
        self.d.pull(src_path, target_path)

    def check(self):
        logger.info('检查并维持设备端守护进程处于运行状态')
        self.d.healthcheck()

    def open_url(self, url):
        """
        通过url打开web页面或者app schema
        @param url: 页面url，https://www.baidu.com，taobao://taobao.com
        @return:
        """
        logger.info(f'打开链接: {url}')
        self.d.open_url(url)

    def shell(self, cmd, timeout=60):
        """
        执行短周期shell脚本
        @param cmd: shell字符串或list，pwd，["ls", "-l"]
        @param timeout: 超时时间
        @return:
        """
        logger.info(f'执行shell命令: {cmd}')
        output, exit_code = self.d.shell(cmd, timeout=timeout)
        return output, exit_code

    def start_session(self, pkg_name=None):
        """
        启动应用并生成session
        @param pkg_name: 应用包名
        @return:
        """
        logger.info(f'启动{pkg_name}session')
        if not pkg_name:
            pkg_name = self.pkg_name
        self.session = self.d.session(pkg_name)

    def stop_session(self):
        logger.info(f'关闭session并停止应用')
        self.session.close()

    def check_session(self):
        logger.info(f'检查session是否可用')
        is_running = self.session.running()
        logger.info(is_running)
        return is_running

    def screenshot(self, file_name):
        """
        截图并保存到预定路径并上传到allure报告
        @param file_name: foo.png or fool
        @return:
        """
        # 把文件名处理成test.png的样式
        if '.' in file_name:
            file_name = file_name.split(r'.')[0]
        # 截图并保存到当前目录的images文件夹中
        img_dir = os.path.join(os.getcwd(), 'images')
        if os.path.exists(img_dir) is False:
            os.mkdir(img_dir)
        time_str = time.strftime('%Y%m%d%H%M%S')
        file_path = os.path.join(img_dir,
                                 f'{file_name}-{time_str}.png')
        logger.info(f'截图保存至: {file_path}')
        self.d.screenshot(file_path)
        # 截图并上传到allure报告
        logger.info(f'截图上传至allure报告')
        allure.attach.file(file_path,
                           attachment_type=allure.attachment_type.PNG,
                           name=f'{file_name}-{time_str}')

    # def upload_pic(self, filename):
    #     self.screenshot('tmp.png')
    #     allure.attach.file(
    #         'tmp.png',
    #         attachment_type=allure.attachment_type.PNG,
    #         name=f'{filename}-{get_time()}'
    #     )
    #     os.remove('tmp.png')

    # def input_password(self, text):
    #     self.d(focused=True).set_text(text)

    def get_page_content(self):
        return self.d.dump_hierarchy()

    def get_window_size(self):
        return self.d.window_size()

    def get_serial(self):
        logger.info('获取设备id')
        serial = self.d.serial
        logger.info(serial)
        return serial

    def get_device_info(self):
        logger.info(f'获取设备信息')
        info = self.d.device_info
        logger.info(info)
        return info

    def screen_on(self):
        logger.info('点亮屏幕')
        self.d.screen_on()

    def screen_off(self):
        logger.info('关闭屏幕')
        self.d.screen_off()

    def get_screen_status(self):
        logger.info('获取屏幕点亮状态')
        status = self.d.info.get('screenOn')
        logger.info(status)
        return status

    def unlock(self):
        logger.info('解锁手机')
        self.d.unlock()

    def press(self, key):
        """
        点击原生自带按键
        @param key: 按键名，支持：home、back、left、right、up、down、center、menu、search、enter、delete、recent、volume_up、
                    volume_down、volume_mute、camera、power
        @return:
        """
        logger.info(f'点击key: {key}')
        self.press(key)

    def click(self, x, y):
        logger.info(f'单击坐标: {x},{y}')
        self.d.click(x, y)

    def click_alert(self, alert_list: list):
        logger.info(f'批量点击弹窗: {alert_list}')
        with self.d.watch_context() as ctx:
            for alert in alert_list:
                ctx.when(alert).click()
            ctx.wait_stable()

    def double_click(self, x, y):
        logger.info(f'双击坐标: {x},{y}')
        self.d.double_click(x, y)

    def long_click(self, x, y):
        logger.info(f'长按坐标: {x},{y}')
        self.d.long_click(x, y)

    def swipe(self, sx, sy, ex, ey):
        logger.info(f'从坐标{sx},{sy} 滑到 {ex},{ey}')
        self.d.swipe(sx, sy, ex, ey)

    def swipe_left(self, scale=0.9):
        logger.info('往左滑动')
        self.d.swipe_ext('left', scale=scale)

    def swipe_right(self, scale=0.9):
        logger.info('往右滑动')
        self.d.swipe_ext('right', scale=scale)

    def swipe_up(self, scale=0.8):
        logger.info('往上滑动')
        self.d.swipe_ext('up', scale=scale)

    def swipe_down(self, scale=0.8):
        logger.info('往下滑动')
        self.d.swipe_ext('down', scale=scale)

    def scroll_down_fast(self):
        logger.info('快速往下滑动')
        self.d(scrollable=True).fling()

    def scroll_down_slow(self, step=50):
        """
        通过step控制滑动速度
        @param step:
        @return:
        """
        logger.info('慢速往下滑动')
        self.d(scrollable=True).scroll(steps=step)

    def scroll_up_fast(self):
        logger.info('快速往上滑动')
        self.d(scrollable=True).fling.vert.backward()

    def scroll_up_down(self, step):
        """
        通过step控制滑动速度
        @param step:
        @return:
        """
        logger.info('慢速往下滑动')
        self.d(scrollable=True).scroll.vert.backward(steps=step)

    def scroll_bottom_fast(self):
        logger.info('快速滑到底部')
        self.d(scrollable=True).fling.toEnd()

    def scroll_bottom_slow(self, step=50):
        """
        通过step控制滑动速度
        @param step:
        @return:
        """
        logger.info('慢速滑到底部')
        self.d(scrollable=True).scroll.toEnd(steps=step)

    def scroll_top_fast(self):
        logger.info('快速滑到顶部')
        self.d(scrollable=True).fling.toBeginning()

    def scroll_top_slow(self, step=50):
        """
        通过step控制滑动速度
        @param step:
        @return:
        """
        logger.info('慢速滑到顶部')
        self.d(scrollable=True).scroll.toBeginning(steps=step)

    def scroll_to(self, *args, **kwargs):
        logger.info(f'滑动到元素: {kwargs}')
        self.d(scrollable=True).scroll.to(*args, **kwargs)

    def drag(self, sx, sy, ex, ey):
        logger.info(f'从坐标{sx},{sy} 拖动到坐标{ex},{ey}')
        self.d.drag(sx, sy, ex, ey)

    def send_keys(self, text, clear=True):
        logger.info(f'输入: {text}')
        self.d.set_fastinput_ime(True)
        if clear:
            self.d.clear_text()
        self.d(focused=True).set_text(text)
        self.d.set_fastinput_ime(False)

    def set_ori_left(self):
        logger.info('屏幕向右边转动')
        self.d.set_orientation("l")

    def set_ori_right(self):
        logger.info('屏幕向左边转动')
        self.d.set_orientation('r')

    def set_ori_natural(self):
        logger.info('屏幕恢复原始转向')
        self.d.set_orientation('n')

    def start_record(self, file_name='output'):
        logger.info('开始录制')
        img_dir = os.path.join(os.getcwd(), 'images')
        if os.path.exists(img_dir) is False:
            os.mkdir(img_dir)
        time_str = time.strftime('%m%d%H%M%S')
        file_path = os.path.join(img_dir,
                                 f'{file_name}-{time_str}.mp4')
        self.d.screenrecord(file_path)

    def stop_record(self):
        logger.info('停止录屏')
        self.d.screenrecord.stop()






