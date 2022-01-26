# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['honeypot', 'honeypot.templatetags']

package_data = \
{'': ['*'], 'honeypot': ['templates/honeypot/*']}

install_requires = \
['Django>=2.2,<5.0']

setup_kwargs = {
    'name': 'django-honeypot',
    'version': '1.0.3',
    'description': 'Django honeypot field utilities',
    'long_description': '===============\ndjango-honeypot\n===============\n\n.. image:: https://github.com/jamesturk/django-honeypot/workflows/Test/badge.svg\n\n.. image:: https://img.shields.io/pypi/v/django-honeypot.svg\n    :target: https://pypi.python.org/pypi/django-honeypot\n\nDjango application that provides utilities for preventing automated form spam.\n\nProvides template tags, view decorators, and middleware to add and verify honeypot fields to forms.\n\nWritten by James Turk with contributions by Flavio Curella and Daniel Greenfeld.\n\nSource: https://github.com/jamesturk/django-honeypot/\n\nRequirements\n============\n\n* python >= 3.7\n* django >= 2.2\n\n(django-honeypot 0.7 supports Django 1.11 and Python 2.7)\n\nUsage\n=====\n\nsettings.py\n-----------\n\nBe sure to add ``honeypot`` to ``INSTALLED_APPS`` in settings.py.\n\nYou will almost always need to define ``HONEYPOT_FIELD_NAME`` which is the name to use for the honeypot field.  Some sophisticated bots will attempt to avoid fields named honeypot, so it may be wise to name the field something slightly more realistic such as "phonenumber" or "body2".\n\n``HONEYPOT_VALUE`` is an option that you can specify to populate the honeypot field, by default the honeypot field will be empty and any text entered into it will result in a failed POST.  ``HONEYPOT_VALUE`` can be a string or a callable that takes no arguments.\n\n``HONEYPOT_VERIFIER`` is an advanced option that you can specify to validate the honeypot.  The default verifier ensures that the contents of the honeypot field matches ``HONEYPOT_VALUE``.  Using a combination of a callable for ``HONEYPOT_VALUE`` and ``HONEYPOT_VERIFIER`` it is possible to implement a more advanced technique such as using timestamps.\n\nAdding honeypot fields to specific forms and views\n--------------------------------------------------\n\nIt is possible to add honeypot fields to specific forms and ensure that specific views check for a valid honeypotin ``request.POST``.  This can be accomplished by using the ``render_honeypot_field`` template tag:\n\nAt the top of a template file include the line::\n\n    {% load honeypot %}\n\nAnd then within any form including the tag::\n\n    {% render_honeypot_field "field_name" %}\n\nwill render a honeypot field named "field_name" that is hidden by default.  The name of the honeypot field will default to ``HONEYPOT_FIELD_NAME`` if one is not provided.\n\nTo ensure that the honeypot field is both present and correct you will need to use ``check_honeypot`` decorator from ``honeypot.decorators``:\n\n.. code:: python\n\n    from honeypot.decorators import check_honeypot\n\n    @check_honeypot(field_name=\'hp_field_name\')\n    def post_comment(request):\n        ...\n\n    @check_honeypot\n    def other_post_view(request):\n        ...\n\nThis decorator will ensure that a field exists in ``request.POST`` that is named \'field_name\'.  ``@check_honeypot`` without arguments will use the default ``HONEYPOT_FIELD_NAME``.\n\nAdding honeypot fields site-wide\n--------------------------------\n\nSometimes it is desirable to add honeypots to all forms site-wide.  This is particularly useful when dealing with apps that render their own forms.  For this purpose three middlewares are provided, similar in functionality to django\'s own CSRF middleware.\n\nAll of these middleware live in ``honeypot.middleware``.\n\n``HoneypotResponseMiddleware`` analyzes the output of all responses and rewrites any forms that use ``method="POST"`` to contain a honeypot field, just as if they had started with ``{% render_honeypot_field %}``.  Borrowing heavily from ``django.contrib.csrf.middleware.CsrfResponseMiddleware`` this middleware only rewrites responses with Content-Type text/html or application/xhtml+xml.\n\n``HoneypotViewMiddleware`` ensures that for all incoming POST requests to views ``request.POST`` contains a valid honeypot field as defined by the ``HONEYPOT_FIELD_NAME``, ``HONEYPOT_VALUE``, and ``HONEYPOT_VERIFIER`` settings.  The result is the same as if every view in your project were decorated with ``@check_honeypot``.\n\n``HoneypotMiddleware`` is a combined middleware that applies both ``HoneypotResponseMiddleware`` and ``HoneypotViewMiddleware``, this is the easiest way to get honeypot fields site-wide and can be used in many if not most cases.\n\nCustomizing honeypot display\n----------------------------\n\nThere are two templates used by django-honeypot that can be used to control various aspects of how the honeypot functionality is presented to the user.\n\n``honeypot/honeypot_field.html`` is used to render the honeypot field.  It is given two context variables ``fieldname`` and ``value``, corresponding to ``HONEYPOT_FIELD_NAME`` and ``HONEYPOT_VALUE`` or any overrides in effect (such as a custom field name passed to the template tag).\n\n``honeypot/honeypot_error.html`` is the error page rendered when a bad request is intercepted.  It is given the context variable ``fieldname`` representing the name of the honeypot field.\n\n',
    'author': 'James Turk',
    'author_email': 'dev@jamesturk.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jamesturk/django-honeypot/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
