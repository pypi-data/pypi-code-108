# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_grpc']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=1.0.0', 'grpcio>=1.0.0', 'protobuf>3.0.0']

setup_kwargs = {
    'name': 'flask-grpc',
    'version': '0.1.1',
    'description': 'A grpc client for Flask.',
    'long_description': 'flask-grpc\n====================\n\nA grpc client for Flask.\n\nUsage\n-------\n\ninit\n\n.. code-block:: python\n\n    channel_wrapper = ChannelWrapper(\n        target="gaea-partner-python-grpc-dev-cuwmnyhgmq-uc.a.run.app:443",\n        secure=True,\n        credentials=grpc.ssl_channel_credentials(),\n    )\n    channel_wrapper.init_app(app)\n\n    health_stub = StubWrapper(health_pb2_grpc.HealthStub, channel_wrapper)\n\nviews\n\n.. code-block:: python\n\n    @app.route("/grpc")\n    def grpc_api():\n        reply = health_stub.Check(health_pb2.HealthCheckRequest())\n        return f"grpc response: {reply}"\n',
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
