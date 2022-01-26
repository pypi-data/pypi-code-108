from unipipeline.errors.uni_error import UniError


class UniPayloadError(UniError):
    pass


class UniPayloadParsingError(UniPayloadError):
    pass


class UniAnswerPayloadParsingError(UniPayloadParsingError):
    pass


class UniPayloadSerializationError(UniPayloadError):
    pass
