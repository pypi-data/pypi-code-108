from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


class MailerError(Exception):
    pass


class Mailer:
    """ The Mailer class holds helper functions for sending template emails """

    @classmethod
    def send_email(
        cls,
        to_emails,
        subject,
        template,
        context,
        bcc=None,
        attachments=None,
        reply_to=None,
        from_email=None,
    ):
        if not len(to_emails):
            raise MailerError("no TO EMAIL provided")

        if not template:
            raise MailerError("no email template provided")

        if not from_email:
            from_email = f"MetLife Legal Plans <{settings.SUPPORT_EMAIL_ADDRESS}>"

        email_context = {
            "support_phone_number": settings.SUPPORT_PHONE_NUMBER,
            "support_email_address": settings.SUPPORT_EMAIL_ADDRESS,
            "panel_email_address": settings.PANEL_EMAIL_ADDRESS,
        }
        email_context.update(context)

        email_text = render_to_string(f"email/{template}.txt", email_context)
        email_html = render_to_string(f"email/{template}.html", email_context)

        message = EmailMultiAlternatives(
            subject=subject,
            body=email_text,
            from_email=from_email,
            to=to_emails,
            bcc=bcc,
            reply_to=reply_to,
        )

        message.attach_alternative(email_html, "text/html")
        if attachments:
            for item in attachments:
                message.attach(*item)

        try:
            message.send()
            return True
        # TODO: handle specific exceptions
        except Exception as e:
            # TODO: report exception
            print(e, vars(e))
            return False

    @classmethod
    def send_account_notice(cls, user, subject, text):
        return cls.send_email(
            [user.email],
            f"Account Notice: {subject}",
            "mlp_transactional_email",
            {
                "user": user,
                "notice": text,
            },
        )
