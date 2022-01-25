import logging
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from catswalk.scraping.request import CWRequest
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
from catswalk.scraping.types.type_webdriver import EXECUTION_ENV, DEVICE, DEVICE_MODE
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from PIL import Image
from io import BytesIO
from catswalk.scraping.driverfunc.wait import wait_until_images_loaded
from catswalk.scraping.driverfunc.jquery import import_jquer


logger = logging.getLogger()

class CWWebDriver:
    def __init__(self, binary_location: str = None, executable_path: str = None, execution_env: EXECUTION_ENV = EXECUTION_ENV.LOCAL, device = DEVICE.DESKTOP_GENERAL, proxy: str = None, implicitly_wait = 5.0, debug:bool = False):
        """[summary]

        Args:
            binary_location (str): [description]
            executable_path (str): [description]
            execution_env (str, optional): [local, local_headless, aws]. Defaults to "local".
            proxy (str, optional): [description]. Defaults to None.
        """
        self.binary_location = binary_location
        self.executable_path = executable_path
        self.execution_env = execution_env
        self.proxy = proxy
        self.device = device
        self.debug = debug
        self.scrolled = False
        self.prev_class = None

        print(f"device: {device}")

        options = Options()
        if self.execution_env == EXECUTION_ENV.LOCAL_HEADLESS:
            options.binary_location = self.binary_location
            options.add_argument('--headless') # https://www.ytyng.com/blog/ubuntu-chromedriver/
            options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
            options.add_argument("start-maximized")  # open Browser in maximized mode
            options.add_argument("disable-infobars")  # disabling infobars
            options.add_argument("--disable-extensions")  # disabling extensions
            options.add_argument("--disable-gpu")  # applicable to windows os only
            options.add_argument("--no-sandbox")  # Bypass OS security model
        elif self.execution_env == EXECUTION_ENV.AWS_LAMBDA:
            os.environ['HOME'] = '/opt/browser/'
            self.executable_path = "/opt/browser/chromedriver"
            options.binary_location = "/opt/browser/headless-chromium"
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--single-process")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1280x1696")
            options.add_argument("--disable-application-cache")
            options.add_argument("--disable-infobars")
            options.add_argument("--hide-scrollbars")
            options.add_argument("--enable-logging")
            options.add_argument("--log-level=0")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--homedir=/tmp")
            options.add_argument('--disable-dev-shm-usage')
        else:
            options.binary_location = self.binary_location
        if self.proxy:
            logging.info("WebDriverSession proxy on")
            options.add_argument(f"proxy-server={self.proxy}")

        if device.value.mode == DEVICE_MODE.MOBILE:
            device_name = device.value.agent
            # https://chromium.googlesource.com/chromium/src/+/167a7f5e03f8b9bd297d2663ec35affa0edd5076/third_party/WebKit/Source/devtools/front_end/emulated_devices/module.json
            #device_name = "Galaxy S5"
            print(device_name)
            mobile_emulation = { "deviceName": device_name }
            options.add_experimental_option("mobileEmulation", mobile_emulation)

        caps = DesiredCapabilities.CHROME
        caps['loggingPrefs'] = {'performance': 'INFO'}
        #logging.info(f"WebDriverSession.__init__ : {binary_location}, {executable_path}, {proxy}, {execution_env}")
        self.driver = webdriver.Chrome(options=options, executable_path=self.executable_path, desired_capabilities=caps)
        self.driver.implicitly_wait(implicitly_wait)


    def __enter__(self):
        """

        :return:
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.close()

    def close(self):
        """[Close WebDriverSession, if chromewebdriver dosen't kill, plsease execute "killall chromedriver"]
        
        """
        self.driver.quit()

    def reload(self):
        self.driver.refresh()

    @property
    def cookies(self):
        """[Get cookie info]

        Returns:
            [type]: [description]
        """
        return self.driver.get_cookies()

    def to_request_session(self) -> CWRequest:
        """[summary]
        
        Returns:
            Request -- [description]
        """
        session = CWRequest()
        for cookie in self.driver.get_cookies():
            self.session.cookies.set(cookie["name"], cookie["value"])
        return session

    def wait_rendering_by_id(self, id, timeout=20):
        """[summary]
        
        Arguments:
            id {[type]} -- [description]
        
        Keyword Arguments:
            timeout {int} -- [description] (default: {20})
        """
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.ID, id)))

    def wait_rendering_by_class(self, _class, by_css_selector: bool, timeout=20):
        """[summary]
        
        Arguments:
            _class {[type]} -- [description]
        
        Keyword Arguments:
            timeout {int} -- [description] (default: {20})
        """
        print(f"wait_rendering_by_class: {_class}")
        if by_css_selector:
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, _class)))
        else:
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, _class)))

    def transition(self, url: str):
        """[summary]

        Args:
            url (str): [description]
        """
        self.driver.get(url)
        self.scrolled = False

    def get(self, url: str):
        self.transition(url=url)
        #WebDriverWait(self.driver, 10).until(EC.url_changes(url))
        soup = self.html
        self.driver.maximize_window()
        return soup

    def __wait_print(self):
        wait_until_images_loaded(driver=self.driver)
        if self.position_height != 0:
            self.scroll_by_offset(offset=1)
            self.scroll_by_offset(offset=-1)
            self.scroll_by_offset(offset=-1)
            self.scroll_by_offset(offset=1)

    def print_screen_by_class_name(self, class_name:str, output_path: str, filename:str) -> str:
        """[summary]

        Args:
            class_name (str): [description]
            output_path (str): [description]
            filename (str): [description]
        """
        # Get Screen Shot
        fullpath = f"{output_path}/{filename}.png"
        self.__wait_print()
        png = self.driver.find_element_by_class_name(class_name).screenshot_as_png
        # ファイルに保存
        with open(fullpath, 'wb') as f:
            f.write(png)
        return fullpath


    def print_screen_by_size(self, w, h, path, filename, start_w: int = 0, start_h: int = 0):
        """
        hw = self.driver.get_window_size()
        w = hw["width"]
        h = hw["height"]
        """
        self.__wait_print()
        #self.driver.save_screenshot(f"{path}/tmp_{filename}.png")
        print(f"print_screen_by_size: {start_w}, {start_h}, {w}, {h}")
        
        img_binary = self.driver.get_screenshot_as_png()
        img = Image.open(BytesIO(img_binary))
        print(f"print_screen_by_size, {start_w}, {start_h}, {w}, {h}")
        crop_dim = (start_w, start_h, w, h) # left top right bottom
        img = img.crop(crop_dim)
        fullpath = f"{path}/{filename}.png"
        img.save(fullpath)
        
        return fullpath

    def print_screen_by_hight(self, h, path, filename, scale: int = 1, index:int = 1):
        # htmlタグからクライアントのwindowサイズを抜き出す
        html = self.driver.find_element_by_tag_name('html')
        inner_width = int(html.get_attribute("clientWidth"))
        inner_height = int(html.get_attribute("clientHeight"))
        print(f"inner_width: {inner_width}, inner_height:{inner_height}")

        if self.execution_env == EXECUTION_ENV.LOCAL:
            if self.device == DEVICE.MOBILE_iPad_Pro or self.device == DEVICE.DESKTOP_GENERAL:
                scale = 2
            else:
                scale = 3
            w = inner_width * scale
            #scaled_h = h * scale
        else:
            if self.device == DEVICE.MOBILE_iPad_Pro or self.device == DEVICE.DESKTOP_GENERAL:
                scale = 2
            else:
                scale = 3
            w = inner_width * scale
            #scaled_h = h * scale
        fullpath = self.print_screen_by_size(w=int(w), h=int(h), path=path, filename=filename)
        return fullpath

    def print_screen_by_class_hight(self, class_name, path, filename, index:int = 1):
        current_e = self.get_elem_by_class(class_name=class_name, index = index)
        current_location = current_e.location
        current_size = current_e.size
        window_hw = self.driver.get_window_size()
        print(f"print_screen_by_class_hight: location: {current_location}, size: {current_size}, window_hw: {window_hw}")

        # htmlタグからクライアントのwindowサイズを抜き出す
        html = self.driver.find_element_by_tag_name('html')
        inner_width = int(html.get_attribute("clientWidth"))
        inner_height = int(html.get_attribute("clientHeight"))
        print(f"inner_width: {inner_width}, inner_height:{inner_height}")

        # prev_class info
        # TBD: Desktop & Lamdaの時の横のscaleを正す
        prev_e = None
        if self.prev_class:
            print(f"prev_class: {self.prev_class}")
            prev_e = self.get_elem_by_class(class_name=self.prev_class["class_name"], index = self.prev_class["index"])
            prev_location = prev_e.location
        if self.execution_env == EXECUTION_ENV.LOCAL:
            if self.device == DEVICE.MOBILE_iPad_Pro or self.device == DEVICE.DESKTOP_GENERAL:
                scale = 2
            else:
                scale = 3
            w = inner_width * scale
            if prev_e:
                print(f'current_location_y {current_location["y"]}, prev_location_y: {prev_location["y"]}, current_size_height_: {current_size["height"]}')
                h = (current_location["y"] - prev_location["y"]) * scale - (current_size["height"] / 2)
            else:
                h = current_location["y"] * scale
        else:
            if self.device == DEVICE.MOBILE_iPad_Pro or self.device == DEVICE.DESKTOP_GENERAL:
                scale = 2
            else:
                scale = 3
            w = inner_width * scale
            if prev_e:
                print(f'current_location_y {current_location["y"]}, prev_location_y: {prev_location["y"]}, current_size_height_: {current_size["height"]}')
                h = (current_location["y"] - prev_location["y"]) * scale - (current_size["height"] / 2)
            else:
                h = current_location["y"] * scale
        print(f"w: {w}")
        print(f"h: {h}")

        fullpath = self.print_screen_by_size(w=w, h=h, path=path, filename=filename)

        return fullpath

    def print_screen_by_window(self, path, filename):
        """[summary]

        Args:
            path ([type]): [description]
            filename ([type]): [description]

        Returns:
            [type]: [description]
        """
        # Get Screen Shot
        fullpath = f"{path}/{filename}.png"
        self.__wait_print()
        self.driver.save_screenshot(fullpath)
        return fullpath

    def get_elem_by_class(self, class_name:str, index:int = 1):
        if len(class_name.split(" ")) > 1:
            _class_name = "." + ".".join(class_name.split(" "))
            self.wait_rendering_by_class(_class_name, True)
            elems = self.driver.find_elements_by_css_selector(_class_name)
        else:
            self.wait_rendering_by_class(class_name, False)
            elems = self.driver.find_elements_by_class_name(class_name)
        print(f"get_elem_by_class len:{len(elems)}")

        e = elems[index - 1]
        """
        location = e.location
        size = e.size
        #w, h = size['width'], size['height']
        window_hw = self.driver.get_window_size()
        print(f"get_elem_by_class: class_name: {class_name}, location: {location}, size: {size}, window_hw: {window_hw}")
        """
        return e

    def click_by_class_name(self, class_name:str, check_exist:bool = False, index:int = 1) -> str:
        """[summary]

        Args:
            class_name (str): [description]

        Returns:
            str: [description]
        """
        # Get Screen Shot
        if check_exist:
            if not self.is_exist_class(class_name=class_name):
                return f"{class_name} not found"
        elem = self.get_elem_by_class(class_name, index = index)
        elem.click()
        if self.debug:
            time.sleep(5)


    def scroll_by_offset(self, offset = 0):
        script = "window.scrollTo(0, window.pageYOffset + " + str(offset) + ");"
        self.driver.execute_script(script)

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_by_key(self, element, scroll_time):
        for num in range(0, scroll_time):
            element.send_keys(Keys.PAGE_DOWN)

    def smooth_scroll_to_bottom(self, scroll_pause_time = 0.5):
        # lazy対応
        # https://stackoverflow.com/questions/62600288/how-to-handle-lazy-loaded-images-in-selenium
        print("smooth_scroll_to_bottom")
        i = 0
        time.sleep(scroll_pause_time)
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            print(f"smooth_scroll_to_bottom: {new_height}")
            if new_height == last_height:
                break
            last_height = new_height
            i += 1
            if i == 5:
                break

    def move_to_element_by_class_name(self, class_name:str, index:int = 1) -> str:
        """[summary]

        Args:
            class_name (str): [description]

        Returns:
            str: [description]
        """
        if not self.scrolled:
            self.smooth_scroll_to_bottom()
        element = self.get_elem_by_class(class_name=class_name, index=index)
        element.location_once_scrolled_into_view
        self.scrolled = True
        self.prev_class = {"class_name": class_name, "index": index}
        if self.debug:
            time.sleep(5)

    def is_exist_class(self, class_name: str) -> bool:
        """[summary]

        Args:
            class_name (str): [description]

        Returns:
            bool: [description]
        """
        html = self.html
        _class_name = "." + ".".join(class_name.split(" "))
        if html.select(_class_name):
            logger.debug(f"is_exist_class, {class_name} is found")
            return True
        else:
            logger.debug(f"is_exist_class, {class_name} not found")
            return False
        
    @property
    def position_height(self):
        hight = self.driver.execute_script("return document.body.scrollHeight")
        print(f"position_height: {hight}")
        return hight

    @property
    def html(self):
        html = self.driver.page_source.encode('utf-8')
        return BeautifulSoup(html, "lxml")

    @property
    def log(self):
        result = []
        for entry in self.driver.get_log('performance'):
            result.append(entry['message'])
        return result
