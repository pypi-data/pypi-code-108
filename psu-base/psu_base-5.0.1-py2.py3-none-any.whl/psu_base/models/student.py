from django.db import models
from psu_base.classes.Log import Log

log = Log()


class Student(models.Model):
    """Generic Student Identity Record"""

    date_created = models.DateTimeField(auto_now_add=True)

    email_address = models.CharField(max_length=128, blank=False, null=False)
    alt_email_address = models.CharField(max_length=128, blank=True, null=True)

    pidm = models.IntegerField(blank=False, null=False)
    username = models.CharField(max_length=128, blank=False, null=False, db_index=True)
    psu_id = models.CharField(max_length=9, blank=False, null=False, db_index=True)

    # Store name here for searching registrations
    first_name = models.CharField(max_length=60, blank=True, null=True, db_index=True)
    last_name = models.CharField(max_length=60, blank=True, null=True, db_index=True)

    def emails(self):
        """Get a list of known emails"""
        email_list = [self.email_address]
        if self.alt_email_address:
            email_list.append(self.alt_email_address)
        return list(set(email_list))

    def display_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __repr__(self):
        return f"Student: {self}"

    def __str__(self):
        return f"{self.display_name()} ({self.username})"

    @classmethod
    def get(cls, pk):
        """
        Get Student from ID
        """
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_psu_id(cls, psu_id):
        """
        Get Student from ID
        """
        try:
            return cls.objects.get(psu_id=psu_id)
        except cls.DoesNotExist:
            return None
