import yaml
from os.path import exists
from gitlab_evaluate.models.ci_rules import CiRules
import pathlib

path = "./evaluate/data"
if not exists(path):
    print("Using absolute path")
    path = f"{pathlib.Path(__file__).parent.parent.absolute()}/data"
else:
    print("Using relative path")

def get_readiness_config():
    with open(f"{path}/default-rules-config.yml", "r") as f:
        return CiRules(**yaml.safe_load(f))

def get_readiness_report_headers():
    with open(f"{path}/ci-readiness-report.yml", "r") as f:
        return yaml.safe_load(f)

def get_migration_report_headers():
    with open(f"{path}/migration-report.yml", "r") as f:
        return yaml.safe_load(f)