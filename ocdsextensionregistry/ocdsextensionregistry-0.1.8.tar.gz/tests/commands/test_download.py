import logging
import os
import sys
from glob import glob

import pytest

from ocdsextensionregistry.cli.__main__ import main

args = ['ocdsextensionregistry', 'download']


def test_command(capsys, monkeypatch, tmpdir):
    monkeypatch.setattr(sys, 'argv', args + [str(tmpdir), 'location==v1.1.4'])
    main()

    assert capsys.readouterr().out == ''

    tree = list(os.walk(tmpdir))

    assert len(tree) == 4
    # extensions
    assert tree[0][1] == ['location']
    assert tree[0][2] == []
    # versions
    assert tree[1][1] == ['v1.1.4']
    assert tree[1][2] == []
    # files
    assert tree[2][1] == ['codelists']
    assert sorted(tree[2][2]) == ['LICENSE', 'README.md', 'extension.json', 'release-schema.json']
    # codelists
    assert tree[3][1] == []
    assert sorted(tree[3][2]) == ['geometryType.csv', 'locationGazetteers.csv']


def test_command_versions(capsys, monkeypatch, tmpdir):
    monkeypatch.setattr(sys, 'argv', args + [str(tmpdir), 'location'])
    main()

    assert capsys.readouterr().out == ''

    tree = list(os.walk(tmpdir))

    assert len(tree[1][1]) > 1


# Take the strictest of restrictions.
def test_command_versions_collision(capsys, monkeypatch, tmpdir):
    monkeypatch.setattr(sys, 'argv', args + [str(tmpdir), 'location==v1.1.4', 'location'])
    main()

    assert capsys.readouterr().out == ''

    tree = list(os.walk(tmpdir))

    assert len(tree[1][1]) == 1


def test_command_versions_invalid(capsys, monkeypatch, tmpdir, caplog):
    caplog.set_level(logging.INFO, logger='ocdsextensionregistry')

    with pytest.raises(SystemExit) as excinfo:
        monkeypatch.setattr(sys, 'argv', args + [str(tmpdir), 'location=v1.1.4'])
        main()

    assert capsys.readouterr().out == ''

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message == "Couldn't parse 'location=v1.1.4'. Use '==' not '='."
    assert excinfo.value.code == 1


# Require the user to decide what to overwrite.
def test_command_repeated(capsys, monkeypatch, tmpdir, caplog):
    caplog.set_level(logging.INFO, logger='ocdsextensionregistry')
    argv = args + [str(tmpdir), 'location==v1.1.4']

    monkeypatch.setattr(sys, 'argv', argv)
    main()

    with pytest.raises(SystemExit) as excinfo:
        monkeypatch.setattr(sys, 'argv', argv)
        main()

    assert capsys.readouterr().out == ''

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message.endswith('Set the --overwrite option.')
    assert excinfo.value.code == 1


def test_command_repeated_overwrite_any(capsys, monkeypatch, tmpdir):
    argv = args + [str(tmpdir), 'location==v1.1.4']
    pattern = str(tmpdir / '*' / '*' / 'extension.json')

    monkeypatch.setattr(sys, 'argv', argv)
    main()

    # Remove a file, to test whether its download is repeated.
    os.unlink(glob(pattern)[0])

    monkeypatch.setattr(sys, 'argv', argv + ['--overwrite', 'any'])
    main()

    assert capsys.readouterr().out == ''

    assert len(glob(pattern)) == 1


def test_command_repeated_overwrite_none(capsys, monkeypatch, tmpdir):
    argv = args + [str(tmpdir), 'location==v1.1.4']
    pattern = str(tmpdir / '*' / '*' / 'extension.json')

    monkeypatch.setattr(sys, 'argv', argv)
    main()

    # Remove a file, to test whether its download is repeated.
    os.unlink(glob(pattern)[0])

    monkeypatch.setattr(sys, 'argv', argv + ['--overwrite', 'none'])
    main()

    assert capsys.readouterr().out == ''

    assert len(glob(pattern)) == 0


def test_command_repeated_overwrite_live(capsys, monkeypatch, tmpdir):
    argv = args + [str(tmpdir), 'location==v1.1.4', 'location==master']
    pattern = str(tmpdir / '*' / '*' / 'extension.json')

    monkeypatch.setattr(sys, 'argv', argv)
    main()

    # Remove files, to test which downloads are repeated.
    for filename in glob(pattern):
        os.unlink(filename)

    monkeypatch.setattr(sys, 'argv', argv + ['--overwrite', 'live'])
    main()

    assert capsys.readouterr().out == ''

    filenames = glob(pattern)

    assert len(filenames) == 1
    assert filenames[0] == str(tmpdir / 'location' / 'master' / 'extension.json')


def test_command_help(capsys, monkeypatch, caplog):
    with pytest.raises(SystemExit) as excinfo:
        monkeypatch.setattr(sys, 'argv', ['ocdsextensionregistry', '--help'])
        main()

    assert capsys.readouterr().out.startswith('usage: ocdsextensionregistry [-h]')

    assert len(caplog.records) == 0
    assert excinfo.value.code == 0
