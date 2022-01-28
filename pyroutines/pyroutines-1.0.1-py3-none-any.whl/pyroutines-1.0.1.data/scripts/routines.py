from os import listdir, path, mkdir
from pyautogui import click, locateOnScreen
from time import time
from datetime import datetime as dt
import logging as log


def save_logs(message, method_name, error=False):
    """
    :param message: Detailed message to display in console and log file - type[string / fstring]
    :type message: str
    :param method_name: Name of the method where the log save routine is being called
    :type method_name: str
    :param error: Defines whether the log to be saved will be an error or just information
    :type error: bool
    """

    if not path.exists('logs'):
        mkdir("logs")
    if error:
        log.basicConfig(filename='logs/application.log', level=log.ERROR,
                        format=f'%(asctime)s: %(levelname)s IN {method_name} - DETAILS: %(message)s')
        log.error(message)

        date_now = f"{dt.now().date()} - {dt.now().time().replace(microsecond=0)}"
        print(f'{date_now} ERROR IN {method_name} - DETAILS: {message}')

    else:
        log.basicConfig(filename='logs/application.log', level=log.INFO,
                        format=f'%(asctime)s: %(levelname)s: %(message)s')
        log.info(message)

        date_now = f"{dt.now().date()} - {dt.now().time().replace(microsecond=0)}"
        print(f'{date_now} INFORMATION - DETAILS: {message}')


def move_to_image(path_images, auto_click=False):
    """
    :param path_images: location path of the list of images to be interpreted
    :type path_images: str
    :param auto_click: parameter to know if it is necessary to click on the image when finding it on the screen
    :type auto_click: bool
    :return: returns a boolean if it finds the image
    :rtype: bool
    """
    success = False
    try:
        i = 0
        list_images = listdir(path_images)
        while i < 3:
            for image in list_images:
                img = path_images + image
                start = time()
                end = time().__add__(3)

                while start < end:
                    if auto_click:
                        if locateOnScreen(img):
                            click(img)
                            success = True
                    else:
                        if locateOnScreen(img):
                            success = True
                    if success:
                        break
                    start = time()

                if success:
                    break
            if success:
                break
            i += 1
    except Exception as ex:
        save_logs(f'{ex}', 'move to image', True)
    finally:
        return success
