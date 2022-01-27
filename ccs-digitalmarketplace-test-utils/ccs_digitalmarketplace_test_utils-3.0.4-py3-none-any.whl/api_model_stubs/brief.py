from .base import BaseAPIModelStub


class BriefStub(BaseAPIModelStub):
    resource_name = 'briefs'
    user = {
        "active": True,
        "role": "buyer",
        "emailAddress": "buyer@email.com",
        "id": 123,
        "name": "Buyer User"
    }
    default_data = {
        "id": 1234,
        "title": "I need a thing to do a thing",
        "frameworkSlug": "digital-outcomes-and-specialists",
        "frameworkName": "Digital Outcomes and Specialists",
        "frameworkFramework": "digital-outcomes-and-specialists",
        "frameworkStatus": "live",
        "framework": {
            "family": "digital-outcomes-and-specialists",
            "name": "Digital Outcomes and Specialists",
            "slug": "digital-outcomes-and-specialists",
            "status": "live",
        },
        "lotName": "Digital Specialists",
        "lotSlug": "digital-specialists",
        "isACopy": False,
        "status": "draft",
        "createdAt": "2016-03-29T10:11:12.000000Z",
        "updatedAt": "2016-03-29T10:11:13.000000Z",
        "links": {}
    }

    optional_keys = [
        ('lotName', 'lot_name'),
        ('lotSlug', 'lot_slug'),
        ('clarificationQuestions', 'clarification_questions'),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if kwargs.get('user_id'):
            self.response_data['users'] = [self.user.copy()]
            self.response_data['users'][0]['id'] = kwargs.pop('user_id')
            del self.response_data['user_id']

        # Allow snake case framework_* kwargs for backwards compatibility
        for nested_framework_key, camelcase_key, snakecase_kwarg in [
            ('family', 'frameworkFramework', 'framework_family'),
            ('name', 'frameworkName', 'framework_name'),
            ('slug', 'frameworkSlug', 'framework_slug'),
            ('status', 'frameworkStatus', 'framework_status'),
        ]:
            if kwargs.get(snakecase_kwarg):
                # Update top level key
                self.response_data[camelcase_key] = kwargs.get(snakecase_kwarg)
                # Update nested key, deleting the snakecase kwarg which will have been updated already in super()
                self.response_data['framework'][nested_framework_key] = kwargs.get(snakecase_kwarg)
                del self.response_data[snakecase_kwarg]

        if (
            ("framework_slug" in kwargs or "frameworkSlug" in kwargs)
            and ("framework_name" not in kwargs and "frameworkName" not in kwargs)
            and ("framework_family" not in kwargs and "frameworkFramework" not in kwargs)
        ):
            # The brief model serialisation includes both new-style and old-style framework keys,
            # and the deprecated `frameworkFramework` field. Consumers should use `brief['framework']['family']`,
            # not `brief['frameworkFamily']` or `brief['frameworkFramework]`, but we should still make sure
            # our test stubs reflect the model.
            self.response_data.update(
                self._format_framework(self.response_data["frameworkSlug"], new_style=True, old_style=True)
            )
            self.response_data["frameworkFramework"] = self.response_data["frameworkFamily"]
            del self.response_data["frameworkFamily"]

        # Status-dependent values
        if self.response_data['status'] != "draft":
            self.response_data["publishedAt"] = "2016-03-29T10:11:14.000000Z"
            self.response_data["applicationsClosedAt"] = "2016-04-07T00:00:00.000000Z"
            self.response_data["clarificationQuestionsClosedAt"] = "2016-04-02T00:00:00.000000Z"
            self.response_data["clarificationQuestionsPublishedBy"] = "2016-04-02T00:00:00.000000Z"
            if kwargs.get('clarification_questions_closed') is not None:
                self.response_data["clarificationQuestionsAreClosed"] = kwargs.pop('clarification_questions_closed')
                del self.response_data['clarification_questions_closed']
            else:
                self.response_data["clarificationQuestionsAreClosed"] = False

        if self.response_data['status'] == "withdrawn":
            self.response_data["withdrawnAt"] = "2016-05-07T00:00:00.000000Z"
        elif self.response_data['status'] == "unsuccessful":
            self.response_data["unsuccessfulAt"] = "2016-05-07T00:00:00.000000Z"
        elif self.response_data['status'] == "cancelled":
            self.response_data["cancelledAt"] = "2016-05-07T00:00:00.000000Z"

    def single_result_response(self):
        # users and clarificationQuestions are always included in API response
        if 'users' not in self.response_data:
            self.response_data['users'] = [self.user.copy()]

        if 'clarificationQuestions' not in self.response_data:
            self.response_data['clarificationQuestions'] = []

        return {
            self.resource_name: self.response_data
        }
