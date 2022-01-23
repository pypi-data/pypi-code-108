# -*- coding: utf-8 -*-
from time import perf_counter

import polling2

from typing import Union
from logging import getLogger
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, \
    StaleElementReferenceException, \
    TimeoutException

from .drivers_tools import driver_field_validation, web_drivers_tuple, web_element_validation
from .finders import find_element

log = getLogger(__name__)


def is_field_exist(driver=None,
                   field: dict = None,
                   web_element: WebElement = None,
                   until: int = 5,
                   avoid_move_to: bool = False) -> Union[WebElement, None]:
    """
    Test if the field given as a {"type":"id","value":"toto"} dictionary exists.
    :param avoid_move_to:
    :param driver: a selenium web driver
    :param field: a dictionary representing the web element to search
    :param web_element: a web_element to search from
    :param until: an int as the wait time in second
    :raise TypeError: driver isn't of the expected type
    :return: a web element if exist, None otherwise
    """
    try:
        driver_field_validation(driver, field, log)
        web_element_validation(web_element, log)

        return polling2.poll(lambda: find_element(driver, field, web_element, avoid_move_to),
                             ignore_exceptions=(NoSuchElementException,
                                                StaleElementReferenceException),
                             step=0.2,
                             timeout=until)

    except polling2.TimeoutException:
        log.info(f"information.is_field_exist raised a TimeoutException for "
                 f"the following field '{field}'")
        return None


def is_field_contains_text(driver=None,
                           field: dict = None,
                           web_element: WebElement = None,
                           text: str = None,
                           avoid_move_to: bool = False) -> bool:
    """
    Check if the given field contains the text either as a DOM text or value text.
    {"type":"id","value":"toto"}
    :param avoid_move_to:
    :param driver: a selenium web driver
    :param field: a dictionary representing the web element to search
    :param web_element: a web_element to search from
    :param text: a string for the text to be in the field
    :raise AssertionError: driver isn't of the expected type
    :return: True if the field contains the text, False otherwise
    """
    element = is_field_exist(driver=driver,
                             field=field,
                             web_element=web_element,
                             avoid_move_to=avoid_move_to)
    if element is None:
        log.warning(f"Cannot find the element {field} to check the text from")
        return False
    return (element.text is not None and text in element.text) or (
            element.get_attribute("value") is not None
            and text in element.get_attribute("value"))


def is_alert_present(driver=None, until: int = 5):
    """
    Tells if whatever an alert is present or not.
    :param driver: a selenium web driver
    :param until: time to wait.
    :return: True or False.
    """
    try:
        driver_field_validation(driver, {"type": "id", "value": "fake"}, log)
        if WebDriverWait(driver, until).until(EC.alert_is_present()):
            return True
    except TimeoutException:
        return False


def element_text(driver=None,
                 field: dict = None,
                 web_element: WebElement = None,
                 avoid_move_to: bool = False) -> Union[str, None]:
    """
    Return the text of the element
    :param avoid_move_to:
    :param driver: a selenium web driver
    :param field: a dictionary corresponding to the field to retrieve the text
    :param web_element: a webElement to search the field from
    :raise TypeError: from finders.find_element method
    :raise ValueError: from finders.find_element method
    :raise Exception: if text and value are defined but not identical
    :return: the element text or value, empty if no text or value
    """
    element = find_element(driver=driver,
                           field=field,
                           web_element=web_element,
                           avoid_move_to=avoid_move_to)
    if element is None:
        log.warning(f"Cannot find the element {field} to retrieve the text from")
        return None
    element_text_ = element.text
    element_value = element.get_attribute("value")

    if element_text_ and not element_value:
        return element_text_
    elif not element_text_ and element_value:
        return element_value
    elif element_text_ is not None and element_value is not None \
            and element_text_ in element_value and element_value in element_text_:
        return element_text_
    elif element_text_ is not None and element_value is not None and (
            element_text_ not in element_value or element_value not in element_text_):
        raise Exception("Can't serve the element 'text' having both data for text and"
                        " attribute value")
    else:
        return ""


def how_many_windows(driver=None):
    """
    Return the number of windows at the method execution.
    :param driver: a selenium web driver
    :return: the number of windows
    """
    driver_field_validation(driver, {"type": "id", "value": "fake"}, log)
    return len(driver.window_handles)


def is_field_displayed(driver=None,
                       field: dict = None,
                       web_element: WebElement = None,
                       avoid_move_to: bool = False,
                       wait_until: int = 5):
    """
    Check if the element is displayed. You may not interact with it.
    :param driver: a selenium web driver
    :param field: a dictionary corresponding to the field to retrieve the text
    :param web_element: a webElement to search the field from
    :param avoid_move_to: Avoid to move into view the WebElement
    :param wait_until: The default wait field existence and display
    :return: Boolean. True if element is displayed, false otherwise.
    """
    element = is_field_exist(driver=driver,
                             field=field,
                             web_element=web_element,
                             avoid_move_to=avoid_move_to,
                             until=wait_until)
    if element is None:
        log.info(f"Element '{field}' doesn't exist in the DOM")
        return False
    try:
        polling2.poll(lambda: element.is_displayed(),
                      step=0.2,
                      timeout=wait_until,
                      ignore_exceptions=(NoSuchElementException,
                                         StaleElementReferenceException,
                                         ElementNotInteractableException)
                      )
        return True
    except polling2.TimeoutException:
        log.info(f"Element '{field}' is not displayed")
        return False


def is_field_enabled(driver=None,
                     field: dict = None,
                     web_element: WebElement = None,
                     attribute: str = None,
                     avoid_move_to: bool = False,
                     wait_until: int = 5) -> bool:
    """
    Check if the element is enabled.
    :param driver: a selenium web driver
    :param field: a dictionary representing the web element to search
    :param web_element: a web_element to search from
    :param attribute: the attribute to check for enabled
    :param avoid_move_to: Avoid to move into view the WebElement
    :param wait_until: The default wait field existence and display
    :return: Boolean. True if element is enabled, false otherwise for non attribute.
            Attribute string otherwise
    """
    element = is_field_exist(driver=driver,
                             field=field,
                             web_element=web_element,
                             avoid_move_to=avoid_move_to,
                             until=wait_until)
    if element is None:
        return False
    if attribute is not None:
        return element.get_attribute(attribute)
    else:
        return element.is_enabled()


def where_am_i(driver=None):
    """
    Return the current location URL
    :param driver: a selenium web driver
    :return: String. The current URL
    """
    if driver is None or not isinstance(driver, web_drivers_tuple()):
        raise TypeError("Driver is expected as a WebDriver")

    return driver.current_url


def is_checkbox_checked(driver=None,
                        field: dict = None,
                        web_element: WebElement = None,
                        is_angular: bool = False,
                        avoid_move_to: bool = False,
                        wait_until: int = 5):
    """
    Return the checkbox status
    :param avoid_move_to:
    :param driver: a selenium web driver
    :param field: a dictionary representing the web element to search
    :param web_element: a web_element to search from
    :param is_angular: boolean
    :param wait_until: The default wait field existence and display
    :return: boolean
    """
    element = is_field_exist(driver=driver,
                             field=field,
                             web_element=web_element,
                             avoid_move_to=avoid_move_to,
                             until=wait_until)
    if element is None:
        log.warning(f"Element {field} not found")
    if is_angular:
        return bool(element.get_attribute("ng-reflect-checked"))
    else:
        return bool(element.get_attribute("checked"))


def retrieve_tabular(driver=None,
                     field=None,
                     web_element=None,
                     row_and_col=("tr", "td", "th")) -> Union[list, None]:
    """
    Return the tabular as a list of elements.
    Elements are either lists or dictionaries depending on the presence of headers
    :param driver: a selenium web driver
    :param field: a dictionary representing the web element to search
    :param web_element: a web_element to search from
    :param row_and_col: a tuple of row and col tags plus header tag. Defaulted to ('tr', 'td',
    'th').
     Please mind the order. ROW, COL, COL HEADER
    :return: list
    """
    tabular = find_element(driver, field, web_element=web_element)
    if tabular is None:
        log.warning(f"Tabular {field} has not been found")
        return tabular
    rows = tabular.find_elements_by_tag_name(row_and_col[0])
    tabular_as_list = []

    for row in rows:
        columns = row.find_elements_by_tag_name(row_and_col[1])
        if not columns:
            columns = row.find_elements_by_tag_name(row_and_col[2])
        tabular_as_list.append([column.text for column in columns])

    return tabular_as_list


def wait_for_another_window(driver, until: int = 1) -> bool:
    """Wait for another window for at most 'until' seconds
        :param driver: ta selenium web driver
        :param until: the maximum duration to wait
        :return True if another windows pops in the duration False otherwise
        """
    try:
        start = perf_counter()
        under_max_time = True
        while len(driver.window_handles) == 1 and under_max_time:
            if int(perf_counter() - start) > until:
                under_max_time = False
        return under_max_time
    except Exception as exception:
        log.error(f"Retrieve the following error:\n {exception.args}")
