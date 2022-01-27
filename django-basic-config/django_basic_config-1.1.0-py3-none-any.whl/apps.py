from django.apps import AppConfig

class Django_ConfigConfig(AppConfig):

    name = 'django_config'

    default_auto_field = 'django.db.models.AutoField'
    # if you have lots of rows:
    # default_auto_field = 'django.db.models.BigAutoField'

#-- END AppConfig class Django_ConfigConfig --#
