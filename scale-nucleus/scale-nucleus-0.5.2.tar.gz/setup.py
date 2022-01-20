# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nucleus',
 'nucleus.data_transfer_object',
 'nucleus.metrics',
 'nucleus.modelci',
 'nucleus.modelci.data_transfer_objects',
 'nucleus.modelci.eval_functions']

package_data = \
{'': ['*']}

install_requires = \
['Sphinx>=4.2.0,<5.0.0',
 'aiohttp>=3.7.4,<4.0.0',
 'isort>=5.10.1,<6.0.0',
 'nest-asyncio>=1.5.1,<2.0.0',
 'numpy>=1.19.5,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'requests>=2.23.0,<3.0.0',
 'scipy>=1.5.4,<2.0.0',
 'tqdm>=4.41.0,<5.0.0']

extras_require = \
{':python_full_version >= "3.6.1" and python_version < "3.7"': ['dataclasses>=0.7,<0.8']}

setup_kwargs = {
    'name': 'scale-nucleus',
    'version': '0.5.2',
    'description': 'The official Python client library for Nucleus, the Data Platform for AI',
    'long_description': '# Nucleus\n\nhttps://dashboard.scale.com/nucleus\n\nAggregate metrics in ML are not good enough. To improve production ML, you need to understand their qualitative failure modes, fix them by gathering more data, and curate diverse scenarios.\n\nScale Nucleus helps you:\n\n- Visualize your data\n- Curate interesting slices within your dataset\n- Review and manage annotations\n- Measure and debug your model performance\n\nNucleus is a new way—the right way—to develop ML models, helping us move away from the concept of one dataset and towards a paradigm of collections of scenarios.\n\n## Installation\n\n`$ pip install scale-nucleus`\n\n## Common issues/FAQ\n\n### Outdated Client\n\nNucleus is iterating rapidly and as a result we do not always perfectly preserve backwards compatibility with older versions of the client. If you run into any unexpected error, it\'s a good idea to upgrade your version of the client by running\n```\npip install --upgrade scale-nucleus\n```\n\n## Usage\n\nFor the most up to date documentation, reference: https://dashboard.scale.com/nucleus/docs/api?language=python.\n\n## For Developers\n\nClone from github and install as editable\n\n```\ngit clone git@github.com:scaleapi/nucleus-python-client.git\ncd nucleus-python-client\npip3 install poetry\npoetry install\n```\n\nPlease install the pre-commit hooks by running the following command:\n\n```python\npoetry run pre-commit install\n```\n\nWhen releasing a new version please add release notes to the changelog in `CHANGELOG.md`.\n\n**Best practices for testing:**\n(1). Please run pytest from the root directory of the repo, i.e.\n\n```\npoetry run pytest tests/test_dataset.py\n```\n\n(2) To skip slow integration tests that have to wait for an async job to start.\n\n```\npoetry run pytest -m "not integration"\n```\n\n## Pydantic Models\n\nPrefer using [Pydantic](https://pydantic-docs.helpmanual.io/usage/models/) models rather than creating raw dictionaries \nor dataclasses to send or receive over the wire as JSONs. Pydantic is created with data validation in mind and provides very clear error \nmessages when it encounters a problem with the payload.\n\nThe Pydantic model(s) should mirror the payload to send. To represent a JSON payload that looks like this:\n```json\n{\n  "example_json_with_info": {\n      "metadata": {\n        "frame": 0\n      },\n      "reference_id": "frame0",\n      "url": "s3://example/scale_nucleus/2021/lidar/0038711321865000.json",\n      "type": "pointcloud"\n    },\n  "example_image_with_info": {\n      "metadata": {\n        "author": "Picasso"\n      },\n      "reference_id": "frame0",\n      "url": "s3://bucket/0038711321865000.jpg",\n      "type": "image"\n    },\n}\n```\n\nCould be represented as the following structure. Note that the field names map to the JSON keys and the usage of field \nvalidators (`@validator`).\n\n```python\nimport os.path\nfrom pydantic import BaseModel, validator\nfrom typing import Literal\n\n\nclass JsonWithInfo(BaseModel):\n    metadata: dict  # any dict is valid\n    reference_id: str\n    url: str\n    type: Literal["pointcloud", "recipe"]\n\n    @validator("url")\n    def has_json_extension(cls, v):\n        if not v.endswith(".json"):\n            raise ValueError(f"Expected \'.json\' extension got {v}")\n        return v\n\n\nclass ImageWithInfo(BaseModel):\n    metadata: dict  # any dict is valid\n    reference_id: str\n    url: str\n    type: Literal["image", "mask"]\n\n    @validator("url")\n    def has_valid_extension(cls, v):\n        valid_extensions = {".jpg", ".jpeg", ".png", ".tiff"}\n        _, extension = os.path.splitext(v)\n        if extension not in valid_extensions:\n            raise ValueError(f"Expected extension in {valid_extensions} got {v}")\n        return v\n\n\nclass ExampleNestedModel(BaseModel):\n    example_json_with_info: JsonWithInfo\n    example_image_with_info: ImageWithInfo\n\n# Usage:\nimport requests\npayload = requests.get("/example")\nparsed_model = ExampleNestedModel.parse_obj(payload.json())\nrequests.post("example/post_to", json=parsed_model.dict())\n```\n\n\n### Migrating to Pydantic\n- When migrating an interface from a dictionary use `nucleus.pydantic_base.DictCompatibleModel`. That allows you to get\nthe benefits of Pydantic but maintaints backwards compatibility with a Python dictionary by delegating `__getitem__` to \nfields.\n- When migrating a frozen dataclass use `nucleus.pydantic_base.ImmutableModel`. That is a base class set up to be \nimmutable after initialization.\n\n**Updating documentation:**\nWe use [Sphinx](https://www.sphinx-doc.org/en/master/) to autogenerate our API Reference from docstrings.\n\nTo test your local docstring changes, run the following commands from the repository\'s root directory:\n```\npoetry shell\ncd docs\nsphinx-autobuild . ./_build/html --watch ../nucleus\n```\n`sphinx-autobuild` will spin up a server on localhost (port 8000 by default) that will watch for and automatically rebuild a version of the API reference based on your local docstring changes.\n',
    'author': 'Scale AI Nucleus Team',
    'author_email': 'nucleusapi@scaleapi.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://scale.com/nucleus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
