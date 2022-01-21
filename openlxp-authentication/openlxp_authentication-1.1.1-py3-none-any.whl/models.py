from django.conf import settings
from django.db import models
from django.db.models.base import Model
from social_core.backends.saml import SAMLAuth, SAMLIdentityProvider
from social_django.strategy import DjangoStrategy


class SAMLConfiguration(Model):
    """Model for storing SAML configurations in the database"""
    name = models.CharField(unique=True, max_length=50)
    entity_id = models.CharField(max_length=300)
    url = models.URLField()
    cert = models.TextField()

    def attributes():
        """Creates JSON dictionary mapping user attributes"""
        return dict.fromkeys(["attr_" + attr for attr in settings.USER_ATTRIBUTES], '')
    attribute_mapping = models.JSONField(default=attributes)

    def endpoint(self):
        """Returns the relative endpoint to trigger a login using this configuration"""
        return f"/login/{SAMLDBAuth.name}/?idp=" + self.name


class SAMLDBAuth(SAMLAuth):
    """Authentication backend that uses SAML configurations from the database"""
    name = 'samldb'

    def get_idp(self, idp_name):
        conf_name = idp_name.split(
            '/')[-2] if idp_name.split('/')[-1] == '' else idp_name.split('/')[-1]
        idp_config = SAMLConfiguration.objects.get(name=conf_name)
        config_map = {"entity_id": idp_config.entity_id,
                      "url": idp_config.url, "x509cert": idp_config.cert, **idp_config.attribute_mapping}
        return SAMLIdentityProvider(conf_name, **config_map)


class SAMLDBStrategy(DjangoStrategy):
    """Strategy to use a custom hostname and port if provided"""

    def build_absolute_uri(self, path=None):
        baseurl = super().build_absolute_uri(path=path)
        host = getattr(settings, 'OVERIDE_HOST', False)
        replace = getattr(settings, 'BAD_HOST', False)
        if(host != False and replace != False and not (baseurl is None)):
            baseurl = baseurl.replace(replace, host, 1)
        return baseurl

    def request_host(self):
        host = getattr(settings, 'OVERIDE_HOST', False)
        if(host != False):
            return '//'.join(host.split('//')[1:])
        else:
            return super().request_host()

    def request_port(self):
        port = getattr(settings, 'OVERIDE_HOST', False)
        if(port != False):
            return port.split(':')[-1]
        else:
            return super().request_port()
