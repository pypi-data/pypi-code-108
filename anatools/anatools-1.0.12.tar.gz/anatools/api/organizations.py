"""
Organizations API calls.
"""

def getOrganizations(self):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getOrganizations",
            "variables": {},
            "query": """query 
                getOrganizations {
                    getOrganizations {
                        organizationId
                        name
                        role
                    }
                }"""})
    return self.errorhandler(response, "getOrganizations")


def editOrganization(self, organizationId, name):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editOrganization",
            "variables": {
                "organizationId": organizationId,
                "name": name
            },
            "query": """mutation 
                editOrganization($organizationId: String!, $name: String!) {
                    editOrganization(organizationId: $organizationId, name: $name) 
                }"""})
    return self.errorhandler(response, "editOrganization")
