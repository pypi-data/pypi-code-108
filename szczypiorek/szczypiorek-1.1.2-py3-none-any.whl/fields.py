
from . import fields_validators as val


class BaseField:

    def __init__(
            self,
            required=True,
            default=None,
            allow_null=False,
            description=None,
            as_env=None,
            as_file=None):

        self.required = required
        self.default = default
        self.allow_null = allow_null
        self.description = description
        self.as_env = as_env
        self.as_file = as_file

    def to_python(self, field_name, value):

        if not self.allow_null:
            val.not_null(field_name, value)

        elif value is None and self.allow_null:
            return val.NULL


class BooleanField(BaseField):

    def to_python(self, field_name, value):

        # -- base validation
        result = super(BooleanField, self).to_python(field_name, value)
        if result == val.NULL:
            return None

        if isinstance(value, bool):
            return value

        if value.upper() == 'TRUE':
            return True

        elif value.upper() == 'FALSE':
            return False

        else:
            raise val.ValidatorError(
                f'env.{field_name}: Cannot cast {value} to boolean')


class CharField(BaseField):

    def __init__(self, min_length=None, max_length=None, **kwargs):
        self.min_length = min_length
        self.max_length = max_length
        super(CharField, self).__init__(**kwargs)

    def to_python(self, field_name, value):

        # -- base validation
        result = super(CharField, self).to_python(field_name, value)
        if result == val.NULL:
            return None

        val.length(
            field_name,
            value,
            min_length=self.min_length,
            max_length=self.max_length)

        return value


class FloatField(BaseField):

    def to_python(self, field_name, value):

        # -- base validation
        result = super(FloatField, self).to_python(field_name, value)
        if result == val.NULL:
            return None

        try:
            return float(value)

        except ValueError:
            raise val.ValidatorError(
                f'env.{field_name}: Cannot cast {value} to float')


class IntegerField(BaseField):

    def to_python(self, field_name, value):

        # -- base validation
        result = super(IntegerField, self).to_python(field_name, value)
        if result == val.NULL:
            return None

        try:
            return int(float(value))

        except ValueError:
            raise val.ValidatorError(
                f'env.{field_name}: Cannot cast {value} to integer')


class URLField(BaseField):

    def to_python(self, field_name, value):

        # -- base validation
        result = super(URLField, self).to_python(field_name, value)
        if result == val.NULL:
            return None

        val.url(field_name, value)

        return value
