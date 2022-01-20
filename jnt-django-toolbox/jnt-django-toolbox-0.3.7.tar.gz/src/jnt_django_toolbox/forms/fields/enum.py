from django.forms import MultipleChoiceField, TypedChoiceField


class EnumChoiceField(TypedChoiceField):
    """Form field for enum."""


class MultipleEnumChoiceField(MultipleChoiceField):
    """Multiple form field for enum."""

    def __init__(self, enum, *args, **kwargs) -> None:
        """Init MultipleEnumChoiceField."""
        self.enum = enum
        kwargs["choices"] = enum.choices
        super().__init__(*args, **kwargs)
