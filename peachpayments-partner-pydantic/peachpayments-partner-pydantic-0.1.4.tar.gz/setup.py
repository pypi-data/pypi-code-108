# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['peachpayments_partner_pydantic']

package_data = \
{'': ['*']}

install_requires = \
['email-validator>=1.1.3,<2.0.0',
 'ipaddress>=1.0.23,<2.0.0',
 'iso4217>=1.6.20180829,<2.0.0',
 'peachpayments-partner>=0.0.24,<0.0.25',
 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'peachpayments-partner-pydantic',
    'version': '0.1.4',
    'description': 'PeachPayments Partner Pydantic library contains Pydantic schemas to help integrate PeachPayments with their partners.',
    'long_description': '# PeachPayments Partner Pydantic Library\n\n## Overview\n\n**PeachPayments Partner Pydantic Library** is a platform-agnostic Python package to help Payment Service Providers in integrating with PeachPayments. This library provides functionality to validate request and response data using Pydantic Python library.\n\n**Source Code**: <https://gitlab.com/peachpayments/peachpayments-partner-pydantic/>\n\n* * *\n\n### Key terms\n\n| Term                     | Definition                                                                                                         |\n| ------------------------ | ------------------------------------------------------------------------------------------------------------------ |\n| Partner API              | A service provided by Peach Payments to enable Payment Service Providers to become available on the Peach Platform |\n| Payment Service Provider | A payment service provider who integrates with the Partner API                                                     |\n| Outbound API call        | API calls sent from Partner API to the Payment Service Provider                                                    |\n| Inbound API call         | API calls sent from Payment Service Provider to Partner API                                                        |\n\n## Usage\n\nPackage requires Python 3.9+\n\n### Installation\n\n```sh\n# pip\n$ pip3 install peachpayments-partner-pydantic\n```\n\n```sh\n# poetry\n$ poetry add peachpayments-partner-pydantic\n```\n\n### Field validation\n\n**Scenario:** Payment Service Provider written in FastAPI receives a debit request from PeachPayments.\n\n```python\n# ... imports\nfrom peachpayments_partner_pydantic.schemas import DebitRequest, DebitResponse\n\n@router.post(\n    "/v1/debit",\n    response_model=schemas.DebitResponse,\n)\ndef debit_request(\n    *, debit_in: schemas.DebitRequest\n) -> Any:\n    # Store the transaction\n    transaction = Transaction.create_from_debit(debit_in)\n    # Validate the debit response\n    debit_response = DebitResponse(**transaction.to_debit_response_fields())\n    return debit_response.dict()\n```\n\n### Translating exception to PeachPayments error response\n\n**Scenario:** Payment Service Provider written in FastAPI receives a request with a validation error from PeachPayments.\n\n#### 1. Write validation exception handler\n\n```python\n# app/exception_handlers.py\nfrom fastapi import Request, status\nfrom fastapi.exceptions import RequestValidationError\nfrom fastapi.responses import JSONResponse\nfrom peachpayments_partner_pydantic.exception_handlers import exception_to_response\n\nasync def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:\n    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=exception_to_response(exc))\n```\n\n#### 2. Connect it to the application\n\n```python\n# app/main.py\nfrom fastapi import FastAPI\nfrom fastapi.exceptions import RequestValidationError\nfrom app.exception_handlers import validation_exception_handler\n\napplication = FastAPI(\n    exception_handlers={RequestValidationError: validation_exception_handler},\n)\n```\n',
    'author': 'PeachPayments',
    'author_email': 'support@peachpayments.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/peachpayments/peachpayments-partner-pydantic/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
