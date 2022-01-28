"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""


class ResponseSeverity:
    """Коды уровней важности сообщений.
    See also: https://en.wikipedia.org/wiki/Syslog

    >>> ResponseSeverity.Info
    info
    """
    # Emergency - система не работоспособна
    Emergency: str = "emergency"
    # Critical - состояние системы критическое
    Critical: str = "critical"
    # Error - сообщения об ошибках
    Error: str = "error"
    # Warning - предупреждения о возможных проблемах
    Warning: str = "warning"
    # Notice - сообщения о нормальных, но важных событиях
    Notice: str = "notice"
    # Informational - информационные сообщения
    Info: str = "info"
    # Debug - отладочные сообщения
    Debug: str = "debug"


class ResponseStatusDict(object):
    MS_0000 = (200, "MS_0000", "Success.", ResponseSeverity.Info)
    MS_ID_0001 = (201, "MS_ID_0001", "Created.", ResponseSeverity.Info)
    MS_ID_0002 = (200, "MS_ID_0002", "Updated.", ResponseSeverity.Info)
    MS_ID_0003 = (200, "MS_ID_0003", "Deleted.", ResponseSeverity.Info)

    MS_ID_0010 = (400, "MS_ID_0010", "Invalid Content Type.", ResponseSeverity.Error)
    MS_ID_0011 = (400, "MS_ID_0011", "Invalid Content.", ResponseSeverity.Error)
    MS_ID_0012 = (400, "MS_ID_0012", "Invalid Token.", ResponseSeverity.Error)
    MS_ID_0013 = (401, "MS_ID_0013", "Expired Token.", ResponseSeverity.Error)
    MS_ID_0014 = (401, "MS_ID_0014", "Token Not Defined.", ResponseSeverity.Error)

    # Identity
    MS_ID_0100 = (401, "MS_ID_0100", "Invalid credentials. Invalid email format.", ResponseSeverity.Error)
    MS_ID_0101 = (401, "MS_ID_0101", "Invalid credentials.", ResponseSeverity.Error)
    MS_ID_0102 = (400, "MS_ID_0102", "Invalid email format.", ResponseSeverity.Error)
    MS_ID_0103 = (400, "MS_ID_0103", "Password too weak.", ResponseSeverity.Warning)
    MS_ID_0104 = (403, "MS_ID_0104", "User already exists.", ResponseSeverity.Error)
    MS_ID_0105 = (500, "MS_ID_0105", "Unknown error.", ResponseSeverity.Critical)

    # password reset
    MS_ID_0106 = (400, "MS_ID_0106", "Invalid email format.", ResponseSeverity.Error)
    MS_ID_0107 = (400, "MS_ID_0107", "Email must be specified.", ResponseSeverity.Error)
    MS_ID_0108 = (400, "MS_ID_0108", "Invalid email address.", ResponseSeverity.Error)
    MS_ID_0109 = (400, "MS_ID_0109", "Invalid recovery code.", ResponseSeverity.Error)
    # password update
    MS_ID_0110 = (400, "MS_ID_0110", "Password must be specified.", ResponseSeverity.Error)
    MS_ID_0111 = (400, "MS_ID_0111", "Invalid old password.", ResponseSeverity.Error)

    # Любой успешный ответ
    Success = MS_0000
    Created = MS_ID_0001
    Updated = MS_ID_0002
    Deleted = MS_ID_0003
    # Auth
    TokenNotDefined = MS_ID_0014
    InvalidToken = MS_ID_0012
    ExpiredToken = MS_ID_0013
    InvalidContentType = MS_ID_0010
    InvalidContent = MS_ID_0011
