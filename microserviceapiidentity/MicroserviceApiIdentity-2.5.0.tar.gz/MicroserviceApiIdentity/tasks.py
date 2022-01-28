"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""
from flask import current_app
from MicroserviceApiIdentity.models import UsersModel, RecoveryCodesModel
from MicroserviceApiIdentity.config import configuration
from MicroserviceApiIdentity.app import celery
from MicroserviceApiIdentity.controllers.users_recovery_codes import UsersRecoveryCodesController

from MicroserviceLibSender.smtp import SenderSMTPClient


@celery.task(time_limit=15)
def send_email_registration(email, password):
    """send mail message with recovery code"""
    sender = SenderSMTPClient(
        dsn=configuration.get('sender_smtp', 'dsn'),
        secret_key=configuration.get('sender_smtp', 'secret_key'),
        project_id=configuration.get('sender_smtp', 'project_id'),
        content_type=configuration.get('sender_smtp', 'content_type'),
    )
    args = (email, password)
    sender.send("ProCDN.net User Registration", "Login: %s<br/>Password: %s" % args, email)

    return True


@celery.task(time_limit=15)
def send_email_password_updated(email, password):
    """send mail message with recovery code
    """
    sender = SenderSMTPClient(
        dsn=configuration.get('sender_smtp', 'dsn'),
        secret_key=configuration.get('sender_smtp', 'secret_key'),
        project_id=configuration.get('sender_smtp', 'project_id'),
        content_type=configuration.get('sender_smtp', 'content_type'),
    )
    args = (email, password)
    sender.send("ProCDN.net New Password", "Login: %s<br/>Password: %s" % args, email)
    return True


@celery.task(time_limit=15)
def send_email_password_reseted(email, password):
    """send mail message with new password
    """
    sender = SenderSMTPClient(
        dsn=configuration.get('sender_smtp', 'dsn'),
        secret_key=configuration.get('sender_smtp', 'secret_key'),
        project_id=configuration.get('sender_smtp', 'project_id'),
        content_type=configuration.get('sender_smtp', 'content_type'),
    )
    args = (email, password)
    sender.send("ProCDN.net New Password", "Login: %s<br/>Password: %s" % args, email)


# @celery.task(time_limit=15)
@celery.task()
def send_email_password_recovery_code(email):
    """
    # see also: http://jinja.pocoo.org/docs/2.10/api/

    {
        "email": {"type": "string"}
    }

    :param args: dict
    :return:
    """
    # check exists email
    if not UsersModel.is_exists_email(email):
        current_app.logger.warning('specified email address not exists: {}'.format(email))

    # get user_id by email
    user = UsersModel.get_item_by_email(email)
    # create recovery code
    recovery_code = UsersRecoveryCodesController.code_generate()
    # remove old recovery codes for user
    UsersRecoveryCodesController.delete(user.id)
    # write new recovery code to database
    RecoveryCodesModel.create(user.id, recovery_code)

    sender = SenderSMTPClient(
        dsn=configuration.get('sender_smtp', 'dsn'),
        secret_key=configuration.get('sender_smtp', 'secret_key'),
        project_id=configuration.get('sender_smtp', 'project_id'),
        content_type=configuration.get('sender_smtp', 'content_type'),
    )
    args = (
        recovery_code,
        # todo: разместить в конфигурации
        "https://www.rest-api.ru/account/password_reset_step2.html"
    )
    sender.send("Confirmation Code", "Code: %s<br/>URL: %s" % args, email)
    return True
