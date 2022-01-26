# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mongoengine_softdelete']

package_data = \
{'': ['*']}

install_requires = \
['mongoengine>=0.16.3', 'pymongo>=3.6.1']

setup_kwargs = {
    'name': 'mongoengine-softdelete',
    'version': '0.0.5',
    'description': 'Soft delete for MongoEngine',
    'long_description': '[![CircleCI](https://circleci.com/gh/dolead/mongoengine-softdelete.svg?style=shield)](https://app.circleci.com/pipelines/github/dolead/mongoengine-softdelete) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/6d09806a72f44b65aeb72cbbafa9c986)](https://www.codacy.com/gh/dolead/mongoengine-softdelete/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dolead/mongoengine-softdelete&amp;utm_campaign=Badge_Grade)\n\n# MongoEngine Soft Delete\n\nMake a document soft deletable.\n\n## Installation\n\nInstall `mongoengine-softdelete` through pip as usual:\n\n    pip install mongoengine-softdelete\n\n## Usage\n\nHere is an example on how to use a soft deletable document:\n\n    from mongoengine_softdelete.document import SoftDeleteNoCacheDocument    \n\n    class IceCream(SoftDeleteNoCacheDocument):\n        meta = {\n            \'collection\': \'ice_cream\',\n            \'soft_delete\': {\'deleted\': True},\n            \'indexes\': [ \'flavor\' ],\n            \'strict\': False\n        }\n\n        flavor = fields.StringField(required=True)\n        color = fields.StringField(required=True)\n        price = fields.FloatField(default=0)\n        created_at = fields.DateTimeField()\n\n        # Declare the field used to check if the record is soft deleted\n        # this field must also be reported in the `meta[\'soft_delete\']` dict\n        deleted = fields.BooleanField(default=False)\n\n    # Save a new document\n    ice = IceCream(flavor="Vanilla", color="White").save()\n    assert not ice.is_soft_deleted\n\n    # Mark the document as soft deleted\n    ice.soft_delete()\n    assert len(IceCream.objects()) == 0\n    assert ice.is_soft_deleted\n\n    # Soft undelete the document\n    ice.soft_undelete()\n    assert len(IceCream.objects()) > 0\n    assert not ice.is_soft_deleted\n\n## Tests\n\nThe test suit requires that you run a local instance of MongoDB on the standard\nport and have `pytest` installed.  \nYou can run tests with the `pytest` command or with `make test`.\n\nLinting is done with `mypy` and `pycodestyle` with the `make lint` command.\n',
    'author': 'Benjamin Hirschfield',
    'author_email': 'benjamin.hirschfield@dolead.com',
    'maintainer': 'Benjamin Hirschfield',
    'maintainer_email': 'benjamin.hirschfield@dolead.com',
    'url': 'https://github.com/dolead/mongoengine-softdelete',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
