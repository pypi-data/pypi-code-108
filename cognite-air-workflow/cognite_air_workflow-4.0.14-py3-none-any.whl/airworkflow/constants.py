from pathlib import Path
from typing import Dict

from cognite.airworkflow.model.project import Project, ProjectInfo
from cognite.airworkflow.util import env, repoconfighelpers

# List of base constants
working_path = env.get_env_value("PWD")
ROOT_DIR = Path(working_path)
FUNCTIONS_PATH = ROOT_DIR / "functions"
IGNORE_MODELS_PATH = ROOT_DIR / ".ignore_models"
SCHEDULE_MANAGER_EXTERNAL_IDS = [
    "cognitedata/air-ds-infrastructure/schedulemanager:latest",
    "cognitedata/air-functions/schedulemanager:latest",
    "cognitedata/air-ds-infrastructure/schedulemanager2:latest",
]

REPO_CONFIG = ROOT_DIR / "repoconfig.yaml"

REPO_CONFIG_PROJECT_FUNCTION_MAP = "ProjectFunctionMap"
# Paths within a functions folder
FUNCTION_REL_PATH = Path("function")
FUNCTION_REL_CONFIG_PATH = FUNCTION_REL_PATH / "config.yaml"
FUNCTION_REL_RESOURCE_PATH = FUNCTION_REL_PATH / "resources"
FUNCTION_REL_DEPLOYMENT_PATH = FUNCTION_REL_RESOURCE_PATH / "dependencies.yaml"
FUNCTION_REL_INIT_PATH = FUNCTION_REL_PATH / "__init__.py"

# WORK FLOW PATHS
WORK_FLOW_PATH = ROOT_DIR / ".github" / "workflows"
WORK_FLOWS = [WORK_FLOW_PATH / p for p in ["build-master.yaml", "build-pr.yaml", "delete-pr.yaml"]]

# CONFIG PATHS
BASE_PATH = Path(__file__).parent.resolve()
CHANGED_CODE_SCRIPT_PATH = BASE_PATH / "file_changed.sh"
SCHEMAS_PATH = BASE_PATH / "schemas"
DEPLOYMENT_SCHEMA_PATH = SCHEMAS_PATH / "deployment-schema.yaml"
CONFIG_SCHEMA_PATH = SCHEMAS_PATH / "config-schema.yaml"

url_dict = repoconfighelpers.get_url_dict()
AUTHENTICATION: Dict = {}
for project in Project.NAME.value:
    if project in url_dict:
        project_config = url_dict[project]
        if isinstance(project_config, list):  # legacy
            project_authentication = ProjectInfo(
                project=project, client_key_name=project_config[1], base_url=str(project_config[0])
            )
        elif isinstance(project_config, dict):  # OIDC
            project_authentication = ProjectInfo(
                project=project,
                base_url=project_config["base_url"],
                tenant_id=project_config["tenant_id"],
                client_id=project_config["client_id"],
                secret_name=project_config["secret_name"],
                token_url=project_config["token_url"],
                scopes=project_config["scopes"],
            )
        else:
            project_authentication = ProjectInfo(project, "AIR_API_KEY", str(project_config))

    else:
        project_authentication = ProjectInfo(project, "AIR_API_KEY")
    AUTHENTICATION[project] = project_authentication


# GitHub/Lab constants
gitlab_function_name_addition = "FUNCTION_NAME_ADDITION"
gitlab_ci_project = "CI_PROJECT_PATH"

# String variable definitions
COGNITE_CLIENT_NAME = "AIR Functions Client"
