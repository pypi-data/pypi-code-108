from sdsRayanArvin.Dataset.RuleData import RuleData
from sdsRayanArvin.Repository import Repository


class Rule(Repository):
    def allRule(self):
        res = self.Request.sendWithToken('GET', 'rule_group')
        try:
            return RuleData(res['success']).data
        except:
            return []
