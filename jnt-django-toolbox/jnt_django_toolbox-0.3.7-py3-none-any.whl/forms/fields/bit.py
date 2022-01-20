from collections.abc import Iterable

from django.forms import IntegerField, ValidationError
from django.utils.functional import empty

from jnt_django_toolbox.forms.widgets.readonly import BitFieldReadOnlyWidget
from jnt_django_toolbox.models.fields.bit.types import BitHandler


class BitFieldFormField(IntegerField):
    """Form field for bit field."""

    readonly_widget = BitFieldReadOnlyWidget

    def __init__(self, choices=(), widget=empty, *args, **kwargs):
        """Initializing."""
        from jnt_django_toolbox.forms.widgets import BitFieldWidget

        if widget is empty:
            widget = BitFieldWidget

        if isinstance(kwargs["initial"], int):
            iv = kwargs["initial"]
            iv_list = []
            for i in range(0, min(len(choices), 63)):
                if (1 << i) & iv > 0:
                    iv_list += [choices[i][0]]
            kwargs["initial"] = iv_list
        self.widget = widget
        super().__init__(widget=widget, *args, **kwargs)
        self.choices = choices
        self.widget.choices = choices

    def clean(self, value):
        """Validate value."""
        if not value:
            return 0

        # Assume an iterable which contains an item per flag that's enabled
        result = BitHandler(0, [key for key, value in self.choices])
        for k in value:
            try:
                setattr(result, str(k), True)
            except AttributeError:
                raise ValidationError("Unknown choice: {0}".format(k))
        return int(result)

    def has_changed(self, initial, data):
        """Check changed field."""
        changed = super().has_changed(initial, data)
        if changed:
            changed = self._has_changed(initial, data)

        return changed

    def _has_changed(self, initial, data) -> bool:
        """Check is changed field."""
        initial_value = 0

        if isinstance(initial, BitHandler):
            initial_value = int(initial)
        elif isinstance(initial, Iterable):
            initial_value = self.clean(initial)

        return self.clean(data) != initial_value
