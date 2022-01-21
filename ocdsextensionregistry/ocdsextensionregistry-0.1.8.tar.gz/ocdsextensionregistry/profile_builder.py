"""
.. code:: python

    from ocdsextensionregistry import ProfileBuilder

    builder = ProfileBuilder('1__1__4', {
        'lots': 'v1.1.4',
        'bids': 'v1.1.4',
    })

This initializes a profile of OCDS 1.1.4 with two extensions. Alternately, you can pass a list of extensions' metadata
URLs, base URLs, download URLs, and/or absolute paths to local directories, for example:

.. code:: python

    builder = ProfileBuilder('1__1__4', [
      'https://raw.githubusercontent.com/open-contracting-extensions/ocds_coveredBy_extension/master/extension.json',
      'https://raw.githubusercontent.com/open-contracting-extensions/ocds_options_extension/master/',
      'https://github.com/open-contracting-extensions/ocds_techniques_extension/archive/master.zip',
      'file:///absolute/path/to/ocds_lots_extension',
    ])

After initializing the profile, you can then:

-  :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_schema_patch` to get the profile's patch of ``release-schema.json``
-  :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.patched_release_schema` to get the patched version of ``release-schema.json``
-  :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.extension_codelists` to get the profile's codelists
-  :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.patched_codelists` to get the patched codelists
-  :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.extensions` to iterate over the profile's versions of extensions
"""  # noqa: E501

import csv
import json
import logging
import os
import re
from io import StringIO
from urllib.parse import urljoin, urlsplit

import json_merge_patch
from jsonref import JsonRef

from .codelist import Codelist
from .extension_registry import ExtensionRegistry
from .extension_version import ExtensionVersion
from .util import _resolve_zip

logger = logging.getLogger('ocdsextensionregistry')


class ProfileBuilder:
    def __init__(self, standard_tag, extension_versions, registry_base_url=None, standard_base_url=None,
                 schema_base_url=None):
        """
        Accepts an OCDS version and either a dictionary of extension identifiers and versions, or a list of extensions'
        metadata URLs, base URLs and/or download URLs, and initializes a reader of the extension registry.

        :param str standard_tag: the OCDS version tag, e.g. ``'1__1__4'``
        :param extension_versions: the extension versions
        :param str registry_base_url: the registry's base URL, defaults to
                                      ``'https://raw.githubusercontent.com/open-contracting/extension_registry/main/'``
        :param str standard_base_url: the standard's base URL, defaults to
                                      ``'https://codeload.github.com/open-contracting/standard/zip/' + standard_tag``
        :param str schema_base_url: the schema's base URL, e.g.
                                    ``'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/'``
        :type extension_versions: dict or list
        """
        # Allows setting the registry URL to e.g. a pull request, when working on a profile.
        if not registry_base_url:
            registry_base_url = 'https://raw.githubusercontent.com/open-contracting/extension_registry/main/'
        if not standard_base_url and standard_tag:
            standard_base_url = 'https://codeload.github.com/open-contracting/standard/zip/' + standard_tag

        self.standard_tag = standard_tag
        self.extension_versions = extension_versions
        self.registry_base_url = registry_base_url
        self.standard_base_url = standard_base_url
        self.schema_base_url = schema_base_url
        self._registry = None
        self._file_cache = {}

    @property
    def registry(self):
        if self._registry is None:
            self._registry = ExtensionRegistry(self.registry_base_url + 'extension_versions.csv')

        return self._registry

    def extensions(self):
        """
        Returns the matching extension versions from the registry.
        """
        if isinstance(self.extension_versions, dict):
            for identifier, version in self.extension_versions.items():
                yield self.registry.get(id=identifier, version=version)
        else:
            for url in self.extension_versions:
                parsed = urlsplit(url)
                data = dict.fromkeys(['Id', 'Date', 'Version', 'Base URL', 'Download URL'])
                if parsed.scheme == 'file':
                    data['Download URL'] = url
                elif url.endswith('/extension.json'):
                    data['Base URL'] = url[:-14]
                elif url.endswith('/'):
                    data['Base URL'] = url
                else:
                    data['Download URL'] = url
                yield ExtensionVersion(data)

    def release_schema_patch(self, extension_field=None, language='en'):
        """
        Returns the consolidated release schema patch.

        :param str extension_field: the property with which to annotate each definition and field with the name of the
                                    extension in which the definition or field is defined
        :param str language: the language to use for the name of the extension
        """
        output = {}

        # Replaces `null` with sentinel values, to preserve the null'ing of fields by extensions in the final patch.
        for extension in self.extensions():
            patch = extension.remote('release-schema.json', default='{}')
            patch = json.loads(re.sub(r':\s*null\b', ': "REPLACE_WITH_NULL"', patch))
            if extension_field:
                _add_extension_field(patch, extension.metadata['name'][language], extension_field)
            json_merge_patch.merge(output, patch)

        return json.loads(json.dumps(output).replace('"REPLACE_WITH_NULL"', 'null'))

    def patched_release_schema(self, schema=None, extension_field=None, language='en'):
        """
        Returns the patched release schema.

        :param dict schema: the release schema
        :param str extension_field: the property with which to annotate each definition and field with the name of the
                                    extension in which the definition or field is defined
        :param str language: the language to use for the name of the extension
        """
        if not schema:
            schema = json.loads(self.get_standard_file_contents('release-schema.json'))

        json_merge_patch.merge(schema, self.release_schema_patch(extension_field=extension_field, language=language))

        if self.schema_base_url:
            schema['id'] = urljoin(self.schema_base_url, 'release-schema.json')

        return schema

    def _dereferenced_patched_release_schema(self):
        return JsonRef.replace_refs(self.patched_release_schema())

    def release_package_schema(self, schema=None, embed=False):
        """
        Returns a release package schema. If the profile builder was initialized with ``schema_base_url``, updates
        schema URLs.

        :param dict schema: the release schema
        :param bool embed: whether to embed or ``$ref``'erence the patched release schema
        """
        if not schema:
            schema = json.loads(self.get_standard_file_contents('release-package-schema.json'))

        if self.schema_base_url:
            schema['id'] = urljoin(self.schema_base_url, 'release-package-schema.json')
            if embed:
                patched = self._dereferenced_patched_release_schema()
                schema['properties']['releases']['items'] = patched
            else:
                url = urljoin(self.schema_base_url, 'release-schema.json')
                schema['properties']['releases']['items']['$ref'] = url

        return schema

    def record_package_schema(self, schema=None, embed=False):
        """
        Returns a record package schema. If the profile builder was initialized with ``schema_base_url``, updates
        schema URLs.

        :param dict schema: the record schema
        :param bool embed: whether to embed or ``$ref``'erence the patched release schema
        """
        if not schema:
            schema = json.loads(self.get_standard_file_contents('record-package-schema.json'))

        if self.schema_base_url:
            schema['id'] = urljoin(self.schema_base_url, 'record-package-schema.json')
            if embed:
                patched = self._dereferenced_patched_release_schema()
                schema['definitions']['record']['properties']['compiledRelease'] = patched
                schema['definitions']['record']['properties']['releases']['oneOf'][1]['items'] = patched
            else:
                url = urljoin(self.schema_base_url, 'release-schema.json')
                schema['definitions']['record']['properties']['compiledRelease']['$ref'] = url
                schema['definitions']['record']['properties']['releases']['oneOf'][1]['items']['$ref'] = url

        return schema

    def standard_codelists(self):
        """
        Returns the standard's codelists as Codelist objects.
        """
        codelists = {}

        # Populate the file cache.
        self.get_standard_file_contents('release-schema.json')

        # This method shouldn't need to know about `_file_cache`.
        for path, content in self._file_cache.items():
            name = os.path.basename(path)
            if 'codelists' in path.split('/') and name:
                codelists[name] = Codelist(name)
                codelists[name].extend(csv.DictReader(StringIO(content)), 'OCDS Core')

        return list(codelists.values())

    def extension_codelists(self):
        """
        Returns the extensions' codelists as Codelist objects.

        The extensions' codelists may be new, or may add codes to (+name.csv), remove codes from (-name.csv) or replace
        (name.csv) the codelists of the standard or other extensions.

        Codelist additions and removals are merged across extensions. If new codelists or codelist replacements differ
        across extensions, an error is raised.
        """
        codelists = {}

        # Keep the original content of codelists, to compare across extensions.
        originals = {}

        for extension in self.extensions():
            # We use the "codelists" field in extension.json (which standard-maintenance-scripts validates). An
            # extension is not guaranteed to offer a download URL, which is the only other way to get codelists.
            for name in extension.metadata.get('codelists', []):
                content = extension.remote('codelists/' + name)

                if name not in codelists:
                    codelists[name] = Codelist(name)
                    originals[name] = content
                elif not codelists[name].patch:
                    assert originals[name] == content, f'codelist {name} differs across extensions'
                    continue

                codelists[name].extend(csv.DictReader(StringIO(content)), extension.metadata['name']['en'])

        # If a codelist replacement (name.csv) is consistent with additions (+name.csv) and removals (-name.csv), the
        # latter should be removed. In other words, the expectations are that:
        #
        # * A codelist replacement shouldn't omit added codes.
        # * A codelist replacement shouldn't include removed codes.
        # * If codes are added after a codelist is replaced, this should result in duplicate codes.
        # * If codes are removed after a codelist is replaced, this should result in no change.
        #
        # If these expectations are not met, an error is raised. As such, profile authors only have to handle cases
        # where codelist modifications are inconsistent across extensions.
        for codelist in list(codelists.values()):
            basename = codelist.basename
            if codelist.patch and basename in codelists:
                name = codelist.name
                codes = codelists[basename].codes
                if codelist.addend:
                    for row in codelist:
                        code = row['Code']
                        assert code in codes, f'{code} added by {name}, but not in {basename}'
                    logger.info('%s has the codes added by %s - ignoring %s', basename, name, name)
                else:
                    for row in codelist:
                        code = row['Code']
                        assert code not in codes, f'{code} removed by {name}, but in {basename}'
                    logger.info('%s has no codes removed by %s - ignoring %s', basename, name, name)
                del codelists[name]

        return list(codelists.values())

    def patched_codelists(self):
        """
        Returns patched and new codelists as Codelist objects.
        """
        codelists = {}

        for codelist in self.standard_codelists():
            codelists[codelist.name] = codelist

        for codelist in self.extension_codelists():
            if codelist.patch:
                basename = codelist.basename
                if codelist.addend:
                    # Add the rows.
                    codelists[basename].rows.extend(codelist.rows)
                    # Note that the rows may not all have the same columns, but DictWriter can handle this.
                else:
                    # Remove the codes. Multiple extensions can remove the same codes.
                    removed = codelist.codes
                    codelists[basename].rows = [row for row in codelists[basename] if row['Code'] not in removed]
            else:
                # Set or replace the rows.
                codelists[codelist.name] = codelist

        return list(codelists.values())

    def get_standard_file_contents(self, basename):
        """
        Returns the contents of the file within the standard.

        Downloads the given version of the standard, and caches the contents of files in the schema/ directory.
        """
        if not self._file_cache:
            zipfile = _resolve_zip(self.standard_base_url, 'schema')
            names = zipfile.namelist()

            path = names[0]
            if self.standard_tag < '1__1__5':
                path += 'standard/schema/'
            else:
                path += 'schema/'
            start = len(path)

            for name in names[1:]:
                if path in name:
                    self._file_cache[name[start:]] = zipfile.read(name).decode('utf-8')

        return self._file_cache[basename]


def _add_extension_field(schema, extension_name, field_name, pointer=None):
    if pointer is None:
        pointer = ()
    if isinstance(schema, list):
        for item in schema:
            _add_extension_field(item, extension_name, field_name=field_name, pointer=pointer)
    elif isinstance(schema, dict):
        if len(pointer) > 1 and pointer[-2] in ('definitions', 'properties') and 'title' in schema:
            schema[field_name] = extension_name
        for key, value in schema.items():
            _add_extension_field(value, extension_name, field_name=field_name, pointer=pointer + (key,))
