"""The ``django-keygen`` package provides an easy and convenient way to generate
secure secret keys for use with ``django`` driven web applications.

The ``SECRET_KEY`` setting in Django is used to provide
`cryptographic signing <https://docs.djangoproject.com/en/2.2/topics/signing/>`_
and is an important part of building secure Django applications.
While it is mostly used to sign session cookies, other common uses
include generating secure URL's, protecting form content in hidden fields,
and restricting access to private resources.

Installation
------------

The ``django-keygen`` package is pip installable:

.. code-block:: bash

   $ pip install django-keygen

To integrate the package with an existing django application, add it to
the ``installed_apps`` list in the application settings:

.. code-block:: python

   >>> INSTALLED_APPS = [
   ...    'django-keygen',
   ...    ...
   ... ]

Python Usage
------------

Key generation is available using the ``KeyGen`` class:

.. doctest:: python

   >>> from django_keygen import KeyGen
   >>> key_generator = KeyGen()
   >>> secret_key = key_generator.gen_secret_key()

By default, keys are generated using the full range of ascii charaters and
are 50 characters long. This can be overwritted using key word arguments:

.. doctest:: python

   >>> from string import ascii_lowercase
   >>> secret_key = key_generator.gen_secret_key(length=55, chars=ascii_lowercase)

Command Line Usage
------------------

The command line interface is accessible via the django management tool:

.. code-block:: bash

   $ python manage.py genkey

Just like the Python interface, you can specify the key length and charecter set used to generate the key:

.. code-block:: bash

   $ python manage.py genkey 50 some_character_set

Security Notices
----------------

It is considered bad security practice to use short security keys generating
using few unique characters. To safeguard against this, a ``SecurityError``
is raised when ``django-keygen`` is asked to generate an insecure key.

.. doctest:: python

   >>> secret_key = key_generator.gen_secret_key(length=5, chars='abc')
   Traceback (most recent call last):
   ...
   django_keygen.exceptions.SecurityException: Secret key length is short. Consider increasing the length of the generated key.
   ...

The error can be ignored by specifying ``force=True``, in which case a warning
is issued instead:

.. doctest:: python

   >>> secret_key = key_generator.gen_secret_key(length=5, chars='abc', force=True)
"""

import string
from warnings import warn

from django.utils.crypto import get_random_string

from django_keygen.exceptions import SecurityWarning, SecurityException

__version__ = '1.0.0'
__author__ = 'Daniel Perrefort'


class KeyGen:
    """Generates and prints a new secret key"""

    @property
    def default_chars(self) -> str:
        """Default character set used to generate secret keys"""

        return string.ascii_letters + string.digits + string.punctuation

    def gen_secret_key(self, length: int = 50, chars: str = None, force: bool = False) -> str:
        """Generate a secret key for Django

        Args:
            length: The length of the key
            chars: Optionally use only the given characters
            force: Issue warnings instead of exceptions for unsafe security options
        """

        chars = chars or self.default_chars
        if length <= 0:
            raise ValueError('Key length must be greater than zero.')

        msg = None
        if length < 30:
            msg = 'Secret key length is short. Consider increasing the length of the generated key.'

        elif len(set(chars)) < 20:
            msg = 'Secret key generated with few unique characters. Try increasing the character set size.'

        if msg and force:
            warn(msg, SecurityWarning)

        elif msg:
            raise SecurityException(msg)

        return get_random_string(length, chars)
