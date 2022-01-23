# -*- coding: utf-8 -*-
import logging
from typing import List, Union

from deprecated.classic import deprecated

from .drivers_tools import driver_field_validation, move_to, web_element_validation
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

log = logging.getLogger(__name__)


def __find_element(web_element, field: dict):
    switcher = {
        "id": web_element.find_element_by_id,
        "name": web_element.find_element_by_name,
        "class_name": web_element.find_element_by_class_name,
        "css": web_element.find_element_by_css_selector,
        "link_text": web_element.find_element_by_link_text,
        "partial_link_text": web_element.find_element_by_partial_link_text,
        "tag_name": web_element.find_element_by_tag_name,
        "xpath": web_element.find_element_by_xpath
    }
    return switcher[field["type"]](field["value"])


def __find_elements(web_element, field: dict):
    switcher = {
        "id": web_element.find_elements_by_id,
        "name": web_element.find_elements_by_name,
        "class_name": web_element.find_elements_by_class_name,
        "css": web_element.find_elements_by_css_selector,
        "link_text": web_element.find_elements_by_link_text,
        "partial_link_text": web_element.find_elements_by_partial_link_text,
        "tag_name": web_element.find_elements_by_tag_name,
        "xpath": web_element.find_elements_by_xpath
    }
    return switcher[field["type"]](field["value"])


def find_element(driver=None,
                 field: dict = None,
                 web_element: WebElement = None,
                 avoid_move_to: bool = False) -> Union[WebElement, None]:
    """
    Look up for the field described as a dictionary {"type": string, "value":}.
    Example: {"type": "id", "value": "frmCentreNumber"}
    Optionally, you can specify a text an call the find_from_elements method
    :param driver: a selenium web driver
    :param field: a dictionary
    :param web_element: a web_element to search from
    :param avoid_move_to: avoid to move to the found element
    :raise AssertionError: if driver is not a proper web driver instance or
            the field is not a dictionary
    :raise KeyError: If the field variable doesn't contain the expected keys i.e. type and value
    :raise NoSuchElementException: If the field doesn't exist
    :return: a selenium web element
    """
    try:
        driver_field_validation(driver, field, log)
        web_element_validation(web_element, log)

        if "text" in field:
            return find_from_elements(driver=driver,
                                      field=field,
                                      text=field['text'],
                                      web_element=web_element,
                                      avoid_move_to=avoid_move_to)

        if web_element is None:
            element = __find_element(driver, field)
        else:
            element = __find_element(web_element, field)

        if not avoid_move_to:
            move_to(driver, element, f"Find element: {field}")
        return element
    except NoSuchElementException as no_such_element:
        log.debug(f"In find_element didn't find the element '{field}'."
                  f" Exception is '{no_such_element.args}'")
        return None


def find_elements(driver=None, field=None, web_element=None) -> List[WebElement]:
    """
    Look up for the field described as a dictionary {"type": string, "value":}.
    Example: {"type": "id", "value": "frmCentreNumber"}
    :param web_element:
    :param driver: a selenium web driver
    :param field: a dictionary
    :raise AssertionError: if driver is not a proper web driver instance or
            the field is not a dictionary
    :raise KeyError: If the field variable doesn't contain the expected keys i.e. type and value
    :return: a list of selenium web element
    """

    driver_field_validation(driver, field, log)
    web_element_validation(web_element, log)
    # Define the association between a type and a selenium find action
    if web_element is not None:
        return __find_elements(web_element, field)
    else:
        return __find_elements(driver, field)


def find_from_elements(driver=None,
                       field=None,
                       text=None,
                       web_element=None,
                       avoid_move_to: bool = False) -> Union[WebElement, None]:
    """
    Try to locate an element using his text
    :param driver: a selenium web driver
    :param field: a dictionary
    :param text: a string
    :param web_element: a WebElement to search from
    :param avoid_move_to: avoid to move to the found element
    :raise AssertionError: from the finders.find_elements method
    :raise KeyError: from the finders.find_elements method
    :raise NoSuchElementException: when no element is found
    :return: a selenium web element
    """
    elements = find_elements(driver=driver, field=field, web_element=web_element)
    return_element = None

    if text is None:
        raise AttributeError("text must be provided")
    if not isinstance(text, str):
        raise AttributeError("text must be a string")
    if not text:
        raise ValueError("text must be non-empty")

    for element in elements:
        if element.text == text:
            log.debug(element.text)
            return_element = element
            break
        if element.get_attribute("value") == text:
            log.debug(element.get_attribute("value"))
            return_element = element
            break

    if return_element is None:
        log.debug(f"Element designed by field '{field}' and text '{text}'"
                  " could not be located.")
    elif not avoid_move_to:
        move_to(driver, return_element, f"Find from elements '{field}' and '{text}'")
    return return_element


@deprecated(version="1.0.5", reason="You should use find_element with a web_element")
def find_sub_element_from_element(web_element=None, field=None):
    """
    Return a sub element from the element
    :param web_element:
    :param field:
    :return:
    """
    try:
        assert isinstance(web_element, WebElement), "web_element must be a WebElement object"
        assert isinstance(field, dict), "Field must be a dictionary"
        if "type" not in field.keys() or "value" not in field.keys():
            raise KeyError("The field argument doesn't contains either the 'type' or 'value' key.")

        switcher = {
            "id": web_element.find_element_by_id,
            "name": web_element.find_element_by_name,
            "class_name": web_element.find_element_by_class_name,
            "css": web_element.find_element_by_css_selector,
            "link_text": web_element.find_element_by_link_text,
            "partial_link_text": web_element.find_element_by_partial_link_text,
            "tag_name": web_element.find_element_by_tag_name,
            "xpath": web_element.find_element_by_xpath
        }

        element = switcher[field["type"]](field["value"])
        actions = ActionChains(web_element.parent)
        actions.move_to_element(element)
        actions.perform()
        return element
    except AssertionError as assertion:
        log.error("finders.find_sub_element_from_element raised an assertion with"
                  " following input\n web_element:'{}', field:'{}'. "
                  "Assertion is '{}'".format(web_element, field, assertion.args))
        raise
    except KeyError as key_error:
        log.error("In find_sub_element_from_element didn't find the method for '{}'"
                  " finder method".format(field["type"]))
        raise KeyError(key_error)
