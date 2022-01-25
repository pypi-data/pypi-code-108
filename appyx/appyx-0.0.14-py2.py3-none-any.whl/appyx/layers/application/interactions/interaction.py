class Interaction:
    """
    This class models an interaction between the application and some interface.
    This class follows the Command pattern.
    Its responsible of executing the interaction and answering a Result.
    It encapsulates the logic of interacting with an external actor regardless of the type of interface.
    All handlers of external requests (command line, web, gui, etc) should collaborate with instances of this class.
    """
    def execute(self):
        raise NotImplementedError('Subclass responsibility')
