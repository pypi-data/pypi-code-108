import unittest

from mock import Mock, MagicMock

from cloudshell.email.email_config import EmailConfig


class TestEmailConfig(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_initialize_default_port(self):
        self.email_config = EmailConfig('SMTP Host', 'user', 'pass', 'from address')

        self.assertEqual(self.email_config.smtp_server, 'SMTP Host')
        self.assertEqual(self.email_config.user, 'user')
        self.assertEqual(self.email_config.password, 'pass')
        self.assertEqual(self.email_config.from_address, 'from address')
        self.assertEqual(self.email_config.smtp_port, 587)

    def test_initialize_non_default_port(self):
        self.email_config = EmailConfig('SMTP Host', 'user', 'pass', 'from address', 9000)

        self.assertEqual(self.email_config.smtp_server, 'SMTP Host')
        self.assertEqual(self.email_config.user, 'user')
        self.assertEqual(self.email_config.password, 'pass')
        self.assertEqual(self.email_config.from_address, 'from address')
        self.assertEqual(self.email_config.smtp_port, 9000)

    def test_create_from_email_config_resource(self):
        # arrange

        decrypted_pass = Mock()

        email_config_resource = Mock(ResourceModelName="email_config_model")
        smtp_server = Mock(Name=f"{email_config_resource.ResourceModelName}.SMTP Server")
        smtp_port = MagicMock(Name=f"{email_config_resource.ResourceModelName}.SMTP Port")
        from_address = Mock(Name=f"{email_config_resource.ResourceModelName}.From Address")
        user = Mock(Name=f"{email_config_resource.ResourceModelName}.User")
        password = Mock(Name=f"{email_config_resource.ResourceModelName}.Password")
        portal_url = Mock(Name=f"{email_config_resource.ResourceModelName}.Portal URL")
        email_config_resource.ResourceAttributes = [smtp_server, smtp_port, from_address, user, password, portal_url]

        api = Mock()
        api.GetResourceDetails.return_value = email_config_resource
        api.DecryptPassword.return_value = decrypted_pass

        # act
        email_config = EmailConfig.create_from_email_config_resource(api, Mock())

        # assert
        self.assertEqual(smtp_server.Value, email_config.smtp_server)
        self.assertEqual(int(smtp_port.Value), email_config.smtp_port)
        self.assertEqual(from_address.Value, email_config.from_address)
        self.assertEqual(user.Value, email_config.user)
        self.assertEqual(decrypted_pass.Value, email_config.password)
        self.assertEqual(portal_url.Value, email_config.portal_url)

