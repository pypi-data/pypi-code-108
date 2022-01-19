from django.db import models
from psu_base.classes.Log import Log
from psu_base.services import utility_service

log = Log()


class Error(models.Model):
    """Record an unexpected error"""

    app_code = models.CharField(
        max_length=15,
        verbose_name="Application Code",
        help_text="Application that this error belongs to.",
        blank=False,
        null=False,
    )

    path = models.CharField(
        max_length=128,
        help_text="This holds the path on which the error occurred",
        blank=False,
        null=False,
    )

    parameters = models.CharField(
        max_length=500,
        help_text="This holds the request parameters",
        blank=True,
        null=True,
    )

    code_detail = models.CharField(
        max_length=128,
        help_text="file, function, and line number of error",
        blank=True,
        null=True,
    )

    sso_user = models.CharField(
        max_length=128,
        help_text="This holds the logged-in user (which could be a provisional email address)",
        blank=True,
        null=True,
    )
    impersonated_user = models.CharField(
        max_length=128,
        help_text="This holds the impersonated user (which could be a provisional email address)",
        blank=True,
        null=True,
    )
    proxied_user = models.CharField(
        max_length=128,
        help_text="This holds the proxied user (which could be a provisional email address)",
        blank=True,
        null=True,
    )

    date_created = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=1,
        help_text="Indicates the status of the error (New, Ignored, Resolved)",
        blank=False,
        null=False,
        default="N",
    )

    error_friendly = models.CharField(
        max_length=128, help_text="Error that the user saw", blank=True, null=True
    )
    error_system = models.CharField(
        max_length=128, help_text="Actual system error", blank=True, null=True
    )
    debug_info = models.CharField(
        max_length=128, help_text="Additional debug info", blank=True, null=True
    )
    stacktrace = models.TextField(help_text="StackTrace", blank=True, null=True)
    browser = models.CharField(
        max_length=200, help_text="Browser info", blank=True, null=True
    )

    def stacktrace_html(self):
        if self.stacktrace:
            trace_lines = self.stacktrace.splitlines()
            if len(trace_lines) > 1:
                lines = [
                    f"<b>{trace_lines[0]}</b>",
                    f"""<i style="color:blue;cursor:pointer;" onclick="$('#e-st-{self.id}').removeClass('hidden');">""",
                    f"""show stacktrace</i>"""
                    f'<ul class="list-group hidden" id="e-st-{self.id}">',
                ]
                for ll in trace_lines[1:]:
                    lines.append(f"""<li class="list-group-item">{ll}</li>""")
                lines.append("</ul>")
                return "".join(lines)
        return self.stacktrace if self.stacktrace else ""
