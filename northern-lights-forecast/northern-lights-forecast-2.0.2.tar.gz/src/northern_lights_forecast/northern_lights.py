"""Check the web for signs of northern lights.

This script implements an automated Northern Lights forecast
by taking advantage of web scraping of the web site of the IMAGE Magnetometer.
At a given threshold of the derivative of the X component,
a notification is sent to let the user know a substorm has occurred.

The script is run every hour from 18:00 through 04:00 during
the months September through March, using crontab to automate the task.
To edit the crontab script, type
```sh
env EDITOR=nano crontab -e
```
into the terminal.
"""
import logging
from logging.handlers import RotatingFileHandler

import requests
import telegram_send

import northern_lights_forecast.image_analysis as ima
import northern_lights_forecast.img as img


def telegram_test() -> None:
    """Test to see if you are able to send with telegram."""
    telegram_send.send(messages=["Test"])


def forecast(loc: str, dy: float) -> str:
    """Different forecasting based on the magnetometer gradient.

    Parameters
    ----------
    loc: str
        Location of the magnetometer / forecast
    dy: float
        Minimum gradient

    Returns
    -------
    str:
        Forecast to send to the telegram bot
    """
    log_formatter = logging.Formatter(
        "[%(asctime)s %(levelname)s] %(message)s", datefmt="%Y/%m/%d %H:%M:%S"
    )
    my_handler = RotatingFileHandler(
        "nlf.log",
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=2,
        encoding=None,
        delay=0,
    )
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.INFO)
    app_log = logging.getLogger("root")
    app_log.setLevel(logging.INFO)
    app_log.addHandler(my_handler)
    app_log.info(f"Smallest gradient in {loc} is {dy}.")
    txt = (
        "\U0001F525"
        + f"Northern Lights Warning in {loc}!"
        + "\U0001F525"
        + f"\n\nGradient: *{dy}*\n\n"
    )
    if dy < -2:
        txt += "There are good chances of seeing northern lights in the next hours!\n\n"
    elif dy < -1:
        txt += (
            "Fair chances of some northern lights the next hours, keep an eye up.\n\n"
        )
    elif dy < -0.5:
        txt += "With little light pollution you might see some northern lights.\n\n"
    else:
        return "None"
    weather_condition = requests.get(f"https://wttr.in/{loc}?format=%C")
    txt += f"The weather conditions right now: *{weather_condition.text.lower()}*.\n\n"
    txt += "__Have a look at: http://fox.phys.uit.no/ASC/ASC01.html __"
    return txt


def nlf(location: str) -> None:
    """Run the Northern Lights Forecast."""
    scaling = img.img_analysis(location)
    dy = ima.grab_blue_line(scaling)
    txt = forecast(location, dy)
    if txt != "None":
        telegram_send.send(messages=[txt], parse_mode="markdown")


def main() -> None:
    """Run 'northern_lights.py'."""
    nlf("Tromsø")


if __name__ == "__main__":
    main()
