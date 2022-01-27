import click
from autogen.runner import Runner
from autogen.database import Warehouse
from autogen.config import Config
import ruamel.yaml
from pathlib import Path


def main():

    # Setup ruamel.yaml
    yml = ruamel.yaml.YAML()
    yml.indent(mapping=2, sequence=4, offset=2)
    yml.preserve_quotes = True

    # Get API key and secret
    api_key = click.prompt("Enter your Fivetran API key", type=str)
    api_secret = click.prompt("Enter your Fivetran API secret", type=str)

    # Create a runner
    runner = Runner(api_key, api_secret)

    # Confirm which group to use
    group_id = get_group_id(runner)

    # Confirm which connector type to use
    connector_selection = get_connector_type(runner, group_id)

    # Get connectors
    connectors = runner.get_connectors(group_id, connector_selection)

    # TODO: change this to work with multiple connectors
    schemas = list(connectors.keys())
    # connector_ids = list(connectors.values())

    # Load config
    config = Config(connector_selection)

    # Update packages.yml
    update_packages(config.name, config.version, yml)

    # Update dbt_project.yml
    update_dbt_project(
        config,
        schemas,
        yml,
    )


def get_group_id(runner):
    groups = runner.get_groups()
    groups_option_list = list(groups.keys())
    if len(groups_option_list) == 1:
        group_id = groups[groups_option_list[0]]
    else:
        print("\nAvailable groups:")
        groups_prompt_msg = (
            "\n".join([f"[{n+1}] {v}" for n, v in enumerate(groups_option_list)])
            + "\nDesired option (enter a number)"
        )
        numeric_group_selection = click.prompt(groups_prompt_msg, type=int)
        group_id = groups[groups_option_list[numeric_group_selection - 1]]
    return group_id


def get_connector_type(runner, group_id):
    print("\nAvailable connectors:")
    connector_types = runner.get_connector_types(group_id)
    connector_prompt_msg = (
        "\n".join([f"[{n+1}] {v}" for n, v in enumerate(connector_types)])
        + "\nDesired option (enter a number)"
    )
    numeric_connector_selection = click.prompt(connector_prompt_msg, type=int)
    connector_selection = connector_types[numeric_connector_selection - 1]
    return connector_selection


def update_packages(package_name, package_version, yml):

    # Create file it not exists
    file = open("packages.yml", "a+").close()

    # TODO: This should be doable in one pass, but having issue with opening modes
    with open("packages.yml", "r") as file:
        packages = yml.load(file)

    # If no packages, create full structure
    if packages is None:
        packages = {"packages": [{"package": package_name, "version": package_version}]}

    # If package is declared already, update version
    elif any([p for p in packages["packages"] if p["package"] == package_name]):
        package = [p for p in packages["packages"] if p["package"] == package_name][0]
        package["version"] = package_version

    # Otherwise, append new package to packages
    else:
        packages["packages"].append(
            {"package": package_name, "version": package_version}
        )

    with open("packages.yml", "w") as file:
        yml.dump(packages, file)


def load_dbt_project(yml):
    with open("dbt_project.yml", "r") as file:
        project = yml.load(file)
    return project


def update_dbt_project(
    config,
    schemas,
    yml,
):
    project = load_dbt_project(yml)

    profile_name = project["profile"]
    dbt_profiles_path = Path(Path.home(), ".dbt", "profiles.yml")

    with open(dbt_profiles_path, "r") as file:
        profiles = yml.load(file)
        credentials = dict(
            profiles[profile_name]["outputs"][profiles[profile_name]["target"]]
        )

    if not project.get("vars"):
        project["vars"] = {}

    project["vars"][config.schema_variable] = schemas[0]
    database = click.prompt(
        f"\nEnter the database/project of your {config.connector}", type=str
    )
    project["vars"][config.database_variable] = database

    warehouse = Warehouse(credentials)
    connector_tables = warehouse.run_query(schemas[:1], database)

    for v in config.enabled_variables:
        if "required_tables" in v:
            enabled = all(item in connector_tables for item in v["required_tables"])
            project["vars"][v["name"]] = enabled

    for v in config.preset_variables:
        if v["type"] == "list":
            project["vars"][v["name"]] = []

    with open("dbt_project.yml", "w") as file:
        yml.dump(project, file)


if __name__ == "__main__":
    main()
