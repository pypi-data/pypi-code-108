from django.utils.translation import gettext_lazy as _
from danceschool.core.registries import ExtrasTemplateBase, extras_templates_registry

@extras_templates_registry.register
class VaccinationExtrasTemplate(ExtrasTemplateBase):
    template = 'danceschool_dancervax/status_response.html'
    description = _('Vaccination status response from DancerVax')
