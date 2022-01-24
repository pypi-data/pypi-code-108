from dataclasses import dataclass
from jinja2 import Template
import requests

from .logger import logger
from . import config


@dataclass
class GitlabRunnerRegistration:
    id: int
    token: str


def register_runner(gitlab_url: str, registration_token: str,
                    description: str, tag_list: list[str],
                    run_untagged: bool = False, maximum_timeout: int = 3600):
    params = {
        "token": registration_token,
        "description": description,
        "tag_list": ",".join(tag_list),
        "run_untagged": run_untagged,
        "maximum_timeout": maximum_timeout
    }

    r = requests.post(f"{gitlab_url}/api/v4/runners", params=params)
    if r.status_code == 201:
        return GitlabRunnerRegistration(**r.json())
    else:
        return None


def unregister_runner(gitlab_url: str, token: str):
    requests.delete(f"{gitlab_url}/api/v4/runners", params={"token": token})


def verify_runner_token(gitlab_url: str, token: str):
    r = requests.post(f"{gitlab_url}/api/v4/runners/verify", params={"token": token})
    return r.status_code == 200


def generate_runner_config(mars_db):
    logger.info("Generate the GitLab runner configuration")
    with open(config.GITLAB_CONF_TEMPLATE_FILE) as f:
        config_toml = Template(f.read()).render(config=config, mars_db=mars_db)

    with open(config.GITLAB_CONF_FILE, 'w') as f:
        f.write(config_toml)
