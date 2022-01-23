# -*- coding: utf-8 -*-
from logging import getLogger
from typing import List

from selenium.common.exceptions import ElementNotSelectableException, NoAlertPresentException, \
    ElementNotInteractableException
from .drivers_tools import driver_field_validation

log = getLogger(__name__)


def intercept_alert(driver=None,
                    messages: List[str] = None,
                    accept: bool = True,
                    value: str = None):
    """
        intercept_alert goal is to provide an easy interface to handle alerts.

        Only the web driver is mandatory.

        Giving only the web driver accept the alert whatever the message is.

        Giving a list of messages, ensure that the alert message is one of the list.
    :param driver: a selenium webdriver
    :param messages: A list of string which should include the alert message.
    :param accept: boolean defaulted to True. Accept or dismiss the alert.
    :param value: The string to be entered in the prompt alert.
    :raise AssertionError: driver, messages, accept and value aren't of the expected type
    :raise ElementNotSelectableException: when trying to send keys on a non-prompt alert
    :raise NoAlertPresentException: when trying to intercept an alert which not present
    :raise Exception: when the alert message is not one of the expected
    :return: 0 if success
    """
    try:
        driver_field_validation(driver, {"type": "id", "value": "fake"}, log)
        if not isinstance(messages, list) and messages is not None:
            log.error("Messages should be a list or None")
            raise TypeError("Messages should be a list or None")
        if not isinstance(accept, bool):
            log.error("Accept is boolean True or False")
            raise TypeError("Accept is boolean True or False")
        if value is not None and not isinstance(value, str):
            log.error("Value is None or a string")
            raise TypeError("Value is None or a string")

        alert_object = driver.switch_to.alert

        if (
                messages is not None
                and isinstance(messages, list)
                and alert_object.text not in messages
        ):
            raise Exception("Message not found")

        if value is not None:
            alert_object.send_keys(value)

        if accept:
            alert_object.accept()
        else:
            alert_object.dismiss()

        return 0

    except ElementNotSelectableException as not_selectable:
        log.error(f"alerts.intercept_alert can't fill the alert popup with '{value}'"
                  f" as there is no input field.\nGet {not_selectable.args}")
        raise ElementNotSelectableException(
            f"Can't fill the alert popup with '{value}' as there is no "
            "input field.") from None
    except ElementNotInteractableException as not_interactable:
        log.error(not_interactable)
        raise ElementNotInteractableException("Cannot found an input field") from None
    except NoAlertPresentException as no_alert:
        log.error(
            f"alerts.intercept_alert can't interact with an alert as there is no "
            f"displayed alert.\nGet {no_alert.args}")
        raise NoAlertPresentException("Can't interact with an alert as there is no "
                                      "displayed alert") from None


def alert_message(driver=None):
    """
        Return the message displayed in the alert.
    :param driver: a selenium webdriver
    :raise AssertionError: driver isn't of the expected type
    :raise NoAlertPresentException: when trying to intercept an alert which not present
    :return: 0 if success
    """
    try:
        driver_field_validation(driver, {"type": "id", "value": "fake"}, log)
        alert_object = driver.switch_to.alert
        return alert_object.text
    except NoAlertPresentException as no_alert:
        log.error(f"alerts.intercept_alert can't interact with an alert as there"
                  f" is no displayed alert.\nGet {no_alert.args}")
        raise NoAlertPresentException("Can't interact with an alert as there is no"
                                      " displayed alert") from None
