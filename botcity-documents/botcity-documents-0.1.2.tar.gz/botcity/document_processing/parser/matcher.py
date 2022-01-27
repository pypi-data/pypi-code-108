from enum import Enum


class DataType(str, Enum):
    NUMBER = "NUMBER"
    YEAR = "YEAR"
    PHONE = "PHONE"
    DATE = "DATE"  # "01/01/2001"
    DATE_MMM_YYYY = "DATE_MMM_YYYY"  # "Feb-2018"
    DATE_DD_MMM_YYYYY = "DATE_DD_MMM_YYYYY"  # "20-Oct-2018 or 20,Oct,2018"
    CITY = "CITY"
    STATE = "STATE"
    EMAIL = "EMAIL"
    TEXT = "TEXT"


class DataTypeMatcher:
    @staticmethod
    def match(text, data_type):
        return text
