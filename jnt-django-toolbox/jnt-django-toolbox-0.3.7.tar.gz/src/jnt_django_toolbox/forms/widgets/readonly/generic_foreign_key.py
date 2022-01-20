from typing import Optional

from django.utils.html import format_html

from jnt_django_toolbox.forms.widgets.readonly.base import BaseReadOnlyWidget
from jnt_django_toolbox.helpers.object_links import object_change_link


class GenericForeignKeyReadonlyWidget(BaseReadOnlyWidget):
    """Generic foreign key readonly widget."""

    def render(self, field_value, field_name, **kwargs) -> Optional[str]:
        """Render foreign key field."""
        if not field_value:
            return None

        return format_html(
            '<span class="gfk-object-type">{0}</span> {1}'.format(
                field_value._meta.model_name,
                object_change_link(field_value),
            ),
        )
