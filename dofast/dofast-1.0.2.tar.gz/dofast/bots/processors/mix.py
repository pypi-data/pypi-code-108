from codefast.axe import axe
from dofast.bots.processors.base import TextProcessor
from dofast.pyavatar import PyAvataaar
from dofast.toolkits.textparser import TextParser
from dofast.weather import Weather
from telegram import Update
from telegram.ext import CallbackContext


class WeatherProcessor(TextProcessor):
    def __init__(self) -> None:
        self.weather = Weather()

    def match(self, text: str) -> bool:
        return TextParser.match(['weather', '天气'], text)

    def run(self, _text: str, update: Update) -> str:
        self.weather.draw_weather_image()
        update.message.reply_photo(open('/tmp/weather.png', 'rb'))
        return True


class AvatarProcessor(TextProcessor):
    def __init__(self) -> None:
        self.avatar = PyAvataaar()

    def match(self, text: str) -> bool:
        return TextParser.match(['avatar', '头像'], text)

    def run(self, _text: str, update: Update) -> bool:
        self.avatar.random()
        update.message.reply_photo(open('/tmp/pyavatar.png', 'rb'))
        update.message.reply_text('Here is your new avatar, enjoy!')
        return True


class ParcelProcessor(TextProcessor):
    def __init__(self) -> None:
        pass

    def match(self, text: str) -> bool:
        return TextParser.is_parcel_arrived(text)

    def run(self, _text: str, update: Update,
            context: CallbackContext) -> bool:
        chat_id = update.message.chat_id
        due_time = axe.today() + 'T' + '22:45'
        due = axe.diff(axe.now(), due_time, seconds_only=True)
        update.message.reply_text(
            'Msg received, alert at {} in {} seconds.'.format(due_time, due))
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return
        context.job_queue.run_once(self.alarm,
                                   due,
                                   context=chat_id,
                                   name=str(chat_id))
        return True
