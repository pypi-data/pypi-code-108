
import unittest

from flask_opsgenie.entities import OpsgenieAlertParams, AlertPriority

class TestOpsgenieAlertParams(unittest.TestCase):

    def test_init_defaults(self):

        opsgenie_params = OpsgenieAlertParams(
            opsgenie_token="fake_token",
            alert_tags=None,
            alert_alias=None,
            alert_status_alias=None,
            alert_latency_alias=None,
            alert_exception_alias=None,
            alert_priority="P4",
            alert_responder=None,
            opsgenie_api_base=None,
            alert_details={"host": "testhost"}
        )

        self.assertEqual(opsgenie_params.alert_tags[0], "flask-alert")
        self.assertEqual(opsgenie_params.alert_details.get("service_id"), "flask-service-testhost")
        self.assertEqual(opsgenie_params.alert_priority.value, AlertPriority.P4.value)
