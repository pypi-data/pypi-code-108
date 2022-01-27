from sym.sdk.util.template.sym import get_flows, handles_to_users


class TestSymIntegrationInterface:
    def test_missing_body(self):
        v1 = get_flows(user="andrew@symops.io")
        v2 = handles_to_users(
            service_type="pager_duty",
            external_id=None,
            matchers_and_emails=[({"user_id": "P123456"}, None)],
        )

        assert v1 is None
        assert v2 is None
