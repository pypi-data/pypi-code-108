from pymedquery.config.logger import get_logger


class Logger:
    def __init__(self, name: str):
        self.logger = get_logger(name)

        self.info_log = []
        self.success_log = []
        self.warning_log = []
        self.error_log = []

    def info(self, message: str):
        self.logger.info(message)
        self.info_log.append(message)

    def success(self, message: str):
        self.logger.success(message)
        self.success_log.append(message)

    def warning(self, message: str):
        self.logger.warning(message)
        self.warning_log.append(message)

    def error(self, message: str):
        self.logger.error(message)
        self.error_log.append(message)

    def get_log(self, type_name: str) -> list:
        if type_name == "info":
            return self.info_log
        elif type_name == "success":
            return self.success_log
        elif type_name == "warning":
            return self.warning_log
        elif type_name == "error":
            return self.error_log
        self.logger.error(f"TRIED GETTING AN INVALID LOGGER: {type_name}")
        return []

    def get_log_length(self, type_name: str) -> int:
        if type_name == "info":
            return len(self.info_log)
        elif type_name == "success":
            return len(self.success_log)
        elif type_name == "warning":
            return len(self.warning_log)
        elif type_name == "error":
            return len(self.error_log)

        self.logger.error(f"TRIED GETTING AN INVALID LOGGER LENGTH: {type_name}")
        return 0

    def is_empty(self, type_name: str) -> bool:
        return self.get_log_length(type_name) == 0
