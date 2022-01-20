# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyramid_cloudflare_access', 'pyramid_cloudflare_access.tests']

package_data = \
{'': ['*']}

install_requires = \
['cryptography', 'pyjwt', 'pyramid>=1.7']

setup_kwargs = {
    'name': 'pyramid-cloudflare-access',
    'version': '1.0.0',
    'description': 'A bunch of helpers for successfully running Pyramid on Heroku.',
    'long_description': 'pyramid_cloudflare_access\n=========================\n\nIntroduction\n------------\n\n\nInstallation\n------------\n\nJust do\n\n``pip install pyramid_cloudflare_access``\n\nor\n\n``easy_install pyramid_cloudflare_access``\n\n\nCompatibility\n-------------\n\npyramid_cloudflare_access runs with pyramid>=1.7 and python>=3.6.\nOther versions might also work.\n\n\nUsage\n-----\n\nAdd Cloudfalre config to a production.ini::\n\n    pyramid_cloudflare_access.policy_audience = "my_audience"\n    pyramid_cloudflare_access.team = "https://team.cloudfare-access.com"\n\n\nMore information can be found at https://developers.cloudflare.com/cloudflare-one/identity/users/validating-json#python-example\n\nUsage example for the tween::\n\n    def main(global_config, **settings):\n        config = Configurator(settings=settings)\n        config.include(\'pyramid_cloudflare_access\')\n        return config.make_wsgi_app()\n\n\nReleasing\n---------\n\n#. Update CHANGES.rst.\n#. Update pyproject.toml version.\n#. Run ``poetry check``.\n#. Run ``poetry publish --build``.\n\n\nWe\'re hiring!\n-------------\n\nAt Niteo we regularly contribute back to the Open Source community. If you do too, we\'d like to invite you to `join our team\n<https://niteo.co/careers/>`_!\n',
    'author': 'Niteo',
    'author_email': 'info@niteo.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/teamniteo/pyramid_cloudflare_access',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
