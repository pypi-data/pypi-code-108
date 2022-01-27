# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['limepkg_scrive',
 'limepkg_scrive.config',
 'limepkg_scrive.translations',
 'limepkg_scrive.web_components']

package_data = \
{'': ['*'],
 'limepkg_scrive': ['frontend/*',
                    'frontend/assets/icons/*',
                    'frontend/dist/*',
                    'frontend/dist/assets/icons/*',
                    'frontend/dist/cjs/*',
                    'frontend/dist/collection/*',
                    'frontend/dist/collection/components/lwc-limepkg-scrive-loader/*',
                    'frontend/dist/collection/components/lwc-limepkg-scrive/*',
                    'frontend/dist/esm-es5/*',
                    'frontend/dist/esm/*',
                    'frontend/dist/esm/polyfills/*',
                    'frontend/dist/limepkg-scrive-lwc-components/*',
                    'frontend/dist/loader/*',
                    'frontend/dist/types/*',
                    'frontend/dist/types/components/lwc-limepkg-scrive-loader/*',
                    'frontend/dist/types/components/lwc-limepkg-scrive/*',
                    'frontend/src/components/lwc-limepkg-scrive-loader/*',
                    'frontend/src/components/lwc-limepkg-scrive/*',
                    'frontend/src/interface.d.ts',
                    'frontend/src/interface.d.ts',
                    'frontend/src/lime-web-component-platform.browser.js',
                    'frontend/src/lime-web-component-platform.browser.js']}

install_requires = \
['lime-crm>=2.76.0,<3.0.0']

entry_points = \
{'lime_plugins': ['limepkg-scrive = limepkg_scrive']}

setup_kwargs = {
    'name': 'limepkg-scrive',
    'version': '2.0.1',
    'description': 'Scrive eSigning',
    'long_description': None,
    'author': 'Scrive AB',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.3,<3.8.0',
}


setup(**setup_kwargs)
