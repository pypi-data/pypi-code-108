from appyx.layers.application.application import Application
from appyx.layers.application.interactions.parameters.parameter import Parameter
from appyx.layers.application.interactions.parameters.set_of_parameters import SetOfParameters
from appyx.layers.application.interactions.validators.generic import IsOneOfThese, IsBoolean


class PollsApplication(Application):
    CLOCK_FAKE = 'FAKE'
    CLOCK_SYSTEM = 'SYSTEM'
    QUESTIONS_EPHEMERAL = 'EPHEMERAL'  # or TRANSIENT
    QUESTIONS_PERSISTENT = 'PERSISTENT'

    @classmethod
    def running_context_test_dev(cls):
        initial_parameters = [
            Parameter("clock_behavior", [IsOneOfThese(['FAKE, SYSTEM'])]),
            Parameter("questions_volatility", [IsOneOfThese(['EPHEMERAL', 'PERSISTENT'])]),
            Parameter("run_in_parallel", [IsBoolean()]),
        ]

        default_arguments = {"clock_behavior": 'FAKE'}
        context = SetOfParameters(None,
                                  initial_parameters=initial_parameters,
                                  initial_required_parameter_names=["questions_volatility", "run_in_parallel"],
                                  default_arguments=default_arguments)
        return context

    @classmethod
    def running_context_production(cls):
        initial_parameters = [
            Parameter("clock_behavior", [IsOneOfThese(['FAKE, SYSTEM'])]),
            Parameter("questions_volatility", [IsOneOfThese(['EPHEMERAL', 'PERSISTENT'])]),
        ]

        default_arguments = {"clock_behavior": 'SYSTEM'}
        context = SetOfParameters(None,
                                  initial_parameters=initial_parameters,
                                  initial_required_parameter_names=["questions_volatility"],
                                  default_arguments=default_arguments)

        return context

    def _new_business(self):
        from polls.domain.poll_station import PollStation
        clock = self.clock(self._running_context.get_argument_named("clock_behavior"))
        questions = self._questions(self._running_context.get_argument_named("questions_repository"))
        business = PollStation(clock, questions)
        return business

    def default_running_context(self):
        return self.running_context_test_dev()

    def clock(self, clock_behavior):
        if clock_behavior == self.CLOCK_FAKE:
            from polls.domain.poll_station import FakeClock
            return FakeClock()
        if clock_behavior == self.CLOCK_SYSTEM:
            from polls.domain.poll_station import SystemClock
            return SystemClock()
        raise ValueError(f"Unsupported valid clock behavior: {clock_behavior}")

    def _questions(self, questions_volatility):
        if questions_volatility == self.QUESTIONS_EPHEMERAL:
            from polls.domain.poll_station import QuestionsArchive
            return QuestionsArchive()
        raise ValueError(f"Unsupported valid questions volatility: {questions_volatility}")
