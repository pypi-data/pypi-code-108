import itertools
import json
import logging

from django.db import models

from collections import OrderedDict
from decimal import Decimal

from rest_framework.schemas.openapi import AutoSchema
from rest_framework import serializers
from rest_framework.schemas.utils import is_list_view
from rest_framework.settings import api_settings
from rest_framework.fields import _UnvalidatedField

logger = logging.getLogger()


class BaseSchema(AutoSchema):
    def __init__(self, **kwargs):
        """
            customize_parameters: It is a list of dictionaries of fields available
                in the path that we want to change the description;
                e.g.:
                    path('<str:field>', ContentDistinct.as_view()),
                    customize_parameters = [
                        {
                            'name': 'field',
                            'description': f'field (available options are:\
                                            { available_options} '
                        }
                    ]

            query_parameters: It is a list of dictionaries personalized query params;
                e.g.:
                    query_parameters=[
                        {
                            'name': 'url',
                            'description': 'description',
                            'required': True
                        },
                    ]

            request_serializer: It is the serializer used to check if request is
                valid. It is usually used with APIView and viewsets.ViewSet.
                e.g.:
                    request_serializer=FileSerializer

            required_authorization: It is necessary to have authorization to
                access the route. Future improvement: Add which kind of authorization
                is required; It can be a boolean or a dictionary. The dictionary
                is necessary when the GET has no authorization and other methods
                has.
                e.g:
                    required_authorization={
                        'get': False,
                        'post': True
                    }
                e.g:
                    required_authorization=True

            required_locale: It is necessary to have locale;

            required_software_type: It is necessary to have software type;

            filter_fields: It is used to show the possible filters
                in the query params; It can be used with: generics.ListAPIView and
                viewsets.ModelViewSet; The fields needs to be available in the
                model;
                e.g.:
                    filter_fields=[
                        title', 'subtitle', 'locale'
                    ]
            sort_fields: It is used to show the possible sorting option
                in the query params; It can be used with: generics.ListAPIView and
                viewsets.ModelViewSet; The fields needs to be available in the
                model;
                e.g.:
                    sort_fields=[
                        'title', 'subtitle', 'locale'
                    ]
            responses: It is used to give the possible responses.
                e.g.:
                    responses={
                        200: {
                            'serializer': DocContentDistinctSerializer,
                            'description': 'Returns the available options'
                        },
                        400: {
                            'description': f'This field is not available for distinct. Available options are: {available_options}'
                        }
                    }
            request_serializer_exception: It will be deprecated; It was necessary
            because of the profile service and multiple version in the same view.

            responses_exception: It will be deprecated; It was necessary
            because of the profile service and multiple version in the same view.
        """
        self.customize_parameters = kwargs.pop("customize_parameters", None)
        self.query_parameters = kwargs.pop("query_parameters", None)

        self.request_serializer = kwargs.pop("request_serializer", None)

        self.required_authorization = kwargs.pop(
            "required_authorization", True
        )
        self.required_locale = kwargs.pop("required_locale", True)
        self.required_software_type = kwargs.pop(
            "required_software_type", True
        )
        self.filter_fields = kwargs.pop("filter_fields", [])
        self.sort_fields = kwargs.pop("sort_fields", [])
        self.responses = kwargs.pop("responses", None)

        # FIXME This two exceptions are specific for views with two routes. This should be deprecated!
        self.request_serializer_exception = kwargs.pop("request_serializer_exception", None)
        self.responses_exception = kwargs.pop("responses_exception", None)

        super().__init__(**kwargs)

    def get_filter_parameters(self, path, method):
        if not self.allows_filters(path, method):
            return []
        parameters = []
        for filter_backend in self.view.filter_backends:
            parameters += filter_backend().get_schema_operation_parameters(self.view)

        # # Custom filters
        if self.filter_fields:
            serializer, item_schema = self._custom_get_serializer(path, method)

            for field in serializer.fields.values():
                if field.field_name in self.filter_fields:
                    parameter = {}
                    schema = self.map_field(field)
                    name = f'{ field.field_name }[operator]'

                    available_operators = 'Available operators: gt, gte, lt, \
                        lte. Without operator the comparation is equal to.'

                    if schema['type'] == 'string':
                        available_operators = 'Available operators: contains, \
                            icontains, exact, iexact, in, startswith, \
                            istartswith, endswith, iendswith. Without \
                            operator the comparation is equal to.'
                    description = f'Filter by { field.field_name }. \
                        The available operators are: { available_operators }'

                    if schema['type'] == 'boolean':
                        name = f'{ field.field_name }'
                        description = f'Filter by { field.field_name }'

                    parameter['schema'] = schema
                    parameter['name'] = name
                    parameter['in'] = 'query'
                    parameter['required'] = False
                    parameter['description'] = description
                    parameters += [parameter]

        if self.sort_fields:
            description = f'Sort the queries, the available fields to \
                    sort are: { ", ".join(self.sort_fields) }. Example: \
                    sort_by=asc[{ self.sort_fields[0] }]'

            if len(self.sort_fields) > 1:
                description += f'or sort_by=asc[{ self.sort_fields[0] }],\
                        desc[{ self.sort_fields[1] }]'

            parameters += [{
                'name': 'sort_by',
                'in': 'query',
                'required': False,
                'description': description,
                'schema': {'type': 'string'}
            }]
        return parameters

    def get_components(self, path, method):
        """
        Return components with their properties from the serializer.
        """

        if method.lower() == 'delete':
            return {}

        if self.request_serializer:
            serializer = self.request_serializer()
            content = self.map_serializer(serializer)

        elif self.request_serializer_exception:
            for version in self.request_serializer_exception.keys():
                if version in path:
                    serializer = self.request_serializer_exception[version]()
                    break
            content = self.map_serializer(serializer)
        else:
            # Default from drf code
            serializer = self.get_serializer(path, method)
            if not isinstance(serializer, serializers.Serializer):
                return {}

            content = self.map_serializer(serializer)

        component_name = self.get_component_name(serializer)
        return {component_name: content}

    def get_operation(self, path, method):
        operation = {}
        operation['operationId'] = self.get_operation_id(path, method)
        operation['description'] = self.get_description(path, method)

        # FIXME Should be deprecated after route problem being solved
        if 'v0' in path:
            operation['operationId'] = f'{operation["operationId"]}_v0'

        parameters = []
        parameters += self.get_path_parameters(path, method)
        parameters += self.get_pagination_parameters(path, method)
        parameters += self.get_filter_parameters(path, method)

        if self.customize_parameters:
            parameters = self._update_parameters(parameters)

        parameters = self._default_parameters(parameters, method)

        operation['parameters'] = parameters

        request_body = self.get_request_body(path, method)
        if request_body:
            operation['requestBody'] = request_body
        operation['responses'] = self.get_responses(path, method)
        operation['tags'] = self.get_tags(path, method)
        return operation

    def get_responses(self, path, method):
        if method == 'DELETE':
            return {
                '204': {
                    'description': 'No response body'
                }
            }

        # FIXME responses exception it will be deprecated
        if self.responses_exception:
            responses = {}
            status_code = '201' if method == 'POST' else '200'
            for version in self.responses_exception.keys():
                if version in path:
                    serializer = self.request_serializer_exception[version]()
                    responses[status_code] = {
                        'content': {
                            'application/json' : {
                                'schema': {
                                    '$ref': '#/components/schemas/{}'.format(self.get_component_name(serializer))
                                }
                            }
                        },
                        'description': ""
                    }

            if self.responses:
                responses.update(self._custom_response(self.responses))
            return responses

        elif self.responses:
            responses = self._custom_response(self.responses)
            return responses

        self.response_media_types = self.map_renderers(path, method)

        serializer = self.get_serializer(path, method)

        if not isinstance(serializer, serializers.Serializer):
            item_schema = {}
        else:
            item_schema = self._get_reference(serializer)

        if is_list_view(path, method, self.view):
            response_schema = {
                'type': 'array',
                'items': item_schema,
            }
            paginator = self.get_paginator()
            if paginator:
                response_schema = paginator.get_paginated_response_schema(
                    response_schema
                )
        else:
            response_schema = item_schema

        status_code = '201' if method == 'POST' else '200'

        return {
            status_code: {
                'content': {
                    ct: {'schema': response_schema}
                    for ct in self.response_media_types
                },
                # description is a mandatory property,
                # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#responseObject
                # TODO: put something meaningful into it
                'description': ""
            }
        }

    def get_request_body(self, path, method):
        if method not in ('PUT', 'PATCH', 'POST'):
            return {}

        self.request_media_types = self.map_parsers(path, method)

        serializer, item_schema = self._custom_get_serializer(path, method)

        return {
            'content': {
                ct: {'schema': item_schema}
                for ct in self.request_media_types
            }
        }

    def _custom_get_serializer(self, path, method):
        if self.request_serializer:
            serializer = self.request_serializer()
            item_schema = self._get_reference(serializer)
            return serializer, item_schema

        elif self.request_serializer_exception:
            for version in self.request_serializer_exception.keys():
                if version in path:
                    serializer = self.request_serializer_exception[version]()
                    item_schema = self._get_reference(serializer)
                    return serializer, item_schema

        serializer = self.get_serializer(path, method)

        if not isinstance(serializer, serializers.Serializer):
            item_schema = {}
        else:
            item_schema = self._get_reference(serializer)
        return serializer, item_schema

    def _update_parameters(self, parameters):
        for cust_parameter, parameter in itertools.product(self.customize_parameters, parameters):
            if cust_parameter['name'] == parameter['name']:
                parameter['description'] = cust_parameter['description']

        return parameters

    def _default_parameters(self, parameters, method):
        if self.required_authorization:
            add_authorization = self.required_authorization
            if type(self.required_authorization) is dict:
                add_authorization = self.required_authorization[method.lower()]

            if add_authorization:
                parameters += [{
                    'name': 'Authorization',
                    'in': 'header',
                    'required': True,
                    'description': 'The structure to authenticate is: "JWT " + idToken or "TWT " + adminToken)',
                    'schema': {'type': 'string'}
                }]

        if self.required_locale:
            parameters += [{
                'name': 'Accept-Language',
                'in': 'header',
                'required': True,
                'description': 'Example: Accept-Language=pt-PT',
                'schema': {'type': 'string'}
            }]

        if self.required_software_type:
            parameters += [{
                'name': 'Software-Type',
                'in': 'header',
                'required': True,
                'description': 'Options are: Web or Application or Backoffice. Example: Software-Type=Web.',
                'schema': {'type': 'string'}
            }]

        if self.query_parameters:
            for query_param in self.query_parameters:
                parameters += [{
                    'name': query_param['name'],
                    'in': 'query',
                    'required': query_param['required'] if 'required' in query_param.keys() else False,
                    'description': query_param['description'],
                    'schema': {'type': 'string'}
                }]
        return parameters

    def _custom_response(self, responses):
        custom_response = {}
        for status, res in responses.items():
            if 'serializer' not in res.keys():
                custom_response[status] = res
                continue

            serializer = res['serializer']()
            description = res['description'] if 'description' in res.keys() else ''
            custom_response[status] = {
                'content': {
                    'application/json': {
                        'schema': self.map_serializer(serializer)
                    }
                },
                'description': description
            }

        return custom_response

    def map_field(self, field):
        """
            This function was obtained from the django rest framework and
            the only part changed was the addition of the if clause for
            the serializers.JSONField
        """
        # Nested Serializers, `many` or not.
        if isinstance(field, serializers.ListSerializer):
            return {
                'type': 'array',
                'items': self.map_serializer(field.child)
            }
        if isinstance(field, serializers.Serializer):
            data = self.map_serializer(field)
            data['type'] = 'object'
            return data

        # Related fields.
        if isinstance(field, serializers.ManyRelatedField):
            return {
                'type': 'array',
                'items': self.map_field(field.child_relation)
            }
        if isinstance(field, serializers.PrimaryKeyRelatedField):
            model = getattr(field.queryset, 'model', None)
            if model is not None:
                model_field = model._meta.pk
                if isinstance(model_field, models.AutoField):
                    return {'type': 'integer'}

        # ChoiceFields (single and multiple).
        # Q:
        # - Is 'type' required?
        # - can we determine the TYPE of a choicefield?
        if isinstance(field, serializers.MultipleChoiceField):
            return {
                'type': 'array',
                'items': self.map_choicefield(field)
            }

        if isinstance(field, serializers.ChoiceField):
            return self.map_choicefield(field)

        # ListField.
        if isinstance(field, serializers.ListField):
            mapping = {
                'type': 'array',
                'items': {},
            }
            if not isinstance(field.child, _UnvalidatedField):
                mapping['items'] = self.map_field(field.child)
            return mapping

        # DateField and DateTimeField type is string
        if isinstance(field, serializers.DateField):
            return {
                'type': 'string',
                'format': 'date',
            }

        if isinstance(field, serializers.DateTimeField):
            return {
                'type': 'string',
                'format': 'date-time',
            }

        # "Formats such as "email", "uuid", and so on, MAY be used even though undefined by this specification."
        # see: https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#data-types
        # see also: https://swagger.io/docs/specification/data-models/data-types/#string
        if isinstance(field, serializers.EmailField):
            return {
                'type': 'string',
                'format': 'email'
            }

        if isinstance(field, serializers.URLField):
            return {
                'type': 'string',
                'format': 'uri'
            }

        if isinstance(field, serializers.UUIDField):
            return {
                'type': 'string',
                'format': 'uuid'
            }

        if isinstance(field, serializers.IPAddressField):
            content = {
                'type': 'string',
            }
            if field.protocol != 'both':
                content['format'] = field.protocol
            return content

        if isinstance(field, serializers.DecimalField):
            if getattr(field, 'coerce_to_string', api_settings.COERCE_DECIMAL_TO_STRING):
                content = {
                    'type': 'string',
                    'format': 'decimal',
                }
            else:
                content = {
                    'type': 'number'
                }

            if field.decimal_places:
                content['multipleOf'] = float('.' + (field.decimal_places - 1) * '0' + '1')
            if field.max_whole_digits:
                content['maximum'] = int(field.max_whole_digits * '9') + 1
                content['minimum'] = -content['maximum']
            self._map_min_max(field, content)
            return content

        if isinstance(field, serializers.FloatField):
            content = {
                'type': 'number',
            }
            self._map_min_max(field, content)
            return content

        if isinstance(field, serializers.IntegerField):
            content = {
                'type': 'integer'
            }
            self._map_min_max(field, content)
            # 2147483647 is max for int32_size, so we use int64 for format
            if int(content.get('maximum', 0)) > 2147483647 or int(content.get('minimum', 0)) > 2147483647:
                content['format'] = 'int64'
            return content

        if isinstance(field, serializers.FileField):
            return {
                'type': 'string',
                'format': 'binary'
            }

        if isinstance(field, serializers.JSONField) and field.help_text and '{' in field.help_text:
            try:
                json_field_schema = json.loads(field.help_text)
                if 'default' in json_field_schema.keys():
                    json_field_schema.pop("default")
                if 'additionalProperties' in json_field_schema.keys():
                    json_field_schema.pop("additionalProperties")
                return json_field_schema
            except Exception as e:
                logger.info(f'Error in schema. Converting string to json. {e}')

        # Simplest cases, default to 'string' type:
        FIELD_CLASS_SCHEMA_TYPE = {
            serializers.BooleanField: 'boolean',
            serializers.JSONField: 'object',
            serializers.DictField: 'object',
            serializers.HStoreField: 'object',
        }
        return {'type': FIELD_CLASS_SCHEMA_TYPE.get(field.__class__, 'string')}
