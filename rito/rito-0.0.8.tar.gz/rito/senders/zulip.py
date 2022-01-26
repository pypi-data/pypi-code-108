# TODO retrieve environment variables for Zulip bot
# TODO link to zulip bot documentation for setting up and filling out environment variables

class RitoZulipBotHandler(object):
    '''
    Handles sending zulip messages through Zulip bot API
    '''

    def usage(self):
        return '''TODO usage info'''

    def handle_message(self, message, bot_handler):
        # add your code here
        pass

handler_class = RitoZulipBotHandler


def send_message(channel, text):
    # TODO construct a zulip bot handler and use send_message()?
    pass

# bot_handler.send_message: https://zulip.com/api/writing-bots#bot_handlersend_message