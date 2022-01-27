from tcell_agent.version import VERSION
import sys
import os


class AgentConfig(dict):
    def __init__(self, framework_details):
        dict.__init__(self)

        self['agent_type'] = 'Python'
        self['agent_version'] = VERSION
        self['default_cache_dir'] = os.path.abspath('tcell/cache')
        self['default_config_file_dir'] = os.getcwd()
        self['default_log_dir'] = os.path.abspath('tcell/logs')
        self['default_preload_policy_file_dir'] = os.getcwd()
        self['overrides'] = {
            'applications': [{
                'enable_json_body_inspection': True
            }]
        }

        if os.environ.get('TCELL_AGENT_HOME') and not os.environ.get('TCELL_AGENT_CONFIG'):
            self['overrides']['config_file_path'] = os.path.join(os.getcwd(), "tcell_agent.config")

        if framework_details:
            self['agent_details'] = {'language': 'Python',
                                     'language_version': '.'.join([str(sys.version_info.major), str(sys.version_info.minor), str(sys.version_info.micro)]),
                                     'app_framework': framework_details.get('app_framework'),
                                     'app_framework_version': framework_details.get('app_framework_version')}
