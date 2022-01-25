import unittest
from unittest.mock import patch, mock_open, MagicMock

from mock import Mock, ANY

from cloudshell.email.email_service import EmailService
import smtplib

default_html = '''
<!DOCTYPE html>
<html lang="en">
<div>
    <h2 style="text-align: center;"><span style="color: #F76723;"><strong>Welcome to cloudshell-email</strong></span></h2>
</div>
<div>
    <p><span style="color: #000000;">This is the default html template using the cloudshell-email package.</span></p>
</div>
<div>
    <p><span style="color: #000000;">The cloudshell-email package can be used to send emails to users from orchestration scripts.</span></p>
</div>
<div>
    <p><span style="color: #000000;"><strong>You can view cloudshell-email usage guide here:</strong></span></p>
</div>
<div>
    <span style="color: #000000;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <a href="https://github.com/QualiSystemsLab/cloudshell-email"> Github Repo </a>
    </span>
</div>
</body>
</html>
'''

arg_html = '''
<!DOCTYPE html>
<html lang="en">
<div>
    <h2 style="text-align: center;"><span style="color: #F76723;"><strong>Welcome to Training</strong></span></h2>
</div>
<div>
    <p><span style="color: #000000;">Please retain this email as it is how you will access your online lab environment. It also contains your credentials (if needed) and links to helpful materials.</span></p>
</div>
<div>
    <p><span style="color: #000000;">I&rsquo;m looking forward to our class together</span></p>
</div>
<div>
    <p><span style="color: #000000;"><strong>To access your CloudShell Environment please use the following:</strong></span></p>
</div>
<div>
    <span style="color: #000000;"><span style="color: #F76723;"><strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Environment details:</strong></span></span><br>
</div>
<div>
    <span style="color: #000000;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <a href="{sandbox_link}"> Environment Link </a>
    </span>
</div>
</body>
</html>
'''

not_default_html = '''
{sandbox_link}
'''

args_html = '''
{arg1}
{arg2}
{arg3}
'''


class TestEmailService(unittest.TestCase):

    def setUp(self) -> None:
        self.email_config = Mock()
        self.logger = Mock()
        self.email_service = EmailService(self.email_config, self.logger)

    def test_send_no_email_address(self):
        # arrange
        self.email_service._load_and_format_template = Mock()
        self.email_service._send = Mock()

        # act
        excepted = False
        try:
            self.email_service.send_email([], Mock())
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], 'Empty list of email addresses')

        # assert
        self.assertTrue(excepted)
        self.email_service._load_and_format_template.assert_not_called()
        self.email_service._send.assert_not_called()

    def test_send_email_invalid_address(self):
        # arrange
        self.email_service._load_and_format_template = Mock()
        self.email_service._send = Mock()
        invalid_email = 'aaa@bbb'

        # act
        excepted = False
        try:
            self.email_service.send_email([invalid_email], Mock())
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], 'aaa@bbb is not a valid email address')

        # assert
        self.assertTrue(excepted)
        self.email_service._load_and_format_template.assert_not_called()
        self.email_service._send.assert_not_called()

    def test_send_email_valid_and_invalid_address(self):
        # arrange
        self.email_service._load_and_format_template = Mock()
        self.email_service._send = Mock()
        valid_email = 'aaa@bbb.com'
        invalid_email = 'aaa@bbb'

        # act
        excepted = False
        try:
            self.email_service.send_email([valid_email, invalid_email], Mock())
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], 'aaa@bbb is not a valid email address')

        # assert
        self.assertTrue(excepted)
        self.email_service._load_and_format_template.assert_not_called()
        self.email_service._send.assert_not_called()

    def test_send_email_mulitple_valid_and_invalid_address(self):
        # arrange
        self.email_service._load_and_format_template = Mock()
        self.email_service._send = Mock()
        valid_email = 'aaa@bbb.com'
        valid_email2 = 'aaa2@bbb.com'
        valid_email3 = 'aaa3@bbb.com'
        invalid_email = 'aaa@bbb'
        invalid_email2 = 'aaa2@bbb'
        invalid_email3 = 'aaa3@bbb'

        emails = [invalid_email, invalid_email2, valid_email, valid_email2, invalid_email3, valid_email3]

        # act
        excepted = False
        try:
            self.email_service.send_email(emails, Mock())
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], 'aaa@bbb,aaa2@bbb,aaa3@bbb are not valid email addresses')

        # assert
        self.assertTrue(excepted)
        self.email_service._load_and_format_template.assert_not_called()
        self.email_service._send.assert_not_called()

    def test_cc_send_email_mulitple_valid_and_invalid_address(self):
        # arrange
        self.email_service._load_and_format_template = Mock()
        self.email_service._send = Mock()
        valid_email = 'aaa@bbb.com'
        valid_email2 = 'aaa2@bbb.com'
        valid_email3 = 'aaa3@bbb.com'
        invalid_email = 'aaa@bbb'
        invalid_email2 = 'aaa2@bbb'
        invalid_email3 = 'aaa3@bbb'

        emails = [invalid_email, invalid_email2, valid_email, valid_email2, invalid_email3, valid_email3]

        # act
        excepted = False
        try:
            self.email_service.send_email([valid_email], Mock(), cc_email_address=emails)
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], 'aaa@bbb,aaa2@bbb,aaa3@bbb are not valid email addresses')

        # assert
        self.assertTrue(excepted)
        self.email_service._load_and_format_template.assert_not_called()
        self.email_service._send.assert_not_called()

    def test_cc_send_email_valid(self):
        # arrange
        self.email_service._load_and_format_template = Mock()
        self.email_service._send = Mock()
        self.email_service._email_config.default_html = None
        valid_email = 'aaa@bbb.com'

        # act
        self.email_service.send_email([valid_email], Mock())

        # assert
        self.email_service._load_and_format_template.assert_called_once()
        self.email_service._send.assert_called_once()

    def test_is_valid_email_address_pass(self):
        valid_emails = ["aaa@bbb.com", "a@a-bc.info", "x@y.zz", "x@a123.yy"]

        for email in valid_emails:
            self.assertTrue(
                EmailService.is_valid_email_address(email))

    def test_is_valid_email_address_fail(self):
        invalid_emails = ["a.b@", "a.b", "ab", "a@b", "@", "@abc.com", "@abc",
                          "a@a$.com", "a@!.com", "a@sdsd&.com", "a@_.com", "abc@dsds.-com"]

        for email in invalid_emails:
            result = self.email_service.is_valid_email_address(email)
            self.assertFalse(result)

    def test_load_default_template(self):
        # arrange
        self.email_service._send = Mock()

        # act
        content = self.email_service._load_and_format_template('default')

        # assert
        self.assertEqual(content, default_html)

    def test_load_template(self):
        # arrange
        self.email_service._send = Mock()

        arg = dict()
        arg['sandbox_link'] = 'Portal Link'

        # act
        with patch("builtins.open", mock_open(read_data=not_default_html)) as mock_file:
            content = self.email_service._load_and_format_template('', **arg)

        # assert
        self.assertEqual(content, not_default_html.format(**arg))

    def test_load_template_with_args(self):
        # arrange
        self.email_service._send = Mock()

        extra_args = dict()
        extra_args['arg1'] = 'argument1'
        extra_args['arg2'] = 'argument2'
        extra_args['arg3'] = 'argument3'

        # act
        with patch("builtins.open", mock_open(read_data=args_html)) as mock_file:
            content = self.email_service._load_and_format_template('', **extra_args)

        # assert
        self.assertEqual(content, args_html.format(**extra_args))

    @patch('builtins.open', side_effect=Exception())
    def test_load_template_exception(self, mock_open):
        # arrange
        self.email_service._send = Mock()

        # act
        excepted = False
        try:
            self.email_service._load_and_format_template('')
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], 'Failed loading email template')
        self.assertTrue(excepted)

    @patch('smtplib.SMTP')
    def test_send(self, mock_smtp):
        # arrange
        email = 'aaa@bbb.com'
        self.email_service._email_config.from_address = 'aaa@bbb.com'

        mock_smtp.return_value = Mock()

        # act
        self.email_service._send([email], 'Default Subject', arg_html, [email])

        # assert
        mock_smtp.return_value.ehlo.assert_called_once()
        mock_smtp.return_value.starttls.assert_called_once()
        mock_smtp.return_value.login.assert_called_once()
        mock_smtp.return_value.sendmail.assert_called_once()
        mock_smtp.return_value.close.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_smtprecipientsrefused(self, mock_smtp):
        # arrange
        from_address = 'aaa@bbb.com'
        to_address = 'ccc@ddd.com'
        cc = 'eee@fff.com'
        self.email_service._email_config.from_address = from_address
        smtp_obj = Mock()
        smtp_obj.sendmail.side_effect = smtplib.SMTPRecipientsRefused('Failed to send email: '
                                                                      'All recipients were refused.')
        mock_smtp.return_value = smtp_obj

        # act
        # assert
        with self.assertRaises(smtplib.SMTPRecipientsRefused) as cm:
            self.email_service._send([to_address], 'Default Subject', arg_html, [cc])
        self.assertEqual(
            str(cm.exception.args[0]),
            'Failed to send email: All recipients were refused.'
        )

    @patch('smtplib.SMTP')
    def test_send_smtpsenderrefused(self, mock_smtp):
        # arrange
        from_address = 'aaa@bbb.com'
        to_address = 'ccc@ddd.com'
        cc = 'eee@fff.com'
        self.email_service._email_config.from_address = from_address
        smtp_obj = Mock()
        smtp_obj.sendmail.side_effect = smtplib.SMTPSenderRefused('-1',
                                                                  'The server didn\'t accept the '
                                                                  'from_addr.',
                                                                  from_address)
        mock_smtp.return_value = smtp_obj

        # act
        # assert
        with self.assertRaises(smtplib.SMTPSenderRefused) as cm:
            self.email_service._send([to_address], 'Default Subject', arg_html, [cc])
        self.assertEqual(
            str(cm.exception.args[1]),
            'The server didn\'t accept the from_addr.'
        )

    @patch('smtplib.SMTP')
    def test_send_smtpdataerror(self, mock_smtp):
        # arrange
        from_address = 'aaa@bbb.com'
        to_address = 'ccc@ddd.com'
        cc = 'eee@fff.com'
        self.email_service._email_config.from_address = from_address
        smtp_obj = Mock()
        smtp_obj.sendmail.side_effect = smtplib.SMTPDataError('-1',
                                                              'The server replied with an '
                                                              'unexpected error code.')
        mock_smtp.return_value = smtp_obj

        # act
        # assert
        with self.assertRaises(smtplib.SMTPDataError) as cm:
            self.email_service._send([to_address], 'Default Subject', arg_html, [cc])
        self.assertEqual(
            str(cm.exception.args[1]),
            'The server replied with an unexpected error code.'
        )

    @patch('smtplib.SMTP')
    def test_send_smtpnotsupportederror(self, mock_smtp):
        # arrange
        from_address = 'aaa@bbb.com'
        to_address = 'ccc@ddd.com'
        cc = 'eee@fff.com'
        self.email_service._email_config.from_address = from_address
        smtp_obj = Mock()
        smtp_obj.sendmail.side_effect = smtplib.SMTPNotSupportedError('One or more source or '
                                                                      'delivery addresses require '
                                                                      'internationalized email '
                                                                      'support, but the server '
                                                                      'does not advertise the '
                                                                      'required SMTPUTF8 capability.')
        mock_smtp.return_value = smtp_obj

        # act
        # assert
        with self.assertRaises(smtplib.SMTPNotSupportedError) as cm:
            self.email_service._send([to_address], 'Default Subject', arg_html, [cc])
        self.assertEqual(
            str(cm.exception.args[0]),
            'One or more source or delivery addresses require internationalized email support, '
            'but the server does not advertise the required SMTPUTF8 capability.'
        )

    def test_is_email_configured(self):
        self.assertTrue(self.email_service.is_email_configured())

    def test_is_not_email_configured(self):
        self.email_service._email_config = None
        self.assertFalse(self.email_service.is_email_configured())

    @patch('smtplib.SMTP')
    def test_validate_email_config(self, mock_smtp):
        # arrange
        mock_smtp.return_value = Mock()

        # act
        self.email_service.validate_email_config()

        # assert
        mock_smtp.return_value.ehlo.assert_called_once()
        mock_smtp.return_value.starttls.assert_called_once()
        mock_smtp.return_value.login.assert_called_once()
        mock_smtp.return_value.close.assert_called_once()

    @patch('smtplib.SMTP')
    def test_validate_email_config_smtpheloerror(self, mock_smtp):
        # arrange
        smtp_obj = Mock()
        smtp_obj.login.side_effect = smtplib.SMTPHeloError('-1', 'Failed to login to SMTP server')
        mock_smtp.return_value = smtp_obj

        # act
        # assert
        with self.assertRaises(smtplib.SMTPHeloError) as cm:
            self.email_service.validate_email_config()
        self.assertEqual(
            str(cm.exception.args[1]),
            'Failed to login to SMTP server'
        )

    @patch('smtplib.SMTP')
    def test_validate_email_config_smtpauthenticationerror(self, mock_smtp):
        # arrange
        smtp_obj = Mock()
        smtp_obj.login.side_effect = smtplib.SMTPAuthenticationError('-1',
                                                                     'The server didn\'t accept '
                                                                     'the username/password '
                                                                     'combination.')
        mock_smtp.return_value = smtp_obj

        # act
        # assert
        with self.assertRaises(smtplib.SMTPAuthenticationError) as cm:
            self.email_service.validate_email_config()
        self.assertEqual(
            str(cm.exception.args[1]),
            'The server didn\'t accept the username/password combination.'
        )

    @patch('smtplib.SMTP')
    def test_validate_email_config_smtpnotsupportederror(self, mock_smtp):
        # arrange
        smtp_obj = Mock()
        smtp_obj.login.side_effect = smtplib.SMTPNotSupportedError('SMTP AUTH extension not '
                                                                   'supported by server.')
        mock_smtp.return_value = smtp_obj

        # act
        # assert
        with self.assertRaises(smtplib.SMTPNotSupportedError) as cm:
            self.email_service.validate_email_config()
        self.assertEqual(
            str(cm.exception.args[0]),
            'SMTP AUTH extension not supported by server.'
        )

    @patch('smtplib.SMTP')
    def test_validate_email_config_smtpexception(self, mock_smtp):
        # arrange
        smtp_obj = Mock()
        smtp_obj.login.side_effect = smtplib.SMTPException('No suitable authentication method found.')
        mock_smtp.return_value = smtp_obj

        # act
        # assert
        with self.assertRaises(smtplib.SMTPException) as cm:
            self.email_service.validate_email_config()
        self.assertEqual(
            str(cm.exception.args[0]),
            'No suitable authentication method found.'
        )

    @patch('smtplib.SMTP')
    def test_validate_email_config_runtimeerror(self, mock_smtp):
        # arrange
        smtp_obj = Mock()
        smtp_obj.login.side_effect = RuntimeError('No SSL support included in this Python.')
        mock_smtp.return_value = smtp_obj

        # act
        # assert
        with self.assertRaises(RuntimeError) as cm:
            self.email_service.validate_email_config()
        self.assertEqual(
            str(cm.exception.args[0]),
            'No SSL support included in this Python.'
        )

    def test_send_error_email_raise_error_no_api(self):
        with self.assertRaisesRegex(ValueError, "CloudShell Automation API is required"):
            self.email_service.send_error_email(Mock(), Mock())

    def test_send_error_email(self):
        # arrange
        api = Mock()
        api.GetReservationDetails.return_value.ReservationDescription.TopologiesInfo = MagicMock()
        self.email_service = EmailService(self.email_config, self.logger, api)
        self.email_service.send_email = Mock()
        to_email_address = Mock()
        sandbox_id = Mock()

        # act
        self.email_service.send_error_email(to_email_address, sandbox_id)

        # assert
        self.email_service.send_email.assert_called_once()

    def test_send_error_email_gets_exc_info(self):
        # arrange
        api = Mock()
        api.GetReservationDetails.return_value.ReservationDescription.TopologiesInfo = MagicMock()
        self.email_service = EmailService(self.email_config, self.logger, api)
        self.email_service.send_email = Mock()
        to_email_address = Mock()
        sandbox_id = Mock()

        # act
        try:
            raise ValueError("some error")
        except:
            self.email_service.send_error_email(to_email_address, sandbox_id, get_exc_info=True)

        # assert
        self.email_service.send_email.assert_called_once()
        self.assertEqual(self.email_service.send_email.call_args.args[3]['ErrorMessage'], "some error")

    def test_send_error_email_can_override_subject(self):
        # arrange
        api = Mock()
        api.GetReservationDetails.return_value.ReservationDescription.TopologiesInfo = MagicMock()
        self.email_service = EmailService(self.email_config, self.logger, api)
        self.email_service.send_email = Mock()
        to_email_address = Mock()
        sandbox_id = Mock()
        subject = Mock()

        # act
        self.email_service.send_error_email(to_email_address, sandbox_id, subject=subject)

        # assert
        self.email_service.send_email.assert_called_once_with(to_email_address, subject, ANY, ANY, ANY)

    def test_send_error_email_no_sandbox_link(self):
        # arrange
        self.email_config.portal_url = None
        api = Mock()
        api.GetReservationDetails.return_value.ReservationDescription.TopologiesInfo = MagicMock()
        self.email_service = EmailService(self.email_config, self.logger, api)
        self.email_service.send_email = Mock()
        to_email_address = Mock()
        sandbox_id = Mock()

        # act
        self.email_service.send_error_email(to_email_address, sandbox_id)

        # assert
        self.email_service.send_email.assert_called_once()
        self.assertEqual(self.email_service.send_email.call_args.args[3]['SandboxLink'], "")

    @patch("cloudshell.email.email_service.build_sandbox_url")
    def test_send_error_email_with_sandbox_link(self, build_sandbox_url_mock):
        # arrange
        build_sandbox_url_mock.return_value = "sandbox_url"
        api = Mock()
        api.GetReservationDetails.return_value.ReservationDescription.TopologiesInfo = MagicMock()
        self.email_service = EmailService(self.email_config, self.logger, api)
        self.email_service.send_email = Mock()
        to_email_address = Mock()
        sandbox_id = Mock()

        # act
        self.email_service.send_error_email(to_email_address, sandbox_id)

        # assert
        self.email_service.send_email.assert_called_once()
        self.assertEqual(self.email_service.send_email.call_args.args[3]['SandboxLink'],
                         '<a href="sandbox_url">Link to sandbox</a><br/><br/>')
