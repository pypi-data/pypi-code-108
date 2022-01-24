import abc

from basics.base import Base


class UnableToGenerateValidResponse(Exception):
    pass


class ConversationEngineBase(Base, metaclass=abc.ABCMeta):

    def __init__(self, model_evaluator, debug=False, name=None):
        super().__init__(pybase_logger_name=name)

        self._model_evaluator = model_evaluator

        self._debug = debug

        self._conversation_context = {}

    def reset_state(self):
        self._conversation_context = {}
        self._model_evaluator.reset_state()

    def execute_command(self, command, user_name=None):
        """

        :param command:
        :param user_name: Optional, user name of the user who input the command

        :return: <system message> = None, when the conversation engine did not process any command
        """
        return None

    @abc.abstractmethod
    def respond(self, inputs, conversation_start=False):
        """

        :param inputs: Dict with one or more different toes of inputs
        :param conversation_start: Boolean

        :return: <response to input>, <score(s)>
        """
        self._log.error("Please implement this method in a child class")


class BasicConversationEngine(ConversationEngineBase):

    def __init__(self,
                 io_processor,
                 model_evaluator,
                 select_token_func,
                 sequence_end_token=None,
                 is_sequence_end_func=None,
                 max_response_length=-1,
                 **kwargs):
        super().__init__(model_evaluator, **kwargs)

        self._select_token_func = select_token_func

        if sequence_end_token is None and is_sequence_end_func is None:
            raise Exception("Define sequence_end_token or is_sequence_end_func")

        if sequence_end_token is not None and is_sequence_end_func is not None:
            raise Exception("Either define sequence_end_token or is_sequence_end_func")

        if sequence_end_token is not None:
            self._log.debug("Creating is_sequence_end_func using sequence_end_token")
            is_sequence_end_func = lambda response, scores: response[-1] == sequence_end_token

        self._io_processor = io_processor

        self.sequence_end_token = sequence_end_token
        self._is_sequence_end_func = is_sequence_end_func

        self._max_response_length = max_response_length

    def respond(self, inputs, conversation_start=False):
        processed_inputs = self._io_processor.process_inputs(inputs, conversation_start)

        self._model_evaluator.update_context(processed_inputs, self._conversation_context, conversation_start)

        return self._create_response()

    def _create_response(self, **kwargs):
        """
        Called after model context updated

        :return:
        :rtype:
        """

        self._will_create_response()

        prediction_context = {}
        prev_token = None
        response = []
        scores = []
        while True:
            prediction_data = self._model_evaluator.predict_next_token(prev_token,
                                                                       prediction_context,
                                                                       self._conversation_context)
            # Obtain most likely word token and its score
            score, token = self._select_token_func(prediction_data)

            # Add new token and score
            response += [self._unwrap(token)]
            scores += [self._unwrap(score)]

            if self._is_sequence_end(response, scores):
                break

            if len(response) >= self._max_response_length > 0:
                break

            prev_token = token

        response, scores = self._process_response(response, scores)

        return response, scores

    def _will_create_response(self):
        pass

    def _is_sequence_end(self, response, scores):
        return self._is_sequence_end_func(response=response, scores=scores)

    def _process_response(self, response, scores):
        return self._io_processor.process_response(response, scores=scores)

    def _unwrap(self, tensor):
        """
        Unwrap scalar tensor

        :param tensor:
        :return:
        """
        return tensor
