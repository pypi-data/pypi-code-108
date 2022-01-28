from enum import Enum

from codefast.utils import deprecated

from .pipe import author

@deprecated('decode() is deprecated, use pipe.author.get() instead.')
def decode(keyword: str) -> str:
    from .pipe import author
    return author.get(keyword)

''' Channels:
1. Global_News_Podcast, t.me/messalert, personal, info on weather, data traffic.
2. cccache, t.me/cccache, public, share IT, video info
3. Global_Notices, t.me/plutoshare, fund alert.
'''
CHANNEL_MESSALERT = 'messalert'
CHANNEL_CCCACHE = 'cccache'
CHANNEL_PLUTOSHARE = 'plutoshare'

class BotEnum(Enum):
    COMMON = 1     # i.e., @vpsmoni714_bot, connected to channel Global_News_Podcast, Global_Notices and cccache.
    WECHAT = 2     # i.e., @wechat117Bot, connected to channel Global_Notices
    XB117BOT = 3     # i.e., @f117bot, connected to channel cccache

FERNET_KEY_UNSAFE=b'ekNQTZ7tH/+KHFrernOUWReb1LmWtRj9TU8kme0WyQs='