import random
import time
import codefast as cf
import requests
from rss.core import AuthOnce
from rss.data import TELEGRAM


class Telegram(object):
    @staticmethod
    def post_to_channel(bot: str,
                        channel: str,
                        msg: str,
                        timeout: int = 60) -> bool:
        cf.info('posting {} to channel {}'.format(msg, channel))
        url = "https://api.telegram.org/bot{}/sendMessage?chat_id=@{}&text={}".format(
            bot, channel, msg)
        resp = requests.get(url, timeout=timeout)
        return resp


class TelegramChannelPoster(object):
    def __init__(self, bot_name: str, channel_name: str):
        self.bot_name = bot_name
        self.channel_name = channel_name

    def post(self, msg: str) -> bool:
        # To avoid 429 error, https://bit.ly/3tzcVhF
        time.sleep(random.randint(1, 3))
        auth = AuthOnce().info()
        bot = auth[self.bot_name]
        channel = auth[self.channel_name]
        resp = Telegram.post_to_channel(bot, channel, msg)
        msg = f"message {msg} SUCCESSFULLY posted to {channel}"
        if resp.status_code == 200:
            cf.info(msg)
            return True
        else:
            msg += f", {resp}"
            cf.error(msg)
            return False


tcp = TelegramChannelPoster(TELEGRAM['bot_name'], TELEGRAM['channel_name'])
