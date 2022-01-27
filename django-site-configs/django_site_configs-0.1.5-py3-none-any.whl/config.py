from django.core.exceptions import ObjectDoesNotExist
from .models import SiteConfigModel

class SiteConfigBaseClass():
    key = None
    label = None
    site = None
    instance = None
    value = dict()
    default = dict()
    form_class = None
    is_superuser_config = False

    def __init__(self, site, key):
        self.site = site
        try:
            site_conf = SiteConfigModel.objects.get(site=site, key=key)
            self.instance = site_conf
            self.value = site_conf.value
        except ObjectDoesNotExist:
            pass

    def get_key_value(self, key=None):
        if key:
            return self.value.get(key, self.default.get(key))
        elif self.value:
            return self.value
        return self.default

    # can pass in a dictionary or a single key and value
    # easier to accomodate settings with multiple values
    def save(self, data, value_key = None):
        config, created = SiteConfigModel.objects.get_or_create(site=self.site, key=self.key)
        if value_key:
            config.value.update({
                value_key: data
            })
        elif isinstance(data, dict):
            config.value.update(data)
        config.save()
        self.instance = config
        self.value = config.value

    def delete(self):
        if self.instance:
            self.instance.delete()
            self.instance = None
            self.value = dict()

    
