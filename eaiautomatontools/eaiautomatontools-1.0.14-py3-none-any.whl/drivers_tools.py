# -*- coding: utf-8 -*-
import logging
from os import remove
from time import sleep

from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement

log = logging.getLogger(__name__)


def web_drivers_tuple():
    return (webdriver.firefox.webdriver.WebDriver,
            webdriver.chrome.webdriver.WebDriver,
            webdriver.ie.webdriver.WebDriver,
            webdriver.edge.webdriver.WebDriver)


def fullpage_screenshot(driver, file):
    log.debug("Starting full page screenshot")
    total_width = driver.execute_script("return document.body.offsetWidth")
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = driver.execute_script("return document.body.clientWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    log.debug("Total: ({0}, {1}), Viewport: ({2},{3})".format(total_width, total_height,
                                                              viewport_width, viewport_height))
    rectangles = []
    i = 0
    while i < total_height:
        ii = 0
        top_height = i + viewport_height

        if top_height > total_height:
            top_height = total_height

        while ii < total_width:
            top_width = ii + viewport_width

            if top_width > total_width:
                top_width = total_width

            log.debug("Appending rectangle ({0},{1},{2},{3})".format(ii, i, top_width, top_height))
            rectangles.append((ii, i, top_width, top_height))
            ii = ii + viewport_width
        i = i + viewport_height
    stitched_image = Image.new('RGB', (total_width, total_height))
    previous = None
    part = 0
    for rectangle in rectangles:
        # TODO Scroll to top saving the current position (?)
        if previous is not None:
            driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            log.debug("Scrolled To ({0},{1})".format(rectangle[0], rectangle[1]))
            sleep(0.2)
        file_name = "part_{0}.png".format(part)
        log.debug("Capturing {0} ...".format(file_name))
        driver.get_screenshot_as_file(file_name)
        screenshot = Image.open(file_name)
        if rectangle[1] + viewport_height > total_height:
            offset = (rectangle[0], total_height - viewport_height)
        else:
            offset = (rectangle[0], rectangle[1])
        log.debug("Adding to stitched image with offset ({0}, {1})".format(offset[0], offset[1]))
        stitched_image.paste(screenshot, offset)
        del screenshot
        remove(file_name)
        part = part + 1
        previous = rectangle
    try:
        stitched_image.save(file)
    except IOError:
        return False
    log.info("Screenshot saved: {}".format(file))
    return True


def move_to(driver=None, element: WebElement = None, caller_message: str = ''):
    if driver is None or not isinstance(driver, web_drivers_tuple()):
        log.error("Driver is expected")
        raise TypeError("Driver is expected")
    if element is None or not isinstance(element, WebElement):
        log.error("Element is expected")
        raise TypeError("Element is expected")
    try:
        if 'firefox' in driver.capabilities['browserName']:
            x = element.location['x']
            y = element.location['y']
            scroll_by_coord = 'window.scrollTo(%s,%s);' % (
                x,
                y
            )
            scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
            driver.execute_script(scroll_by_coord)
            driver.execute_script(scroll_nav_out_of_way)
        actions = ActionChains(driver)
        actions.move_to_element(element)
        actions.perform()
    except Exception as exception:
        log.warning(f"'{caller_message}'\nCannot move to with chain actions."
                    f" Get:\n {exception.args[0]}")
        driver.execute_script("arguments[0].scrollIntoView();", element)
        raise Exception(f"'{caller_message}'\n{exception.args[0]}")


def __field_validation(field=None, logger=None):
    """
    Check if the field contains the expected keys and values for the type key.
    :param field: a dictionary
    :return: True if field is correct false otherwise
    """
    field_type = ("id",
                  "name",
                  "class_name",
                  "link_text",
                  "css",
                  "partial_link_text",
                  "xpath",
                  "tag_name")
    if any(key not in field.keys() for key in ("type", "value")):
        logger.error("The field argument doesn't contains either the 'type' or 'value' key.")
        raise KeyError("The field argument doesn't contains either the 'type' or 'value' key.")
    if field['type'] not in field_type:
        logger.error(f"The field type is not one the expected: '{field_type}")
        raise ValueError(f"The field type is not one the expected: '{field_type}")


def driver_field_validation(driver, field, logger):
    if driver is None or not isinstance(driver, web_drivers_tuple()):
        logger.error("Driver is expected")
        raise TypeError("Driver is expected")
    if not isinstance(field, dict):
        logger.error(f"{field} is not a dictionary")
        raise TypeError(f"{field} is not a dictionary")
    __field_validation(field, logger)


def web_element_validation(web_element, logger):
    if web_element is not None and not isinstance(web_element, WebElement):
        logger.error("When provided web_element must be a WebElement"
                     f"Get {type(web_element)}")
        raise AttributeError("When provided web_element must be a WebElement"
                             f"Get {type(web_element)}")  # TODO change to TypeError
