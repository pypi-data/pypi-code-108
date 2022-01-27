# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_httpserver']

package_data = \
{'': ['*']}

install_requires = \
['Werkzeug>=2.0.0']

extras_require = \
{'dev': ['flake8>4.0.0',
         'pytest',
         'pytest-cov',
         'coverage',
         'ipdb',
         'requests',
         'sphinx',
         'sphinx_rtd_theme',
         'reno',
         'autopep8',
         'mypy',
         'types-requests'],
 'doc': ['sphinx', 'sphinx_rtd_theme', 'reno'],
 'test': ['flake8>4.0.0',
          'pytest',
          'pytest-cov',
          'coverage',
          'requests',
          'mypy',
          'types-requests']}

entry_points = \
{'pytest11': ['pytest_httpserver = pytest_httpserver.pytest_plugin']}

setup_kwargs = {
    'name': 'pytest-httpserver',
    'version': '1.0.4',
    'description': 'pytest-httpserver is a httpserver for pytest',
    'long_description': '[![Build Status](https://github.com/csernazs/pytest-httpserver/workflows/build/badge.svg?branch=master)](https://github.com/csernazs/pytest-httpserver/actions?query=workflow%3Abuild+branch%3Amaster)\n[![Documentation Status](https://readthedocs.org/projects/pytest-httpserver/badge/?version=latest)](https://pytest-httpserver.readthedocs.io/en/latest/?badge=latest)\n [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)\n[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=K6PU3AGBZW4QC&item_name=pytest-httpserver&currency_code=EUR&source=url)\n[![codecov](https://codecov.io/gh/csernazs/pytest-httpserver/branch/master/graph/badge.svg?token=MX2JXbHqRH)](https://codecov.io/gh/csernazs/pytest-httpserver)\n\n## pytest_httpserver\n\nHTTP server for pytest\n\n\n### Nutshell\n\nThis library is designed to help to test http clients without contacting the real http server.\nIn other words, it is a fake http server which is accessible via localhost can be started with\nthe pre-defined expected http requests and their responses.\n\n### Example\n\n#### Handling a simple GET request\n```python\ndef test_my_client(httpserver): # httpserver is a pytest fixture which starts the server\n    # set up the server to serve /foobar with the json\n    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})\n    # check that the request is served\n    assert requests.get(httpserver.url_for("/foobar")).json() == {\'foo\': \'bar\'}\n```\n\n#### Handing a POST request with an expected json body\n```python\ndef test_json_request(httpserver): # httpserver is a pytest fixture which starts the server\n    # set up the server to serve /foobar with the json\n    httpserver.expect_request("/foobar", method="POST", json={"id": 12, "name": "foo"}).respond_with_json({"foo": "bar"})\n    # check that the request is served\n    assert requests.post(httpserver.url_for("/foobar"), json={"id": 12, "name": "foo"}).json() == {\'foo\': \'bar\'}\n```\n\n\nYou can also use the library without pytest. There\'s a with statement to ensure that the server is stopped.\n\n\n```python\nwith HTTPServer() as httpserver:\n    # set up the server to serve /foobar with the json\n    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})\n    # check that the request is served\n    print(requests.get(httpserver.url_for("/foobar")).json())\n```\n\n### Documentation\n\nPlease find the API documentation at https://pytest-httpserver.readthedocs.io/en/latest/.\n\n### Features\n\nYou can set up a dozen of expectations for the requests, and also what response should be sent by the server to the client.\n\n\n#### Requests\n\nThere are three different types:\n\n- **permanent**: this will be always served when there\'s match for this request, you can make as many HTTP requests as you want\n- **oneshot**: this will be served only once when there\'s a match for this request, you can only make 1 HTTP request\n- **ordered**: same as oneshot but the order must be strictly matched to the order of setting up\n\nYou can also fine-tune the expected request. The following can be specified:\n\n- URI (this is a must)\n- HTTP method\n- headers\n- query string\n- data (HTTP body of the request)\n- JSON (HTTP body loaded as JSON)\n\n\n#### Responses\n\nOnce you have the expectations for the request set up, you should also define the response you want to send back.\nThe following is supported currently:\n\n- respond arbitrary data (string or bytearray)\n- respond a json (a python dict converted in-place to json)\n- respond a Response object of werkzeug\n- use your own function\n\nSimilar to requests, you can fine-tune what response you want to send:\n\n- HTTP status\n- headers\n- data\n\n\n### Missing features\n* HTTP/2\n* Keepalive\n* ~~TLS~~\n\n### Donation\n\nIf you want to donate to this project, you can find the donate button at the top\nof the README.\n\nCurrently, this project is based heavily on werkzeug. Werkzeug does all the heavy lifting\nbehind the scenes, parsing HTTP request and defining Request and Response objects, which\nare currently transparent in the API.\n\nIf you wish to donate, please consider donating to them: https://palletsprojects.com/donate\n',
    'author': 'Zsolt Cserna',
    'author_email': 'cserna.zsolt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/csernazs/pytest-httpserver',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
