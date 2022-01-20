from django.forms import CheckboxSelectMultiple
from django.utils.encoding import force_text

from jnt_django_toolbox.models.fields.bit.types import BitHandler


class BitFieldWidget(CheckboxSelectMultiple):
    """Widget for bit field."""

    def render(self, name, value, attrs=None, choices=(), renderer=None):
        """Render widget."""
        if isinstance(value, BitHandler):
            value = [k for k, v in value if v]
        elif isinstance(value, int):
            real_value = []
            div = 2
            for k, _ in self.choices:
                if value % div != 0:
                    real_value.append(k)
                    value -= value % div
                div *= 2
            value = real_value
        return super().render(name, value, attrs=attrs)

    def _has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if initial != data:
            return True
        initial_set = {force_text(value) for value in initial}
        data_set = {force_text(value) for value in data}
        return data_set != initial_set
