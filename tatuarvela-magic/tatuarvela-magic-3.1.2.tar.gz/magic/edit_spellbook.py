import subprocess  # nosec

import click

from magic.shared.config import SPELLBOOK_EDITOR, SPELLBOOK_PATH


def edit_spellbook():
    print(f"Opening spellbook in {click.style(SPELLBOOK_EDITOR, fg='cyan')}...")
    subprocess.call([SPELLBOOK_EDITOR, SPELLBOOK_PATH])  # nosec
