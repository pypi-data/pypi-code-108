from cloudcix.client import Client


class OTP:
    """
    The OTP Application is a software system that manages CloudCIX two factor authentication radius server

    It allows Users to create a secret for there CloudCIX user's email and have it added to the CloudCIX radius server
    and implement 2FA

    """
    _application_name = 'otp'

    otp = Client(
        _application_name,
        'otp/',
    )

    otp_auth = Client(
        application=_application_name,
        service_uri='otp_auth/{email}',
    )
