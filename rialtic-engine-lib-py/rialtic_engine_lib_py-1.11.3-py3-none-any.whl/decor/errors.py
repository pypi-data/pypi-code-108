from enginelib.errors import Error


class InvalidParameterError(Error):
    pass


class InsightLookupError(Error):
    pass


class DecisionTreeError(Error):
    pass


class CustomParameterError(Error):
    pass
