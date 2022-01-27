from .base import BaseAPIModelStub


class AuditEventStub(BaseAPIModelStub):
    resource_name = 'auditEvents'
    default_data = {
            'id': 123,
            'type': "update_brief_response",
            'acknowledged': False,
            'user': "supplier@example.com",
            'data': {
                "briefResponseData": {
                    "essentialRequirementsMet": True
                },
                "briefResponseId": 44444
            },
            'objectType': "BriefResponse",
            'objectId': 44444,
            'createdAt': "2018-12-10T01:02:03.000000Z",
            'links': {
                "self": "http://localhost/audit-events/123",
            }
    }
    optional_keys = [
        ('userName', 'include_user')
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if kwargs.get("acknowledged"):
            self.response_data["acknowledgedAt"] = "2018-12-11T01:02:03.000000Z"
            self.response_data["acknowledgedBy"] = "acknowledger@example.com"
