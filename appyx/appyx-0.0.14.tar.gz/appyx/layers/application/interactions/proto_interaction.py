from appyx.layers.application.interactions.interaction import Interaction


class ProtoInteraction(Interaction):
    """
    Models an interaction that is not yet fully designed.
    It encapsulates and isolates the logic in one method: execute.
    The execute method must return an instance of Result.
    The main value of using this class is to accomplish the first step: decouple logic from interface.

    Parameters for the logic can be passed in the constructor or added via setters. Not in execute().
    This class makes no assumptions nor leads towards any of those strategies.
    The driving factor of this class is to provide a place where to extract the logic from some interface code.
    Browsing the subclasses of this class you can see all the logic in your application that has been isolated
    but not yet modeled into a proper Interaction.
    Thus, the list of subclasses of this class serves as a sort of To-Do list.
    """

    def execute(self):
        raise NotImplementedError('Subclass responsibility')
