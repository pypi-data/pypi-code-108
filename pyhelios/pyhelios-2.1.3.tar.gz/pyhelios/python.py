from warnings import filterwarnings
from traitlets.config import Config
from pygments.formatters import HtmlFormatter
from IPython import start_ipython
from IPython.terminal.prompts import Prompts
from IPython.terminal.prompts import Token
from pyhelios.highlight import DraculaPygments


class HeliosPrompt(Prompts):
    def in_prompt_tokens(self):
        return [
            (Token.Prompt, self.vi_mode()),
            (Token.Prompt, ">>> "),
            (Token.PromptNum, ""),
            (Token.Prompt, ""),
        ]

    def out_prompt_tokens(self):
        return [
            (Token.OutPrompt, ""),
            (Token.OutPromptNum, ""),
            (Token.OutPrompt, ""),
        ]


def ipython(args):
    filterwarnings("ignore")
    c = Config()
    c.InteractiveShellApp.exec_lines = ["import pyhelios"]
    c.InteractiveShell.colors = "Linux"
    c.InteractiveShell.separate_in = ""
    c.TerminalInteractiveShell.highlighting_style = HtmlFormatter(
        style=DraculaPygments
    ).style
    c.InteractiveShell.confirm_exit = False
    c.TerminalIPythonApp.display_banner = False
    c.TerminalInteractiveShell.highlighting_style_overrides = {
        Token.Prompt: "",
        Token.PromptNum: "",
        Token.OutPrompt: "",
        Token.OutPromptNum: "",
    }
    c.TerminalInteractiveShell.prompts_class = HeliosPrompt
    start_ipython(argv=args, config=c)
