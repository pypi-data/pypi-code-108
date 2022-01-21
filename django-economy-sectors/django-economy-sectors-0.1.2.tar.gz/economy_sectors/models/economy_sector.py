from typing import Optional

from django.db import models

from economy_sectors.utils import STANDARDS, get_or_none


class EconomySector(models.Model):
    standard = models.IntegerField(
        choices=STANDARDS,
        default=STANDARDS.unspecified,
        help_text="The standard this code is defined by."
    )
    level = models.PositiveSmallIntegerField()
    standard_label = models.CharField(max_length=256)
    english_label = models.CharField(max_length=256, null=True)
    code = models.CharField(max_length=16, help_text="Code as defined by the standard.")
    parent = models.ForeignKey(
        to='self',
        related_name='children',
        null=True,
        on_delete=models.CASCADE
    )
    top_parent = models.ForeignKey(
        to='self',
        related_name='bottom_children',
        null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = [('standard', 'code')]

    def get_corresponding_sector(self, to_standard: STANDARDS) -> Optional['EconomySector']:
        """
        Find the corresponding sector to another standard.

        Args:
            to_standard: The target standard to which we want to convert.
        """

        relation: EconomySectorRelation = get_or_none(
            EconomySectorRelation.objects,
            from_sector=self,
            to_standard=to_standard
        )

        return relation.to_sector if relation else None

    def __str__(self):
        return f'{self.english_label or self.standard_label}-{self.code}'


class EconomySectorRelation(models.Model):
    from_sector = models.ForeignKey(
        to='EconomySector',
        on_delete=models.CASCADE,
        related_name='relations_as_from',
        help_text="The economy sector we want to convert."
    )
    to_standard = models.IntegerField(
        choices=STANDARDS,
        help_text="The standard to which the conversion is happening."
    )
    to_sector = models.ForeignKey(
        to='EconomySector',
        on_delete=models.CASCADE,
        related_name='relations_as_to',
        help_text="The corresponding sector in the required standard."
    )

    class Meta:
        unique_together = [('from_sector', 'to_standard', 'to_sector')]

    def __str__(self):
        return f'{self.from_sector.code}-{self.to_sector.code}'
