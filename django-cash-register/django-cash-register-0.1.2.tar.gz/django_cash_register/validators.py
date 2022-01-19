from django.core.exceptions import ValidationError


def validate_not_minus(value):
    if value <= 0.0:
        raise ValidationError('%(value)s must be greater than 0', params={'value': value},)
