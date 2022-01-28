import logging
import time
import uuid

from django.conf import settings
from django.utils import timezone

from isc_common import setAttr
from isc_common.auth.models.user import User
from isc_common.bit import IsBitOn, TurnBitOn, TurnBitOff
from isc_common.datetime import DateToStr
from isc_common.http.DSRequest import DSRequest
from isc_common.ws.webSocket import WebSocket
from tracker.models.messages_state import Messages_state
from tracker.models.messages_theme import Messages_theme
from twits.models.chat_user_user import Chat_user_user
from twits.models.chat_user_user_theme import Chat_user_user_theme
from twits.models.chat_users_view import Chat_usersView

logger = logging.getLogger(__name__)


class LoginRequest(DSRequest):

    @classmethod
    def get_chats(cls, user):
        tetatet_chats_reciver = []
        tetatet_chats_sender = []
        tetatet_chats = []

        key = 'LoginRequest.get_chats'
        settings.LOCKS.acquire(key)
        for chat in Chat_user_user.objects.filter(user_reciver=user):
            tetatet_chats_reciver.append(dict(
                id=chat.common_id,
                props=chat.props._value,
                sender_id=chat.user_sender.id,
                fullname=chat.user_sender.get_full_name,
                shortname=chat.user_sender.get_short_name,
                theme_ids=[item.theme.id for item in Chat_user_user_theme.objects.filter(chat_user_user__common_id=chat.common_id)],
                view_theme_ids=[item.theme.id for item in Chat_user_user_theme.objects.filter(chat_user_user__common_id=chat.common_id) if item.chat_user_user.user_sender == user],
                readonly=True
            ))

        for chat in Chat_user_user.objects.filter(user_sender=user):
            tetatet_chats_sender.append(dict(
                id=chat.common_id,
                props=chat.props._value,
                reciver_id=chat.user_reciver.id,
                fullname=chat.user_reciver.get_full_name,
                shortname=chat.user_reciver.get_short_name,
                theme_ids=[item.theme.id for item in Chat_user_user_theme.objects.filter(chat_user_user__common_id=chat.common_id)],
                view_theme_ids=[item.theme.id for item in Chat_user_user_theme.objects.filter(chat_user_user__common_id=chat.common_id) if item.chat_user_user.user_sender == user],
                readonly=False
            ))

        for chat in tetatet_chats_reciver:
            chat2 = [item for item in tetatet_chats_sender if item.get('id') == chat.get('id')]
            read_only = len(chat2) == 0
            if read_only:
                tetatet_chats.append(chat)
            else:
                compulsory_reading = IsBitOn(chat.get('props'), 0)
                if compulsory_reading:
                    props = TurnBitOn(chat2[0].get('props'), 0)
                else:
                    props = TurnBitOff(chat2[0].get('props'), 0)
                setAttr(chat2[0], 'props', props)
                tetatet_chats.append(chat2[0])

        for chat in tetatet_chats_sender:
            chat2 = [item for item in tetatet_chats if item.get('id') == chat.get('id')]
            if len(chat2) == 0:
                tetatet_chats.append(chat)

        group_chats = [
            dict(
                id=chat_users.chat.id,
                props=chat_users.props._value,
                code=chat_users.chat.code,
                name=chat_users.chat.name,
                readonly=chat_users.readonly,
                theme_ids=[
                    Messages_theme.objects.get_or_create(
                        code=f'group_{chat_users.chat.code}',
                        defaults=dict(
                            name=f'Чат: {chat_users.chat.name}',
                            creator=User.admin_user(),
                            editing=False,
                            deliting=False,
                            parent=Messages_theme.group_chats_theme(),
                            description='Группа создана автоматически'))[0].id
                ],
            ) for chat_users in Chat_usersView.objects.filter(user=user)]
        settings.LOCKS.release(key)

        return dict(
            group_chats=group_chats,
            tetatet_chats=tetatet_chats,
        )

    @classmethod
    def send_bot_message(cls, user, bot, message, compulsory_reading=False):
        _user = user
        _bot = bot

        key = 'LoginRequest.send_bot_message'
        settings.LOCKS.acquire(key)
        if not isinstance(_user, User) and isinstance(_user, int):
            _user = User.objects.get(id=_user)

        if not isinstance(_bot, User) and isinstance(_bot, int):
            _bot = User.objects.get(id=_bot)

        props = TurnBitOn(0, 0) if compulsory_reading else TurnBitOff(0, 0)
        chat_user_user, created = Chat_user_user.objects.get_or_create(
            user_sender=_bot,
            user_reciver=_user,
            defaults=dict(props=props)
        )

        def send():
            channel = f'tetatet_{chat_user_user.common_id}'

            _message = dict(
                channel=channel,
                date=DateToStr(timezone.now(), '%d.%m.%Y, %H:%M:%S', 3),
                guid=uuid.uuid4(),
                host=settings.WS_HOST,
                message=f'<pre>{message}</pre>',
                message_state_delivered_id=Messages_state.message_state_delivered().id,
                message_state_delivered_name=Messages_state.message_state_delivered().name,
                message_state_new_id=Messages_state.message_state_new().id,
                message_state_new_name=Messages_state.message_state_new().name,
                message_state_readed_id=Messages_state.message_state_readed().id,
                message_state_readed_name=Messages_state.message_state_readed().name,
                message_state_not_readed_id=Messages_state.message_state_not_readed().id,
                message_state_not_readed_name=Messages_state.message_state_not_readed().name,
                path='twit',
                port=settings.WS_PORT,
                props=0,
                theme_ids=[item.theme.id for item in Chat_user_user_theme.objects.filter(chat_user_user=chat_user_user)],
                type='message',
                user__color=_bot.color if _bot.color else 'black',
                user__full_name=_bot.get_full_name,
                user__short_name=_bot.get_short_name,
                user_id=_bot.id
            )

            WebSocket.send_message(
                host=settings.WS_HOST,
                port=settings.WS_PORT,
                channel=channel,
                message=_message,
                logger=logger
            )

        if created:
            from twits.models.chats import ChatsManager
            ChatsManager.refresh_chat_menu(user=_user, logger=logger)
            time.sleep(3)
            send()
        else:
            if chat_user_user.props._value != props:
                chat_user_user.props = props
                chat_user_user.save()

                from twits.models.chats import ChatsManager
                ChatsManager.refresh_chat_menu(user=_user, logger=logger)
                time.sleep(3)
            send()
        settings.LOCKS.release(key)
