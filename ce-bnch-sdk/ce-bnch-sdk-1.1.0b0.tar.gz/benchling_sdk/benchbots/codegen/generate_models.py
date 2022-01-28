from typing import Dict, Union

from jinja2 import Environment, PackageLoader

from benchling_sdk.benchbots.codegen.helpers import reformat_code_str
from benchling_sdk.benchbots.types.manifest import (
    DropdownDependency,
    EntitySchemaDependency,
    Manifest,
    SchemaDependency,
)


def generate_model(dependency: Union[EntitySchemaDependency, SchemaDependency, DropdownDependency]) -> str:
    env = Environment(
        loader=PackageLoader("benchling_sdk.benchbots.codegen", "templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    if isinstance(dependency, (EntitySchemaDependency, SchemaDependency)):
        template = env.get_template("schema_instance_model.py.jinja2")
    else:
        template = env.get_template("dropdown_model.py.jinja2")

    return reformat_code_str(template.render(dependency=dependency))


def generate_models(manifest: Manifest) -> Dict[str, str]:
    assert manifest.dependencies
    return {
        dependency.snake_case_name: generate_model(dependency)
        for dependency in manifest.dependencies
        if isinstance(dependency, (EntitySchemaDependency, SchemaDependency))
        and dependency.fieldDefinitions
        or isinstance(dependency, DropdownDependency)
    }
