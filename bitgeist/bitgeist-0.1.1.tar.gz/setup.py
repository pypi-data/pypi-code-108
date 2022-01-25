# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bitgeist']

package_data = \
{'': ['*'], 'bitgeist': ['resources/*']}

install_requires = \
['torch>=1.10.0,<2.0.0']

setup_kwargs = {
    'name': 'bitgeist',
    'version': '0.1.1',
    'description': 'bitgeist is a Python library to convert deep neural network models into c source code.',
    'long_description': '# bitgeist\n\nbitgeist is a Python library to convert deep neural network models into c source code.\n\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install bitgeist.\n\n```bash\npip install bitgeist\n```\n\n## Usage\n\n```python\nimport bitgeist as bg\n\n# transform a pytorch model to c code\nprint(bg.transform(model))\n\n```\n\nExample:\n\n````python\n    ...\n    class MnistModel(nn.Module):\n\n        def __init__(self, downsample=None):\n            super(MnistModel, self).__init__()\n\n            inputs = 28 * 28\n            hidden = 120\n            output = 10\n\n            self.l1 = DenseBlock(inputs, hidden, downsample=downsample)\n            self.action = nn.PReLU(hidden)\n            self.l2 = DenseBlock(hidden, output, downsample=downsample)\n\n        def forward(self, x):\n            out = self.l1(x)\n            out = self.action(out)\n            out = self.l2(out)\n            return out\n\n    model = MnistModel(nn.Dropout(0.2)).to(device)\n\n    # train the model \n    \n    ...\n    \n    print("total training time = {} hours".format(training_time))\n\n    print(bg.transform(model)) #print or write to file ...\n   ...\n````\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n## License\n\n[MIT](https://choosealicense.com/licenses/mit/)\n',
    'author': 'germar',
    'author_email': 'g.schlegel@geisten.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
