"""
Complex operations making use of this library's classes are organized into this API module.
"""

import csv
import json
import os
from contextlib import contextmanager

from .exceptions import DoesNotExist
from .profile_builder import ProfileBuilder
from .util import json_dump

VALID_FIELDNAMES = ('Code', 'Title', 'Description', 'Extension')


def build_profile(basedir, standard_tag, extension_versions, registry_base_url=None, standard_base_url=None,
                  schema_base_url=None, update_codelist_urls=None):
    """
    Pulls extensions into a profile.

    - Merges extensions' JSON Merge Patch files for OCDS' release-schema.json (schema/profile/release-schema.json)
    - Writes extensions' codelist files (schema/profile/codelists)
    - Patches OCDS' release-schema.json with extensions' JSON Merge Patch files (schema/patched/release-schema.json)
    - Patches OCDS' codelist files with extensions' codelist files (schema/patched/codelists)
    - Updates the "codelists" field in extension.json

    The profile's codelists exclude deprecated codes and add an Extension column.

    :param str basedir: the profile's ``schema/`` directory
    :param str standard_tag: the OCDS version tag, e.g. ``'1__1__4'``
    :param extension_versions: the extension versions
    :param str registry_base_url: the registry's base URL, defaults to
                                  ``'https://raw.githubusercontent.com/open-contracting/extension_registry/main/'``
    :param str standard_base_url: the standard's base URL, defaults to
                                  ``'https://codeload.github.com/open-contracting/standard/zip/' + standard_tag``
    :param str schema_base_url: the schema's base URL, e.g.
                                ``'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/'``
    :param update_codelist_urls: a function that accepts a schema as text and a list of names of codelists and replaces
                                 the OCDS documentation's codelist page URLs with the profile's codelist page URLs
    """
    @contextmanager
    def open_file(name, mode='r'):
        """
        Creates the directory if it doesn't exist.
        """
        os.makedirs(os.path.dirname(name), exist_ok=True)

        f = open(name, mode)
        try:
            yield f
        finally:
            f.close()

    def write_json_file(data, *parts):
        with open_file(os.path.join(basedir, *parts), 'w') as f:
            json_dump(data, f)
            f.write('\n')

    def write_codelist_file(codelist, fieldnames, *parts):
        with open_file(os.path.join(basedir, *parts, 'codelists', codelist.name), 'w') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n', extrasaction='ignore')
            writer.writeheader()
            writer.writerows(codelist)

    builder = ProfileBuilder(standard_tag, extension_versions, registry_base_url, standard_base_url, schema_base_url)
    extension_codelists = builder.extension_codelists()
    directories_and_schemas = {
        'profile': {
            'release-schema.json': builder.release_schema_patch(),
        },
        'patched': {
            'release-schema.json': builder.patched_release_schema(),
            'release-package-schema.json': builder.release_package_schema(),
        }
    }

    # Write the JSON Merge Patch and JSON Schema files.
    for directory, schemas in directories_and_schemas.items():
        for filename, schema in schemas.items():
            write_json_file(schema, directory, filename)

    # Write the extensions' codelists.
    for codelist in extension_codelists:
        write_codelist_file(codelist, codelist.fieldnames, 'profile')

    # Write the patched codelists.
    for codelist in builder.patched_codelists():
        codelist.add_extension_column('Extension')
        codelist.remove_deprecated_codes()
        fieldnames = [fieldname for fieldname in codelist.fieldnames if fieldname in VALID_FIELDNAMES]
        write_codelist_file(codelist, fieldnames, 'patched')

    # Update the "codelists" field in extension.json.
    with open(os.path.join(basedir, 'profile', 'extension.json')) as f:
        metadata = json.load(f)

    codelists = [codelist.name for codelist in extension_codelists]

    if codelists:
        metadata['codelists'] = codelists
    else:
        metadata.pop('codelists', None)

    # Update the "dependencies" and "testDependencies" fields in extension.json, without duplication.
    extensions = set()
    for extension in builder.extensions():
        extensions.add(extension.id)

    for field in ('dependencies', 'testDependencies'):
        metadata[field] = set()

        for extension in builder.extensions():
            for url in extension.metadata.get(field, []):
                try:
                    extension = builder.registry.get_from_url(url)
                    if extension.id in extensions:
                        continue
                    extensions.add(extension.id)
                except DoesNotExist:
                    pass
                metadata[field].add(url)

        if metadata[field]:
            metadata[field] = sorted(metadata[field])
        else:
            del metadata[field]

    write_json_file(metadata, 'profile', 'extension.json')

    if update_codelist_urls:
        codelists = [codelist.basename for codelist in extension_codelists]
        for directory, schemas in directories_and_schemas.items():
            for filename, schema in schemas.items():
                path = os.path.join(basedir, directory, filename)
                with open(path) as f:
                    content = f.read()
                with open(path, 'w') as f:
                    f.write(update_codelist_urls(content, codelists))
