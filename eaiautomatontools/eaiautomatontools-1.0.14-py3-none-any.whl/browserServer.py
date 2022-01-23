# Could held the webdriver instance so that we could interact with the browser.
# -*- coding: utf-8 -*-
import os.path
import logging
import tempfile
from typing import List, Union

from deprecated import deprecated
from shutil import rmtree
from datetime import datetime
from selenium import webdriver
# Driver's options
from selenium.webdriver.chrome.options import Options as ChrOptions
from selenium.webdriver.firefox.options import Options as FfOptions
from selenium.webdriver.edge.options import Options as EdgOptions
from selenium.webdriver.opera.options import Options as OpeOptions
from selenium.webdriver.remote.webelement import WebElement
# Driver Manager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.opera import OperaDriverManager
from webdriver_manager.utils import ChromeType
# Self 
from .navigators import go_to_url, enter_frame, go_to_window
from .finders import find_element, find_elements, find_from_elements, \
    find_sub_element_from_element
from .actions import fill_element, fill_elements, mouse_click, select_in_dropdown, set_checkbox, \
    click_element, select_in_angular_dropdown, hover_element, select_in_elements
from .alerts import alert_message, intercept_alert
from .information import is_alert_present, is_field_exist, is_field_contains_text, \
    element_text, is_field_displayed, is_field_enabled, how_many_windows, wait_for_another_window, \
    where_am_i, \
    is_checkbox_checked, retrieve_tabular
from .drivers_tools import fullpage_screenshot, move_to

log = logging.getLogger(__name__)


class BrowserServer:
    """
    The BrowserServer is a convenient object which instantiate a selenium web driver.
    It serves all automaton tools such as finders, actions, alert and navigators.
    Although these tools can be used separately and are tested separately,
    it will be easier to use them from this class.
    Please see the eaiautomatontools specific doctest.
    Todo set others webdriver executables
    """

    __OPTIONS_SWITCHER = {
        "chrome": ChrOptions,
        "headless-chrome": ChrOptions,
        "chromium": ChrOptions,
        "headless-chromium": ChrOptions,
        "firefox": FfOptions,
        "opera": OpeOptions,
        "edge": EdgOptions
    }

    __DRIVER_MANAGER = {
        "chrome": ChromeDriverManager,
        "headless-chrome": ChromeDriverManager,
        "chromium": ChromeDriverManager,
        "headless-chromium": ChromeDriverManager,
        "firefox": GeckoDriverManager,
        "edge": EdgeChromiumDriverManager,
        "opera": OperaDriverManager
    }

    __WEB_DRIVERS = {
        "chrome": webdriver.Chrome,
        "headless-chrome": webdriver.Chrome,
        "chromium": webdriver.Chrome,
        "headless-chromium": webdriver.Chrome,
        "firefox": webdriver.Firefox,
        "edge": webdriver.Edge,
        "safari": webdriver.Safari,
        "opera": webdriver.Opera
    }

    def __init__(self):
        # Definition of private attributes and references
        # All strings allowed for the browser name and version
        self.__authorized_name_version = ("chrome", "firefox", "opera",
                                          "edge", "safari", "headless-chrome",
                                          "chromium", "headless-chromium")
        # Browser window's status
        self.__launched = False

        # Screenshot save folder
        self.__temp_save_to = os.path.normpath(os.path.join(tempfile.gettempdir(),
                                                            "automaton_screenshots"))
        if os.path.exists(self.__temp_save_to):
            rmtree(self.__temp_save_to)
        os.makedirs(self.__temp_save_to)
        log.debug(self.__temp_save_to)

        # Definition of private attributes
        self.__web_driver = None  # The webdriver
        self.__browser_name = None  # The browser's name used
        self.__driver_path = None  # The path to the webdriver executable

        # Definition of options
        self.__driver_options = []

    @property
    def driver_options(self):
        return self.__driver_options

    @driver_options.setter
    def driver_options(self, options):
        if isinstance(options, list):
            if not options:
                self.__driver_options = []
            elif all(isinstance(item, str) for item in options):
                self.__driver_options.extend(options)
            else:
                log.warning(f"Options '{options}' is not of the proper type")
        elif isinstance(options, str):
            self.__driver_options.append(options)
        else:
            log.warning(f"Options '{options}' is not of the proper type")

    @property
    def is_launched(self):
        return self.__launched

    @property
    def webdriver(self):
        """Read only webdriver"""
        return self.__web_driver

    @property
    def browser_name(self):
        """Read - Set browser name with restrictions"""
        return self.__browser_name

    @browser_name.setter
    def browser_name(self, name: str):
        if name.casefold() not in self.__authorized_name_version:
            raise ValueError(f"Unknown browser name. "
                             f"Get {name.casefold()} instead of {self.__authorized_name_version}")
        self.__browser_name = name.casefold()
        self.__driver_path = None

    @property
    def driver_path(self):
        return self.__driver_path

    @driver_path.setter
    def driver_path(self, new_path: str):
        if new_path is not None and new_path:
            if os.path.exists(new_path):
                self.__driver_path = new_path
            else:
                raise ValueError("Expecting an existing file")
        else:
            raise ValueError("Expecting a non empty path")

    @staticmethod
    def __serve_time():
        return int(datetime.now().timestamp() * 1000000)

    def serve(self):
        """
        Create the webdriver instance
        Todo incorporate the outside module resources locator
        TODO Handle the case where you don't want to use the webdriver manager
        :return: 0 if success
        """
        # todo use the data in order to launch the expected webdriver
        if self.browser_name is None:
            raise AttributeError("You must set a browser name. "
                                 f"Use one of '{self.__authorized_name_version}'")
        elif self.browser_name == "safari":
            self.__web_driver = BrowserServer.__WEB_DRIVERS[self.browser_name](
                executable_path=self.driver_path)
        elif "headless-chrom" in self.browser_name:
            option = BrowserServer.__OPTIONS_SWITCHER[self.browser_name]()
            option.add_experimental_option('excludeSwitches', ['enable-logging'])
            if self.driver_options:
                for opt in self.driver_options:
                    option.add_argument(opt)
            option.headless = True
            if self.__driver_path is None:
                if "ium" in self.browser_name:
                    self.__driver_path = BrowserServer.__DRIVER_MANAGER[self.browser_name](
                        chrome_type=ChromeType.CHROMIUM).install()
                else:
                    self.__driver_path = BrowserServer.__DRIVER_MANAGER[
                        self.browser_name]().install()
            self.__web_driver = BrowserServer.__WEB_DRIVERS[self.browser_name](
                executable_path=self.__driver_path,
                options=option
            )
        elif "chrom" in self.browser_name:
            # Hack https://stackoverflow.com/questions/64927909/
            # failed-to-read-descriptor-from-node-connection-a-device-attached-to-the-system
            if self.__driver_path is None:
                if "ium" in self.browser_name:
                    self.__driver_path = BrowserServer.__DRIVER_MANAGER[self.browser_name](
                        chrome_type=ChromeType.CHROMIUM).install()
                else:
                    self.__driver_path = BrowserServer.__DRIVER_MANAGER[
                        self.browser_name]().install()
            option = BrowserServer.__OPTIONS_SWITCHER[self.browser_name]()
            option.add_experimental_option('excludeSwitches', ['enable-logging'])
            if self.driver_options:
                for opt in self.driver_options:
                    option.add_argument(opt)
            self.__web_driver = BrowserServer.__WEB_DRIVERS[self.browser_name](
                executable_path=self.__driver_path,
                options=option
            )
        elif self.browser_name is not None:
            if self.__driver_path is None:
                self.__driver_path = BrowserServer.__DRIVER_MANAGER[self.browser_name]().install()

            option = BrowserServer.__OPTIONS_SWITCHER[self.browser_name]()
            if self.driver_options:
                for opt in self.driver_options:
                    option.add_argument(opt)
            self.__web_driver = BrowserServer.__WEB_DRIVERS[self.browser_name](
                executable_path=self.__driver_path,
                options=option)

        else:
            raise AttributeError("You must set a browser name. "
                                 f"Use one of '{self.__authorized_name_version}'")
        self.__launched = True
        return 0

    def close(self):
        """
        Close the webdriver
        :return:
        """
        self.webdriver.quit()
        self.__web_driver = None
        self.__launched = False
        return 0

    def __full_screenshot(self, filename: str):
        return fullpage_screenshot(self.webdriver, filename)

    def take_a_screenshot(self, save_to: str = None, is_full_screen: bool = True):
        """
        Take a screenshot and save the file to the given folder
        Each screenshot is followed by a timestamp. The file pattern is screenshot-<timestamp>.png
        :param save_to: path location to save the screenshot to
        :param is_full_screen: defaulted to 'True' capture the full page or the current screenview
        :return: 0 if success
        """
        try:
            # Process the filename
            if save_to is None:
                filename = os.path.join(
                    self.__temp_save_to, "screenshot-{}.png".format(self.__serve_time()))
            else:
                log.debug("Try to save to '{}'".format(save_to))
                filename = os.path.join(save_to, "screenshot-{}.png".format(self.__serve_time()))
            if is_full_screen:
                result = self.__full_screenshot(filename)
            else:
                result = self.webdriver.get_screenshot_as_file(filename)
            if not result:
                log.error("The screenshot could not be done."
                          " Please check if the file path is correct."
                          " Get '{}'".format(repr(result)))
                raise IOError("The screenshot could not be done."
                              " Please check if the file path is correct."
                              " Get '{}'".format(repr(result)))
            return os.path.realpath(filename)
        except IOError as io_error:
            log.error(f"Screenshot raised an IO error '{io_error.args[0]}'")
            raise IOError(io_error.args[0]) from None
        except Exception as exception:
            log.error(f"Screenshot raised an error '{exception.args[0]}'")
            raise Exception(exception.args[0]) from None

    # Start of convenient usage of the automaton tools
    # Navigation
    def go_to(self, url: str = None):
        """Navigate to the given url"""
        return go_to_url(driver=self.webdriver, url=url)

    def enter_frame(self, field=None, web_element: WebElement = None):
        """Enter the frame found using the find_element method"""
        return enter_frame(driver=self.webdriver, field=field, web_element=web_element)

    def go_to_window(self, handle: Union[str, int] = None, title: str = None):
        """Switch to a window providing either the window handle or window title"""
        return go_to_window(driver=self.webdriver, handle=handle, title=title)

    # Finders
    def find_element(self,
                     field: dict = None,
                     web_element: WebElement = None,
                     avoid_move_to: bool = False):
        """Find element using the current webdriver or the provided WebElement"""
        return find_element(driver=self.webdriver,
                            field=field,
                            web_element=web_element,
                            avoid_move_to=avoid_move_to)

    def find_elements(self, field: dict = None, web_element: WebElement = None):
        """Find elements using the current webdriver or the provided WebElement"""
        return find_elements(driver=self.webdriver, field=field, web_element=web_element)

    def find_from_elements(self,
                           field: dict = None,
                           text: str = None,
                           web_element: WebElement = None):
        """Find element from a list of elements based on the text (exact match)"""
        return find_from_elements(driver=self.webdriver,
                                  field=field,
                                  text=text,
                                  web_element=web_element)

    @deprecated(version="1.0.5", reason="You should user find_element with a web_element")
    def find_sub_element_from_element(self, field=None):
        """
        Find the webelement contained in another webelement.
        If no parent is provided try to return the webelement
        :param field:
        :return:
        """
        if "parent" not in field:
            return self.find_element(field=field)
        element = self.find_element(field=field["parent"])
        return find_sub_element_from_element(element, field=field)

    # Actions
    def fill_element(self, field: dict = None, web_element: WebElement = None, value: str = None):
        """Fill the element with the value. Use the find_element method to find it"""
        return fill_element(driver=self.webdriver,
                            field=field,
                            web_element=web_element,
                            value=value)

    def fill_elements(self, fields: dict = None, web_element: WebElement = None, data: dict = None):
        """Fill data in the respective field. data and fields keys must match.
        data keys must be in field keys"""
        return fill_elements(driver=self.webdriver,
                             fields=fields,
                             web_element=web_element,
                             data=data)

    # TODO add unit test
    def click_element(self, field: dict = None, web_element: WebElement = None):
        """Perform a click element on the element. Use the find_element method to find it"""
        return click_element(driver=self.webdriver,
                             field=field,
                             web_element=web_element)

    def mouse_click(self, field: dict = None, web_element: WebElement = None):
        """Perform a mouse click on the field. Use the find_element method to find if"""
        return mouse_click(driver=self.webdriver,
                           field=field,
                           web_element=web_element)

    def select_in_dropdown(self, field: dict = None, visible_text: str = None, value: str = None):
        """Select in field dropdown either the option by its visible text or its value"""
        return select_in_dropdown(driver=self.webdriver,
                                  field=field,
                                  visible_text=visible_text,
                                  value=value)

    def move_to(self, web_element: WebElement,
                caller_message: str = "From BrowserServer instance."):
        """Bring the element into the screenplay"""
        return move_to(driver=self.webdriver,
                       element=web_element,
                       caller_message=caller_message)

    # TODO add unit test
    def select_in_angular_dropdown(self, root_field=None, visible_text=None):
        """Select a field within a mat_option list

    If root_field is defined then click it and search for visible_text in mat-option elements.
    Otherwise only search for visible_text in mat-options elements"""
        return select_in_angular_dropdown(driver=self.webdriver,
                                          root_field=root_field,
                                          visible_text=visible_text)

    def set_checkbox(self, field: dict = None,
                     is_checked: bool = None,
                     web_element: WebElement = None):
        """Set the field checkbox to the is_checked state"""
        return set_checkbox(driver=self.webdriver,
                            field=field,
                            is_checked=is_checked,
                            web_element=web_element)

    # TODO add unit test
    def hover_element(self, field: dict = None):
        return hover_element(driver=self.webdriver, field=field)

    # TODO add unit test
    def select_in_elements(self,
                           field: dict = None,
                           displayed_text: str = None,
                           web_element: WebElement = None) -> int:
        """Do a click on the element which text match"""
        return select_in_elements(driver=self.webdriver,
                                  field=field,
                                  displayed_text=displayed_text,
                                  web_element=web_element)

    def execute_script(self, script: str, *args):
        """Delegate to the current webdriver the execute_script.
         See :func:selenium.webdriver.remote.webdriver.execute_script
        """
        self.webdriver.execute_script(script, *args)

    # Alerts
    def alert_message(self):
        """Return the message displayed in the alert."""
        return alert_message(driver=self.webdriver)

    def intercept_alert(self, messages: List[str] = None, accept: bool = True, value: str = None):
        """intercept_alert goal is to provide an easy interface to handle alerts.

        Without arguments, accept the alert whatever the message is.

        Giving a list of messages, ensure that the alert message is one of the list.

        Giving value, insert it in the prompt field.
        """
        return intercept_alert(driver=self.webdriver, messages=messages,
                               accept=accept, value=value)

    # Information

    def is_alert_present(self, until: int = 5):
        """Tells if whatever an alert is present or not."""
        return is_alert_present(driver=self.webdriver, until=until)

    def is_field_exist(self,
                       field: dict = None,
                       web_element: WebElement = None,
                       until: int = 5,
                       avoid_move_to: bool = True):
        """Check the field existence in the DOM. Unless specified doesn't bring into view the
        element"""
        return is_field_exist(driver=self.webdriver,
                              field=field,
                              web_element=web_element,
                              until=until,
                              avoid_move_to=avoid_move_to)

    def is_field_contains_text(self,
                               field: dict = None,
                               web_element: WebElement = None,
                               text: str = None) -> bool:
        """Test if the field contains the text."""
        return is_field_contains_text(driver=self.webdriver,
                                      field=field,
                                      web_element=web_element,
                                      text=text)

    def element_text(self,
                     field: dict = None,
                     web_element: WebElement = None,
                     avoid_move_to: bool = False) -> Union[str, None]:
        """Return the element text as string or None if field is not found"""
        return element_text(driver=self.webdriver,
                            field=field,
                            web_element=web_element,
                            avoid_move_to=avoid_move_to)

    def is_field_displayed(self,
                           field: dict = None,
                           web_element: WebElement = None,
                           avoid_move_to: bool = True,
                           wait_until: int = 5) -> bool:
        """Check if field is displayed"""
        return is_field_displayed(driver=self.webdriver,
                                  field=field,
                                  web_element=web_element,
                                  avoid_move_to=avoid_move_to,
                                  wait_until=wait_until)

    def is_field_enabled(self,
                         field: dict = None,
                         web_element: WebElement = None,
                         attribute: str = None,
                         avoid_move_to: bool = False,
                         wait_until: int = 5) -> bool:
        """Check if the field is enabled"""
        return is_field_enabled(driver=self.webdriver,
                                field=field,
                                web_element=web_element,
                                attribute=attribute,
                                avoid_move_to=avoid_move_to,
                                wait_until=wait_until)

    def how_many_windows(self) -> int:
        """Current number of handles"""
        return how_many_windows(driver=self.webdriver)

    def retrieve_tabular(self,
                         field: dict = None,
                         web_element: WebElement = None,
                         row_and_col: tuple = ("tr", "td", "th")) -> List[list]:
        """Retrieve a tabular as a list of list of cells' content (str)"""
        return retrieve_tabular(driver=self.webdriver, field=field, web_element=web_element,
                                row_and_col=row_and_col)

    # TODO add unit test
    def where_am_i(self) -> str:
        """Current URL"""
        return where_am_i(driver=self.webdriver)

    # TODO add unit test
    def is_checkbox_checked(self,
                            field: dict = None,
                            web_element: WebElement = None,
                            is_angular: bool = False):
        return is_checkbox_checked(driver=self.webdriver, field=field, web_element=web_element,
                                   is_angular=is_angular)

    def wait_for_another_window(self, wait_until: int = 1) -> bool:
        """Wait for another window to pop"""
        return wait_for_another_window(driver=self.webdriver, until=wait_until)
