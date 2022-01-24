from .BaseMicrosoftAPI import BaseMicrosoftAPI
import requests

class GraphAPI(BaseMicrosoftAPI):
    def __init__(self, tenant_ID, app_ID, secret_key):
       super().__init__(tenant_ID, app_ID, secret_key,
                        'https://graph.microsoft.com/.default')

    def list_users(self, properties=None):
        if properties:
            parameters = ','.join(properties)
            url = f'https://graph.microsoft.com/v1.0/users?$select={parameters}'
        else:
            url = 'https://graph.microsoft.com/v1.0/users'
        response = self.call_api(url)
        return response

    def list_subscribed_skus(self):
        url = 'https://graph.microsoft.com/v1.0/subscribedSkus'
        response = self.call_api(url)
        return response

    def office365_active_user_detail(self, params):
        urls = {
            'period': f"https://graph.microsoft.com/v1.0/reports/"\
                      f"getOffice365ActiveUserDetail(period='D{params[1]}')",
            'date': f"http://graph.microsoft.com/v1.0/reports/"\
                    f"getOffice365ActiveUserDetail(date={params[1]})"
        }

        url = urls.get(params[0])
        response = self.call_api_stream(url)
        return response

    def office365_mailbox_usage_detail(self, period):
        supported_periods = [7, 30, 90, 180]
        if period not in supported_periods:
            print(f'office_365_mailbox_usage_detail: please use one of'\
                  f'supported periods: {period}')
            # raise error
            return None
        else:
            url = f"https://graph.microsoft.com/v1.0/reports/"\
                  f"getMailboxUsageDetail(period='D{period}')"
            response = self.call_api_stream(url)
            return response

# Possibilities --------------------------------------------------------------
# users/delta
#    def office365_services_user_counts(self):
# 
