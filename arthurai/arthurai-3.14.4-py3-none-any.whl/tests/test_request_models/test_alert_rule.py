import pytest

from tests.test_request_models.fixtures import AlertRuleDict_1, \
    AlertRuleJson_1, AlertRuleObject_1, AlertRuleObject_2, AlertRuleDict_2, AlertRuleJson_2, \
    AlertRuleObject_3, AlertRuleDict_3, AlertRuleJson_3
from arthurai.core.alerts import AlertRule


class TestAlertRule:

    @pytest.mark.parametrize("alert_rule_object, alert_rule_dict, alert_rule_json", [
        (AlertRuleObject_1, AlertRuleDict_1, AlertRuleJson_1),
        (AlertRuleObject_2, AlertRuleDict_2, AlertRuleJson_2),
        (AlertRuleObject_3, AlertRuleDict_3, AlertRuleJson_3)
    ])
    def test_alert_rule_model(self, alert_rule_object, alert_rule_dict, alert_rule_json):
        assert alert_rule_object.to_json() == alert_rule_json
        assert AlertRule.from_json(alert_rule_json) == alert_rule_object

        assert alert_rule_object.to_dict() == alert_rule_dict
        assert AlertRule.from_dict(alert_rule_dict) == alert_rule_object
