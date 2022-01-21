# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['uuidtools']
install_requires = \
['uuid>=1.30,<2.0']

setup_kwargs = {
    'name': 'uuidtools',
    'version': '0.1.0',
    'description': 'Utility for find, extract, exchange and permutate uuids in string and pandas series',
    'long_description': '\n# UUIDTools\n\nUUIDTools is a tiny toolkit for working with uuids inside pandas dataframes or series,\nthis toolkit will help you to extract uuids from string (normalized and not normalized) databases,\nand also permutate the ids into new ones preserving all the relations between diffrent tables.\n\n## Requierments:\n\nPython 3\nuuid\n\n## Installation:\n\n> pip install UUIDTools\n\n## Usage and use case: \n\nThe usecase of this tool is mainly to copy SQL based tables with relations,\nhaving two tables that you want to copy and export or reinsert but with different ids:\n\n| ID                                   | parent ID                            |\n|--------------------------------------|--------------------------------------|\n| 2d452c66-7ede-403e-8b72-fe02d8bd24ed | d009237f-1899-421a-b2d1-21fa3f7c3103 |\n| 2d452c66-7ede-403e-8b72-fe02d8bd24ed | edb66645-fef8-4359-b0e8-097868ed0747 |\n| 9d044ff0-1c81-4bb8-b15b-33e60abfcc9c | f22fd493-fcd5-46ac-9014-3a4b1a96b4f2 |\n\n\n| ID (Parent)                          | Name     |\n|--------------------------------------|----------|\n| d009237f-1899-421a-b2d1-21fa3f7c3103 | Person 1 |\n| edb66645-fef8-4359-b0e8-097868ed0747 | Person 2 |\n| f22fd493-fcd5-46ac-9014-3a4b1a96b4f2 | Person 3 |\n\n\nIf you need to generate new ids but you want to preserve the relations you can not\ngenerate new random ids, this library will use the previous id as a seed for the next id generation\n\n| IDs                                                                                                   |\n|-------------------------------------------------------------------------------------------------------|\n| d009237f-1899-421a-b2d1-21fa3f7c3103, something that is not id, d009237f-1899-421a-b2d1-21fa3f7c3103  |\n| d980ce44-c8c3-4eb6-8e4c-1dbaed891c21                                                                  |\n| f22fd493-fcd5-46ac-9014-3a4b1a96b4f2, d4b8fb9f-c048-4a60-8860-9b0edff0d838, bla bla                   |\n\nUsing this tool you can easily get the uuids contained:\n\n| IDs                                                                        |\n| {d009237f-1899-421a-b2d1-21fa3f7c3103}                                     |\n| {d980ce44-c83c-4eb6-8e4c-1dbaed891c21}                                     |\n| {f22fd493-fcd5-46ac-9014-3a4b1a96b4f2,d980ce44-c8c3-4eb6-8e4c-1dbaed891c21}|\n\nWhich is the set of the uuids above.\n\n\n',
    'author': 'Pablo Ruiz',
    'author_email': 'pablo.ruiz@imogate.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
