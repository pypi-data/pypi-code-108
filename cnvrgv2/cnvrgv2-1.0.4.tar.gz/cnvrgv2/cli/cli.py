import os
import sys
import click
import codecs
import locale

from cnvrgv2.cli.modules.config import config
from cnvrgv2.cli.modules.ssh.ssh import ssh_group
from cnvrgv2.cli.utils import messages
from cnvrgv2.cli.modules.users import users
from cnvrgv2.cli.logger.logger import CnvrgLogger
from cnvrgv2.cli.modules.project.project import project_group
from cnvrgv2.cli.modules.dataset.dataset import dataset_group
from cnvrgv2.cli.modules.project.experiment import experiment_group

"""
To avoid issues reading unicode chars from stdin or writing to stdout, we need to ensure that the
python3 runtime is correctly configured, if not, we try to force to utf-8.
"""
if codecs.lookup(locale.getpreferredencoding()).name == 'ascii':
    utf_8_locales = set([loc for loc in locale.locale_alias.values() if loc.lower().endswith((".utf-8", ".utf8"))])
    english_locales = [loc for loc in utf_8_locales if loc.lower().startswith('en_us')]

    if len(english_locales) > 0:
        os.environ['LANG'] = english_locales[0]
        os.environ['LC_ALL'] = english_locales[0]

    if codecs.lookup(locale.getpreferredencoding()).name == 'ascii':
        print("Could not set locale variable automatically.")
        print("Please set the LANG and LC_ALL env variables to a proper value before calling this script.")
        print("The following suitable locales were discovered:")
        print(', '.join('{}'.format(k) for k in utf_8_locales))
        sys.exit(-1)


@click.group()
def entry_point():
    pass


def safe_entry_point():
    try:
        entry_point()
    except Exception as e:
        click.echo(messages.CLI_UNEXPECTED_ERROR.format(str(e)), err=True)


entry_point.add_command(users.login)
entry_point.add_command(users.logout)
entry_point.add_command(CnvrgLogger.set_logs_keep_duration)
entry_point.add_command(project_group)
entry_point.add_command(experiment_group)
entry_point.add_command(dataset_group)
entry_point.add_command(ssh_group)
entry_point.add_command(config)
