from cognite.client import CogniteClient


def retrieve_air_api_url(client: CogniteClient, staging: bool = True):
    cluster = client.config.base_url.split(".cognitedata")[0].split("//")[1]
    cluster = "" if cluster == "api" else f"{cluster}."
    url = f"https://air-api.{'staging.' if staging else ''}{cluster}cognite.ai/project/" + client.config.project
    return url
