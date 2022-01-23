from sdsRayanArvin.Repository import Repository


class RuleExe(Repository):
    def RuleRunOnId(self, ID_rule):
        res = self.Request.sendWithToken('GET', 'run/' + ID_rule)
        return res['status']