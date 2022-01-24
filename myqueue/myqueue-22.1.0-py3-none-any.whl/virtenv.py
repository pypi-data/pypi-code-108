"""Automatically activate venv's."""
from __future__ import annotations
from pathlib import Path
import warnings


def find_activation_scripts(folders: list[Path]) -> dict[Path, Path]:
    """Find virtualenv activation scripts."""
    scripts: dict[Path, Path] = {}
    for folder in folders:
        found = []
        while True:
            if folder in scripts:
                script = scripts[folder]
                break

            script = folder / 'venv/activate'
            if script.is_file():
                warnings.warn('Please put your activate script in the '
                              'venv/bin/ folder!')
                found.append(folder)

                break

            script = folder / 'venv/bin/activate'
            if script.is_file():
                found.append(folder)
                break

            newfolder = folder.parent
            if newfolder == Path('/'):
                break
            found.append(folder)
            folder = newfolder

        if script.is_file():
            for dir in found:
                scripts[dir] = script

    return {folder: scripts[folder]
            for folder in folders
            if folder in scripts}


if __name__ == '__main__':
    import sys
    scripts = find_activation_scripts([Path(dir).absolute()
                                       for dir in sys.argv[1:]])
    for folder, script in scripts.items():
        print(f'{folder}: {script}')
