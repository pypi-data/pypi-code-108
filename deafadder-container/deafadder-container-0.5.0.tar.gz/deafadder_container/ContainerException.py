class DeafAdderContainerException(Exception):
    pass


class InstanceNotFound(DeafAdderContainerException):
    pass


class MultipleAutowireReference(DeafAdderContainerException):
    pass


class AnnotatedDeclarationMissing(DeafAdderContainerException):
    pass
