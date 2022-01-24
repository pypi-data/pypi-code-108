"""
Filter the versions of extensions in the registry, and access information about matching versions:

.. code:: python

    from ocdsextensionregistry import ExtensionRegistry

    extensions_url = 'https://raw.githubusercontent.com/open-contracting/extension_registry/main/extensions.csv'
    extension_versions_url = 'https://raw.githubusercontent.com/open-contracting/extension_registry/main/extension_versions.csv'

    registry = ExtensionRegistry(extension_versions_url, extensions_url)
    for version in registry.filter(core=True, version='v1.1.4', category='tender'):
        print(f'The {version.metadata[name][en]} extension ("{version.id}") is maintained at {version.repository_html_page}')
        print(f'Run `git clone {version.repository_url}` to make a local copy in a {version.repository_name} directory')
        print(f'Get its patch at {version.base_url}release-schema.json\\n')

Output::

    The Enquiries extension ("enquiries") is maintained at https://github.com/open-contracting-extensions/ocds_enquiry_extension
    Run `git clone git@github.com:open-contracting-extensions/ocds_enquiry_extension.git` to make a local copy in a ocds_enquiry_extension directory
    Get its patch at https://raw.githubusercontent.com/open-contracting-extensions/ocds_enquiry_extension/v1.1.4/release-schema.json

To work with the files within a version of an extension:

-  :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.metadata` parses and provides consistent access to the information in ``extension.json``
-  :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.schemas` returns the parsed contents of schema files
-  :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.codelists` returns the parsed contents of codelist files (see more below)
-  :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.files` returns the unparsed contents of all files

See additional details in :doc:`extension_version`.
"""  # noqa: E501

import csv
from io import StringIO
from urllib.parse import urlsplit

from .exceptions import DoesNotExist, MissingExtensionMetadata
from .extension import Extension
from .extension_version import ExtensionVersion
from .util import _resolve


class ExtensionRegistry:
    def __init__(self, extension_versions_data, extensions_data=None):
        """
        Accepts extension_versions.csv and, optionally, extensions.csv as either URLs or data (as string) and reads
        them into ExtensionVersion objects. If extensions_data is not provided, the extension versions will not have
        category or core properties. URLs starting with ``file://`` will be read from the filesystem.
        """
        self.versions = []

        # If extensions data is provided, prepare to merge it with extension versions data.
        extensions = {}
        if extensions_data:
            extensions_data = _resolve(extensions_data)
            for row in csv.DictReader(StringIO(extensions_data)):
                extension = Extension(row)
                extensions[extension.id] = extension

        extension_versions_data = _resolve(extension_versions_data)
        for row in csv.DictReader(StringIO(extension_versions_data)):
            version = ExtensionVersion(row)
            if version.id in extensions:
                version.update(extensions[version.id])
            self.versions.append(version)

    def filter(self, **kwargs):
        """
        Returns the extension versions in the registry that match the keyword arguments.

        :raises MissingExtensionMetadata: if the keyword arguments refer to extensions data, but the extension registry
                                          was not initialized with extensions data
        """
        try:
            return [ver for ver in self.versions if all(getattr(ver, k) == v for k, v in kwargs.items())]
        except AttributeError as e:
            self._handle_attribute_error(e)

    def get(self, **kwargs):
        """
        Returns the first extension version in the registry that matches the keyword arguments.

        :raises DoesNotExist: if no extension version matches
        :raises MissingExtensionMetadata: if the keyword arguments refer to extensions data, but the extension registry
                                          was not initialized with extensions data
        """
        try:
            return next(ver for ver in self.versions if all(getattr(ver, k) == v for k, v in kwargs.items()))
        except StopIteration:
            raise DoesNotExist(f'Extension version matching {kwargs!r} does not exist.')
        except AttributeError as e:
            self._handle_attribute_error(e)

    def get_from_url(self, url):
        """
        Returns the first extension version in the registry whose base URL matches the given URL.

        :raises DoesNotExist: if no extension version matches
        """
        parsed = urlsplit(url)
        path = parsed.path.rsplit('/', 1)[0] + '/'
        return self.get(base_url=parsed._replace(path=path).geturl())

    def __iter__(self):
        """
        Iterates over the extension versions in the registry.
        """
        for version in self.versions:
            yield version

    def _handle_attribute_error(self, e):
        if "'category'" in str(e.args) or "'core'" in str(e.args):
            raise MissingExtensionMetadata('ExtensionRegistry must be initialized with extensions data.') from e
        raise
