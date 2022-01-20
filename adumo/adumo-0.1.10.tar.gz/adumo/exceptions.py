class AdumoFailedInit(Exception):
    pass


class AdumoInvalidCard(Exception):
    pass


class AdumoInvalidRequestedAmount(Exception):
    pass


class CreditCardProcessorCardNotEnrolled3ds(Exception):
    pass


class AdumoFailedTransaction(Exception):
    def __init__(self, status_code, status_message):
        self.status_message = status_message
        self.status_code = status_code

        super().__init__(status_code, status_message)


class CreditCardProcessorInvalidResponse(Exception):
    def __init__(self, response):
        message = f"Adumo did not return JSON. Response {response}"

        super().__init__(message)


class CreditCardProcessor3dsFailure(Exception):
    def __init__(self, status_code, status_message):
        self.status_code = status_code
        self.status_message = status_message

        super().__init__(status_code, status_message)
