from appyx.layers.domain.validators.object_validator import ObjectValidator


class Presenter:
    """
        I model the cropping of information made to a domain object when it is exposed to a client.
    """
    @classmethod
    def format_date(cls, a_date, a_format=None):
        if a_format is None:
            return cls.format_date(a_date, a_format=cls.default_date_format())
        return a_date.strftime(a_format)

    @classmethod
    def format_datetime(cls, a_datetime, a_format=None):
        if a_format is None:
            return cls.format_datetime(a_datetime, a_format=cls.default_datetime_format())
        return a_datetime.strftime(a_format)

    @classmethod
    def default_date_format(cls):
        return "%Y/%m/%d"

    @classmethod
    def default_datetime_format(cls):
        return ObjectValidator.default_datetime_format()
