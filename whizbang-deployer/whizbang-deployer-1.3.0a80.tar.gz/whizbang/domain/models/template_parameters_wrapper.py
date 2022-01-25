from whizbang.domain.models.json_serializable import JsonSerializable
from whizbang.domain.models.template_parameters_base import TemplateParametersBase


class TemplateParametersWrapper(JsonSerializable):
    def __init__(self, parameters: TemplateParametersBase = None):
        self.schema = 'https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#'
        self.contentVersion = '1.0.0.0'
        self.parameters = parameters
