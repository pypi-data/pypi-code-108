from django.utils.datastructures import MultiValueDict
from mock import patch

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.config.configuration import TCellAgentConfiguration, set_config
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.rust.native_agent import create_native_agent


class NativeAgentBuilder(object):
    """
    Creates a Native Agent with correct Mocks to override config file.
    """
    def __new__(cls, config={}):  # pylint: disable=dangerous-default-value
        set_config(TCellAgentConfiguration())

        patched_env = {'TCELL_AGENT_LOG_ENABLED': 'false',
                       'TCELL_AGENT_APP_ID': 'TestAppId-AppId',
                       'TCELL_AGENT_API_KEY': 'TestAppId-AppId',
                       'TCELL_AGENT_API_URL': 'https://us.agent.tcell.insight.rapid7.com/api/v1',
                       'TCELL_AGENT_INPUT_URL': 'https://us.input.tcell.insight.rapid7.com/api/v1',
                       'TCELL_AGENT_JS_AGENT_API_URL': 'https://us.agent.tcell.insight.rapid7.com/api/v1',
                       'TCELL_AGENT_JS_AGENT_URL': 'https://us.jsagent.tcell.insight.rapid7.com/tcellagent.min.js'}

        patched_env.update(config)
        with patch.dict("os.environ", patched_env):
            return create_native_agent({})


class ConfigurationBuilder(object):
    """
    Provides defaults for all settings accessed by tests.

    """
    def __init__(self):
        self.configuration = TCellAgentConfiguration()
        self.configuration.app_id = "TestAppId-AppId"
        self.configuration.api_key = "TestAppId-AppId"
        self.configuration.tcell_api_url = "https://us.agent.tcell.insight.rapid7.com/api/v1"
        self.configuration.tcell_input_url = "https://us.input.tcell.insight.rapid7.com/api/v1"
        self.configuration.js_agent_url = "https://us.jsagent.tcell.insight.rapid7.com/tcellagent.min.js"
        self.configuration.reverse_proxy = True
        self.configuration.reverse_proxy_ip_address_header = "X-Forwarded-For"

        from tcell_agent.global_state import set_after_agent_started_instrumentation
        set_after_agent_started_instrumentation()  # disables LFI/OS instrumentation

    def update_attribute(self, attribute, setting):
        setattr(self.configuration, attribute, setting)
        return self

    def set_config(self):
        set_config(self.configuration)

    def build(self):
        return self.configuration


class ContextBuilder(object):
    """
    Provides defaults for most settings used in a request

    """

    def __init__(self):
        self.context = TCellInstrumentationContext()
        self.context.session_id = "session-id"
        self.context.user_id = "user-id"
        self.context.user_agent = "user-agent"
        self.context.remote_address = "127.0.0.1"
        self.context.route_id = "route-id"
        self.context.path = "/some/path"
        self.context.fullpath = "/some/path?hide-my-value=sensitive"
        self.context.uri = "http://domain.com/some/path?hide-my-value=sensitive"
        self.context.ip_blocking_triggered = False
        self.context.method = "GET"
        self.context.referrer = "http://domain.com/home?_utm=some-value"

    def update_attribute(self, attribute, setting):
        setattr(self.context, attribute, setting)
        return self

    def build(self):
        return self.context


class AppSensorMetaBuilder(object):
    """
    Provides defaults for most settings used in a request

    """

    def __init__(self):
        self.appsensor_meta = AppSensorMeta()
        self.appsensor_meta.session_id = "session-id"
        self.appsensor_meta.user_id = "user-id"
        self.appsensor_meta.user_agent_str = "user-agent"
        self.appsensor_meta.remote_address = "127.0.0.1"
        self.appsensor_meta.route_id = "route-id"
        self.appsensor_meta.path = "/some/path"
        self.appsensor_meta.location = "http://domain.com/some/path?hide-my-value=sensitive"
        self.appsensor_meta.method = "GET"
        self.appsensor_meta.get_dict = MultiValueDict()
        self.appsensor_meta.post_dict = MultiValueDict()
        self.appsensor_meta.cookie_dict = {}
        self.appsensor_meta.headers_dict = {}
        self.appsensor_meta.files_dict = MultiValueDict()
        self.appsensor_meta.request_content_bytes_len = 0
        self.appsensor_meta.path_dict = {}
        self.appsensor_meta.response_content_bytes_len = 0
        self.appsensor_meta.response_code = 200
        self.appsensor_meta.request_processed = True
        self.appsensor_meta.response_processed = True
        self.appsensor_meta.csrf_reason = None
        self.appsensor_meta.sql_exceptions = []
        self.appsensor_meta.database_result_sizes = []

    def update_attribute(self, attribute, setting):
        setattr(self.appsensor_meta, attribute, setting)
        return self

    def build(self):
        return self.appsensor_meta
