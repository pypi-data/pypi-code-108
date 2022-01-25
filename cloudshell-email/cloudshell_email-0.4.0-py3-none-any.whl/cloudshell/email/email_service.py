import logging
import re
import smtplib
import sys
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List

from cloudshell.api.cloudshell_api import CloudShellAPISession

from cloudshell.email.constants import DEFAULT_HTML, VALID_EMAIL_REGEX
from cloudshell.email.email_config import EmailConfig
from cloudshell.email.email_helpers import build_email_template_full_path, build_sandbox_url


class EmailService:

    def __init__(self, email_config: EmailConfig, logger: logging.Logger, api: CloudShellAPISession = None):
        self._email_config = email_config
        self._logger = logger
        self._api = api

    @staticmethod
    def is_valid_email_address(email: str) -> bool:
        return True if re.fullmatch(VALID_EMAIL_REGEX, email) else False

    def send_error_email(self, to_email_address: List[str], sandbox_id: str, subject: str = '', error_message: str = '',
                         error_details: str = '', get_exc_info: bool = False, cc_email_address: List[str] = []) -> None:
        """
        :param get_exc_info: If True will try to get current exception details using sys.exc_info() and
        'error_message' and 'error_details' parameters will be ignored. If False then 'error_message' and
        'error_details' parameter values will be used
        :return:
        """
        # build sandbox url
        if self._email_config.portal_url:
            sandbox_url = build_sandbox_url(self._email_config.portal_url, sandbox_id)
            sandbox_url_html = f"<a href=\"{sandbox_url}\">Link to sandbox</a><br/><br/>"
        else:
            sandbox_url_html = ''

        # get exception info
        if get_exc_info:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            error_details = "<br/>".join(err_lines)
            error_message = str(exc_value)

        template_parameters = {
            "SandboxLink": sandbox_url_html,
            "ErrorMessage": error_message,
            "ErrorDetails": error_details
        }

        # get sandbox details
        if self._api:
            sandbox_details = self._api.GetReservationDetails(sandbox_id).ReservationDescription
            template_parameters.update({
                "SandboxName": sandbox_details.Name,
                "SandboxOwner": sandbox_details.Owner,
                "SandboxId": sandbox_id,
                "DomainName": sandbox_details.DomainName,
                "SandboxDescription": sandbox_details.Description,
                "SandboxBlueprint": sandbox_details.TopologiesInfo[0].Alias if sandbox_details.TopologiesInfo else ""
            })

            if not subject:
                subject = f"Sandbox '{sandbox_details.Name}' has encountered an error"
        else:
            raise ValueError("CloudShell Automation API is required to use default error email template. Please "
                             "provide CloudShellAPISession instance to EmailService constructor")

        # get absolute path to the default error email template
        template_path = build_email_template_full_path("email_templates/default_error.htm", __file__)

        self.send_email(to_email_address, subject, template_path, template_parameters, cc_email_address)

    def is_email_configured(self) -> bool:
        return True if self._email_config else False

    def send_email(self, to_email_address: List[str], subject: str = '',
                   template_name: str = 'default',
                   template_parameters: Dict[str, str] = {},
                   cc_email_address: List[str] = []):

        if len(to_email_address) == 0:
            self._logger.exception('Empty list of email addresses')
            raise Exception('Empty list of email addresses')

        invalid_emails = []
        for email_address in to_email_address:
            if not self.is_valid_email_address(email_address):
                invalid_emails.append(email_address)

        for email_address in cc_email_address:
            if not self.is_valid_email_address(email_address):
                invalid_emails.append(email_address)

        invalid_string = ','.join(invalid_emails)

        if len(invalid_emails) == 1:
            self._logger.exception(f'{invalid_string} is not a valid email address')
            raise Exception(f'{invalid_string} is not a valid email address')
        elif len(invalid_emails) > 1:
            self._logger.exception(f'{invalid_string} are not valid email addresses')
            raise Exception(f'{invalid_string} are not valid email addresses')

        if self._email_config.default_html:
            if self._email_config.default_parameters:
                if template_parameters:
                    self._email_config.default_parameters.update(template_parameters)

                if self._email_config.default_subject:
                    self._send(to_email_address, self._email_config.default_subject,
                               self._email_config.default_html.format(**self._email_config.default_parameters),
                               cc_email_address)
                else:
                    self._send(to_email_address, subject,
                               self._email_config.default_html.format(**self._email_config.default_parameters),
                               cc_email_address)
            else:
                if self._email_config.default_subject:
                    self._send(to_email_address, self._email_config.default_subject,
                               self._email_config.default_html.format(**template_parameters), cc_email_address)
                else:
                    self._send(to_email_address, subject,
                               self._email_config.default_html.format(**template_parameters), cc_email_address)
        else:
            message = self._load_and_format_template(template_name, **template_parameters)
            self._send(to_email_address, subject, message, cc_email_address)

    def _login(self) -> smtplib.SMTP:
        try:
            smtp = smtplib.SMTP(
                host=self._email_config.smtp_server,
                port=self._email_config.smtp_port
            )
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self._email_config.user, self._email_config.password)
            return smtp
        except smtplib.SMTPHeloError:
            self._logger.exception('Failed to login: The server didn’t reply properly '
                                   'to the helo greeting.')
            raise
        except smtplib.SMTPAuthenticationError:
            self._logger.exception('Failed to login: The server didn’t accept the '
                                   'username/password combination.')
            raise
        except smtplib.SMTPNotSupportedError:
            self._logger.exception('Failed to login: The AUTH command is not supported '
                                   'by the server.')
            raise
        except smtplib.SMTPException:
            self._logger.exception('Failed to login: No suitable authentication method was found.')
            raise
        except RuntimeError:
            self._logger.exception('Failed to login: SSL/TLS support is not available '
                                   'to your Python interpreter.')
            raise

    def _send(self, to_address, subject, message, cc=None):
        from_address = self._email_config.from_address
        msg = MIMEMultipart('alternative')
        msg['From'] = ';'.join(from_address) if isinstance(from_address, list) else from_address
        msg['To'] = ';'.join(to_address) if isinstance(to_address, list) else to_address
        msg['Subject'] = subject
        if cc:
            msg["Cc"] = ';'.join(cc) if isinstance(cc, list) else cc
        mess = MIMEText(message, 'html')
        msg.attach(mess)

        smtp = self._login()

        try:
            smtp.sendmail(
                from_addr=from_address,
                to_addrs=[to_address, cc] if cc else to_address,
                msg=msg.as_string()
            )
        except smtplib.SMTPRecipientsRefused:
            self._logger.exception('Failed to send email: All recipients were refused.')
            raise
        except smtplib.SMTPSenderRefused:
            self._logger.exception('Failed to send email: The server didn’t accept the from_addr.')
            raise
        except smtplib.SMTPDataError:
            self._logger.exception('Failed to send email: The server replied with an unexpected '
                                   'error code.')
            raise
        except smtplib.SMTPNotSupportedError:
            self._logger.exception('Failed to send email: SMTPUTF8 was given in the mail_options '
                                   'but is not supported by the server.')
            raise
        finally:
            smtp.close()

    def _load_and_format_template(self, template_name, **extra_args):
        try:
            if template_name == 'default':
                content = DEFAULT_HTML
            else:
                with open(template_name, 'r') as f:
                    html_string = f.read()
                    content = html_string.format(**extra_args)
        except Exception:
            self._logger.exception('Failed loading email template')
            raise Exception('Failed loading email template')

        return content

    def validate_email_config(self) -> None:
        """Validates SMTP server configuration.

        Returns:
            None
        Raises:
            smtplib.SMTPHeloError
            smtplib.SMTPAuthenticationError
            smtplib.SMTPNotSupportedError
            smtplib.SMTPException
            RuntimeError
        """
        smtp = self._login()
        smtp.close()
