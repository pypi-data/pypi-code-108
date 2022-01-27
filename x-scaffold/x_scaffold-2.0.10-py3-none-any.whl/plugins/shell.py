from asyncio import subprocess
import subprocess
import os

from ..context import ScaffoldContext
from ..steps import ScaffoldStep
from ..runtime import ScaffoldRuntime
from ..plugin import ScaffoldPluginContext
from ..rendering import render_text

color = {
    'PURPLE': '\033[35m',
    'CYAN':  '\033[36m',
    'BLUE':  '\033[34m',
    'GREEN':  '\033[32m',
    'YELLOW':  '\033[33m',
    'RED':  '\033[31m',
    'BOLD':  '\033[1m',
    'UNDERLINE':  '\033[4m',
    'ITALIC':  '\033[3m',
    'END':  '\033[0m',
}


def init(context: ScaffoldPluginContext):
    context.add_step('shell', ShellStep())


class ShellStep(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        commands = render_text(step, context)
        term_colors = dict_to_str(color, 'TERM_%s="%s"\n')
        cmd = """
set +x -ae
%s
%s
""" % (term_colors, commands)
        subprocess.run(cmd, cwd=context.get('__target', '.'), check=True, shell=True)
        # rc = os.system(cmd)
        # if rc != 0:
        #     raise RuntimeError('Failed to execute command')


def dict_to_str(d, fmt='%s=%s\n'):
    s = ''
    for x in d:
        s += fmt % (x, d[x])
    return s
