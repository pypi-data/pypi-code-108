import dataclasses
from typing import List


@dataclasses.dataclass
class AgilicusScopes:
    applications: List[str]
    audits: List[str]
    catalogues: List[str]
    challenges: List[str]
    diagnostics: List[str]
    files: List[str]
    issuers: List[str]
    messages: List[str]
    metrics: List[str]
    orgs: List[str]
    sysgroups: List[str]
    traffic_tokens: List[str]
    users: List[str]
    permissions: List[str]

    def to_list(self):
        scopes = []
        for endpoint, scope_list in self.__dict__.items():
            # Translate _ to - since we're representing these as python vars
            endpoint_name = endpoint.replace("_", "-")
            for scope in scope_list:
                scopes.append(f"urn:agilicus:api:{endpoint_name}:{scope}")

        return list(set(scopes))


# Please keep this list in sync with the one in
# portal/src/app/core/services/auth-service.service.ts
DEFAULT_SCOPES = ["urn:agilicus:api:*?"]

ADMIN_SCOPES = ["urn:agilicus:api:*:creator?"]


def get_default_scopes():
    return DEFAULT_SCOPES


def get_admin_scopes():
    return ADMIN_SCOPES
