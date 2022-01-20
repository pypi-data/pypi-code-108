'''
When a transport representation is given it can be validated during
construction.

Validation is defined by a validator, given by the validator field of the
serializer. This field can hold a reference to an object that implements a
validate method. When this method is called with a transport representation it
should either return a normalized version of the representation or raise an
error.

Predefined validators are the CerberusValidator and the JSONSchemaValidator.
The CerberusValidator checks objects against a cerberus schema definition. The
JSONSchemaValidator checks against JSON Schemes.
'''

import json
from io import StringIO
from os.path import dirname
from urllib.parse import urlparse

import cerberus
import jsonschema
from lxml import etree
from requests import get

from .problem import Problem


def _validation_error(detail):
    return Problem.unsupported_media_type(detail=detail)


class Validator:
    def validate(self, representation):
        raise NotImplementedError()


class JSONSchemaValidator(Validator):
    def __init__(self, spec_file_name, format_checker=None):
        self.format_checker = format_checker
        with open(spec_file_name, 'r') as f:
            self.schema = json.load(f)

    def validate(self, representation):
        try:
            jsonschema.validate(instance=representation,
                                schema=self.schema,
                                format_checker=self.format_checker)
            return representation
        except jsonschema.exceptions.ValidationError as exc:
            raise _validation_error('%s' % exc)


class CerberusValidator(Validator):
    def __init__(self, schema_description):
        self.validator = cerberus.Validator(schema_description['schema'])

        if 'allow_unknown' in schema_description:
            self.validator.allow_unknown = schema_description['allow_unknown']

    def validate(self, representation):
        try:
            if not self.validator.validate(representation):
                raise _validation_error('%s' % self.validator.errors)
            else:
                return self.validator.normalized(representation)
        except cerberus.validator.DocumentError as exc:
            raise _validation_error('%s' % exc)


class XSDValidator(Validator):
    def __init__(self, xsd_path):
        def _resolve_url(path):
            response = get(path)
            response.raise_for_status()

            if not any(map(lambda content_type: (response
                                                 .headers['Content-Type']
                                                 .startswith(content_type)),
                           {'text/xsd', 'text/xml', 'application/xml'})):
                raise ValueError('unexpected content type: `%s`'
                                 % response.headers['Content-Type'])

            return response.text

        xsd_base_directory = '%s/' % dirname(xsd_path)

        self.parser = etree.XMLParser()

        class UrlResolver(etree.Resolver):
            def resolve(self, referenced_location, id, context):
                if (urlparse(referenced_location).scheme not in
                        {'http', 'https'}):
                    return None

                return self.resolve_string(
                    _resolve_url(referenced_location),
                    context,
                    base_url=xsd_base_directory)

        self.parser.resolvers.add(UrlResolver())

        doc = etree.parse(xsd_path, parser=self.parser,
                          base_url=xsd_base_directory)
        self.xml_schema = etree.XMLSchema(doc)

    def validate(self, representation):
        try:
            self.xml_schema.assertValid(
                etree.parse(
                    StringIO(representation)))
            return representation
        except etree.DocumentInvalid as exc:
            raise _validation_error('%s' % exc)
