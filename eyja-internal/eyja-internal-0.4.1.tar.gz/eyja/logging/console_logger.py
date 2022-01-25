from datetime import datetime


class ConsoleLogger:
    def __init__(self):
        self.start_dt = datetime.utcnow()

    def gray_text(self, message: str):
        return f'\033[02m{message}\033[0m'

    def green_text(self, message: str):
        return f'\033[32m{message}\033[0m'

    def yellow_text(self, message: str):
        return f'\033[93m{message}\033[0m'

    def red_text(self, message: str):
        return f'\033[31m{message}\033[0m'

    def log(self, message):
        delta = datetime.utcnow() - self.start_dt

        print(f'{self.gray_text(f"[{delta}]")} {message}')

    def info(self, message):
        self.log(self.gray_text(message))

    def error(self, message):
        self.log(self.red_text(message))

    def warning(self, message):
        self.log(self.yellow_text(message))

    def success(self, message):
        self.log(self.green_text(message))
