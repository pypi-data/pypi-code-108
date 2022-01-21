import sys

from ocdsextensionregistry.cli.__main__ import main

args = ['ocdsextensionregistry']


def test_command(capsys, monkeypatch, tmpdir):
    monkeypatch.setattr(sys, 'argv', args)
    main()

    assert 'usage: ocdsextensionregistry' in capsys.readouterr().out
