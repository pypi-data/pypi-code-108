from django.core.validators import RegexValidator

# Regex for locale (Example: pt-PT)
locale_regex = RegexValidator(
    regex='^[a-z]{2}\-[A-Z]{2}$',
    message='Locale must have this format pt-PT',
    code='invalid_locale'
)
