# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scrapy_wayback_middleware']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=17.4.0', 'scrapy>=2.0,<3.0']

setup_kwargs = {
    'name': 'scrapy-wayback-middleware',
    'version': '0.3.3',
    'description': 'Scrapy middleware for submitting URLs to the Internet Archive Wayback Machine',
    'long_description': "# Scrapy Wayback Middleware\n\n[![Build status](https://github.com/pjsier/scrapy-wayback-middleware/workflows/CI/badge.svg)](https://github.com/pjsier/scrapy-wayback-middleware/actions)\n\nMiddleware for submitting all scraped response URLs to the [Internet Archive Wayback Machine](https://archive.org/web/) for archival.\n\n## Installation\n\n```bash\npip install scrapy-wayback-middleware\n```\n\n## Setup\n\nAdd `scrapy_wayback_middleware.WaybackMiddleware` to your project's `SPIDER_MIDDLEWARES` settings. By default, the middleware will make `GET` requests to `web.archive.org/save/{URL}`, but if the `WAYBACK_MIDDLEWARE_POST` setting is `True` then it will make POST requests to [`pragma.archivelab.org`](https://archive.readme.io/docs/creating-a-snapshot) instead.\n\n## Configuration\n\nTo configure custom behavior for certain methods, subclass `WaybackMiddleware` and override the `get_item_urls` method to pull additional links to archive from individual items or `handle_wayback` to change how responses from the Wayback Machine are handled. The `WAYBACK_MIDDLEWARE_POST` can be set to `True` to adjust request behavior.\n\n### Duplicate Filtering\n\nIn order to avoid sending duplicate requests with `WAYBACK_MIDDLEWARE_POST` set to `False`, you'll need to either include `web.archive.org` in your spider's `allowed_domains` property (if specified) or disable `scrapy.spidermiddlewares.offsite.OffsiteMiddleware` in your settings.\n\n### Rate Limits\n\nWhile neither endpoint returns headers indicating specific rate limits, the `GET` endpoint at `web.archive.org/save` has a rate limit of 25 requests/minute, resetting each minute. The middleware is configured to wait for 60 seconds whenever it sees a 429 error code to handle this.\n",
    'author': 'pjsier',
    'author_email': 'pjsier@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pjsier/scrapy-wayback-middleware',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
