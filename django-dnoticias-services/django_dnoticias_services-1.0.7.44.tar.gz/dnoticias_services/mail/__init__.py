from dnoticias_services.mail.campaign import create_campaign, send_campaign
from dnoticias_services.mail.mail import (
    send_email,
    send_email_bulk,
    get_user_email_list,
    get_user_datatable_email_list,
)

__all__ = (
    "create_campaign",
    "send_campaign",
    "send_email",
    "send_email_bulk",
    "get_user_email_list",
    "get_user_datatable_email_list",
)
