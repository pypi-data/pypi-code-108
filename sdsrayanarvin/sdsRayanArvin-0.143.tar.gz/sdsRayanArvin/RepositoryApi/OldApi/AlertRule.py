from sdsRayanArvin.Dataset import AlertRuleData
from sdsRayanArvin.Repository import Repository


class AlertRule(Repository):
    def allAlertRule(self):
        res = self.Request.sendWithToken('GET', 'all_alert_communication')
        try:
            return AlertRuleData(res['Alert_Com']).data
        except:
            return []
