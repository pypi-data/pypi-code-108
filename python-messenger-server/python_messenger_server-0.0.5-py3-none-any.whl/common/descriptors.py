from messenger2 import config
import traceback
from ipaddress import ip_address

WAY = traceback.format_stack()[0].split()[1].strip('",').split('/')[-1]
if WAY == 'server_start.py':
    LOGGER = "server_logger"
else:
    LOGGER = "client_logger"


class Port:
    """
    Descriptor for port checking
    """
    def __get__(self, instance, owner):
        return instance.__dict__[self.my_attr]

    def __set__(self, instance, value):

        # print("hello from port descriptor")
        # print(value)
        try:
            if value < 1024 or value > 65535:
                instance.__dict__[LOGGER].error('Неверно заданный порт')
                raise ValueError
        except ValueError:
            instance.__dict__[LOGGER].error(
                'В качастве порта может быть указано только число '
                'в диапазоне от 1024 до 65535.')
            instance.__dict__[LOGGER].error('Задан порт по умолчанию')

            instance.__dict__[self.my_attr] = config.SERVER_PORT
        else:
            instance.__dict__[self.my_attr] = value

        finally:
            print("port descriptor")
            print(f"real value {instance.__dict__[self.my_attr]}")

    def __delete__(self, instance):
        del instance.__dict__[self.my_attr]

    def __set_name__(self, owner, my_attr):
        # owner - владелец атрибута - <class '__main__.Worker'>
        # my_attr - имя атрибута владельца - hours, rate
        self.my_attr = my_attr


class Address:
    """
    Descriptor for ip check
    """

    def __get__(self, instance, owner):
        return instance.__dict__[self.my_attr]

    def __set__(self, instance, value):
        # print("hello from address descriptor")
        # print(value)
        try:
            if value != "":
                ip = ip_address(value)
            else:
                ip = ""
        except ValueError:
            instance.__dict__[LOGGER].error('адрес неправильной конфигурации')
            instance.__dict__[LOGGER].error('Задан адрес по умолчанию')

            instance.__dict__[self.my_attr] = config.USER_ADDRESS
        else:
            instance.__dict__[self.my_attr] = ip

        finally:
            print("address descriptor")
            print(f"real value: {instance.__dict__[self.my_attr]}")

    def __delete__(self, instance):
        del instance.__dict__[self.my_attr]

    def __set_name__(self, owner, my_attr):
        # owner - владелец атрибута - <class '__main__.Worker'>
        # my_attr - имя атрибута владельца - hours, rate
        self.my_attr = my_attr
