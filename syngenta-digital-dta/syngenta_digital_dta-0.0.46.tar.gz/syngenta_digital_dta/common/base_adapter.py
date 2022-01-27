from syngenta_digital_dta.common import publisher


class BaseAdapter:

    def __init__(self, **kwargs):
        self.sns_arn = kwargs.get('sns_arn')
        self.sns_custom = kwargs.get('sns_attributes', {})
        self.sns_defaults = kwargs.get('sns_default_attributes', True)
        self.sns_endpoint = kwargs.get('sns_endpoint')
        self.publisher = publisher
        self.default_attributes = {
            'model_schema': kwargs.get('model_schema'),
            'model_identifier': kwargs.get('model_identifier'),
            'model_version_key': kwargs.get('model_version_key'),
            'author_identifier': kwargs.get('author_identifier')
        }

    def publish(self, operation, data):
        attributes = self.create_format_attibutes(operation)
        self.publisher.publish(
            endpoint=self.sns_endpoint,
            arn=self.sns_arn,
            attributes=attributes,
            data=data
        )

    def create_format_attibutes(self, operation):
        self.default_attributes['operation'] = operation
        custom_attributes = self.get_attributes()
        formatted_attributes = {}
        for key, value in custom_attributes.items():
            if value is not None:
                data_type = 'String' if isinstance(value, str) else 'Number'
                formatted_attributes[key] = {
                    'DataType': data_type,
                    'StringValue': value
                }
        return formatted_attributes

    def get_attributes(self):
        if self.sns_defaults and self.sns_custom:
            return {**self.default_attributes, **self.sns_custom}
        if not self.sns_defaults and self.sns_custom:
            return self.sns_custom
        if self.sns_defaults and not self.sns_custom:
            return self.default_attributes
        return {}
