# -*- coding: utf-8 -*-
import abc

import six
from kavenegar import *
from aparnik.settings import aparnik_settings


@six.add_metaclass(abc.ABCMeta)
class SMSAPI():

    def __init__(self, **kwargs):
        pass

    @abc.abstractmethod
    def otp(self, receptor, otp, app_signature, first_name, last_name):
        pass


class SMSAPIKavenegar(SMSAPI):

    def otp(self, receptor, otp, app_signature, first_name, last_name):
        try:
            if not app_signature:
                app_signature = 'Code:%s' % otp

            api = KavenegarAPI(aparnik_settings.SMS_API_KEY)
            params = {
                'receptor': receptor,
                'template': aparnik_settings.SMS_OTA_NAME,
                'token': otp,
                'token2': app_signature,
                'type': 'sms',  # sms vs call
            }
            response = api.verify_lookup(params)
            # print(response)

        except APIException as e:
            print(e)

        except HTTPException as e:
            print(e)
