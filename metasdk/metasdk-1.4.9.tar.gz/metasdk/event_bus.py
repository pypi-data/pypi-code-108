from typing import List, Callable

from metasdk.__state import get_current_app


class Listen(object):
    """
    Декоратор для оборачивания запускаемых методов.
    С него же снимается инфа о том, какие подписки существуют.
    """

    def __init__(self, entity_id: str, code: List[str], form_pattern: List[str] = None, dispatcher_pattern: List[str] = None, receive_value: bool = False):
        """
        Регистрация метода в шине
        :param entity_id: ID сущности META
        :param code: Коды ObjectLogService META - ADD, SET, REMOVE
        :param form_pattern: Формы, на которые долэен реагировать хендлер, может быть пустым. Если пустой - значит form в event-е может быть заполненным или незаполненным,
                                а если * - то форма долэна быть заполнена, но заполнена любым значением
        :param dispatcher_pattern: Генераторы событий - используются для шины событий как клиент, который продуцирует полезну работу:
                                 запускает фоновые процессы, записыват логи, генерирует события в шину
                                 Примеры:
                                 meta.{META_APP_ALIAS} - мета-приложение
                                 appscript.{SERVICE_ID} - фоновый скрипт (включает в сещя обработчики шины событий)
                                 apiservice.{SERVICE_ID} - http апи сервисы
        :param receive_value: нужно ли добавлять value в событие
        """
        self.entity_id = entity_id
        self.code = code
        self.form_pattern = form_pattern
        self.dispatcher_pattern = dispatcher_pattern
        self.receive_value = receive_value

    def __call__(self, original_func):
        get_current_app().event_bus.add_listener(self, original_func)

        def wrappee(*args, **kwargs):
            return original_func(*args, **kwargs)

        return wrappee


class Listener(object):
    """
    Хранилище функции и настройки
    """

    def __init__(self, listen: Listen, handler_func: Callable):
        self.listen = listen
        self.handler_func = handler_func


class Event(object):
    """
    Объект события с его контентом.
    На основе данных таска запускатора
    """

    def __init__(self, task):
        self.__task = task

        edata = task['data']['event']
        self.event_id = edata.get("eventId")
        self.user_id = int(edata['userId'])
        self.entity_id = str(edata['entityId'])
        self.object_id = str(edata['objectId'])
        self.code = str(edata['code'])
        self.form = str(edata['form']) if edata.get('form') else None
        self.dispatcher = str(edata['dispatcher']) if edata.get('dispatcher') else None
        self.value = edata.get('value')


class EventBus(object):
    """
    Сама Шина. Она же хранит всю карту слушателей
    """
    listener = Listen

    def __init__(self, app) -> None:
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__listeners_map = {}

    def add_listener(self, listen, handler_func):
        entity_id = listen.entity_id
        self.__listeners_map.setdefault(entity_id, [])
        listener = Listener(listen, handler_func)
        self.__listeners_map[entity_id].append(listener)

    def get_listeners(self):
        for listeners in self.__listeners_map.values():
            for listener in listeners:
                yield listener

    def accept(self, task):
        event = Event(task)
        # listener: type Listener
        for listener in self.__listeners_map.get(event.entity_id, []):
            if event.code not in listener.listen.code:
                continue

            if not self.__contains_in_patterns(event.form, listener.listen.form_pattern):
                continue

            if not self.__contains_in_patterns(event.dispatcher, listener.listen.dispatcher_pattern):
                continue

            try:
                self.__app.log.set_entity("event", {
                    "dispatcher": event.dispatcher,
                    "eventId": event.event_id,
                    "userId": event.user_id,
                    "entityId": event.entity_id,
                    "objectId": event.object_id,
                    "code": event.code,
                    "form": event.form,
                })
                listener.handler_func(event)
            finally:
                self.__app.log.set_entity("event", None)

    def __contains_in_patterns(self, in_str, pattern_list):
        if not pattern_list:
            return True

        if not in_str:
            # если нет формы, то паттерны обязаны содержать хотябы один, целиком состоящий из *
            # это будет означать, что любые form годятся для хендлера
            return '*' in pattern_list

        for pattern in pattern_list:
            if pattern.startswith("*"):
                # есть подобие регулярки. Например qwe*
                if in_str.endswith(pattern[1:]):
                    return True
            elif pattern.endswith("*"):
                # есть подобие регулярки
                if in_str.startswith(pattern[:-1]):
                    return True
            else:
                # регулярки нет, можно проверять точным вхождением
                if in_str == pattern:
                    return True
        return False
