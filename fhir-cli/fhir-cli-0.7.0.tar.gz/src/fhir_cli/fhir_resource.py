import json

import requests

from fhir_cli import FHIR_API_URL
from fhir_cli.utils.prettify_json import prettify_json


class FhirValidationError(ValueError):
    pass


class FhirResource:
    """FhirResource represents a fhir resource

    Args:
        resource (dict): dict containing the attributes of the resource
    """

    def __init__(self, resource: dict):
        self.resource = resource

    def __repr__(self):
        raw_json = json.dumps(self.resource, indent=4)
        return prettify_json(raw_json)

    def validate(self):
        """The validate method validates a Fhir resource against a Fhir server

        Raises:
            FhirValidationError: if the Fhir resource is invalid
            HttpError: if the request to the Fhir server returns an error
        """
        serialized_data = json.dumps(self.resource, indent=4)
        profile = None
        try:
            profile = self.resource["meta"]["profile"][0]
        except KeyError:
            pass
        try:
            resource_type = self.resource["resourceType"]
        except KeyError:
            raise FhirValidationError("resource has no resource type")
        r = requests.post(
            f"{FHIR_API_URL}/{resource_type}/$validate{f'?profile={profile}' if profile else ''}",
            data=serialized_data,
            headers={"Content-Type": "application/json+fhir"},
        )
        if r.status_code == 404:
            raise FhirValidationError(f"{resource_type} is an unknown resource type")
        elif r.status_code != 400 and r.status_code != 412:
            r.raise_for_status()
        data = r.json()
        issues = (
            [issue for issue in data["issue"] if issue["severity"] == "error"]
            if "issue" in data
            else []
        )
        if len(issues):
            errors = "\n".join(
                [
                    f"* {issue['location'][0]}: {issue['diagnostics']} at {issue['location'][1]}"
                    if "location" in issue
                    else f"* {issue['diagnostics']}"
                    for issue in issues
                ]
            )
            raise FhirValidationError(f"the FHIR server returned a list of issues\n{errors}")
