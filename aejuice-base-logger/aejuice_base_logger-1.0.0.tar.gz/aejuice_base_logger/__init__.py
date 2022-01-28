from datetime import datetime


class Logger:
    def __init__(self, service_name: str, context: str = "app"):
        self.service_name = service_name
        self.context = context

    def log(self, message: str, context: str = ""):
        print(self.get_log_message(message, context))

    def get_log_message(self, message: str, context: str = ""):
        if context == "":
            context = self.context

        return f"{datetime.now().strftime('%Y-%m-%dT%H:%I:%S')} [{self.service_name}][{context}] - {message}"
