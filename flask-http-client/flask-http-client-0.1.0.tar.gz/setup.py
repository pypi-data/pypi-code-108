# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_http_client']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=1.0.0', 'requests>=2.0.0']

setup_kwargs = {
    'name': 'flask-http-client',
    'version': '0.1.0',
    'description': '',
    'long_description': "HTTP client extension for Flask.\n===========================================\n\n对requests库的包装，在flask配置文件中配置base_url, auth, 转发user-agent等。第一次访问网址生成全局的session, 本次request结束后， 关闭此session。\n\n\n安装\n------\n\n.. code-block:: sh\n\n    pip install flask-http-client\n\n使用\n------\n\n\nFirst init::\n\n    from flask_http_client import HTTPClient\n    http_client = HTTPClient()\n    http_client.init_app(app)\n\nAPI\n----\n\n和requests的API一致，需要注意的是 url = base_url + path，所以base_url和path需要自己做好处理。\n\n.. code-block::\n\n    params = {}\n    resp = http_client.request('GET', '/users/', params=params)\n    resp = http_client.get('/users', params=params)\n\n\n配置项\n------\n\n可以在构造方法修改配置前缀，默认为 HTTP_CLIENT\n\n.. code-block:: py\n\n    http_client = HttpClient(config_prefix='YOUR_CONFIG_PREFIX')\n\n\n=====================   ================================================\n配置项                      说明\n=====================   ================================================\nHTTP_CLIENT_BASE_URL    api的url_prefix\nHTTP_CLIENT_AUTH        requests中的auth参数\n=====================   ================================================\n",
    'author': 'codeif',
    'author_email': 'me@codeif.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
