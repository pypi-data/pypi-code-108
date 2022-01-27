import subprocess

import yaml

from cognite.airworkflow.constants import CHANGED_CODE_SCRIPT_PATH, REPO_CONFIG
from cognite.airworkflow.master_config import get_master_config
from cognite.airworkflow.util import cdf, env


def file_path_changed(pathvalue: str):
    call_bash = subprocess.Popen(["bash", CHANGED_CODE_SCRIPT_PATH, pathvalue], stdout=subprocess.PIPE)
    output = call_bash.communicate()[0]
    encoding = "utf-8"
    return output.decode(encoding)


def check_deployment(function_name: str, project_name: str):
    client = cdf.experimental_client(project_name)
    model_asset = client.assets.retrieve(external_id=function_name)
    if model_asset is None:
        return "True"

    # check if function has been deployed
    repo_name = env.get_env_value("GITHUB_REPOSITORY")
    function_external_id = str(repo_name) + "/" + str(function_name) + ":latest"

    function_asset = client.functions.retrieve(external_id=function_external_id)
    if function_asset is None:
        return "True"

    cdf_model_version = model_asset.metadata["modelVersion"]
    configuration = get_master_config()[1][project_name]
    key1 = [i for i in configuration.keys() if i.parts[-1] == function_name][0]
    model_version = configuration[key1].model_version
    model_version = ".".join(model_version.split(".")[:-1])
    already_deployed = str(model_version != cdf_model_version)
    return already_deployed


def final_string_generator():
    # Read files and send to function
    # CR
    filtered_list = []

    with open(REPO_CONFIG, "r") as f:
        valuesYaml = yaml.load(f, Loader=yaml.FullLoader)

    function_project_mapping = []
    for i in valuesYaml["ProjectFunctionMap"]:
        tenant_name_list = valuesYaml["ProjectFunctionMap"][i]
        function_name_list = [i] * len(tenant_name_list)
        result_string = list(map(lambda x, y: str(x) + "@" + str(y), function_name_list, tenant_name_list))
        function_project_mapping.extend(result_string)

    for i in function_project_mapping:
        function_name, project_name = i.split("@")
        deployment_boolean = check_deployment(function_name, project_name)
        file_path_changed_boolean = file_path_changed("functions/" + function_name)
        file_path_changed_boolean = file_path_changed_boolean.rstrip()
        if file_path_changed_boolean == "True" or deployment_boolean == "True":
            filtered_list.append('"' + i + '"')
    if not filtered_list:
        filtered_list.append('"None_to_deploy"')
    filtered_string = ",".join(map(str, filtered_list))
    final_string = '{"functionproject":[' + filtered_string + "]}"
    print(final_string)


if __name__ == "__main__":
    final_string_generator()
