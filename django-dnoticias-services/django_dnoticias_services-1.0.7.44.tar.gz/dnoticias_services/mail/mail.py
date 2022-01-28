import json
import requests
from urllib.parse import urljoin

from django.conf import settings

from dnoticias_services.mail.base import BaseMailRequest
from dnoticias_services.utils.request import get_headers


class SendEmail(BaseMailRequest):
    def __call__(self, email, template_uuid, brand_group_uuid, subject, context=dict(), from_email=None, from_name=None, attachments=[], track_opens=True, track_clicks=True, api_key=None, timeout=None):
        url = settings.SEND_EMAIL_API_URL
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout
        
        response = requests.post(
            url,
            headers=get_headers(_api_key),
            json={
                "email" : email,
                "template_uuid" : template_uuid,
                "brand_group_uuid" : brand_group_uuid,
                "subject" : subject,
                "context" : context,
                "from_email" : from_email,
                "from_name" : from_name,
                "attachments" : attachments,
                "track_opens" : track_opens,
                "track_clicks" : track_clicks,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

send_email = SendEmail()

class SendEmailBulk(BaseMailRequest):
    def __call__(self, emails=[], template_uuid=None, brand_group_uuid=None, subject="", context=list(), from_email=None, from_name=None, attachments=[], track_opens=True, track_clicks=True, api_key=None, timeout=None):
        url = settings.SEND_EMAIL_BULK_API_URL
        _api_key = api_key or self.api_key
        _timeout = timeout or self.timeout
        
        response = requests.post(
            url,
            headers=get_headers(_api_key),
            json={
                "emails" : emails,
                "template_uuid" : template_uuid,
                "brand_group_uuid" : brand_group_uuid,
                "subject" : subject,
                "context" : context,
                "from_email" : from_email,
                "from_name" : from_name,
                "attachments" : attachments,
                "track_opens" : track_opens,
                "track_clicks" : track_clicks,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

send_email_bulk = SendEmailBulk()


class GetUserEmailList(BaseMailRequest):
    """
    Gets the user email list from dnoticias-mail service.
    """
    def __call__(self, user_id, api_key=None):
        _api_key = api_key or self.api_key

        response = requests.get(
            settings.EMAIL_USER_LIST_API_URL.format(user_id),
            headers=get_headers(_api_key),
        )

        response.raise_for_status()

        return response

get_user_email_list = GetUserEmailList()


class GetUserDatatableEmailList(BaseMailRequest):
    """
    Gets the user email datatable from dnoticias-mail service.
    """
    def __call__(self, request, user_email, api_key=None):
        _api_key = api_key or self.api_key

        request = json.dumps(request.POST)
        
        response = requests.post(
            settings.EMAIL_USER_DATATABLE_LIST_API_URL.format(user_email),
            headers=get_headers(_api_key),
            json=request,
        )

        response.raise_for_status()

        return response

get_user_datatable_email_list = GetUserDatatableEmailList()


__all__ = ("send_email", "send_email_bulk", "get_user_email_list", "get_user_datatable_email_list")
