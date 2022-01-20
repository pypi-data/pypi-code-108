from cnvrgv2.config.error_messages import EMPTY_KAFKA_BROKERS_LIST, EMPTY_KAFKA_INPUT_TOPICS
from cnvrgv2.context import SCOPE
from cnvrgv2.config import routes
from cnvrgv2.errors import CnvrgArgumentsError

from cnvrgv2.modules.base.workflows_base import WorkflowsBase
from cnvrgv2.modules.workflows import Endpoint, EndpointKind, EndpointEnvSetup


class EndpointsClient(WorkflowsBase):
    def __init__(self, project):
        super().__init__(Endpoint, "Endpoint", project._context)

        scope = self._context.get_scope(SCOPE.PROJECT)
        self._route = routes.ENDPOINTS_BASE.format(scope["organization"], scope["project"])

    def create(
        self,
        title,
        file_name,
        function_name,
        kind=EndpointKind.WEB_SERVICE,
        env_setup=EndpointEnvSetup.PYTHON3,
        templates=None,
        kafka_brokers=None,
        kafka_input_topics=None,
        *args,
        **kwargs
    ):
        """
        Create a new endpoint

        @param title: Name of the webapp
        @param templates: List of template names to be used
        @param kind: Integer representing the endpoints type. Use EndpointKind enum
        @param file_name: The file containing the endpoint's functions
        @param function_name: The name of the function the endpoint will route to
        @param env_setup: The interpreter to use. Use EndpointEnvSetup enum
        @param kafka_brokers: List of kafka brokers
        @param kafka_input_topics: List of topics to register as input
        @param args: optional arguments
        @param kwargs: Dictionary. Rest of optional attributes for creation
            image: Image object to create endpoint with
            queue: Name of the queue to run this job on
            kafka_output_topics: List of topics to register as output
        TODO: Add a list of optional attributes
        @return: The newly created webapp object
        """

        kwargs = {
            "kind": kind,
            "file_name": file_name,
            "function_name": function_name,
            "env_setup": env_setup,
            **kwargs
        }

        if kind == EndpointKind.STREAM:
            self._validate_stream_input(kafka_brokers, kafka_input_topics)
            kwargs["kafka_brokers"] = kafka_brokers
            kwargs["kafka_input_topics"] = kafka_input_topics

        return super().create(title, templates, *args, **kwargs)

    def _validate_stream_input(self, kafka_brokers, kafka_input_topics):
        error_dict = dict()
        if type(kafka_brokers) != list or len(kafka_brokers) < 1:
            error_dict[kafka_brokers] = EMPTY_KAFKA_BROKERS_LIST

        if type(kafka_input_topics) != list or len(kafka_input_topics) < 1:
            error_dict[kafka_input_topics] = EMPTY_KAFKA_INPUT_TOPICS

        if error_dict:
            raise CnvrgArgumentsError(error_dict)
