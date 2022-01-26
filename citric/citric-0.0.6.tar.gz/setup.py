# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['citric']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.23.0,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=1.6,<5.0'],
 'docs': ['sphinx==4.4.0',
          'sphinx-autodoc-typehints==1.12.0',
          'sphinx-autoapi==1.8.4',
          'myst-parser==0.16.1',
          'furo==2022.1.2']}

setup_kwargs = {
    'name': 'citric',
    'version': '0.0.6',
    'description': 'A client to the LimeSurvey Remote Control API 2, written in modern Python.',
    'long_description': '# Citric\n\n[![Tests][tests-badge]][tests-link]\n[![Documentation Status][docs-badge]][docs-link]\n[![Updates][updates-badge]][updates-link]\n[![codecov][codecov-badge]][codecov-link]\n[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric?ref=badge_shield)\n[![PyPI version][pypi-badge]][pypi-link]\n[![Python versions][versions-badge]][pypi-link]\n[![PyPI - Downloads][downloads-badge]][pypi-link]\n\nA client to the LimeSurvey Remote Control API 2, written in modern\nPython.\n\n## Installation\n\n```console\n$ pip install citric\n```\n\n## Usage\n\nFor the full JSON-RPC reference, see the [RemoteControl 2 API docs][rc2api].\n\n### Get surveys and questions\n\n```python\nfrom citric import Client\n\nLS_URL = "http://localhost:8001/index.php/admin/remotecontrol"\n\nwith Client(LS_URL, "iamadmin", "secret") as client:\n    # Get all surveys from user "iamadmin"\n    surveys = client.list_surveys("iamadmin")\n\n    for s in surveys:\n        print(s["surveyls_title"])\n\n        # Get all questions, regardless of group\n        questions = client.list_questions(s["sid"])\n        for q in questions:\n            print(q["title"], q["question"])\n```\n\n### Export responses to a `pandas` dataframe\n\n```python\nimport io\nimport pandas as pd\n\nsurvey_id = 123456\n\ndf = pd.read_csv(\n    io.BytesIO(client.export_responses(survey_id, file_format="csv")),\n    delimiter=";",\n    parse_dates=["datestamp", "startdate", "submitdate"],\n    index_col="id",\n)\n```\n\n### Custom `requests` session\n\nIt\'s possible to use a custom session object to make requests. For example, to cache the requests\nand reduce the load on your server in read-intensive applications, you can use\n[`requests-cache`](https://requests-cache.readthedocs.io):\n\n```python\nimport requests_cache\n\ncached_session = requests_cache.CachedSession(\n    expire_after=3600,\n    allowable_methods=["POST"],\n)\n\nwith Client(\n    LS_URL,\n    "iamadmin",\n    "secret",\n    requests_session=cached_session,\n) as client:\n\n    # Get all surveys from user "iamadmin"\n    surveys = client.list_surveys("iamadmin")\n\n    # This should hit the cache. Running the method in a new client context will\n    # not hit the cache because the RPC session key would be different.\n    surveys = client.list_surveys("iamadmin")\n```\n\n### Use a different authentication plugin\n\nBy default, this client uses the internal database for authentication but\n[arbitrary plugins](https://manual.limesurvey.org/Authentication_plugins) are supported by the\n`auth_plugin` argument.\n\n```python\nwith Client(\n    LS_URL,\n    "iamadmin",\n    "secret",\n    auth_plugin="AuthLDAP",\n) as client:\n    ...\n```\n\nCommon plugins are `Authdb` (default), `AuthLDAP` and `Authwebserver`.\n\n### Get uploaded files and move them to S3\n\n```python\nimport base64\nimport io\n\nimport boto3\nfrom citric import Client\n\ns3 = boto3.client("s3")\n\nwith Client(\n    "https://mylimeserver.com/index.php/admin/remotecontrol",\n    "iamadmin",\n    "secret",\n) as client:\n    survey_id = 12345\n    files = client.get_uploaded_files(survey_id)\n    for file in files:\n        content = base64.b64decode(files[file]["content"])  # Decode content\n        question_id = files[file]["meta"]["question"]["qid"]\n        s3.upload_fileobj(\n            io.BytesIO(content),\n            "my-s3-bucket",\n            f"uploads/{survey_id}/{question_id}/{file}",\n        )\n```\n\n## Development\n\nUse pyenv to setup default Python versions for this repo:\n\n```shell\npyenv local 3.10.0 3.9.7 3.8.11 3.7.11 3.6.14\n```\n\nInstall project dependencies\n\n```shell\npoetry install\n```\n\n### Docs\n\nTo generate the documentation site, use the following commands:\n\n```shell\npoetry install -E docs\npoetry run sphinx-build docs build\n```\n\n### Docker\n\nYou can setup a local instance of LimeSurvey with [Docker Compose](https://docs.docker.com/compose/):\n\n```shell\ndocker-compose up -d\n```\n\nNow you can access LimeSurvey at [port 8001](http://localhost:8001/index.php/admin).\n\nImport an existing survey file and start testing with it:\n\n```python\nfrom citric import Client\n\nLS_URL = "http://localhost:8001/index.php/admin/remotecontrol"\n\nwith Client(LS_URL, "iamadmin", "secret") as client:\n    # Import survey from a file\n    with open("examples/limesurvey_survey_432535.lss", "rb") as f:\n        survey_id = client.import_survey(f, "lss")\n    print("New survey:", survey_id)\n```\n\n### Testing\n\nThis project uses [`nox`][nox] for running tests and linting on different Python versions:\n\n```shell\npip install --user --upgrade nox\nnox -r\n```\n\nRun only a linting session\n\n```shell\nnox -rs lint\n```\n\n### pre-commit\n\n```shell\npip install --user --upgrade pre-commit\npre-commit install\n```\n\n### Releasing an upgrade\n\nBump the package version\n\n```shell\npoetry version <version>\npoetry publish\n```\n\n## Credits\n\n- [Claudio Jolowicz][claudio] and [his amazing blog post][hypermodern].\n\n[rc2api]: https://api.limesurvey.org/classes/remotecontrol_handle.html\n[nox]: https://nox.thea.codes/en/stable/\n[claudio]: https://twitter.com/cjolowicz/\n[hypermodern]: https://cjolowicz.github.io/posts/hypermodern-python-01-setup/\n\n<!--Badges-->\n[docs-badge]: https://readthedocs.org/projects/citric/badge/?version=latest\n[docs-link]: https://citric.readthedocs.io/en/latest/?badge=latest\n[updates-badge]: https://pyup.io/repos/github/edgarrmondragon/citric/shield.svg\n[updates-link]: https://pyup.io/repos/github/edgarrmondragon/citric/\n[codecov-badge]: https://codecov.io/gh/edgarrmondragon/citric/branch/master/graph/badge.svg\n[codecov-link]: https://codecov.io/gh/edgarrmondragon/citric\n[tests-badge]: https://github.com/edgarrmondragon/citric/workflows/Tests/badge.svg\n[tests-link]: https://github.com/edgarrmondragon/citric/actions?workflow=Tests\n[pypi-badge]: https://img.shields.io/pypi/v/citric.svg?color=blue\n[versions-badge]: https://img.shields.io/pypi/pyversions/citric.svg\n[downloads-badge]: https://img.shields.io/pypi/dm/citric?color=blue\n[pypi-link]: https://pypi.org/project/citric\n\n\n## License\n[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fedgarrmondragon%2Fcitric?ref=badge_large)\n',
    'author': 'Edgar Ramírez-Mondragón',
    'author_email': 'edgarrm358@gmail.com',
    'maintainer': 'Edgar Ramírez-Mondragón',
    'maintainer_email': 'edgarrm358@gmail.com',
    'url': 'https://github.com/edgarrmondragon/citric',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<3.11',
}


setup(**setup_kwargs)
