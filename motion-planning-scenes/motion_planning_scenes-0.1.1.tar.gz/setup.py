# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['MotionPlanningEnv', 'MotionPlanningGoal', 'MotionPlanningSceneHelpers']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'casadi<=3.5.5',
 'geomdl>=5.3.1,<6.0.0',
 'numpy>=1.15.0,<2.0.0',
 'pytest>=6.2.5,<7.0.0']

setup_kwargs = {
    'name': 'motion-planning-scenes',
    'version': '0.1.1',
    'description': 'Generic motion planning scenes, including goals and obstacles.',
    'long_description': None,
    'author': 'Max',
    'author_email': 'm.spahn@tudelft.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
