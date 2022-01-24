import os
import argparse
import json
import logging
import inspect
import json as js
from types import SimpleNamespace

from brevettiai.utils.module import Module, get_parameter_type
from brevettiai.utils.dict_utils import dict_merger

log = logging.getLogger(__name__)


def _parse_number(x):
    if isinstance(x, (int, float)) or x is None:
        return x
    try:
        return int(x)
    except ValueError:
        return float(x)


def parse_json(x):
    if isinstance(x, str):
        if x:
            try:
                return js.loads(x)
            except Exception as ex:
                log.error(f"Failed parsing JSON string: {x}")
                raise ex
        else:
            return None
    else:
        return x


def vue_dtype(field):
    t_ = field["type"]
    if t_ == "input":
        it_ = field["inputType"]
        if it_ == "number":
            return _parse_number
        else:
            if field.get("isJson", False):
                return parse_json
            return str
    elif t_ == "checkbox":
        return bool
    else:
        if field.get("isJson", False):
            return parse_json
        return lambda x: x


def _set_value_in_tree(ns, value, tree):
    """
    Set value in tree
    :param ns: Path to value
    :param value: value
    :param tree: tree (settings dict)
    :return:
    """
    if value is not None:
        path = ns.split(".")
        x = tree
        for n in path[:-1]:
            x = x.setdefault(n, {})
        else:
            x[path[-1]] = value

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def parse_settings_args(schema, args=None):
    if isinstance(schema, SchemaBuilder):
        schema = schema.schema
    parser = argparse.ArgumentParser()
    for f in schema["fields"]:
        if "model" in f:
            try:
                _type = vue_dtype(f)
                if _type == bool:
                    _type = str2bool
                parser.add_argument("--{model}".format(**f), help=f.get("label", ""), type=_type)
            except argparse.ArgumentError:
                log.info("attempted to add '--{model}' to argparser twice".format(**f))

    settings = {}
    for ns, value in vars(parser.parse_known_args(args)[0]).items():
        _set_value_in_tree(ns, value, settings)

    return settings


def _serialize(obj, ns, **kwargs):
    path = ns.split(".", 1)
    obj = vars(obj) if hasattr(obj, "__dict__") else obj
    if len(path) > 1:
        _serialize(obj[path[0]], path[1], **kwargs)
    else:
        if path[0] in obj:
            obj[path[0]] = js.dumps(obj[path[0]], **kwargs)


def _getter(obj):
    for k, v in vars(obj).items():
        if isinstance(v, SimpleNamespace):
            yield from ((k + "." + n, default) for n, default in _getter(v))
        else:
            yield k, v


def update_schema(schema, settings, ignore=None, field_values=None):
    ignore = set(ignore or set())

    # Find valid fields
    available_fields = {field["model"]: field for field in schema["fields"]
                        if "default" in field and field["model"] not in ignore}

    # Update fields
    for ns, v in _getter(settings):
        if ns in available_fields:
            field = available_fields[ns]
            field["required"] = True
            field["default"] = js.dumps(v) if field.get("isJson") is True else v

    # Update fields with attributes
    for k, v in field_values.items():
        for field in schema["fields"]:
            if "model" in field and field["model"].startswith(k):
                field.update(**v)

    # Hide labels if all fields until next label i
    for i, field in enumerate(schema["fields"]):
        if field.get("type") == "label":
            try:
                next_ = next(x for x in schema["fields"][i + 1:] if x.get("visible") is not False)
            except StopIteration:
                field["visible"] = False
                continue
            if next_.get("type") == "label":
                field["visible"] = False

    return schema


class SchemaBuilder:
    """
    Helper object for generating schemas
    """
    def __init__(self, fields=None, presets=None, modules=None, advanced=True, namespace=None):
        self.fields = fields or []
        self.presets = presets or {}
        self.modules = modules or {}
        self.advanced = advanced
        self.namespace = namespace

    @staticmethod
    def from_schema(schema):
        return SchemaBuilder(fields=schema.get("fields", []), presets=schema.get("presets", {}))

    def add_field(self, field, **kwargs):
        field.setdefault("visible", not self.advanced)
        self.fields.append(field)

        # Add presets to preset dict
        for preset, value in kwargs.items():
            self.add_preset(preset, field, value)

    def add_preset(self, preset, field, value):
        if isinstance(field, str):
            try:
                field = next(f for f in self.fields if f.get("model") == field)
            except StopIteration as e:
                raise ValueError(e, f"Could not find field for preset '{field}'")

        if field.get("isJson", False):
            value = json.dumps(value)

        preset = self.presets.setdefault(preset, {})
        _set_value_in_tree(field["model"], value, preset)

    def append(self, item, *args, **kwargs):
        if isinstance(item, SchemaBuilderFunc):
            item = item.builder(*args, **kwargs)
        if isinstance(item, SchemaBuilder):
            schema = item.schema
            self.fields += schema["fields"]
            dict_merger(item.presets, schema["presets"])
            self.modules.update(item.modules)
        if isinstance(item, list):
            for f in item:
                self.add_field(f)
        return self

    def __add__(self, other):
        if isinstance(other, (SchemaBuilder, list)):
            return self.append(other)
        else:
            super().__add__(other)

    def load_modules(self, settings):
        for ns, module in self.modules.items():
            x = settings
            uri = ns.split(".")
            for p in uri[:-1]:
                x = x.__dict__[p]
            x.__dict__[uri[-1]] = module.from_config(vars(x.__dict__[uri[-1]]))
        return settings

    def filter_fields(self, incl_fields: list = None, excl_fields: list = None, make_visible: list = None):
        field_dict = {}
        for i, f in enumerate(self.fields):
            field_dict.setdefault(f.get("model", f.get("tag", i)), []).append(f)

        if incl_fields:
            fields = [[f] if isinstance(f, dict) else field_dict.get(f, []) for f in incl_fields]
        else:
            excl_fields = excl_fields or []
            fields = [vv for kk, vv in field_dict.items() if len([1 for f in excl_fields if f in kk]) == 0]

        fields = [item for sublist in fields for item in sublist]
        if make_visible:
            for i, f in enumerate(fields):
                f["visible"] = any(mm==f.get("model", f.get("tag", i)) for mm in make_visible)
        self.fields = fields

    @property
    def schema(self):
        if self.namespace is None:
            return dict(
                fields=self.fields,
                presets=self.presets,
            )
        else:
            if self.presets:
                *uri, element = self.namespace.split(".")
                presets = item = {}
                for p in uri:
                    item = item.setdefault(p, {})
                item[element] = self.presets
            else:
                presets = self.presets
            return dict(
                fields=[{**f, model_name: f'{self.namespace}.{f[model_name]}'} for f in self.fields
                        for model_name in [["tag", "model"]["model" in f]]],
                presets=presets,
            )

    def __str__(self):
        return json.dumps(self.schema, indent=2, sort_keys=True)


DEFAULT = "__DEFAULT__"


class SchemaBuilderFunc:
    ns = None
    label = None
    advanced = False
    module = None

    def __init__(self, label=DEFAULT, ns=DEFAULT, advanced=DEFAULT):
        self.label = self.label if label == DEFAULT else label
        self.ns = self.ns if ns == DEFAULT else ns
        self.advanced = self.advanced if advanced == DEFAULT else advanced

    @staticmethod
    def schema(self, builder, ns, *args, **kwargs):
        """
        Overwrite this function to build schema
        """
        return builder

    def builder(self, *args, **kwargs):
        b = SchemaBuilder(advanced=self.advanced)
        if self.label is not None:
            b.add_field(label(self.label))
        self.schema(b, self.ns.rstrip(".") + "." if self.ns else "", *args, **kwargs)
        if self.module is not None:
            b.modules = {self.ns: self.module}
        return b


def generate_application_schema(schema, path="model/settings-schema.json", manifest_path=None):
    """
    Generate application schema and manifest files from schema dictionary or SchemaBuilder object
    :param schema: schema dictionary or SchemaBuilder object
    :param path: target path for schema
    :param manifest_path: set to "MANIFEST.in" to export manifest
    :return:
    """
    if isinstance(schema, SchemaBuilder):
        schema = schema.schema

    with open(path, "w+") as fp:
        json.dump(schema, fp, indent=2, sort_keys=True)

    if manifest_path is not None:
        required_manifest = 'include %s' % os.path.relpath(path).replace(os.sep, '/')
        with open(manifest_path, "a+") as fp:
            fp.seek(0)
            for line in fp:
                if required_manifest == line:
                    return
            else:
                fp.write("\n" + required_manifest)


# Vue fields

class VueSettingsModule(Module):
    @classmethod
    def get_schema(cls, namespace=None):
        """ Get vue-form-generator schema"""
        builder = SchemaBuilder(namespace=namespace)

        signature = inspect.signature(cls.__init__)
        for name, parameter in tuple(signature.parameters.items())[1:]:
            ptype = get_parameter_type(parameter)
            cls.to_schema(builder=builder, name=name, ptype=ptype, default=parameter.default)
        return builder

    def get_settings(self):
        """ Get Vue schema settings model for vue-form-generator"""
        return self.to_settings(self.get_config())

    @classmethod
    def from_settings(cls, settings):
        schema = cls.get_schema()
        settings = apply_schema_to_model(schema, settings)
        config = cls.to_config(settings)
        return cls.from_config(config)

    @classmethod
    def to_config(cls, settings):
        """
        Parse settings from vue-form-generator json model to python config

        Overwrite this if settings data model is different than config data model.
        Remember to overwrite to_settings as well to provide the reverse transformation
        """
        if settings is None:
            return None
        signature = inspect.signature(cls.__init__)
        for name, parameter in tuple(signature.parameters.items())[1:]:
            if name in settings:
                ptype = get_parameter_type(parameter)
                if issubclass(ptype, VueSettingsModule):
                    settings[name] = ptype.to_config(settings[name])
        return settings

    @classmethod
    def to_settings(cls, config):
        """
        Get settings model for vue-schema-generator.

        Overwrite this if you have custom field manipulaion in from settings
        """
        if config is None:
            return None
        signature = inspect.signature(cls.__init__)
        for name, parameter in tuple(signature.parameters.items())[1:]:
            if name in config:
                ptype = get_parameter_type(parameter)
                if issubclass(ptype, VueSettingsModule):
                    config[name] = ptype.to_settings(config[name])
                elif ptype in [int, float, bool, str]:
                    config[name] = ptype(config[name]) if config[name] is not None else config[name]
                elif ptype in {dict, tuple, list}:
                    if hasattr(config[name], "numpy"):
                        config[name] = config[name].numpy()
                    if hasattr(config[name], "tolist"):
                        config[name] = config[name].tolist()
                    if not isinstance(config[name], str):
                        config[name] = js.dumps(config[name], indent=2, sort_keys=True)
                else:
                    del config[name]

        return config

    @classmethod
    def to_schema(cls, builder: SchemaBuilder, name: str, ptype: type, default, **kwargs):
        """
        Transform field to vue-form-generator schema fields.

        overwrite this to provide custom schemas for your Model
        """

        # Get schema for simple fields
        payload = {
            "label": name.replace("_", " ").title()
        }

        # Get schema for subclasses
        if issubclass(ptype, VueSettingsModule):
            sub_schema = ptype.get_schema(namespace=name)
            builder.add_field(label(**payload, tag=name))
            builder.append(sub_schema)
            return

        payload.update({
            "model": name,
            "default": ptype() if default is None or default is inspect._empty else default,
            **kwargs}
        )

        if ptype == int or ptype == float:
            builder.add_field(number_input(**payload))
        elif ptype == bool:
            builder.add_field(checkbox(**payload))
        elif ptype in {dict, tuple, list}:
            builder.add_field(text_area(**{**payload, "json": True}))
        elif ptype == set:
            payload["default"] = list(payload["default"])
            builder.add_field(text_area(**{**payload, "json": True}))
        elif ptype == str:
            builder.add_field(text_input(**payload))
        else:
            # Not a known field type ignore
            print(name, ptype, "not known")


def apply_schema_to_model(schema, model=None, check_required_fields=True):
    if isinstance(schema, SchemaBuilder):
        schema = schema.schema

    model = model or {}
    missing_fields = []
    for field in schema["fields"]:
        if "model" in field and field.get("type", "label") != "label":
            # Get item
            *uri, elem = field["model"].split(".")
            item = model
            for p in uri:
                item = item.setdefault(p, {})

            # Set element in tree
            if elem not in item:
                # Check missing fields
                if check_required_fields and field.get("required", False):
                    missing_fields.append(field["model"])

                item[elem] = field["default"]

            # Parse element in tree
            item[elem] = vue_dtype(field)(item[elem])

    assert len(missing_fields) == 0, "Missing settings: \n %s" % missing_fields

    return model


def label(label, **kwargs):
    return dict(
        type="label",
        label=label,
        **kwargs
    )


def _input_field(label, model, default, required=False, **kwargs):
    """
    Vue input fields
    :param label:
    :param model:
    :param default:
    :param required:
    :param kwargs: Extra fields for vue (hidden, disabled, readonly)
    :return:
    """
    return dict(
        label=label,
        model=model,
        default=default,
        required=required,
        **kwargs
    )


def number_input(label, model, default, required=False, min=0, max=100, step=1, **kwargs):
    return dict(
        type="input",
        inputType="number",
        min=min,
        max=max,
        step=step,
        **_input_field(label, model, default, required=required, **kwargs)
    )


def text_input(label, model, default="", required=False, json=False, **kwargs):
    if not isinstance(default, str):
        default = js.dumps(default, sort_keys=True)
    return dict(
        type="input",
        inputType="text",
        isJson=json,
        **_input_field(label, model, default, required, **kwargs)
    )


def text_area(label, model, default, required=False, hint="", max=5000, placeholder="", rows=4, json=False, **kwargs):
    if not isinstance(default, str):
        default = js.dumps(default, indent=2, sort_keys=True)
    return dict(
        type="textArea",
        hint=hint,
        placeholder=placeholder,
        rows=rows,
        max=max,
        isJson=json,
        **_input_field(label, model, default, required, **kwargs)
    )


def checkbox(label, model, default, required=False, **kwargs):
    return dict(
        type="checkbox",
        **_input_field(label, model, default, required, **kwargs)
    )


def checklist(label, model, default, values, required=False, dropdown=True, **kwargs):
    return dict(
        type="checklist",
        listbox=not dropdown,
        values=values,
        **_input_field(label, model, default, required, **kwargs)
    )


def select(label, model, default, values, required=False, json=False, **kwargs):
    values = [v if isinstance(v, str) else js.dumps(v, indent=2, sort_keys=True) for v in values]
    if not isinstance(default, str):
        default = js.dumps(default, indent=2, sort_keys=True)
    return dict(
        type="select",
        values=values,
        isJson=json,
        **_input_field(label, model, default, required, **kwargs)
    )


# Custom criterion schema fields
def field_classes(label="Classes as json list", model="classes", default="", required=False, **kwargs):
    return text_input(**locals(), json=True, criterionType="classes")


def field_class_mapping(label="Class mapping", model="class_mapping", default="", required=False,
                        hint="Json mapping from folder name to class", **kwargs):
    return text_area(**locals(), json=True, criterionType="class_mapping")
