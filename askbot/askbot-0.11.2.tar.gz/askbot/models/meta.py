"""Models that are not essential to operation of
an askbot instance, but may be used in some cases.
Data in these models can be erased without loss of function.
"""
from django.db import models
from picklefield.fields import PickledObjectField

class ImportRun(models.Model):
    """records information about the data import run"""
    command = models.TextField(default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'askbot'

class ImportedObjectInfo(models.Model):
    """records data about objects imported into askbot
    from other sources.
    This is useful to create redirect urls when object id's change
    """
    old_id = models.IntegerField(help_text='Old object id in the source database')
    new_id = models.IntegerField(help_text='New object id in the current database')
    model = models.CharField(
                default='',
                help_text='dotted python path to model',
                max_length=255
            )
    run = models.ForeignKey(ImportRun, on_delete=models.CASCADE)
    extra_info = PickledObjectField(help_text='to hold dictionary for various data')

    class Meta:
        app_label = 'askbot'
