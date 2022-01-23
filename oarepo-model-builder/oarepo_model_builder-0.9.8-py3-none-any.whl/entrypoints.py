import sys
from pathlib import Path

import pkg_resources

from oarepo_model_builder.builder import ModelBuilder
from oarepo_model_builder.schema import ModelSchema
from oarepo_model_builder.utils.hyphen_munch import HyphenMunch


def create_builder_from_entrypoints(**kwargs):
    output_classes = load_entry_points_list('oarepo_model_builder.ouptuts')
    builder_classes = load_entry_points_list('oarepo_model_builder.builders')
    preprocess_classes = load_entry_points_list('oarepo_model_builder.property_preprocessors')
    model_preprocessor_classes = load_entry_points_list('oarepo_model_builder.model_preprocessors')

    builder_types = [x.TYPE for x in builder_classes]
    output_builder_components = {
        builder_type: load_entry_points_list(f'oarepo_model_builder.builder_components.{builder_type}')
        for builder_type in builder_types
    }

    return ModelBuilder(
        output_builders=builder_classes,
        outputs=output_classes,
        property_preprocessors=preprocess_classes,
        model_preprocessors=model_preprocessor_classes,
        output_builder_components=output_builder_components,
        **kwargs
    )


def load_entry_points_dict(name):
    return {ep.name: ep.load() for ep in pkg_resources.iter_entry_points(group=name)}


def load_entry_points_list(name):
    ret = [(ep.name, ep.load()) for ep in pkg_resources.iter_entry_points(group=name)]
    ret.sort()
    return [x[1] for x in ret]


def load_model_from_entrypoint(schema, ep: pkg_resources.EntryPoint):
    filename = '.'.join(ep.attrs)
    data = pkg_resources.resource_string(ep.module_name, filename)
    return schema._load(filename, content=data)


def load_included_models_from_entry_points():
    ret = {}
    for ep in pkg_resources.iter_entry_points(group='oarepo.models'):
        ret[ep.name] = lambda schema: load_model_from_entrypoint(schema, ep)
    return ret


def load_model(model_filename, package=None, configs=(), black=True, isort=True, sets=(),
               model_content=None, extra_included=None):
    loaders = load_entry_points_dict('oarepo_model_builder.loaders')
    included_models = load_included_models_from_entry_points()
    if extra_included:
        included_models.update(extra_included)
    schema = ModelSchema(model_filename, content=model_content,
                         loaders=loaders, included_models=included_models)
    for config in configs:
        load_config(schema, config, loaders)
    for s in sets:
        k, v = s.split('=', 1)
        schema.schema[k] = v
    check_plugin_packages(schema)
    if package:
        schema.settings['package'] = package
    if 'python' not in schema.settings:
        schema.settings.python = HyphenMunch()
    schema.settings.python.use_isort = isort
    schema.settings.python.use_black = black
    return schema


def load_config(schema, config, loaders):
    old_loaders = schema.loaders
    schema.loaders = loaders
    try:
        loaded_file = schema._load(config)
        schema.merge(loaded_file)
    finally:
        schema.loaders = old_loaders


def check_plugin_packages(schema):
    try:
        required_packages = schema.schema.plugins.packages
    except AttributeError:
        return
    import pkg_resources, subprocess
    known_packages = set(d.project_name for d in pkg_resources.working_set)
    unknown_packages = [rp for rp in required_packages if rp not in known_packages]
    if unknown_packages:
        if input(f'Required packages {", ".join(unknown_packages)} are missing. '
                 f'Should I install them for you via pip install? (y/n) ') == 'y':
            if subprocess.call([
                'pip', 'install', *unknown_packages
            ]):
                sys.exit(1)
            print("Installed required packages, please run this command again")
        sys.exit(1)
