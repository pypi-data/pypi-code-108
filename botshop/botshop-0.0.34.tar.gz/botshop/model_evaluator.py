import abc

from basics.base import Base


class ModelEvaluatorBase(Base, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def reset_state(self):
        self._log.error("Please implement this method in a child class")

    @abc.abstractmethod
    def update_context(self, inputs, conversation_context, conversation_start):
        """

        :param inputs: Dict with one or more different types of inputs
        :param conversation_context: Dict, can be empty initially, and can be filled with
                                     context data when calling this method
        :param conversation_start: Boolean

        :return:
        """
        self._log.error("Please implement this method in a child class")

    @abc.abstractmethod
    def predict_next_token(self, previous_token, prediction_context, conversation_context):
        """

        :param previous_token: Previous token, initially None
        :param prediction_context: Dict, can be used to store intermediate state
        :param conversation_context: Dict, conversation context, updated after each turn using `update_context`

        :return:
        """
        self._log.error("Please implement this method in a child class")
