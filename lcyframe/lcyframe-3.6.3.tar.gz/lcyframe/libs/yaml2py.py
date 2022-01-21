# -*- coding:utf-8 -*-
import os
import sys
import io
import re
import glob
import logging
from jinja2 import Environment, FileSystemLoader, Template
from ruamel.yaml import round_trip_dump, round_trip_load, load, dump_all
from importlib import import_module
import inspect


def impmodule(base, model_dir=None):
    """
    import model class obj global
    warn: the class obj cant not start whit "__"
    :return:
    """
    ROOT = os.environ.app_config["ROOT"]
    model = type("model", (object,), {})
    for m in [x for x in os.listdir(model_dir) if re.findall('[A-Za-z]\w+_model\.py$', x)]:
        m = m[:-3]
        if m == "__init__":
            continue

        model_name = model_dir.replace(ROOT, "").lstrip("/").replace("/", ".") + "." + m.rstrip(".py")
        # for attr_name, value in import_module(model_name).__dict__.items():
        for attr_name, value in inspect.getmembers(import_module(model_name), inspect.isclass):
            if attr_name.startswith("__"):
                continue

            if not hasattr(model, attr_name):
                setattr(model, attr_name, value)
                logging.debug("model [%s] register success!" % attr_name)

    setattr(base, "model", model)

def load_jinja2(name, jinja2_path=""):
    """
    dir must abd path
    :param dir:
    :return:
    """
    if jinja2_path and os.path.exists(jinja2_path):
        jinja_env = Environment(loader=FileSystemLoader(jinja2_path))
        template = jinja_env.get_template('%s.py.j2' % name)
    else:
        jinja2_path = os.path.join(os.path.dirname(__file__), "template")
        if os.path.exists(os.path.join(jinja2_path, name) + ".py.j2"):
            jinja_env = Environment(loader=FileSystemLoader(jinja2_path))
            template = jinja_env.get_template('%s.py.j2' % name)
        else:
            sys.path.append(jinja2_path)
            j2 = import_module("template")
            str = getattr(j2, "%s_j2" % name).decode("u8")
            template = Template(str)

    return template


def snake_to_camel(snake_str):
    return _convert_to_camel(snake_str, '_')


def snake_to_cap(snake_str):
    return _convert_to_camel(snake_str, '_', True)


def _convert_to_camel(snake_cased_str, separator, first_cap=False):
    components = snake_cased_str.split(separator)
    preffix = ""
    suffix = ""
    if components[0] == "":
        components = components[1:]
        preffix = separator
    if components[-1] == "":
        components = components[:-1]
        suffix = separator
    if len(components) > 1:
        camel_cased_str = components[0].title() if first_cap else components[0].lower()
        for x in components[1:]:
            if x.isupper() or x.istitle():
                camel_cased_str += x
            else:
                camel_cased_str += x.title()
    else:
        camel_cased_str = components[0].title()
    return preffix + camel_cased_str + suffix


def extract_dict(some_dict, some_keys):
    return dict([(k, some_dict[k]) for k in some_keys if k in some_dict])


def reduce_result_keys(result):
    if not result:
        return
    record = {}
    for k, v in result.items():
        record[k] = extract_dict(v, ('name', 'type', 'required', 'schema', 'rename'))
    return record


def _filter_params(pkg_dir, schema, ignore_type=["bool", "BOOL"]):
    for f, item in schema["method"].items():
        for params in item.get("parameters", []) or []:
            params_name = params["name"]
            for k, v in params.items():
                if k == "type" and v.lower() in ignore_type:
                    raise Exception("params '%s' can not is bool type in %s" % (params_name, pkg_dir))

            if params["type"] == "json" and not params["required"] and params.get("default") is None:
                raise Exception(
                    "params '%s' is json type. required true or give default in %s" % (params_name, pkg_dir))

        for k, v in (item.get("responses", {}) or {}).items():
            if v is None:
                raise Exception("responses key '%s' value can not is 'None' or empty in %s" % (k, pkg_dir))


def dump_yaml_file(data, path, round_tripping=False):
    with io.open(path, 'w', encoding='utf-8') as writer:
        if round_tripping:
            round_trip_dump(data, writer, allow_unicode=True, )
        else:
            dump_all([data], writer, allow_unicode=True)


def load_yaml_file(path, round_tripping=False):
    with io.open(path, 'r', encoding='utf-8') as reader:
        if round_tripping:
            data = round_trip_load(reader)
        else:
            # data = load(reader)
            import warnings, ruamel.yaml
            # warnings.simplefilter('ignore', ruamel.yaml.error.UnsafeLoaderWarning)
            data = load(reader, Loader=ruamel.yaml.Loader)
    return data


def load_confog(path, round_tripping=False):
    return load_yaml_file(path, round_tripping)


def generate_basepy(path, jinja2_path_dir):
    template = load_jinja2("base", jinja2_path_dir)

    s = template.render(resources={})

    p = path
    with io.open(p, 'w', encoding='utf-8') as w:
        w.write(s)

    logging.debug("base.py", ' .. created')


def load_api_schema(api_schema_dir):
    api_schema_mp = {}

    for pkg_dir in glob.glob('%s/*' % api_schema_dir):
        if os.path.isdir(pkg_dir):
            api_schema_mp.update(load_api_schema(pkg_dir))
        else:
            # for mod_file in glob.glob('%s/*.yml' % pkg_dir):
            resources = []

            if os.path.basename(pkg_dir).count(".") > 1:
                raise Exception("%s file name exists multiple '.'" % (pkg_dir))

            mod_name = os.path.basename(pkg_dir).split(".")[0]
            resources.extend(load_yaml_file(pkg_dir, False))
            for res in resources:

                _filter_params(pkg_dir, res)

                api = res["apis"]
                if api in api_schema_mp:
                    raise Exception("%s has multiple Api named '%s'; error" % (mod_name, api))
                api_schema_mp[api] = {
                    "name": mod_name,
                    "api": res["apis"],
                    "api_title": res.get("name", ""),
                    "api_name": res["handler"],
                    "description": res.get("description", "") or "",
                    "method": res["method"],
                }
                logging.debug('params [%s] load success!' % api)

    return api_schema_mp


def process_resource_context(model_path, resource_def):
    # handler
    resource_def['handler_name'] = resource_def["api_name"][0].upper() + resource_def["api_name"][1:] + "Handler"

    # model
    resource_def["model_dir"] = os.path.basename(model_path)
    resource_def['model_name'] = resource_def["name"][0].upper() + resource_def["name"][1:] + "Model"

    # schema
    resource_def['schema_name'] = resource_def["name"][0].upper() + resource_def["name"][1:] + "Schema"

    return resource_def


def load_resource_handler(model_path, resource_text, jinja2_path=None):
    template = load_jinja2("handler", jinja2_path)

    resources = []
    for resource_def in resource_text:
        resource_context = process_resource_context(model_path, resource_def)
        resources.append(resource_context)

    s = template.render(resources=resources)
    return s


def load_resource_model(model_path, resource_text, jinja2_path=None):
    template = load_jinja2("model", jinja2_path)

    resources = []
    for resource_def in resource_text:
        resource_context = process_resource_context(model_path, resource_def)
        resources.append(resource_context)

    s = template.render(resources=resources)
    return s


def load_resource_model_schema(model_path, resource_text, jinja2_path=None):
    template = load_jinja2("schema", jinja2_path)

    resources = []
    for resource_def in resource_text:
        resource_context = process_resource_context(model_path, resource_def)
        resources.append(resource_context)

    s = template.render(resources=resources)
    return s


def generate_resource_handler(handler_path, model_path, api_schema_mp, jinja2_path_dir):
    resource_mp = {}
    for api, item in api_schema_mp.items():
        resource_mp.setdefault(item["name"], [])
        resource_mp[item["name"]].append(item)

    for mod_name, item in resource_mp.items():
        p = os.path.join(handler_path, mod_name + '_handler.py')
        if os.path.exists(p):
            logging.debug("handler [%s_handler.py] exists.. skip" % mod_name)
            continue

        mod_py_source = load_resource_handler(model_path, item, jinja2_path_dir)

        with io.open(p, 'w', encoding='utf-8') as w:
            w.write(mod_py_source)

        logging.debug("handler [" + mod_name + "_handler.py]", ' .. created')


def generate_resource_model(model_path, api_schema_mp, jinja2_path_dir):
    resource_mp = {}
    for api, item in api_schema_mp.items():
        resource_mp.setdefault(item["name"], [])
        resource_mp[item["name"]].append(item)

    for mod_name, item in resource_mp.items():
        p = os.path.join(model_path, mod_name + '_model.py')
        if os.path.exists(p):
            logging.debug("model [%s_model.py] exists.. skip" % mod_name)
            continue

        mod_py_source = load_resource_model(model_path, item, jinja2_path_dir)

        with io.open(p, 'w', encoding='utf-8') as w:
            w.write(mod_py_source)

        logging.debug("model [" + mod_name + "_model.py]", ' .. created')


def generate_resource_model_schema(schema_path, api_schema_mp, jinja2_path_dir):
    resource_mp = {}
    for api, item in api_schema_mp.items():
        resource_mp.setdefault(item["name"], [])
        resource_mp[item["name"]].append(item)

    for mod_name, item in resource_mp.items():
        p = os.path.join(schema_path, mod_name + '_schema.py')
        if os.path.exists(p):
            logging.debug("schema [%s_schema.py] exists.. skip" % mod_name)
            continue

        mod_py_source = load_resource_model_schema(schema_path, item, jinja2_path_dir)

        with io.open(p, 'w', encoding='utf-8') as w:
            w.write(mod_py_source)

        logging.debug("schema [%s_schema.py] .. created success" % mod_name)

