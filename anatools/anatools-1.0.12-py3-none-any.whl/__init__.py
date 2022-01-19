"""anatools is Rendered.ai’s SDK for connecting to the Platform API. 

- The ``anatools.annotations`` package allows a User to generate annotations locally without the need for the Platform.
- The ``anatools.api`` package is used by the ``anatools.client`` package to access the api.
- The ``anatools.client`` package exposes the Platform API to the User. Everything that a user can do through the Platform Web Interface can be done via the SDK through the ``anatools.client`` package.

The SDK's submodule methods are all exposed to the user, so the full path is not required to call a specific method. 

View the `Introduction to Rendered.ai Documentation`_ to learn more.

.. _Introduction to Rendered.ai Documentation:
        https://support.rendered.ai/gc/Introduction-to-Rendered.ai.1577812005.html

"""

from .client.anaclient import AnaClient
from .annotations.annotations import Annotations