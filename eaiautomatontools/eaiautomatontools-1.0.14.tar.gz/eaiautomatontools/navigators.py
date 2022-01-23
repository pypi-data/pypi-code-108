# -*- coding: utf-8 -*-
from logging import getLogger
from .finders import find_element
from .drivers_tools import web_drivers_tuple
"""
The navigators tool box purpose is to provide some limited but heavy used methods
in order to browse to URL and navigate from browser tabs or windows.

The behaviour of these methods are known so that it will ease the debugging.
"""

# Todo: Add a logger so that it will be easy to search for issues.

log = getLogger(__name__)


def go_to_url(driver=None, url=None):
    """
    Go to a specific url
    :param driver: a selenium web driver
    :param url: a URL as a string
    :raise AssertionError: if driver is not defined
    :return: 0 if succeed
    """
    assert driver is not None and isinstance(driver, web_drivers_tuple()), "Driver is expected."
    driver.get(url)
    return 0


def enter_frame(driver=None, field=None, web_element=None):
    """
    Switch to a frame given by its field identifier
    :param driver: a selenium web driver
    :param field: a dictionary like {"type":"id", "value":"myID"}
    :param web_element: a web_element from which to search the frame
    :raise AssertionError: if driver is not defined
    :return: 0 if succeed
    """
    assert driver is not None and isinstance(driver, web_drivers_tuple()), "Driver is expected."

    driver.switch_to.frame(find_element(driver=driver, field=field, web_element=web_element))
    return 0


def go_to_window(driver=None, handle=None, title=None):
    """
    Switch to a window either giving the handle or the window's title.
    :param driver: a selenium web driver
    :param handle: a window's reference as a string
    :param title: a window's title as a string
    :raise Exception: The number of window with the title is different from 1.
    :raise AssertionError: if driver is not defined
    :return: 0 if succeed
    """
    assert driver is not None and isinstance(driver, web_drivers_tuple()), "Driver is expected."

    if handle is None and title is None:
        raise ValueError("Expect at least one value either the handle or the window title")

    if handle is not None:
        driver.switch_to.window(handle)
    if title is not None:
        current_handle = driver.current_window_handle
        handles = driver.window_handles
        search_result = []
        for handle in handles:
            driver.switch_to.window(handle)
            if driver.title == title:
                search_result.append(handle)
        if len(search_result) != 1:
            driver.switch_to.window(current_handle)
            raise Exception("Too many windows with the same title to switch to. Staying on the "
                            "current window.")
        else:
            driver.switch_to.window(search_result[0])

    return 0
