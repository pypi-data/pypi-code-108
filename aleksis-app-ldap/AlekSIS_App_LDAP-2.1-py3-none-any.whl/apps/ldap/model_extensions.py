from django.utils.translation import gettext_lazy as _

from jsonstore import CharField

from aleksis.core.models import Group, Person

# Fields as import refs for LDAP objects
Group.field(ldap_dn=CharField(verbose_name=_("LDAP Distinguished Name"), blank=True))
Person.field(ldap_dn=CharField(verbose_name=_("LDAP Distinguished Name"), blank=True))
