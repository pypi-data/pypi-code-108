class ContractIbanChangeService:
    def __init__(self, env):
        self.env = env

    def run_from_api(self, **params):
        self.env['contract.iban.change.wizard'].with_delay().run_from_api(**params)
        return {"result": "OK"}
