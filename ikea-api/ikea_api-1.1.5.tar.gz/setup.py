# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ikea_api',
 'ikea_api._endpoints',
 'ikea_api.wrappers',
 'ikea_api.wrappers._parsers']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

extras_require = \
{':python_version < "3.9"': ['typing-extensions>=4.0.0,<5.0.0'],
 'test': ['pytest==6.2.5',
          'pytest-cov==3.0.0',
          'pytest-randomly==3.11.0',
          'responses==0.17.0'],
 'wrappers': ['pydantic>=1.8.2,<2.0.0']}

setup_kwargs = {
    'name': 'ikea-api',
    'version': '1.1.5',
    'description': "Client for several IKEA's APIs",
    'long_description': 'Client for several IKEA APIs.\n\n[![Test](https://github.com/vrslev/ikea-api-client/actions/workflows/test.yml/badge.svg)](https://github.com/vrslev/ikea-api-client/actions/workflows/test.yml)\n[![Coverage](https://codecov.io/gh/vrslev/ikea-api-client/branch/main/graph/badge.svg?token=Z1G75NBIC0)](https://codecov.io/gh/vrslev/ikea-api-client)\n[![Version](https://img.shields.io/github/v/release/vrslev/ikea-api-client?label=Version)](https://github.com/vrslev/ikea-api-client/releases/latest)\n[![Python](https://img.shields.io/pypi/pyversions/ikea_api?label=Python)](https://pypi.org/project/ikea_api)\n[![Downloads](https://img.shields.io/pypi/dm/ikea_api?label=Downloads)](https://pypi.org/project/ikea_api)\n[![License](https://img.shields.io/pypi/l/ikea_api?label=License)](https://github.com/vrslev/ikea-api-client/blob/main/LICENSE)\n\n# Features\n\nWith this library you can access the following IKEA\'s APIs:\n\n- Cart,\n- Delivery Services (actually, Order Capture),\n- Purchases (history and order info),\n- Items info (3 different services),\n- Search.\n\nAlso:\n\n- Fully typed and tested,\n- Has wrappers around most of APIs based on Pydantic.\n\n# Installation\n\n```bash\npip install ikea_api\n```\n\nIf you intend to use wrappers:\n\n```bash\npip install "ikea_api[wrappers]"\n```\n\n# Usage\n\n`IKEA` object unites all available the APIs that are in this package. This is done to share token, country and language.\n\n```python\nfrom ikea_api import IKEA\n\nikea = IKEA(token=None, country_code="ru", language_code="ru")\n```\n\n## Endpoints reference\n\n### 🔑 [Authorization](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/auth.py)\n\nFirst time you open IKEA.com, guest token is being generated and stored in cookies. Same thing must be done in here before using any endpoint.\n\nThis token expires in 30 days.\n\n```python\nikea.login_as_guest()\n```\n\nIt is stored in `token` property:\n\n```python\nikea.token  # Outputs JWT token\n```\n\nPreviously you could login as user (with login and password), but now there\'s very advanced telemetry that I wouldn\'t be able to solve in hundred years 🤪\n\n### 🛒 [Cart](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/cart.py)\n\nWith this endpoint you can do everything you can using IKEA\'s frontend:\n\n- Show the cart\n\n```python\nikea.cart.show()\n```\n\n- Clear it\n\n```python\nikea.cart.clear()\n```\n\n- Add, update and delete items\n\n```python\nikea.cart.add_items({"30457903": 1})  # { item_code: quantity }\n\nikea.cart.update_items({"30457903": 5})\n\nikea.cart.remove_items(["30457903"])\n```\n\n- Set and clear coupon\n\n```python\nikea.cart.set_coupon(...)\n\nikea.cart.clear_coupon()\n```\n\n- and even copy another user\'s cart.\n\n```python\nikea.cart.copy_items(source_user_id=...)\n```\n\nIf you use authorized token (copy-paste from cookies), than you edit your user\'s actual cart.\n\n> 💡\xa0There\'s wrapper that clears current cart and adds items with error handling: if requested item doesn\'t exist, the function just skips it and tries again.\n>\n> ```python\n> from ikea_api.wrappers import add_items_to_cart\n>\n> add_items_to_cart(  # Function returns items that can\'t be added. In this case: [\'11111111\']\n>     ikea,\n>     items={\n>         "30457903": 1,\n>         "11111111": 2,  # invalid item that will be skipped\n>     },\n> )\n> ```\n\n### 🚛 [Order Capture](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/order_capture.py)\n\nCheck pickup or delivery availability. If you need to know whether items are available _in stores_, check out [ikea-availability-checker](https://github.com/Ephigenia/ikea-availability-checker).\n\n```python\norder = ikea.order_capture(\n    zip_code="02215",\n    state_code="MA",  # pass State Code only if your country has them\n)\nhome_delivery_services = order.get_home_delivery_services()\ncollect_delivery_services = order.get_collect_delivery_services()\n```\n\n> 💡\xa0You can use wrapper to add items to cart (clearing cart before and handling unknown item errors if they appear) and parse response in nice Pydantic models:\n>\n> ```python\n> from ikea_api.wrappers import get_delivery_services\n>\n> res = get_delivery_services(\n>    ikea,\n>    items={\n>        "30457903": 1,\n>        "11111111": 2,  # invalid item that will be skipped\n>    },\n>    zip_code="101000",\n> )\n> res.delivery_options  # List of parsed delivery services\n> res.cannot_add  # [\'11111111\']\n> ```\n\n### 📦 [Purchases](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/purchases.py)\n\n#### History\n\nThis method requires authentication, so if you don\'t have authorized token, it won\'t work.\n\n```python\nikea.purchases.history()\n\n# Get all purchases:\nikea.purchases.history(take=10000)\n\n# Pagination:\nikea.purchases.history(take=10, skip=1)\n```\n\n> 💡 Get parsed response with the wrapper:\n>\n> ```python\n> from ikea_api.wrappers import get_purchase_history\n>\n> get_purchase_history(ikea)  # Returns list of parsed purchases\n> ```\n\n#### Order info\n\n```python\nikea.purchases.order_info(order_number=..., email=...)\n\n# If you have authorized token, you can drop email:\nikea.purchases.order_info(order_number="111111111")\n\n# The method also has other params but they\'re mostly internal:\nikea.purchases.order_info(\n    order_number=...,\n    email=...,\n    queries=...,  # Queries that will be included in request, combine any of: ["StatusBannerOrder", "CostsOrder", "ProductListOrder"]. By default, all of them are included.\n    # Params below are relevant to ProductListOrder\n    skip_products=...,\n    skip_product_prices=...,\n    take_products=...,\n)\n```\n\n> 💡 Get parsed response with the wrapper:\n>\n> ```python\n> from ikea_api.wrappers import get_purchase_info\n>\n> get_purchase_info(  # Returns parsed purchase object. Items are not listed.\n>    ikea,\n>    id=...,\n>    email=...,\n> )\n> ```\n\n### 🪑 Item info\n\nGet item specification by item code (product number or whatever). There are 3 endpoints to do this because you can\'t get all the data about all the items using only one endpoint.\n\n```python\nfrom ikea_api import IowsItems, IngkaItems, PipItem\n\nitem_code = "30457903"\nitem_codes = [item_code]\n\n# <=90 items at a time\nIowsItems()([item_codes])\n\n# <=50 items at a time\nIngkaItems()([item_codes])\n\n# 1 item at a time\nPipItem()(item_code)\n```\n\n> 💡 You probably won\'t want to use raw APIs when there\'s convenient "smart" wrapper that combines them all and parses basic info:\n>\n> ```python\n> from ikea_api.wrappers import get_items\n>\n> get_items(["30457903"])\n> ```\n\n### 🔎 [Search](https://github.com/vrslev/ikea-api-client/blob/main/src/ikea_api/_endpoints/search.py)\n\nSearch for products in the product catalog by product name. Optionally also specify a maximum amount of returned search results (defaults to 24) and types of required search results.\n\n```python\nikea.search("Billy")\n\n# Retrieve 10 search results (default is 24)\nikea.search("Billy", limit=10)\n\n# Configure search results types\nikea.search(\n    "Billy",\n    types=...,  # Combine any of: ["PRODUCT", "CONTENT", "PLANNER", "REFINED_SEARCHES", "ANSWER"]\n)\n```\n\n### Utilities\n\n#### Parse item codes\n\nParse item codes from string or list.\n\n```python\nfrom ikea_api import parse_item_codes\n\nassert parse_item_codes("111.111.11") == ["11111111"]\nassert parse_item_codes("11111111, 222.222.22") == ["11111111", "22222222"]\nassert parse_item_codes("111") == []\n```\n\n#### Format item code\n\nParse item code and format it.\n\n```python\nfrom ikea_api import format_item_code\n\nassert format_item_code("11111111") == "111.111.11"\nassert format_item_code("111-111-11") == "111.111.11"\nassert format_item_code("111.111.11") == "111.111.11"\n```\n',
    'author': 'Lev Vereshchagin',
    'author_email': 'mail@vrslev.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vrslev/ikea-api-client',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
