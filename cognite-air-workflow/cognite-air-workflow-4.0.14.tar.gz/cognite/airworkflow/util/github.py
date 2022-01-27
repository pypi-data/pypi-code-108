import json
from typing import List

import requests

from cognite.airworkflow.util import env


def get_open_pr_refs() -> List[str]:
    repository_name = env.get_repo_name_auto()
    url = "https://api.github.com/repos/" + repository_name + "/pulls"
    authorization_string = "Bearer " + env.get_github_token()
    payload = {"state": "open"}
    result = requests.get(
        url, params=payload, headers={"authorization": authorization_string, "content-type": "application/json"}
    )
    json_obj = json.loads(result.content)
    return [pr["head"]["ref"] for pr in json_obj]


def gitlab_open_mrs(project_id: str, gitlab_token: str) -> List[str]:
    url = "http://www.gitlab.com/api/v4/projects/" + project_id + "/merge_requests"

    header = {
        "PRIVATE-TOKEN": gitlab_token,
        "id": project_id,
        "state": "opened",
        "scope": "all",
        "view": "simple",
    }

    reply = requests.get(url, headers=header)
    status = json.loads(reply.content)
    return [pr["source_branch"] for pr in status]
