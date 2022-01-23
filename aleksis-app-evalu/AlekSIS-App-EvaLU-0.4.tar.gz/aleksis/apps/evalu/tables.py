from django.template.loader import render_to_string
from django.utils.translation import gettext as _

import django_tables2 as tables


class EvaluationPartTable(tables.Table):
    """Table to list evaluation parts."""

    class Meta:
        attrs = {"class": "responsive-table highlight"}
        order_by = "order"

    name = tables.LinkColumn("edit_evaluation_part", args=[tables.A("pk")])
    edit = tables.LinkColumn(
        "edit_evaluation_part",
        args=[tables.A("id")],
        text=_("Edit"),
        attrs={"a": {"class": "btn-flat waves-effect waves-orange orange-text"}},
    )
    delete = tables.LinkColumn(
        "delete_evaluation_part",
        args=[tables.A("id")],
        text=_("Delete"),
        attrs={"a": {"class": "btn-flat waves-effect waves-red red-text"}},
    )


class EvaluationPhaseTable(tables.Table):
    """Table to list evaluation phases."""

    class Meta:
        attrs = {"class": "responsive-table highlight"}

    status = tables.Column()
    name = tables.LinkColumn("evaluation_phase", args=[tables.A("id")])

    edit = tables.LinkColumn(
        "edit_evaluation_phase",
        args=[tables.A("id")],
        text=_("Edit"),
        attrs={"a": {"class": "btn-flat waves-effect waves-orange orange-text"}},
    )
    delete = tables.LinkColumn(
        "delete_evaluation_phase",
        args=[tables.A("id")],
        text=_("Delete"),
        attrs={"a": {"class": "btn-flat waves-effect waves-red red-text"}},
    )

    def render_status(self, value, record):
        print(value, record)
        return render_to_string("evalu/phase/status.html", dict(phase=record))
