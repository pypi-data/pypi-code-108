# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['async_stripe',
 'async_stripe.api_resources',
 'async_stripe.api_resources.abstract',
 'async_stripe.api_resources.checkout',
 'async_stripe.api_resources.identity',
 'async_stripe.api_resources.issuing']

package_data = \
{'': ['*']}

install_requires = \
['stripe==2.65.0', 'tornado>=5.1']

setup_kwargs = {
    'name': 'async-stripe',
    'version': '2.65.0',
    'description': "An asynchronous wrapper around Stripe's official python library.",
    'long_description': "# async-stripe\n\n[![Build Status](https://travis-ci.com/bhch/async-stripe.svg?branch=master)](https://travis-ci.com/bhch/async-stripe)\n\nAn asynchronous wrapper around Stripe's official python library. \n\n## How it works\n\nasync-stripe monkey-patches the stripe library and replaces the synchronous \nhttp request methods with asynchronous methods.\n\nMonkey-patching allows us to avoid a complete rewrite and keep the usage api \nsimilar to the official library.\n\nThis **doesn't use threads**, but **actual async coroutines** and \n[non-blocking http client][1] to make requests.\n\n## Install\n\nInstall requires Python 3.6 or newer.\n\n```sh\n$ pip install async-stripe\n```\n\n## Usage\n\nThe usage api is similar to Stripe's official library:\n\n```python\nfrom async_stripe import stripe\n\nstripe.api_key = '<stripe-secret-key>'\n\npayment_intent = await stripe.PaymentIntent.create(amount=1000, currency='usd')\n\nprint(payment_intent.id)\n```\n\n---\n\n**/!\\ Note:** Since this library monkey-patches the actual `stripe` library, \nyou should avoid using the two in the same process.\n\nOnce you import `async_stripe`, the official `stripe` library gets patched with \nasync methods and the original synchronous api won't be available.\n\n---\n\n## Configuration\n\nPlease see [`stripe-python`'s README][5] file for configuring logging and other things.\n\n#### Unsupported configurations:\n\n`async-stripe` aims to be a drop-in async replacement for `stripe`. However, \nthere are a few things which are not yet supported:\n\n - Custom http client: Currently, it's not possible to configure a \n custom http client and Tornado's [`AsyncHTTPClient`][1] will be used by default.\n - Proxy: Connecting to api via a proxy is not supported yet.\n\n## Development and Testing\n\nWhen adding new features and monkey-patches, please add relevant tests and \nensure that all the tests also pass. \n\nIn most cases, you shouldn't need to write the tests yourself: you can just \ncopy-paste the tests form the original stripe library and change the synchronous \nmethods to asynchronous methods. \n\nFor testing, first, [install and run the `stripe-mock` api server][2].\n\nNext, install `pytest`, `pytest-mock` and `pytest-asyncio` python packages in \nyour virtualenv.\n\nFinally, run the tests like this:\n\n```sh\n$ pytest tests\n\n# or run a specific test\n$ pytest tests/api_resources/test_customer.py\n$ pytest tests/api_resources/test_customer.py::TestCustomer\n```\n\n## License\n\nA lot of the code (especially tests) are copied with slight modifications from \nStripe's official library. That code is licensed under \n[MIT License][3].\n\nRest of the original code is licensed under [BSD-3-Clause License][4].\n\n\n[1]: https://www.tornadoweb.org/en/stable/httpclient.html#tornado.httpclient.AsyncHTTPClient\n[2]: https://github.com/stripe/stripe-mock\n[3]: LICENSE.stripe.txt\n[4]: LICENSE.txt\n[5]: https://github.com/stripe/stripe-python/blob/master/README.md",
    'author': 'Bharat Chauhan',
    'author_email': 'tell.bhch@gmail.com',
    'maintainer': 'Bharat Chauhan',
    'maintainer_email': 'tell.bhch@gmail.com',
    'url': 'https://github.com/bhch/async-stripe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
