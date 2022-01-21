class Log:
    def __init__(self):
        pass

    @classmethod
    def info(cls, message, header=None, sub_header=None):
        cls.__log(message, header, sub_header)

    @classmethod
    def question(cls, question):
        print(question, end="")

    @classmethod
    def started(cls, message, sub_header=None):
        cls.__log(message, 'INITIATED', sub_header)

    @classmethod
    def completed(cls, message, sub_header=None):
        cls.__log(message, 'COMPLETED', sub_header)

    @classmethod
    def error(cls, message, sub_header=None):
        cls.__log(message, 'ERROR', sub_header)

    @classmethod
    def __log(cls, message, header=None, sub_header=None):
        result = ""
        if header is not None:
            result = f"{header} | "
        if sub_header is not None:
            result = f"{result}{sub_header} | "
        result = f"{result}{message}"
        print(result)
