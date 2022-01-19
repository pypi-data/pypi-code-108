"""Implementation of commands and message handlers to be used with the telegram bot."""
import configparser

import requests
import telebot

import northern_lights_forecast.image_analysis as ima
import northern_lights_forecast.img as img

config = configparser.ConfigParser()
config.read("config.ini")
TOKEN = config["TELEBOT"]["token"]
# You can set parse_mode by default. HTML or MARKDOWN
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


@bot.message_handler(commands=["start", "help"])
def send_welcome(message) -> None:
    """Send a welcome message with info about the bot."""
    bot.send_message(
        message.chat.id,
        "Oh hi! Welcome to the nlf bot. I'm able to respond to "
        + "/locations and any message that starts with 'forecast'.",
    )


# @bot.message_handler(commands=["resources"])
# def send_resources(message) -> None:
#     """Send a list of resources."""
#     txt = "All nlf supported locations:\n\n"
#     for loc in img.__PLACE__.keys():
#         txt += f"{loc}\n"
#     bot.send_message(message.chat.id, txt)


@bot.message_handler(commands=["locations"])
def send_locations(message) -> None:
    """Send a list of available locations."""
    txt = "All nlf supported locations:\n\n"
    for loc in img.__PLACE__.keys():
        txt += f"{loc}\n"
    bot.send_message(message.chat.id, txt)


def is_forecast(message) -> bool:
    """Check if the message sent starts with 'forecast'."""
    words = message.text.split()
    if words[0].lower() == "forecast" and len(words) > 1:
        return True
    bot.send_message(message.chat.id, "Did you misspell 'forecast'?")
    return False


@bot.message_handler(func=is_forecast)
def get_location_forecast(message) -> None:
    """Run the Northern Lights Forecast."""
    words = message.text.split()[1:]
    # check if any of the words are valid locations
    location = "None"
    for w in words:
        for place in img.__PLACE__.keys():
            if w.lower() in place.lower():
                location = place
    if location == "None":
        # Send message that you did it wrong
        bot.send_message(
            message.chat.id,
            f"None of {words} are valid location(s). Type /locations to "
            + "get a complete list of all locations.",
        )
        return

    bot.send_message(
        message.chat.id,
        f"Checking the magnetometer near {location} from the past ~3 hours...",
    )
    scaling = img.img_analysis(location)
    dy = ima.grab_blue_line(scaling)
    w_s = requests.get(f"https://wttr.in/{location}?format=%c").text
    w_c = requests.get(f"https://wttr.in/{location}?format=%C").text.lower()
    txt = (
        f"The gradient in {location} is now at <b>{dy}</b> with weather conditions "
        + f"described as {w_s}<b>{w_c}</b>{w_s}\n\n"
        + "<i>Usually, less than -0.5 is okay, less than -1 is good "
        + "and less than -2 is get the fuck out right now!</i>"
    )
    bot.send_message(message.chat.id, txt)


bot.infinity_polling()
