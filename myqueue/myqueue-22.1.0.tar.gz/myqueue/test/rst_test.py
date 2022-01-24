from __future__ import annotations
import io
import os
import re
import sys
from pathlib import Path
from subprocess import PIPE, run

import pytest

user = os.environ.get('USER', 'root')
docs = Path(__file__).parent / '../../docs'


def skip(line: str) -> bool:
    for s in ['<task>', '<states>', 'ABC 123']:
        if s in line:
            return True
    return False


def run_document(mq, path: Path, test=False, update=False) -> None:
    assert path.is_file()
    lines = path.read_text().splitlines()
    blocks: list[tuple[str, list[str], int]] = []
    n = 0
    while n < len(lines):
        line = lines[n]
        if line.endswith('::'):
            line = lines[n + 2]
            if line[:5] == '    $' and not skip(line):
                cmd = ''
                output: list[str] = []
                L = 0
                for n, line in enumerate(lines[n + 2:], n + 2):
                    if not line:
                        break
                    if line[4] == '$':
                        if cmd:
                            blocks.append((cmd, output, L))
                        cmd = line[6:]
                        output = []
                        L = n
                    else:
                        output.append(line)
                blocks.append((cmd, output, L))
        n += 1

    pypath = Path().absolute()
    offset = 0
    folder = '.'
    errors = 0
    for cmd, output, L in blocks:
        print('$', cmd)
        if cmd.startswith('mq '):
            os.chdir(folder)
            out = sys.stdout
            sys.stdout = io.StringIO()
            try:
                mq(cmd[3:])
                mq.wait()
            finally:
                actual_output = sys.stdout.getvalue().splitlines()[1:]
                sys.stdout = out
        else:
            actual_output, folder = run_command(cmd, folder, pypath)
        actual_output = ['    ' + line.rstrip()
                         for line in actual_output]
        errors += compare(output, actual_output)
        L += 1 + offset
        lines[L:L + len(output)] = actual_output
        offset += len(actual_output) - len(output)

    if update:
        path.write_text('\n'.join(lines) + '\n')

    if test:
        assert errors == 0


def run_command(cmd: str,
                folder: str,
                pypath: Path) -> tuple[list[str], str]:
    if cmd.startswith('#'):
        return [], folder
    cmd, _, _ = cmd.partition('  #')
    env = os.environ.copy()
    env['PYTHONPATH'] = str(pypath)
    env['LC_ALL'] = 'C'
    result = run(f'cd {folder}; {cmd}; pwd',
                 shell=True, check=True, stdout=PIPE, env=env)
    output = result.stdout.decode().splitlines()
    folder = output.pop()
    return output, folder


def clean(line):
    line = re.sub(r'[A-Z]?[a-z]+\s+[0-9]+\s+[0-9]+:[0-9]+', '############',
                  line)
    line = re.sub(r' 0:[0-9][0-9]', ' 0:##', line)
    line = re.sub(r'[rw.-]{10,11}', '##########', line)
    line = re.sub(r' tot\w+ \d+', ' ##### #', line)
    line = re.sub(rf' {user} \w+ ', ' jensj ##### ', line)
    line = re.sub(r' jensj jensj ', ' jensj ##### ', line)
    return line


def compare(t1, t2):
    t1 = [clean(line) for line in t1]
    t2 = [clean(line) for line in t2]
    if t1 == t2 or '    ...' in t1:
        return 0
    print('<<<<<<<<<<<')
    print('\n'.join(t1))
    print('===========')
    print('\n'.join(t2))
    print('>>>>>>>>>>>')
    return 1


@pytest.mark.docs
def test_docs_workflows(mq, monkeypatch):
    monkeypatch.syspath_prepend('.')
    p = Path('prime')
    p.mkdir()
    for f in docs.glob('prime/*.*'):
        (p / f.name).write_text(f.read_text())
    venv = Path('venv')
    venv.mkdir()
    bin = venv / 'bin'
    bin.mkdir()
    (bin / 'activate').write_text(
        f'export PYTHONPATH={venv.parent.absolute()}\n')
    run_document(mq, docs / 'workflows.rst', test=True)


@pytest.mark.docs
def test_docs_documentation(mq):
    run_document(mq, docs / 'documentation.rst', test=True)


@pytest.mark.docs
def test_docs_quickstart(mq):
    run_document(mq, docs / 'quickstart.rst', test=True)
