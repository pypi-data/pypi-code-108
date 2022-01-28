"""
:author: Thomas Delaet <thomas@delaet.org>

Port for Domintell
:author: Zilvinas Binisevicius <zilvinas@binis.me>

"""
import logging
import domipy

NORMAL_MODE = 0
APP_INFO_MODE = 1
MSG_INFO_WRAPPER = "INFO"
MSG_SESSION_OPENED =  'Session opened'
MSG_SESSION_CLOSED =  'Session closed'
MSG_SESSION_TIMEOUT = 'Session timeout'
MSG_LOGIN_WAITING_FOR_LOGINSW = "Waiting for LOGINPSW"
MSG_LOGIN_REQUESTSALT = "REQUESTSALT"
MSG_HELLO_WORLD = "WORLD"

class ParserError(Exception):
    """
    Error when invalid message is received
    """

class DomintellParser(object):
    """
    Transform Domintell message to Message object
    """

    def __init__(self, controller):
        assert isinstance(controller, domipy.Controller)
        self._mode = NORMAL_MODE
        self.logger = logging.getLogger('domintell')
        self.controller = controller

    def feed(self, data):
        message = self.parse(data)
        if isinstance(message, domipy.Message):
            self.controller.new_message(message)

    def parse(self, data):
        """
        parse message and return Message object, or None
        """
        data = data.lstrip('\r\n ').rstrip('\r\n')
        assert len(data) > 0
        assert len(data) >= domipy.MINIMUM_MESSAGE_SIZE

        self.logger.info("Processing message [%s]", data.strip('\r\n '))
        if len(data) > domipy.MAXIMUM_MESSAGE_SIZE:
            self.logger.warning("Domintell message are maximum %s chars, this one is %s", str(
                domipy.MAXIMUM_MESSAGE_SIZE), str(len(data)))
            return
        ## Real parsing here

        message_components = data.split(':')
        message_type = message_components[0]

        if message_type == MSG_INFO_WRAPPER:
            return self.parse_info(message_components)

        module_type = data[0:3]
        serial_number = data[3:9].strip()
        data_type = data[9:10]
        data_string = data[10:].rstrip()

        i = ['INF', '!! ']

        if module_type == 'APP':
            # looks like we received APPINFO start message
            # check more data
            logging.info("Switching to APPINFO moder")
            if data[0:7] == "APPINFO":
                # switching to APPINFO mode
                self._mode = APP_INFO_MODE

                # TODO: Start timer, to reset mode if end packet is lost
                # ..
                return domipy.ControllMessage('APPINFO', data)
        if module_type == 'END':
            # looks like we received APPINFO END message
            # check more data
            if data[0:11] == "END APPINFO":
                self._mode = NORMAL_MODE
                return domipy.ControllMessage('END APPINFO', data)

        
        if self._mode == APP_INFO_MODE:
            # we are in app info mode, regular messages won't be processed
            if self.contains_all(data, '[|]'):
                # module info message
                return domipy.ModuleInfoMessage(module_type, data)
        else:
            # normal mode
            if module_type in i:
                # some info message
                if data[0:24] == MSG_SESSION_OPENED:
                    return domipy.SessionOpenedMessage(data=data)
                elif data[0:24] == MSG_SESSION_CLOSED:
                    return domipy.SessionClosedMessage(data=data)
                elif data[0:25] == MSG_SESSION_TIMEOUT:
                    return domipy.SessionTimeoutMessage(data=data)
                return domipy.InfoMessage(module_type, data)

            # normal message
            if module_type in domipy.CommandRegistry:
                message = domipy.CommandRegistry[module_type]()
                message.populate(serial_number, data_type, data_string)
                return message
            else:
                self.logger.debug("Unrecognized message [%s]", str(module_type))

    def parse_info(self, message_components):
        if message_components[1] == MSG_SESSION_OPENED:
            return domipy.SessionOpenedMessage(data=message_components[1])
        elif message_components[1] == MSG_LOGIN_REQUESTSALT:
            return domipy.LoginRequestSaltMessage(data=message_components)
        elif message_components[1] == MSG_LOGIN_WAITING_FOR_LOGINSW:
            return domipy.WaitingForLoginswMessage(data=message_components)
        elif message_components[1] == MSG_SESSION_CLOSED:
            return domipy.SessionClosedMessage(data=message_components[1])
        elif message_components[1] == MSG_SESSION_TIMEOUT:
            return domipy.SessionTimeoutMessage(data=message_components[1])
        elif message_components[1] == MSG_HELLO_WORLD:
            return domipy.InfoMessage(data=message_components[1])
        return domipy.InfoMessage("INFO", message_components[1])

    def contains_all(self, current_string, current_set):
        return 0 not in [c in current_string for c in current_set]

    def contains_any(self, current_string, current_set):
        return 1 in [c in current_string for c in current_set]

    

