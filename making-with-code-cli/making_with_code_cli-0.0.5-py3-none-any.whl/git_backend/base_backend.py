from pathlib import Path
from making_with_code_cli.cli_setup import WORK_DIR_PERMISSIONS

class GitBackend:
    """Base class interface to backend git server.
    All Making With Code deployments are backed by a git server, but the nature of the
    server and the strategies for completing tasks vary by backend. 
    """
    INIT_ACTIONS = [
        'create_from_template',
        'clone',
        'mkdir'
    ]

    def __init__(self, settings):
        self.settings = settings

    def init_module(self, module, modpath):
        if not 'init_action' in module:
            raise ValueError(f"There is a problem with the website. Can't initialize module {module['slug']} " + 
                    "without an init action.")
        if not module['init_action'] in self.INIT_ACTIONS:
            raise ValueError(f"There is a problem with the website. Can't initialize module {module['slug']} " + 
                    f"with init action '{module['init_action']}'.")
        if module['init_action'] == "mkdir":
            self.init_mkdir(module, modpath)
        if module['init_action'] == "clone":
            self.init_clone(module, modpath)
        if module['init_action'] == "create_from_template":
            self.init_create_from_template(module, modpath)

    def init_mkdir(self, module, modpath):
        modpath.mkdir(mode=WORK_DIR_PERMISSIONS)

    def init_clone(self, module, modpath):
        raise NotImplemented()

    def init_create_from_template(self, module, modpath):
        raise NotImplemented()


        

