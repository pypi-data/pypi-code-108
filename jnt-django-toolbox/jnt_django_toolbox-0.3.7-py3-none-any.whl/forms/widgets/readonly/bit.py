from typing import Optional

from jnt_django_toolbox.forms.widgets.readonly.base import BaseReadOnlyWidget


class BitFieldReadOnlyWidget(BaseReadOnlyWidget):
    """Readonly widget for bit field."""

    empty_value = "-"

    def __init__(self, formfield=None) -> None:
        """Initializing."""
        self._formfield = formfield

    def render(self, field_value, field_name, **kwargs) -> Optional[str]:
        """Render html-string."""
        checked_values = [
            choice for choice, checked in list(field_value.items()) if checked
        ]

        if not checked_values:
            return self.empty_value

        return ", ".join(
            (
                str(field_value._labels[field_value.keys().index(choice)])
                for choice in checked_values
            ),
        )
