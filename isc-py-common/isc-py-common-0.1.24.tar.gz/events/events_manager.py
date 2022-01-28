import logging

from django.db import transaction

from isc_common.bit import IsBitOn, TurnBitOn
from isc_common.common import blue

logger = logging.getLogger(__name__)


class Event:
    event_type = None
    bot = None

    def __init__(self, **kwargs):
        from events.models.event_types import Event_types
        from events.models.event_type_users import Event_type_users

        for k, v in kwargs.items():
            setattr(self, k, v() if callable(v) else v)

        if not isinstance(self.event_type, Event_types):
            raise Exception(f'Not specified "event_type"')

        self.users = [event_type_users.user for event_type_users in Event_type_users.objects.filter(event_type=self.event_type)]

    def send_message(self, message=None, users_array=None, progress=None, len=None):
        from events.models.event_type_users import Event_type_usersManager
        from isc_common.auth.http.LoginRequets import LoginRequest
        from isc_common.common import blinkString
        from isc_common.progress import Progress
        from isc_common.progress import ProgressDroped
        from tracker.models.messages import MessagesManager
        from isc_common.progress import progress_deleted

        users = self.users.copy()

        if isinstance(users_array, list):
            users.extend(users_array)

        idx = 0
        if isinstance(progress, Progress) and len:
            progress.setQty(len)

        for user in users:
            if isinstance(message, list):
                _message = message[idx]
                idx += 1
            elif isinstance(message, str):
                _message = message
            else:
                raise Exception(f'Недопустимый формат message.')

            msg = f'<h3>Сообщение от:</h3> #{self.event_type.full_name}' \
                  f'<p>{MessagesManager.get_border(_message, user)}'

            if isinstance(progress, Progress):
                progress.setContentsLabel(blinkString(f'Отправка сообщения: {msg} <p/> {user.get_full_name}', bold=True, blink=False, color=blue))

                if len:
                    if progress.step() != 0:
                        raise ProgressDroped(progress_deleted)

            LoginRequest.send_bot_message(
                user=user,
                bot=Event_type_usersManager.get_bot(self.event_type),
                message=msg,
                compulsory_reading=self.event_type.props.compulsory_reading.is_set
            )


class EventsManager:
    events = []

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v() if callable(v) else v)

    def get_event(self, code, name, compulsory_reading=True) -> Event:
        from events.models.event_types import Event_types

        events = [event for event in self.events if event.event_type.code == code]
        if len(events) == 0:
            with transaction.atomic():
                if not isinstance(code, str):
                    raise Exception(f'Not specified "code" event')

                if not isinstance(name, str):
                    raise Exception(f'Not specified "code" event')

                codes = code.split('.')
                names = name.split('.')

                if len(codes) != len(names):
                    raise Exception(f'Not mapping "code" to "name')

                code_path = None
                index = 0
                parent = None
                event = None
                for _code in codes:
                    if code_path is None:
                        code_path = f'{_code}'
                    else:
                        code_path = f'{code_path}.{_code}'

                    props = 0
                    if index == len(codes) - 1:
                        props = TurnBitOn(props, 0)
                        if compulsory_reading:
                            props = TurnBitOn(props, 1)

                    event_type, _ = Event_types.objects.update_or_create(
                        code=code_path,
                        defaults=dict(
                            name=names[index],
                            props=props,
                            parent=parent,
                            editing=False,
                            deliting=False,
                        )
                    )

                    if IsBitOn(event_type.props, 0):
                        event = Event(event_type=event_type)
                        self.events.append(event)

                    index += 1
                    parent = event_type
                return event
        else:
            return events[0]
