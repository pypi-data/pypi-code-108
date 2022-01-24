import logging
from email.mime.application import MIMEApplication
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.mail import EmailMessage
logger = logging.getLogger('dict_config_logger')


def email_verification(email):
    """Function to send email verification"""
    ses = boto3.client('ses')
    check = check_if_email_verified(email)

    if check:
        logger.info("Email is sent for Verification")

        response = ses.verify_email_identity(
            EmailAddress=email
        )

        logger.info(response)


def check_if_email_verified(email):
    """Function to check if email id from user is verified """
    list_emails = list_email_verified()
    if email in list_emails:
        logger.info("Email is already Verified")
        return False
    return True


def list_email_verified():
    """Function to return list of verified emails """

    ses = boto3.client('ses')
    response = ses.list_identities(
        IdentityType='EmailAddress',
        MaxItems=10
    )
    logger.info(response['Identities'])
    return response['Identities']


def send_notifications(email, sender, email_configuration):
    """This function sends email of a log file """

    logger.info('Sending email to recipients')
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = sender

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = email

    # The subject line for the email.
    SUBJECT = email_configuration.get('Subject')

    # The full path to the file that will be attached to the email.
    # LOG_PATH = email_configuration.get('Log_path')
    ATTACHMENT = getattr(settings, "LOG_PATH", None)

    # The HTML body of the email.
    file_name = email_configuration.get('HTML_File')
    BODY_HTML = open('media/' + file_name).read().format(
        paragraph=email_configuration.get('Email_Content'),
        signature=email_configuration.get('Signature'),
        email_us=email_configuration.get('Email_Us'),
        faq_url=email_configuration.get('FAQ_URL'),
        unsubscribe=email_configuration.get('Unsubscribe_Email_ID'))
    # Define the attachment part and encode it using MIMEApplication.
    att = MIMEApplication(open(ATTACHMENT, 'rb').read())

    # Add a header to tell the email client to treat this part as an
    # attachment, and to give the attachment a name.
    att.add_header('Content-Disposition', 'attachment',
                   filename="OpenLXP notifications ")

    for each_recipient in RECIPIENT:
        try:
            # Provide the contents of the email.

            mail = EmailMessage(SUBJECT, BODY_HTML, SENDER,
                                [each_recipient])
            mail.content_subtype = "html"
            # Add the attachment to the parent container.
            mail.attach(att)
            mail.send()
            logging.FileHandler(getattr(settings, "LOG_PATH", None),
                                mode='w')
        # Display an error if something goes wrong.
        except ClientError as e:
            logger.error(e.response['Error']['Message'])
            continue


def send_notifications_with_msg(email, sender, msg, email_configuration):
    """This function sends email of a log file """

    logger.info('Sending email to recipients')
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = sender
    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = email
    # The subject line for the email.
    SUBJECT = email_configuration.get('Subject')

    # # The HTML body of the email.
    file_name = email_configuration.get('HTML_File')
    BODY_HTML = open('media/' + file_name).read().format(
        paragraph=msg,
        signature=email_configuration.get('Signature'),
        email_us=email_configuration.get('Email_Us'),
        faq_url=email_configuration.get('FAQ_URL'),
        unsubscribe=email_configuration.get('Unsubscribe_Email_ID'))

    for each_recipient in RECIPIENT:
        try:
            # Provide the contents of the email.

            mail = EmailMessage(SUBJECT, BODY_HTML, SENDER,
                                [each_recipient])
            mail.content_subtype = "html"
            # Add the attachment to the parent container.
            mail.send()
        # Display an error if something goes wrong.
        except ClientError as e:
            logger.error(e.response['Error']['Message'])
            continue
