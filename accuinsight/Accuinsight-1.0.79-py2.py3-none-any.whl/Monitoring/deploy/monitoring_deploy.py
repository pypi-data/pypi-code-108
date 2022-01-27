import datetime, json

from Accuinsight.modeler.entities.monitoring_deploy_log import DeployLog
from Accuinsight.modeler.entities.alarm import Alarm
from Accuinsight.modeler.clients.modeler_api import DeployLogRestApi
from Accuinsight.modeler.core.MonitoringConst.deploy import DeployConst
from Accuinsight.modeler.utils.os_getenv import get_os_env


class AddDeployLog:
    """
        Object for adding deploy log.
    """

    def __init__(self):
        env_value = get_os_env('ENV')

        self.deploy_log = DeployLog()
        self.deploy_alarm = Alarm()
        self.deploy_log_api = DeployLogRestApi(env_value[DeployConst.BACK_END_API_URL],
                                               env_value[DeployConst.BACK_END_API_PORT],
                                               env_value[DeployConst.BACK_END_API_URI])
        self.swagger = False

    def set_request(self, request):
        self.deploy_log.run_id = request.headers.get('id')

        if "swagger" in request.url:
            self.swagger = True
        else:
            self.swagger = False

    def set_response(self, response):
        response.direct_passthrough = False

        try:
            res_data = response.get_data().decode()
        except UnicodeDecodeError:
            res_data = response.get_data()

        try:
            self.deploy_log.response_data = json.loads(res_data)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            self.deploy_log.response_data = str(res_data)

    def set_slack(self, hook_url):
        if hook_url:
            self.deploy_alarm.notifiers['slack'] = hook_url

    def set_mail(self, address):
        if address:
            self.deploy_alarm.notifiers['mail'] = address

    def add_log(self, messages):
        if not self.swagger:
            if messages:
                self.deploy_alarm.type = "DeployAPI"

                for message in messages:
                    self.deploy_alarm.message = message
                    self.deploy_log_api.call_rest_api('POST', self.deploy_alarm.get_alarm_param(), "alarm")

            self.deploy_log_api.call_rest_api('POST', self.deploy_log.get_logging_param())

    def get_log_info(self):
        try:
            summary_data = json.loads(self.deploy_log_api.call_rest_api('GET', None, 'log_summary'))['data']
        except (TypeError, KeyError):
            summary_data = {'totalCall': 0, 'totalSuccessCall': 0}

        log_info = dict()
        log_info['total_call'] = summary_data['totalCall']
        log_info['total_success_call'] = summary_data['totalSuccessCall']
        log_info['latest_log'] = json.loads(
            self.deploy_log_api.call_rest_api('POST', self.deploy_log.get_logging_param(), 'log_data')
        )['data']

        return log_info
