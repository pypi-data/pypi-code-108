from __future__ import annotations
from typing import Dict

from cloudshell.api.cloudshell_api import CloudShellAPISession

from cloudshell.email.email_helpers import get_resource_attribute_value


class EmailConfig:
    def __init__(self, smtp_server: str, user: str, password: str, from_address: str, smtp_port=587,
                 portal_url: str = '', default_subject: str = '', default_html: str = '',
                 default_parameters: Dict[str, str] = {}):
        """
        :param smtp_server:
        :param user: must in an email_service address format
        :param password: password for user email_service addressx`
        :param from_address: the address to be used as the sender
        :param smtp_port:
        """
        self.smtp_server = smtp_server
        self.user = user
        self.password = password
        self.from_address = from_address
        self.smtp_port = smtp_port
        self.portal_url = portal_url
        self.default_subject = default_subject
        self.default_html = default_html
        self.default_parameters = default_parameters

    @staticmethod
    def create_from_email_config_resource(api: CloudShellAPISession, email_config_resource_name: str) -> EmailConfig:
        config_resource = api.GetResourceDetails(email_config_resource_name)

        smtp_server = get_resource_attribute_value(config_resource, "SMTP Server")
        smtp_port = int(get_resource_attribute_value(config_resource, "SMTP Port"))
        from_address = get_resource_attribute_value(config_resource, "From Address")
        user = get_resource_attribute_value(config_resource, "User")
        password_encrypted = get_resource_attribute_value(config_resource, "Password")
        password = api.DecryptPassword(password_encrypted).Value
        portal_url = get_resource_attribute_value(config_resource, "Portal URL")

        return EmailConfig(smtp_server, user, password, from_address, smtp_port, portal_url)
