import fnmatch

from django.db import models
from django.utils.translation import gettext_lazy as _

from admin_sso import settings


class AssignmentManager(models.Manager):
    def for_email(self, email):
        try:
            username, domain = email.split("@")
        except (AttributeError, TypeError, ValueError):
            return None
        possible_assignments = self.filter(domain=domain)
        used_assignment = None
        for assignment in possible_assignments:
            if assignment.username_mode == settings.ASSIGNMENT_ANY:
                used_assignment = assignment
                break
            elif assignment.username_mode == settings.ASSIGNMENT_MATCH:
                if fnmatch.fnmatch(username, assignment.username):
                    used_assignment = assignment
                    break
            elif assignment.username_mode == settings.ASSIGNMENT_EXCEPT:
                if not fnmatch.fnmatch(username, assignment.username):
                    used_assignment = assignment
                    break
        if used_assignment is None:
            return None
        return used_assignment


class Assignment(models.Model):
    username_mode = models.IntegerField(choices=settings.ASSIGNMENT_CHOICES)
    username = models.CharField(max_length=255, blank=True)
    domain = models.CharField(max_length=255)
    copy = models.BooleanField(default=False)
    weight = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("-weight",)
        verbose_name = _("Assignment")
        verbose_name_plural = _("Assignments")

    def __str__(self):
        return "{}({}) @{}".format(
            dict(settings.ASSIGNMENT_CHOICES)[self.username_mode],
            self.username,
            self.domain,
        )

    objects = AssignmentManager()
