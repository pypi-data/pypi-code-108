from .base import BaseAPIModelStub


class BriefResponseStub(BaseAPIModelStub):
    resource_name = 'briefResponses'
    brief = {
        "id": 1234,
        "title": "I need a thing to do a thing",
        "status": "live",
        "applicationsClosedAt": "2016-11-22T11:22:33.444444Z",
        "framework": {
            "family": "digital-outcomes-and-specialists",
            "name": "Digital Outcomes and Specialists 3",
            "slug": "digital-outcomes-and-specialists-3",
            "status": "live"
        }
    }
    award_details = {
        "awardedContractStartDate": "2017-03-01",
        "awardedContractValue": "10000"
    }
    default_data = {
        "availability": "25/01/2017",
        "createdAt": "2016-11-01T11:22:33.444444Z",
        "essentialRequirements": [],
        "essentialRequirementsMet": True,
        "id": 54321,
        "links": {
            "brief": "http://localhost:5000/brief/1234",
            "self": "http://localhost:5000/brief-responses/54321",
            "supplier": "http://localhost:5000/supplier/1234"
        },
        "niceToHaveRequirements": [],
        "respondToEmailAddress": "contactme@example.com",
        "submittedAt": "2016-11-21T12:00:01.000000Z",
        "status": "submitted",
        "supplierId": 1234,
        "supplierName": "My Little Company",
        "supplierOrganisationSize": "micro",
    }

    def _make_brief_ids_consistent(self, **kwargs):
        """
        Use kwargs["brief"]["id"] if given
        Otherwise use kwargs["brief_id"] if given
        """
        brief_id = 1234
        if 'brief_id' in kwargs:
            brief_id = kwargs.get('brief_id')
            del self.response_data['brief_id']
        if kwargs.get('brief', {}).get('id'):
            brief_id = kwargs['brief']['id']

        self.response_data['briefId'] = brief_id
        self.response_data['brief']['id'] = brief_id
        self.response_data['links']['brief'] = "http://localhost:5000/brief/{}".format(brief_id)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if "brief" not in kwargs:
            self.response_data["brief"] = self.brief.copy()

        if kwargs.get("framework_slug") is not None:
            self.response_data["brief"]["framework"]["slug"] = kwargs.pop("framework_slug")
            del self.response_data["framework_slug"]

        # Update IDs and links
        self._make_brief_ids_consistent(**kwargs)
        if kwargs.get('supplier_id') is not None:
            supplier_id = kwargs.get('supplier_id')
            self.response_data['supplierId'] = supplier_id
            self.response_data['links']['supplier'] = "http://localhost:5000/supplier/{}".format(supplier_id)
            del self.response_data['supplier_id']
        if kwargs.get("id") is not None:
            self.response_data["links"]["self"] = "http://localhost:5000/brief-response/{}".format(kwargs.get("id"))

        if "status" in kwargs:
            if kwargs.get("status") == "pending-awarded":
                self.response_data['awardDetails'] = {'pending': True}
            if kwargs.get("status") == "awarded":
                self.response_data['awardDetails'] = self.award_details.copy()
                self.response_data['awardedAt'] = "2017-01-21T12:00:01.000000Z"
            self.response_data["status"] = kwargs.pop("status")
