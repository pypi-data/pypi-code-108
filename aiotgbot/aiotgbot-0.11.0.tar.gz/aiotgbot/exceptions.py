from typing import Optional

__all__ = ('TelegramError', 'MigrateToChat', 'RetryAfter', 'BadGateway',
           'RestartingTelegram', 'BotBlocked', 'BotKicked')


class TelegramError(Exception):
    pattern: Optional[str] = None

    def __init__(self, error_code: int, description: str) -> None:
        super().__init__(f'{error_code} {description}')
        self.error_code = error_code
        self.description = description

    @classmethod
    def match(cls, description: str) -> bool:
        return cls.pattern is not None and cls.pattern in description.lower()


class MigrateToChat(TelegramError):

    def __init__(self, error_code: int, description: str,
                 chat_id: int) -> None:
        super().__init__(error_code, description)
        self.error_code = error_code
        self.description = description
        self.chat_id = chat_id


class RetryAfter(TelegramError):

    def __init__(self, error_code: int, description: str,
                 retry_after: int) -> None:
        super().__init__(error_code, description)
        self.error_code = error_code
        self.description = description
        self.retry_after = retry_after


class BadGateway(TelegramError):
    pattern = 'bad gateway'


class RestartingTelegram(TelegramError):
    pattern = 'restart'


class BotBlocked(TelegramError):
    pattern = 'bot was blocked by the user'


class BotKicked(TelegramError):
    pattern = 'bot was kicked from a chat'
