"""A django application for easy handling of custom error pages.

Django provides `built-in support <https://docs.djangoproject.com/en/4.0/topics/http/views/#customizing-error-views>`_
for deploying customizing error views. However, this functionality requires
the definition of custom view objects (and associated tests) that are
copy and pasted between projects.

The ``django-easy-error`` package simplifies the management of custom HTTP
error pages by packaging redundant code into a dedicated, pip installable
solution. It provides automatic request routing to user customizable error
pages for 400, 403, 404, and 500 errors (the same as those supported by
django).


Installation
------------

The ``django-easy-error`` package is pip installable:

.. code-block:: bash

   $ pip install django-easy-error

To integrate the package with an existing django application, add it to
the ``installed_apps`` list in the application settings:

.. doctest:: python

   >>> INSTALLED_APPS = [
   ...    'django-easy-error',
   ... ]

Next, add the following import statement to your project's root url
configuration file (I.e., your primary ``urls.py`` file):

.. doctest:: python

   >>> from django_easy_error.handlers import *


Although it is not required, you should consider customizing your HTML error
templates. See below for further instructions.

Configuring Custom Templates
----------------------------

A very simple error page is included with the package out of the box
(see `the source <https://github.com/djperrefort/django-easy-error/blob/main/django_easy_error/templates/simple_error/default.html>`_
if your interested in what that template looks like). However, users can easily
customize their error pages by creating their own template files.

By default, all HTTP errors are redirected to the HTML template located in
your template directory under ``simple_error/default.html``. Template files
can also be specified for individual HTTP error codes using the naming scheme
``simple_error/http_[ERROR CODE].html``. For example, an 404 error will
render the template located at ``simple_error/http_404.html``.

.. note:: Django only supports custom error hanldes for HTTP error codes
   400, 403, 404, and 500. As such, only template for these four errors
   are supported.

Rendered templates are automatically provided different context values
depending on the corresponding error code.

Context Values for 400 Errors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+------------------------+----------------------------------------------------+
| Template Variable Name | Value                                              |
+========================+====================================================+
| error_code             | 400                                                |
+------------------------+----------------------------------------------------+
| description            | Bad Request                                        |
+------------------------+----------------------------------------------------+
| description_long       | The server could not process your request.         |
+------------------------+----------------------------------------------------+

Context Values for 403 Errors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+------------------------+-------------------------------------------------------------+
| Template Variable Name | Value                                                       |
+========================+=============================================================+
| error_code             | 403                                                         |
+------------------------+-------------------------------------------------------------+
| description            | Forbidden                                                   |
+------------------------+-------------------------------------------------------------+
| description_long       | You are not authorized for access to the requested content. |
+------------------------+-------------------------------------------------------------+

Context Values for 404 Errors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+------------------------+-------------------------------------------------------+
| Template Variable Name | Value                                                 |
+========================+=======================================================+
| error_code             | 404                                                   |
+------------------------+-------------------------------------------------------+
| description            | Page Not Found                                        |
+------------------------+-------------------------------------------------------+
| description_long       | The server could not find the resource you requested. |
+------------------------+-------------------------------------------------------+

Context Values for 500 Errors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+------------------------+----------------------------------------------------+
| Template Variable Name | Value                                              |
+========================+====================================================+
| error_code             | 500                                                |
+------------------------+----------------------------------------------------+
| description            | Internal Server Error                              |
+------------------------+----------------------------------------------------+
| description_long       | The server has encountered an internal error.      |
+------------------------+----------------------------------------------------+

"""

from django.conf import settings

__version__ = '1.0.0'
__author__ = 'Daniel Perrefort'

# Allow reloading of the module without Django raising an error
# This is useful for running tests without a running django server
try:
    settings.configure()

except RuntimeError:
    pass

# Set default setting values
try:
    getattr(settings, 'ERROR_CODE_DESCRIPTIONS')

except AttributeError:
    setattr(settings, 'ERROR_CODE_DESCRIPTIONS', {
        400: 'Bad Request',
        403: 'Forbidden',
        404: 'Page Not Found',
        500: 'Internal Server Error'
    })

try:
    getattr(settings, 'ERROR_CODE_DESCRIPTIONS_LONG')

except AttributeError:
    setattr(settings, 'ERROR_CODE_DESCRIPTIONS_LONG', {
        400: 'The server could not process your request.',
        403: 'You are not authorized for access to the requested content.',
        404: 'The server could not find the resource you requested.',
        500: 'The server has encountered an internal error.',
    })
