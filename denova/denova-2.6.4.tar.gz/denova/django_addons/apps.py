try:
    from django.apps import AppConfig
    from django.utils.translation import gettext_lazy as _
except ModuleNotFoundError:
    import sys
    sys.exit('Django required')

class DjangoAddonsConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'denova.django_addons'
    verbose_name = _("Django Addons")
