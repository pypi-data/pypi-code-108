from ansible.plugins.callback import CallbackBase

import os

DOCUMENTATION = '''
    options:
      file_name:
        description: ""
        ini:
          - section: callback_test_callback
            key: file_name
        required: True
        type: string
'''


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 1.0
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys,
                                                var_options=var_options,
                                                direct=direct)

        self.file_name = self.get_option('file_name')

    def v2_on_any(self, *args, **kwargs):
        path = os.path.join(os.path.dirname(__file__), self.file_name)
        self._display.display("Touching file: {}".format(path))
        with open(path, 'w'):
            pass
