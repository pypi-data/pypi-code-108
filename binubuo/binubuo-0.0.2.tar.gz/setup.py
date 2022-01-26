from setuptools import setup, find_packages
from pathlib import Path

readme = """# Binubuo

**Binubuo** is a simple and powerful client to the Binubuo API. The API is used to generate fake or synthetic data that is realistic.
```python
>>> from binubuo import binubuo
>>> b = binubuo('<RapidAPI key>')
>>> print(b.generate('person', 'full_name'))
Andrew Howard
>>> print(b.generate('finance', 'bank_account_id'))
GE02Pu5783332775138823
>>> print(b.generate('consumer', 'food_item'))
Pumpkin Spice, Atlantic Salmon, 2 Bonless Fillets
>>> print(b.generate('time', 'date'))
1945-02-10T17:37:09Z
```

The Binubuo API has more than 150+ real life data generators, across 10+ data domains such as person, finance, computer, investment and many more. For full details on what type
of data Binubuo can generate and uder which domains, you can see the full list here: https://binubuo.com/ords/r/binubuo_ui/binubuo/documentation-generators

To use the python client, you need an API key from RapidAPI. If you do not have an account with RapidAPI, you can create one here: https://rapidapi.com/auth/sign-up

## Installing Binubuo client and supported versions

Binubuo is available and installable from PyPI:

    $ python -m pip install binubuo

Binubuo officially supports Python 2.7 & 3.6+.

## Features

**Binubuo** supports many data domains and data generators. The below list is just a few examples. Look here for the full list: https://binubuo.com/ords/r/binubuo_ui/binubuo/documentation-generators

* Basic
    * Natural
    * Integer
    * Float
* Business
    * Industry
    * Company Name
* Computer
    * Email
    * Url
    * File Name
    * ipv6
    * Domain Name
* Consumer
    * Food Item
    * Nonfood Item
* Finance
    * Credit Card Number
    * Account Transaction
    * Bank Account ID
    * Transaction Status
* Games
    * Coin Toss
    * Dice Roll
* Investment
    * Fund Name
    * ISIN
    * Swift ID
    * Risk Rating
* Location
    * City
    * Zipcode
    * Address
    * Street Name
* Logistics
    * BIC
    * Container Number
    * Shipping Company
* Medical
    * ICD10
* Person
    * Full name
    * Age
    * Job Title
    * Personal ID
* Phone
    * Phone Number
    * MEID
    * IMSI
    * IMEI
    * Operator Code
* Science
    * Chemical Element
    * Scale
    * Tree
    * Planet
* Text
    * Word
    * Adjective
    * Sentence
* Time
    * Date
    * Day
    * Epoch
    * Timestamp
* Transport
    * License Plate
    * ICAO
    * IMO
"""

packages = ['binubuo']

requires = [
    'requests>=2.0.0; python_version >= "3"'
]

setup(
    name='binubuo',
    version='0.0.2',
    description='Client package for Binubuo synthetic data generator',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://binubuo.com',
    author='Morten',
    author_email='morten@binubuo.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing :: Mocking',
        'Topic :: Utilities',
    ],
    keywords='synthetic, testdata, mocking',
    packages=packages,
    package_dir={'binubuo': 'binubuo'},
    install_requires=requires,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*',
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/morten-egan/binubuo-python-client/issues/new',
        'Funding': 'https://donate.pypi.org',
        'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://github.com/pypa/sampleproject/',
    },
)