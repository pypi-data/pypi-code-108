class RuleValidationFailure:
    def __init__(
        self,
        rule,
    ):
        pass


class DuplicateRule(Exception):
    pass


class IncompatibleRules(Exception):
    pass


class ValidationError(Exception):
    pass


class InvalidCallable(Exception):
    pass


class MalformedConditionLikeSpec(Exception):
    pass


class MalformedContainerItemSpec(Exception):
    pass


class MalformedDataPathSpec(Exception):
    pass
