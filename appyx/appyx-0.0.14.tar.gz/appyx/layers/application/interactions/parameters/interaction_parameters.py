from appyx.layers.application.interactions.parameters.set_of_parameters import SetOfParameters


class InteractionParameters(SetOfParameters):
    """
    I model the set of parameters and arguments that an interaction handles.
    """

    def _command(self):
        return self._interaction()

    def _interaction(self):
        return self._context
