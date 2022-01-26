from enum import Enum


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value

    # https://docs.python.org/3.6/library/enum.html#using-automatic-values
    def _generate_next_value_(name, start, count, last_values):
        return name


class StatusColor(StrEnum):
    CRITICAL = "#0F0F0F"
    FATAL = CRITICAL
    ERROR = "#E01E5A"
    WARNING = "#FF7900"
    WARN = WARNING
    NOTICE = "#FFCC00"
    INFO = "#1890ff"
    DEBUG = "#888888"
    SUCCESS = "#2EB67D"
