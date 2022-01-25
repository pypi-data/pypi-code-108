from whizbang.config.app_config import AppConfig
from whizbang.domain.handler.handler_base import HandlerBase
from whizbang.domain.manager.az.az_webapp_manager import AzWebappManager
from whizbang.domain.models.webapp_settings import WebappSettings


class WebappHandler(HandlerBase):
    def __init__(self, app_config: AppConfig, manager: AzWebappManager):
        HandlerBase.__init__(self, app_config=app_config)
        self.manager = manager

    def add_setting(self, setting_key: str,
                    setting_value: str,
                    resource_group: str,
                    webapp_name: str):
        webapp_settings = WebappSettings(resource_group=resource_group,
                                         webapp_name=webapp_name,
                                         setting_key=setting_key,
                                         setting_value=setting_value)
        return self.manager.add_setting(settings=webapp_settings)

    def set_continuous_deployment(self, enable_continuous_deployment: bool,
                                  webapp_name: str,
                                  resource_group_name: str,
                                  deployment_slot_name: str = 'production'):
        return self.manager.set_continuous_deployment(enable_continuous_deployment=enable_continuous_deployment,
                                                      webapp_name=webapp_name,
                                                      resource_group_name=resource_group_name,
                                                      deployment_slot_name=deployment_slot_name)

    def swap_deployment_slot(self, deployment_slot_name: str,
                             webapp_name: str,
                             resource_group_name: str):
        return self.manager.swap_deployment_slot(deployment_slot_name=deployment_slot_name,
                                                 webapp_name=webapp_name,
                                                 resource_group_name=resource_group_name)
