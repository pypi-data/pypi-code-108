from pathlib import Path

import click


@click.command(name='bash_history')
@click.argument('path', type=click.Path(exists=True),
                default=Path('~/.bash_history').expanduser())
def main(path):
    from puddl.contrib.file.models import Device, File
    file = File.objects.upsert(
        device=Device.objects.me(),
        path=path
    )
    from .models import BashHistory
    BashHistory.objects.from_file(file)
