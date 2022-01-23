# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['djstripe',
 'djstripe.management',
 'djstripe.management.commands',
 'djstripe.migrations',
 'djstripe.models']

package_data = \
{'': ['*'],
 'djstripe': ['locale/fr/LC_MESSAGES/*',
              'locale/ru/LC_MESSAGES/*',
              'templates/djstripe/admin/*',
              'templates/djstripe/admin/webhook_endpoint/*']}

install_requires = \
['django>=3.2.5', 'jsonfield>=3.0', 'stripe>=2.48.0']

extras_require = \
{'docs': ['mkdocs>=1.1.2,<2.0.0',
          'mkdocstrings>=0.16.0,<0.17.0',
          'mkdocs-material>=7.2.8,<8.0.0',
          'mkdocs-autorefs>=0.3.0,<0.4.0',
          'mike>=1.1.2,<2.0.0']}

setup_kwargs = {
    'name': 'dj-stripe',
    'version': '2.7.0a1',
    'description': 'Django + Stripe made easy',
    'long_description': '# dj-stripe - Django + Stripe Made Easy\n\n[![Stripe Verified Partner](https://img.shields.io/static/v1?label=Stripe&message=Verified%20Partner&color=red&style=for-the-badge)](https://stripe.com/docs/libraries#community-libraries)\n<br>\n\n[![CI tests](https://github.com/dj-stripe/dj-stripe/actions/workflows/ci.yml/badge.svg)](https://github.com/dj-stripe/dj-stripe/actions/workflows/ci.yml)\n[![Package Downloads](https://img.shields.io/pypi/dm/dj-stripe)](https://pypi.org/project/dj-stripe/)\n[![Documentation](https://img.shields.io/static/v1?label=Docs&message=READ&color=informational&style=plastic)](https://dj-stripe.github.io/dj-stripe/)\n[![Sponsor dj-stripe](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=red&style=plastic)](https://github.com/sponsors/dj-stripe)\n[![MIT License](https://img.shields.io/static/v1?label=License&message=MIT&color=informational&style=plastic)](https://github.com/sponsors/dj-stripe)\n\nStripe Models for Django.\n\n## Introduction\n\ndj-stripe implements all of the Stripe models, for Django. Set up your\nwebhook endpoint and start receiving model updates. You will then have\na copy of all the Stripe models available in Django models, as soon as\nthey are updated!\n\nThe full documentation is available [on Read the Docs](https://dj-stripe.github.io/dj-stripe/).\n\n## Features\n\n-   Stripe Core\n-   Stripe Billing\n-   Stripe Cards (JS v2) and Sources (JS v3)\n-   Payment Methods and Payment Intents (SCA support)\n-   Support for multiple accounts and API keys\n-   Stripe Connect (partial support)\n-   Tested with Stripe API `2020-08-27` (see [API versions](api_versions.md#dj-stripe_latest_tested_version))\n\n## Requirements\n\n-   Django 3.2.5+\n-   Python 3.7+\n-   PostgreSQL engine (recommended) 9.6+\n-   MySQL engine: MariaDB 10.2+ or MySQL 5.7+\n-   SQLite: Not recommended in production. Version 3.26+ required.\n\n--8<-- "docs/installation.md"\n\n## Changelog\n\n[See release notes on Read the Docs](https://dj-stripe.github.io/dj-stripe/history/2_5_0/).\n\n## Funding and Support\n\n[![Stripe Logo](./logos/stripe_blurple.svg)](https://stripe.com)\n\nYou can now become a sponsor to dj-stripe with [GitHub Sponsors](https://github.com/sponsors/dj-stripe).\n\nWe\'ve been bringing dj-stripe to the world for over 7 years and are excited to be able to start\ndedicating some real resources to the project.\n\nYour sponsorship helps us keep a team of maintainers actively working to improve dj-stripe and\nensure it stays up-to-date with the latest Stripe changes. If you use dj-stripe commercially, we would encourage you to invest in its continued\ndevelopment by [signing up for a paid plan](https://github.com/sponsors/dj-stripe).\nCorporate sponsors [receive priority support and development time](project/support.md).\n\nAll contributions through GitHub sponsors flow into our [Open Collective](https://opencollective.com/dj-stripe), which holds our funds and keeps\nan open ledger on how donations are spent.\n\n## Our Gold sponsors\n\n<style>\nimg[alt="Stripe Logo"] {\n    max-width: 250px;\n}\n</style>\n\n[![Stripe Logo](./logos/stripe_blurple.svg)](https://stripe.com)\n\n## Similar libraries\n\n-   [dj-paypal](https://github.com/HearthSim/dj-paypal)\n    ([PayPal](https://www.paypal.com/))\n-   [dj-paddle](https://github.com/paddle-python/dj-paddle)\n    ([Paddle](https://paddle.com/))\n',
    'author': 'Alexander Kavanaugh',
    'author_email': 'alex@kavdev.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/dj-stripe/dj-stripe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.12,<4.0.0',
}


setup(**setup_kwargs)
