"""
Limits API calls.
"""

def getPlatformLimits(self, tier=None, setting=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getPlatformLimits",
            "variables": {
                "tier": tier,
                "setting": setting
            },
            "query": """query 
                getPlatformLimits($tier: String, $setting: String) {
                    getPlatformLimits(tier: $tier, setting: $setting){
                        setting
                        tier
                        value
                    }
                }"""})
    return self.errorhandler(response, "getPlatformLimits")


def setPlatformLimit(self, tier, setting, limit):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "setPlatformLimits",
            "variables": {
                "setting": setting,
                "tier": tier,
                "limit": limit
            },
            "query": """mutation 
                setPlatformLimits($tier: String!, $setting: String!, $limit: Int!) {
                    setPlatformLimits(tier: $tier, setting: $setting, limit: $limit)
                }"""})
    return self.errorhandler(response, "setPlatformLimits")


def getOrganizationLimits(self, organizationId, setting=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getOrganizationLimits",
            "variables": {
                "organizationId": organizationId,
                "setting": setting
            },
            "query": """query 
                getOrganizationLimits($organizationId: String!, $setting: String) {
                    getOrganizationLimits(organizationId: $organizationId, setting: $setting){
                        organizationId
                        setting
                        limit
                        usage
                    }
                }"""})
    return self.errorhandler(response, "getOrganizationLimits")

def setOrganizationLimit(self, organizationId, setting, limit):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "setOrganizationLimits",
            "variables": {
                "organizationId": organizationId,
                "setting": setting,
                "limit": limit
            },
            "query": """mutation 
                setOrganizationLimits($organizationId: String!, $setting: String!, $limit: Int!) {
                    setOrganizationLimits(organizationId: $organizationId, setting: $setting, limit: $limit)
                }"""})
    return self.errorhandler(response, "setOrganizationLimits")


def getWorkspaceLimits(self, workspaceId, setting=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getWorkspaceLimits",
            "variables": {
                "workspaceId": workspaceId,
                "setting": setting
            },
            "query": """query 
                getWorkspaceLimits($workspaceId: String!, $setting: String) {
                    getWorkspaceLimits(workspaceId: $workspaceId, setting: $setting){
                        workspaceId
                        setting
                        limit
                        usage
                    }
                }"""})
    return self.errorhandler(response, "getWorkspaceLimits")


def setWorkspaceLimit(self, workspaceId, setting, limit):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "setWorkspaceLimits",
            "variables": {
                "workspaceId": workspaceId,
                "setting": setting,
                "limit": limit
            },
            "query": """mutation 
                setWorkspaceLimits($workspaceId: String!, $setting: String!, $limit: Int!) {
                    setWorkspaceLimits(workspaceId: $workspaceId, setting: $setting, limit: $limit)
                }"""})
    return self.errorhandler(response, "setWorkspaceLimits")


def getOrganizationUsage(self, organizationId, year, month, workspaceId=None, member=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getOrganizationUsage",
            "variables": {
                "organizationId": organizationId,
                "workspaceId": workspaceId,
                "member": member,
                "year": year,
                "month": month
            },
            "query": """query 
                getOrganizationUsage($organizationId: String!, $workspaceId: String, $member: String, $year: String!, $month: String!) {
                    getOrganizationUsage(organizationId: $organizationId, workspaceId: $workspaceId, member: $member, year: $year, month: $month){
                        channel
                        instanceType
                        time
                    }
                }"""})
    return self.errorhandler(response, "getOrganizationUsage")

