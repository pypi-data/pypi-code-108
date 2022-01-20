
try:
    from .base import Core
    from . import chariot
except:
    from base import Core
    import chariot



"""
SDK入口
"""


class CLI(object):

    def __init__(self, plugins):
        # 所有自写脚本的类对象
        self.plugins = plugins


    def run(self):

        core = Core()

        cmd = core.get_cmd()  # command: run, http, or test

        # mains
        if cmd == 'run':
            inp = core.get_stdin()  # input
            chariot.run(inp, self.plugins)
        elif cmd == "http":
            chariot.http(self.plugins)
        elif cmd == 'test':
            inp = core.get_stdin()  # input
            chariot.test(inp, self.plugins)


