from .opencell_resource import OpenCellResource


class AccessFromContract(OpenCellResource):
    def __init__(self, contract):
        self.contract = contract
        self.white_list = ['code', 'subscription']

    @property
    def code(self):
        return self.contract.phone_number

    @property
    def subscription(self):
        return self.contract.code
