import contextlib
import fnmatch
import glob
import json
import os
from functools import reduce
from typing import Optional, Set, List, Dict

import click
import yaml
from box import Box
from marshmallow import ValidationError

from montecarlodata.config import Config
from montecarlodata.errors import complain_and_abort, manage_errors
from montecarlodata.fs_utils import mkdirs
from montecarlodata.iac.client import MonteCarloConfigTemplateClient
from montecarlodata.iac.schemas import ProjectConfig
from montecarlodata.iac.utils import is_dbt_schema, has_montecarlo_property
from montecarlodata.settings import TARGET_DIRECTORY_NAME, PROJECT_CONFIG_FILENAME
from montecarlodata.utils import GqlWrapper


class MonteCarloConfigService:
    def __init__(self, config: Config, request_wrapper: Optional[GqlWrapper] = None, project_dir: str = None):
        request_wrapper = request_wrapper or GqlWrapper(mcd_id=config.mcd_id, mcd_token=config.mcd_token)
        self.client = MonteCarloConfigTemplateClient(request_wrapper)

        if not project_dir:
            self.project_dir = os.getcwd()
        else:
            self.project_dir = os.path.abspath(project_dir)
        self.init()
        self._abort_on_error = True

    def init(self):
        self.target_dir = self._create_target_directory()
        self.project_config = self._load_project_config()

    @manage_errors
    def apply(self, namespace: str, dry_run: bool = False, abort_on_error=True):
        """
        Compile configuration.
        Submit configuration via API
        """
        files, mc_config_dict, _ = self.compile()
        response = self.client.apply_config_template(
            namespace,
            mc_config_dict,
            resource=self.project_config.default_resource,
            dry_run=dry_run
        )

        if response.errors:
            click.echo()
            click.echo('Errors encountered when attempting to apply configuration:')

            system_error = response.errors.get('system_error', {})
            if system_error:
                click.echo(f' - {system_error}')
            else:
                validation_errors = response.errors.get('validation_errors', {})
                click.echo(f' - Validation error: {validation_errors}')

            click.echo()

            if abort_on_error:
                complain_and_abort("Errors encountered, exiting.")

        if response.resource_modifications:
            click.echo()
            click.echo('Modifications:')
            for resource_modification in response.resource_modifications:
                click.echo(f' - {"[DRY RUN] " if dry_run else ""}{resource_modification.type} - {resource_modification.description}')
            click.echo()

            if dry_run:
                click.echo('Dry run, none of the changes have been applied.')
                click.echo()
            else:
                click.echo('Changes successfully applied.')
                click.echo()
        else:
            click.echo()
            click.echo('No changes to configuration found, doing nothing.')
            click.echo()

        return response

    @manage_errors
    def compile(self, abort_on_error=True) -> Dict:
        """
        Gather monitor configuration YAML files from project.
        This may also include DBT schema files with meta properties
        """
        click.echo()
        click.echo("Gathering monitor configuration files.")
        files = self._gather_yaml_files(self.project_config)

        errors_by_file = {}
        mc_config_list: List[Box] = []

        files = sorted(list(files))
        for file in files:
            with open(file, 'r') as f:
                yaml_as_dict = Box(yaml.safe_load(f))

                # This file is a DBT schema file.
                # Let's attempt to parse out special embedded MC sections from meta:
                # See https://docs.getdbt.com/reference/resource-properties/meta
                if is_dbt_schema(yaml_as_dict):
                    for model in yaml_as_dict.models:
                        with contextlib.suppress(KeyError):
                            mc_config = model.meta.montecarlo
                            errors = self._validate_mc_config(mc_config)
                            if errors:
                                errors_by_file[file] = errors
                            mc_config_list.append(mc_config)

                            click.echo(f" - {file} - Embedded monitor configuration found.")

                # This file has a root montecarlo property
                # This can be in a standalone file, and also a DBT schema file
                if has_montecarlo_property(yaml_as_dict):
                    mc_config = yaml_as_dict.montecarlo
                    errors = self._validate_mc_config(mc_config)
                    if errors:
                        errors_by_file[file] = errors
                    mc_config_list.append(mc_config)
                    click.echo(f" - {file} - Monitor configuration found.")

        # Exit if there are errors
        if errors_by_file:
            click.echo()
            click.echo('Configuration validation errors:')
            for file, errors in errors_by_file.items():
                click.echo(f' - File: {file}')
                for error in errors:
                    click.echo(f'    - {error}')
            click.echo()
            if abort_on_error:
                complain_and_abort("Errors encountered, exiting.")

        if not mc_config_list:
            if abort_on_error:
                complain_and_abort("Sorry, we didn't find any YAML files containing Monte Carlo configuration.")

        # Merge configs into a single config
        compiled_mc_config = self._merge_mc_configs(mc_config_list)

        # Write configs to target directory. Useful for debugging.
        with open(os.path.join(self.target_dir, 'montecarlo_configuration.yml'), 'w') as f:
            f.write(compiled_mc_config.to_yaml())

        with open(os.path.join(self.target_dir, 'montecarlo_configuration.json'), 'w') as f:
            json.dump(compiled_mc_config, f, indent=4)

        return files, compiled_mc_config, errors_by_file

    def _create_target_directory(self) -> str:
        target_dir = os.path.join(self.project_dir, TARGET_DIRECTORY_NAME)
        mkdirs(target_dir)
        return target_dir

    def _load_project_config(self) -> ProjectConfig:
        contents = None
        try:
            with open(os.path.join(self.project_dir, PROJECT_CONFIG_FILENAME), 'r') as f:
                contents = f.read()
        except FileNotFoundError:
            complain_and_abort(
                f"Not a Monte Carlo project. Must define {PROJECT_CONFIG_FILENAME} in current working directory.")

        project_config_as_dict = yaml.safe_load(contents)
        try:
            s = ProjectConfig.schema()
            return s.load(project_config_as_dict)
        except ValidationError as e:
            complain_and_abort(f"Encountered a validation problem in {PROJECT_CONFIG_FILENAME}: {e.messages}")

    def _merge_mc_configs(self, mc_config_list: List[Box]) -> Box:
        """
        Merge multiple mc configs into a single one.
        Nested dicts will be merged
        Nested lists will be concatenated
        """
        def merge_configs(x: Box, y: Box):
            x.merge_update(y, box_merge_lists='extend')
            return x

        compiled_mc_config = reduce(merge_configs, mc_config_list)
        compiled_mc_config.pop('box_merge_lists', None)  # Strangly enough, Box adds this add'l key. Remove it

        return compiled_mc_config

    def _validate_mc_config(self, mc_config_dict: Box) -> List[str]:
        """
        Perform simple validation.
        More comprehensive validation is performed server-side
        """
        expected_keys = [
            'field_health',
            'dimension_tracking',
            'json_schema',
            'custom_sql',
            'freshness',
            'volume'
        ]

        errors = []
        for key in expected_keys:
            with contextlib.suppress(KeyError):
                if key in mc_config_dict and not isinstance(mc_config_dict[key], list):
                    errors.append(f'"{key}" property should be a list.')
        return errors

    def _gather_yaml_files(self, project_config: ProjectConfig) -> Set[str]:
        files = set()
        for pattern in project_config.include_file_patterns:
            for fn in glob.glob(os.path.join(self.project_dir, pattern), recursive=True):
                files.add(fn)
        for pattern in project_config.exclude_file_patterns:
            excluded = set(fnmatch.filter(files, os.path.join(self.project_dir, pattern)))
            files = files - excluded
        return files

    @manage_errors
    def delete(self, namespace: str, dry_run: bool = False, abort_on_error=True):
        """
        Delete all monitors in namespace
        """
        response = self.client.delete_config_template(
            namespace,
            dry_run=dry_run
        )

        click.echo(f'\n{"[DRY RUN] " if dry_run else ""}Deleted {response.num_deleted} resources in namespace={namespace}\n')

        return response

