"""
    CUSTOM READERS CLASSES
        - Class which manages reader tasks like auth, requests, pagination
"""
import os

from sailthru import SailthruClient

from sdc_dp_helpers.api_utilities.date_managers import date_handler, date_range
from sdc_dp_helpers.api_utilities.retry_managers import request_handler
from sdc_dp_helpers.sailthru.config_magagers import get_config


class CustomSailThruReader:
    """
        Custom SailThru Reader
    """

    def __init__(self, **kwargs):
        self.config = get_config(kwargs.get('config_path', None))
        self.credentials = get_config(kwargs.get('credentials_path', None))

        self.sailthru_client = SailthruClient(
            api_key=self.credentials.get('api_key', None),
            secret=self.credentials.get('api_secret', None)
        )

    def get_templates(self):
        """
        Dynamically gathers all templates for 'send' stat.
        """
        response = self.sailthru_client.get_templates()
        if response.is_ok():
            return response.get_body()

        raise EnvironmentError(
            f'Error: {response.get_error().get_error_code()}\n'
            f'Mesage: {response.get_error().get_message()}'
        )

    @request_handler(
        wait=int(os.environ.get('REQUEST_WAIT_TIME', 0)),
        backoff_factor=float(os.environ.get('REQUEST_BACKOFF_FACTOR', 0.01)),
        backoff_method=os.environ.get('REQUEST_BACKOFF_METHOD', 0.01)
    )
    def request(self, data, action='stats'):
        """
        Request various stats from Sailthru about primary list membership
        or campaign and triggered message activity.
        Endpoint URL: https://api.sailthru.com/stats
        Additional parameters are dependent on the stat value
        the type of stats you want to request:
            - list
            - blast
            - send
        """
        print(f'Action: {action}\nQuery: {data}')

        response = self.sailthru_client.api_get(
            action=action, data=data
        )

        if not response.is_ok():
            error = response.get_error()
            message = 'APIError:{}, Status Code:{}, Error Code:{}'.format(
                error.get_message(),
                str(response.get_status_code()),
                str(error.get_error_code()))
            if (
                    str(response.get_status_code()) != '404' and
                    str(error.get_error_code()) != '99'
            ):
                raise RuntimeError(message)

            # If there is no data for something like a template,
            # just a warning is printed.
            print(f'Warning: No data in given instance.\n {message}')
        elif response.is_ok():
            return response.get_body()
        else:
            return None

    def run_query(self):
        """
        Consumes a .yaml config file and loops through the date and url
        to return relevant data from Sailthru Get Request.
        """
        data_set = []
        for stat, data in self.config.items():
            data['stat'] = stat
            date_range_list = date_range(
                start_date=data['start_date'],
                end_date=data['end_date']
            )

            # send requires template ids for the request,
            # so all possible templates are generated and loop through
            if stat == 'send':
                templates = self.get_templates()
                # we need to split send date ranges for day-by-day values
                for list_date in date_range_list:
                    for template in templates.get('templates'):
                        template_name = template.get('name')

                        print(f'Template: {template_name}')
                        data['template'] = template_name

                        data['start_date'] = list_date
                        data['end_date'] = list_date
                        request_data = self.request(data=data)

                        if request_data is not None:
                            request_data['stat'] = 'send'
                            request_data['template'] = template_name
                            data_set.append(request_data)

            # blast requires the action be converted from 'stat' to 'blast'
            elif stat == 'blast':
                data['start_date'] = date_handler(data['start_date'])
                data['end_date'] = date_handler(data['end_date'])
                request_data = self.request(action=stat, data=data)
                if request_data is not None:
                    request_data['stat'] = 'blast'
                    data_set.append(request_data)

            elif stat == 'list':
                # list stat does not support start to end date scope, only a single 'date'
                for list_date in date_range_list:
                    print(f'List date range at: {list_date}.')
                    data['date'] = list_date
                    request_data = self.request(data=data)
                    if request_data is not None:
                        request_data['stat'] = data['stat']
                        data_set.append(request_data)

            else:
                raise ValueError(f'Specified stat {stat} is not supported.')

        return data_set
