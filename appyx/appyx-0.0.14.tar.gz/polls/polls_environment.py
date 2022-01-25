from appyx.layers.application.environment import Environment, OneToOne
from polls import settings_stub
from polls.polls_application import PollsApplication
from appyx.layers.application.external_parameters import EnvironmentVariableParameter, CommandLineParameter, \
    SettingsFileParameter


class PollsEnvironment(Environment):
    TEST = 'TEST'
    PROD = 'PROD'

    def _application_class(self):
        return PollsApplication

    def _external_parameters_mapped_to_context_parameters(self):
        environment_parameter = EnvironmentVariableParameter('ENVIRONMENT', self.TEST)
        run_in_parallel_parameter = CommandLineParameter("run-in-parallel", default_value=False)
        questions_repository_parameter = SettingsFileParameter(settings_stub, "QUESTIONS_REPO")

        mappings = [OneToOne('environment', environment_parameter),
                    OneToOne('questions_repository', questions_repository_parameter)]
        if environment_parameter.value() == self.TEST:
            mappings.append(OneToOne('run_in_parallel', run_in_parallel_parameter))
        return mappings

    def _new_application_context(self):
        environment_parameter = EnvironmentVariableParameter('ENVIRONMENT', self.TEST)
        if environment_parameter.value() == self.PROD:
            return PollsApplication.running_context_production()
        else:
            return PollsApplication.running_context_test_dev()
