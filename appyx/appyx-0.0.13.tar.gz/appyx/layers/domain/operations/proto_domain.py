class ProtoDomainOperation:
    """
    Operation:
    Models an operation that can be done in the domain which is important.
    Important is defined as being something that may be referenced
    (i.e. "adding a user" is something only administrators can do),
    composed by several different operations,
    ("send notification" is used in various sensitive operations)
    used in a command, etc.
    Provides an execute method to perform the operation and decouples instantiation from execution.
    ProtoOperation:
    Models an Operation that isn't fully mature and only the basic logic is implemented.
    Arguments for this operation should be defined through setters or the constructor of the class.
    """
    def execute(self):
        """
            Performs a domain operation.
        """
        raise NotImplementedError("Subclass responsibility")
