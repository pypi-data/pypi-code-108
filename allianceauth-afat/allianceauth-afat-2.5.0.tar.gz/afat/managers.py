"""
Managers for our models
"""

# Django
from django.db import models
from django.db.models import Count, F


class AFatLinkQuerySet(models.QuerySet):
    """
    AFatLinkQuerySet
    """

    def annotate_afats_count(self):
        """
        Annotate the amount fats per fat link
        :return:
        :rtype:
        """

        return self.annotate(afats_count=Count(F("afats")))


class AFatLinkManager(models.Manager):
    """
    AFatLinkManager
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Integrate custom QuerySet methods.
        """

        return AFatLinkQuerySet(self.model, using=self._db)

    def select_related_default(self):
        """
        Apply select_related for default query optimizations.
        """

        return self.select_related(
            "link_type", "creator", "character", "creator__profile__main_character"
        )


class AFatManager(models.Manager):
    """
    AFatManager
    """

    def select_related_default(self):
        """
        Apply select_related for default query optimizations.
        """

        return self.select_related("afatlink", "afatlink__link_type", "character")
