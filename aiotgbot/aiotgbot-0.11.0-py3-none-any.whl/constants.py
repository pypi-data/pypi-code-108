from enum import Enum, unique

__all__ = ('RequestMethod', 'ChatType', 'ChatAction', 'ChatMemberStatus',
           'MessageEntityType', 'UpdateType', 'ContentType', 'ParseMode',
           'PollType', 'DiceEmoji', 'InputMediaType', 'InlineQueryResultType',
           'PassportElementType')


@unique
class RequestMethod(str, Enum):
    GET = 'GET'
    POST = 'POST'


@unique
class ChatType(str, Enum):
    PRIVATE = 'private'
    GROUP = 'group'
    SUPERGROUP = 'supergroup'
    CHANNEL = 'channel'


@unique
class ChatAction(str, Enum):
    TYPING = 'typing'
    UPLOAD_PHOTO = 'upload_photo'
    RECORD_VIDEO = 'record_video'
    UPLOAD_VIDEO = 'upload_video'
    RECORD_VOICE = 'record_voice'
    UPLOAD_VOICE = 'upload_voice'
    UPLOAD_DOCUMENT = 'upload_document'
    CHOOSE_STICKER = 'choose_sticker'
    FIND_LOCATION = 'find_location'
    RECORD_VIDEO_NOTE = 'record_video_note'
    UPLOAD_VIDEO_NOTE = 'upload_video_note'


@unique
class ChatMemberStatus(str, Enum):
    CREATOR = 'creator'
    ADMINISTRATOR = 'administrator'
    MEMBER = 'member'
    RESTRICTED = 'restricted'
    LEFT = 'left'
    KICKED = 'kicked'


@unique
class MessageEntityType(str, Enum):
    MENTION = 'mention'
    HASHTAG = 'hashtag'
    CASHTAG = 'cashtag'
    BOT_COMMAND = 'bot_command'
    URL = 'url'
    EMAIL = 'email'
    PHONE_NUMBER = 'phone_number'
    BOLD = 'bold'
    ITALIC = 'italic'
    CODE = 'code'
    PRE = 'pre'
    TEXT_LINK = 'text_link'
    TEXT_MENTION = 'text_mention'
    UNDERLINE = 'underline'
    STRIKETHROUGH = 'strikethrough'
    SPOILER = 'spoiler'


@unique
class UpdateType(str, Enum):
    MESSAGE = 'message'
    EDITED_MESSAGE = 'edited_message'
    CHANNEL_POST = 'channel_post'
    EDITED_CHANNEL_POST = 'edited_channel_post'
    INLINE_QUERY = 'inline_query'
    CHOSEN_INLINE_RESULT = 'chosen_inline_result'
    CALLBACK_QUERY = 'callback_query'
    SHIPPING_QUERY = 'shipping_query'
    PRE_CHECKOUT_QUERY = 'pre_checkout_query'
    POLL = 'poll'
    POLL_ANSWER = 'poll_answer'
    MY_CHAT_MEMBER = 'my_chat_member'
    CHAT_MEMBER = 'chat_member'


@unique
class ContentType(str, Enum):
    TEXT = 'text'
    AUDIO = 'audio'
    DOCUMENT = 'document'
    ANIMATION = 'animation'
    GAME = 'game'
    PHOTO = 'photo'
    STICKER = 'sticker'
    VIDEO = 'video'
    VIDEO_NOTE = 'video_note'
    VOICE = 'voice'
    CONTACT = 'contact'
    LOCATION = 'location'
    VENUE = 'venue'
    NEW_CHAT_MEMBERS = 'new_chat_members'
    LEFT_CHAT_MEMBER = 'left_chat_member'
    INVOICE = 'invoice'
    SUCCESSFUL_PAYMENT = 'successful_payment'
    CONNECTED_WEBSITE = 'connected_website'
    MIGRATE_TO_CHAT_ID = 'migrate_to_chat_id'
    MIGRATE_FROM_CHAT_ID = 'migrate_from_chat_id'
    PINNED_MESSAGE = 'pinned_message'
    NEW_CHAT_TITLE = 'new_chat_title'
    NEW_CHAT_PHOTO = 'new_chat_photo'
    DELETE_CHAT_PHOTO = 'delete_chat_photo'
    GROUP_CHAT_CREATED = 'group_chat_created'
    PASSPORT_DATA = 'passport_data'


@unique
class ParseMode(str, Enum):
    MARKDOWN = 'Markdown'
    HTML = 'HTML'
    MARKDOWN2 = 'Markdown2'


@unique
class PollType(str, Enum):
    QUIZ = 'quiz'
    REGULAR = 'regular'


@unique
class DiceEmoji(str, Enum):
    DICE = '🎲'
    DARTS = '🎯'
    BASKETBALL = '🏀'
    FOOTBALL = '⚽'
    SLOT_MACHINE = '🎰'
    BOWLING = '🎳'


@unique
class InputMediaType(str, Enum):
    PHOTO = 'photo'
    VIDEO = 'video'
    ANIMATION = 'animation'
    AUDIO = 'audio'
    DOCUMENT = 'document'


@unique
class InlineQueryResultType(str, Enum):
    ARTICLE = 'article'
    PHOTO = 'photo'
    GIF = 'gif'
    MPEG4_GIF = 'mpeg4_gif'
    VIDEO = 'video'
    AUDIO = 'audio'
    VOICE = 'voice'
    DOCUMENT = 'document'
    LOCATION = 'location'
    VENUE = 'venue'
    CONTACT = 'contact'
    GAME = 'game'
    STICKER = 'sticker'


@unique
class PassportElementType(str, Enum):
    PERSONAL_DETAILS = 'personal_details'
    PASSPORT = 'passport'
    DRIVER_LICENSE = 'driver_license'
    IDENTITY_CARD = 'identity_card'
    INTERNAL_PASSPORT = 'internal_passport'
    ADDRESS = 'address'
    UTILITY_BILL = 'utility_bill'
    BANK_STATEMENT = 'bank_statement'
    RENTAL_AGREEMENT = 'rental_agreement'
    PASSPORT_REGISTRATION = 'passport_registration'
    TEMPORARY_REGISTRATION = 'temporary_registration'
    PHONE_NUMBER = 'phone_number'
    EMAIL = 'email'
