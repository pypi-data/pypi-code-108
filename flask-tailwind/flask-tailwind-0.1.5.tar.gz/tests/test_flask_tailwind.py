#!/usr/bin/env python

"""Tests for `flask_tailwind` package."""

from click.testing import CliRunner
from flask import Flask

from flask_tailwind import Tailwind, cli


def test_extension():
    app = Flask(__name__)
    tailwind = Tailwind(app)
    assert "tailwind" in app.extensions
    assert app.extensions["tailwind"] == tailwind


def test_cli():
    runner = CliRunner()

    result = runner.invoke(cli.tailwind)
    assert result.exit_code == 0
    assert "Perform Tailwind operations" in result.output

    help_result = runner.invoke(cli.tailwind, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
    assert "init" in help_result.output
