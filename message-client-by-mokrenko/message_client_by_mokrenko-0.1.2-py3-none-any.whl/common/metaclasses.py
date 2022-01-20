"""
В основе метода библиотека dis - анализ кода с помощью его дизассемблирования
(разбор кода на составляющие: в нашем случае - на атрибуты и методы класса)
https://docs.python.org/3/library/dis.html
"""

import dis
from pprint import pprint


class TransportVerifier(type):
    def __init__(cls, clsname, bases, clsdict):
        # print('TransportVerifier', cls, ';', clsname, ';', bases)
        methods = []
        # Атрибуты, используемые в функциях классов
        attrs = []
        # перебираем ключи
        for func in clsdict:
            # Пробуем
            try:
                # Возвращает итератор по инструкциям в предоставленной функции
                # , методе, строке исходного кода или объекте кода.
                if func != '__doc__':
                    ret = dis.get_instructions(clsdict[func])
                # ret - <generator object _get_instructions_bytes at 0x00000062EAEAD7C8>
                # ret - <generator object _get_instructions_bytes at 0x00000062EAEADF48>
                # ...
                # Если не функция то ловим исключение
                # (если порт)
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы и атрибуты.
                for i in ret:
                    # i - Instruction(opname='LOAD_GLOBAL', opcode=116, arg=9, argval='send_message',
                    # argrepr='send_message', offset=308, starts_line=201, is_jump_target=False)
                    # opname - имя для операции
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            # заполняем список методами, использующимися в функциях класса
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            # заполняем список атрибутами, использующимися в функциях класса
                            attrs.append(i.argval)
        # print(methods)
        # print(attrs)
        # Если сокет не инициализировался константами SOCK_STREAM(TCP) AF_INET(IPv4), тоже исключение.
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета.')
        # Обязательно вызываем конструктор предка:
        super().__init__(clsname, bases, clsdict)


# Метакласс для проверки соответствия сервера:
class ServerVerifier(TransportVerifier):
    def __init__(cls, clsname, bases, clsdict):
        # print('ServerVerifier', cls, ';', clsname, ';', bases)
        # clsname - экземпляр метакласса - Server
        # bases - кортеж базовых классов - ()
        # clsdict - словарь атрибутов и методов экземпляра метакласса
        # {'__module__': '__main__',
        # '__qualname__': 'Server',
        # 'port': <descrptrs.Port object at 0x000000DACC8F5748>,
        # '__init__': <function Server.__init__ at 0x000000DACCE3E378>,
        # 'init_socket': <function Server.init_socket at 0x000000DACCE3E400>,
        # 'main_loop': <function Server.main_loop at 0x000000DACCE3E488>,
        # 'process_message': <function Server.process_message at 0x000000DACCE3E510>,
        # 'process_client_message': <function Server.process_client_message at 0x000000DACCE3E598>}
        # Список методов, которые используются в функциях класса:
        methods = []
        # Атрибуты, используемые в функциях классов
        # attrs = []
        # перебираем ключи
        for func in clsdict:
            # Пробуем
            try:
                # Возвращает итератор по инструкциям в предоставленной функции
                # , методе, строке исходного кода или объекте кода.
                if func != '__doc__':
                    ret = dis.get_instructions(clsdict[func])
                else:
                    continue
                # ret - <generator object _get_instructions_bytes at 0x00000062EAEAD7C8>
                # ret - <generator object _get_instructions_bytes at 0x00000062EAEADF48>
                # ...
                # Если не функция то ловим исключение
                # (если порт)
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы и атрибуты.
                for i in ret:
                    # i - Instruction(opname='LOAD_GLOBAL', opcode=116, arg=9, argval='send_message',
                    # argrepr='send_message', offset=308, starts_line=201, is_jump_target=False)
                    # opname - имя для операции
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            # заполняем список методами, использующимися в функциях класса
                            methods.append(i.argval)
                    # elif i.opname == 'LOAD_ATTR':
                    #     if i.argval not in attrs:
                    #         # заполняем список атрибутами, использующимися в функциях класса
                    #         attrs.append(i.argval)
        print(methods)
        # Если обнаружено использование недопустимого метода connect, вызываем исключение:
        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')


# Метакласс для проверки корректности клиентов:
class ClientVerifier(TransportVerifier):
    def __init__(cls, clsname, bases, clsdict):
        # pprint(clsdict)
        # Список методов, которые используются в функциях класса:
        methods = []
        attrs = []
        for func, value in clsdict.items():
            # Проверяем, чтобы socket не присваивался на уровне класса

            if str(value).find('.socket') != -1:
                raise TypeError('Создание сокетов на уровне класса запрещено!')

            # Пробуем
            try:
                if func != '__doc__':
                    ret = dis.get_instructions(clsdict[func])
                else:
                    continue
                # Если не функция то ловим исключение
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы.
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            # print(i)
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            # заполняем список атрибутами, использующимися в функциях класса
                            attrs.append(i.argval)
        # print(methods)
        # Если обнаружено использование недопустимого метода accept, listen, socket бросаем исключение:
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещённого метода')
        # Наличие метода create_presence считаем корректным использованием сокетов
        if 'create_presence' in clsdict.keys():
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
