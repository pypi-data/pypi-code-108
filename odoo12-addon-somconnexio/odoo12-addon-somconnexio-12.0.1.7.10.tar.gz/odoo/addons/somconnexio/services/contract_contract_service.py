class ContractService:
    def __init__(self, env):
        self.env = env

    def create(self, **params):
        self.env['contract.contract'].with_delay().create_contract(**params)
        return {"result": "OK"}

    def count(self):
        domain_contracts = [('is_terminated', '=', False)]
        domain_members = [
            ('parent_id', '=', False), ('customer', '=', True),
            '|', ('member', '=', True), ('coop_candidate', '=', True)
        ]
        number = self.env['contract.contract'].sudo().search_count(domain_contracts)
        result = {"contracts": number}
        number = self.env['res.partner'].sudo().search_count(domain_members)
        result['members'] = number
        return result
