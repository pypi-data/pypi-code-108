"""
The PromptUI allows you to as a user Yes/No.

"""
try:
    from accpac import *
except ImportError as e:
    pass

import json
from pathlib import Path
from datetime import datetime

def prompt_yes_no(ui_script, title, message):
    conf = {'title': title, 'message': message, 'response': False}
    resp = {}
    ppath = Path(getOrgPath(), 'prompts',
                 datetime.now().strftime("%Y%m%d%H%M%S"))

    if not ppath.parent.exists():
        ppath.parent.mkdir(parents=True)

    try:
        with ppath.open('w') as f:
            f.write(json.dumps(conf))
        # Prompt for pasphrase
        params = "KEY1={}\n".format(str(ppath))
        openExtenderUI(ui_script, params, True)
        with ppath.open('r') as f:
            resp = json.loads(f.read())
    except Exception as err:
        return None
    finally:
        if ppath.exists():
            ppath.unlink()

    return resp.get("response")

class PromptUI(UI):
    """UI for prompting yes/no."""

    # Custom control constants
    BUTTON_WIDTH = 1265
    BUTTON_SPACE = 150

    def __init__(self):
        """Initialize a new UI instance."""
        UI.__init__(self)
        self.onClose = self.onClick
        args = self.get_args()
        if not args:
            error("no prompt file provided")
            raise ValueError("no prompt file provided")

        self.ppath = Path(args[0])
        if not self.ppath.exists():
            error("prompt file doesn't exist.")
            raise ValueError("prompt file doesn't exist.")

        with self.ppath.open('r') as f:
            self.conf = json.loads(f.read())

        self.message(self.conf.get("message", ""),
                     self.conf.get('title', ""),
                     "QUESTION", "YESNO", self.onClick)
        self.show()

    def get_args(self):
        args = []
        for i in range(1, 4):
            arg = getProgramKey("KEY{}".format(i), "")
            args.append(arg)
        return args

    def onClick(self, answer="NO"):
        self.conf['response'] = True
        if answer.lower() != "yes":
            self.conf['response'] = False
        with self.ppath.open("w") as f:
            f.write(json.dumps(self.conf))
        self.closeUI()
