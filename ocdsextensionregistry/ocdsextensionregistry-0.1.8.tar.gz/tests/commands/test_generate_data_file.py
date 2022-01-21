import json
import sys

import pytest

from ocdsextensionregistry.cli.__main__ import main
from tests import read

args = ['ocdsextensionregistry', 'generate-data-file']


def test_command(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', args + ['location==v1.1.4'])
    main()

    assert capsys.readouterr().out == read('location-v1.1.4.json')


def test_command_latest_version_master(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', args + ['location==v1.1.4', 'location==master'])
    main()

    assert json.loads(capsys.readouterr().out)['location']['latest_version'] == 'master'


def test_command_latest_version_default(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', args + ['legalBasis==1.1', 'legalBasis==1.2'])
    main()

    assert json.loads(capsys.readouterr().out)['legalBasis']['latest_version'] == '1.1'


def test_command_latest_version_dated(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', args + ['location==v1.1.5', 'location==v1.1.4'])
    main()

    assert json.loads(capsys.readouterr().out)['location']['latest_version'] == 'v1.1.5'


def test_command_missing_locale_dir(capsys, monkeypatch):
    with pytest.raises(SystemExit) as excinfo:
        monkeypatch.setattr(sys, 'argv', args + ['--languages', 'es', 'location==v1.1.4'])
        main()

    captured = capsys.readouterr()

    assert captured.out == ''
    assert '--locale-dir is required if --languages is set.' in captured.err
    assert excinfo.value.code == 2


def test_command_missing_language(capsys, monkeypatch, tmpdir):
    with pytest.raises(SystemExit) as excinfo:
        monkeypatch.setattr(sys, 'argv', args + ['--locale-dir', '.', '--languages', 'es', 'location==v1.1.4'])
        main()

    captured = capsys.readouterr()

    assert captured.out == ''
    assert 'translations to es are not available' in captured.err
    assert excinfo.value.code == 2


def test_command_locale_dir(capsys, monkeypatch, tmpdir):
    versions_dir = tmpdir.mkdir('outputdir')
    version_dir = versions_dir.mkdir('location').mkdir('v1.1.4')
    locale_dir = tmpdir.mkdir('localedir')
    for locale in ('en', 'es'):
        locale_dir.mkdir(locale)

    version_dir.join('extension.json').write_text('{"name": "Location", "description": "…"}', encoding='utf-8')
    version_dir.join('README.md').write_text('# Location', encoding='utf-8')

    monkeypatch.setattr(sys, 'argv', args + ['--versions-dir', str(versions_dir), '--locale-dir', str(locale_dir),
                                             'location==v1.1.4'])
    main()

    assert json.loads(capsys.readouterr().out) == {
        'location': {
            'id': 'location',
            'category': 'item',
            'core': True,
            'name': {
                'en': 'Location',
                'es': 'Location',
            },
            'description': {
                'en': '…',
                'es': '…',
            },
            'latest_version': 'v1.1.4',
            'versions': {
                'v1.1.4': {
                    'id': 'location',
                    'date': '2019-02-25',
                    'version': 'v1.1.4',
                    'base_url': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.4/',  # noqa: E501
                    'download_url': 'https://api.github.com/repos/open-contracting-extensions/ocds_location_extension/zipball/v1.1.4',  # noqa: E501
                    'publisher': {
                        'name': 'open-contracting-extensions',
                        'url': 'https://github.com/open-contracting-extensions',
                    },
                    'metadata': {
                        'name': {
                            'en': 'Location',
                            'es': 'Location',
                        },
                        'description': {
                            'en': '…',
                            'es': '…',
                        },
                        'documentationUrl': {},
                        'compatibility': ['1.1'],
                    },
                    'schemas': {
                        'record-package-schema.json': {},
                        'release-package-schema.json': {},
                        'release-schema.json': {},
                    },
                    'codelists': {},
                    'readme': {
                        'en': '# Location\n',
                        'es': '# Location\n',
                    },
                },
            },
        },
    }


def test_command_languages(capsys, monkeypatch, tmpdir):
    versions_dir = tmpdir.mkdir('outputdir')
    version_dir = versions_dir.mkdir('location').mkdir('v1.1.4')
    locale_dir = tmpdir.mkdir('localedir')
    for locale in ('en', 'es', 'fr'):
        locale_dir.mkdir(locale)

    version_dir.join('extension.json').write_text('{"name": "Location", "description": "…"}', encoding='utf-8')
    version_dir.join('README.md').write_text('# Location', encoding='utf-8')

    monkeypatch.setattr(sys, 'argv', args + ['--versions-dir', str(versions_dir), '--locale-dir', str(locale_dir),
                                             '--languages', 'es', 'location==v1.1.4'])
    main()

    assert json.loads(capsys.readouterr().out) == {
        'location': {
            'id': 'location',
            'category': 'item',
            'core': True,
            'name': {
                'en': 'Location',
                'es': 'Location',
            },
            'description': {
                'en': '…',
                'es': '…',
            },
            'latest_version': 'v1.1.4',
            'versions': {
                'v1.1.4': {
                    'id': 'location',
                    'date': '2019-02-25',
                    'version': 'v1.1.4',
                    'base_url': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.4/',  # noqa: E501
                    'download_url': 'https://api.github.com/repos/open-contracting-extensions/ocds_location_extension/zipball/v1.1.4',  # noqa: E501
                    'publisher': {
                        'name': 'open-contracting-extensions',
                        'url': 'https://github.com/open-contracting-extensions',
                    },
                    'metadata': {
                        'name': {
                            'en': 'Location',
                            'es': 'Location',
                        },
                        'description': {
                            'en': '…',
                            'es': '…',
                        },
                        'documentationUrl': {},
                        'compatibility': ['1.1'],
                    },
                    'schemas': {
                        'record-package-schema.json': {},
                        'release-package-schema.json': {},
                        'release-schema.json': {},
                    },
                    'codelists': {},
                    'readme': {
                        'en': '# Location\n',
                        'es': '# Location\n',
                    },
                },
            },
        },
    }
