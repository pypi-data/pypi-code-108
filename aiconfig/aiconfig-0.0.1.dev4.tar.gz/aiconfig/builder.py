import copy
import graphviz
import importlib
import inspect
import json
import os
import re
import yaml


class NotBuiltError(Exception):
    ...


class Builder:
    def __init__(self, cf, strict=False, quiet=False, debug=None, target=None, **parameters):
        """
        Recursive function builder class. Based on "cf['builds']", Builder goes through the
        list of builds and, starting at the root and back-tracking recursively, calls
        all of the functions or retrieves the variables defined.

        :param cf: config dictionary with fields "builds" and optionally "parameters", "options",
                   "parent"
        :param strict: raise errors on instantiation if parameters not specified in **parameters
        :param quiet: toggle to True to see full build output
        :param **parameters: key-value pairs specifying the parameters defined in "cf"

        For example to build a single class instance we can do this:
        >>> cf = {
        ...    "builds": {
        ...        "linear_layer": {
        ...             "getter": "torch.nn.Linear",
        ...             "args": {"in_features": 10, "out_features": 20}
        ...         }
        ...    }
        ... }
        >>> print(Builder(cf, quiet=True).build())
        Linear(in_features=10, out_features=20, bias=True)

        To build a class which recursively uses previously built values, these can be referred to
        with a variable, such as, "$input_param". Values in **parameters may be referred to in the
        same way. If the variables in cf["parameters"] are not specified in **parameters, then an
        exception is raised. Values in dictionary cf["options"] may be overridden in **parameters.
        For example:
        >>> cf = {
        ...    "parameters": ["other_param"],
        ...    "options": {"out_features": 20},
        ...    "builds": {
        ...        "input_dimension": {
        ...             "getter": "random.randrange",
        ...             "args": {"start": 11, "stop": 15},
        ...        },
        ...        "linear_layer": {
        ...             "getter": "torch.nn.Linear",
        ...             "args": {"in_features": "$input_dimension",
        ...                      "out_features": "$out_features"}
        ...         }
        ...    }
        ... }
        >>> output = Builder(cf, quiet=True, out_features=30, strict=True).build()
        Traceback (most recent call last):
        ...
        AssertionError: missing parameters ['other_param']
        >>> output = Builder(cf, quiet=True, out_features=30, strict=False).build()
        >>> print(output.in_features > 10)
        True
        >>> print(output.out_features == 30)
        True

        See "./configs" for full examples.
        """

        if 'parent' in cf:
            cf = self._update_cf(cf, cf['parent'])

        if strict:
            missing = [k for k in cf.get('parameters', []) if k not in parameters]
            assert not missing, f'missing parameters {missing}'
        self.parameters = cf.get('options', {})
        self.parameters.update(parameters)
        self.root = cf['root']
        self.cf = cf['builds']
        self.built = {}
        self._variables = {k: v for k, v in parameters.items()}
        self.debug = debug
        self.post_cf = {}
        self.input_variables = set(list(self.parameters.keys()) + list(self.cf.keys()))
        self.quiet = quiet
        self.explicit_builds = {}
        self.G = graphviz.Digraph()
        self.G.attr('node', shape='box')
        for k in self.cf:
            self.G.node(k)
        self.build(do_build=False, target=target)
        self.built = {}

    def _parameters_to_python(self):
        python_ = """"""
        for k in self.parameters:
            python_ += f'{k.upper()} = {json.dumps(self.parameters[k])}\n'
        return python_

    def _variable_reference_to_python(self, var_, type_, item):
        if type_ == 'normal':
            return var_.upper()
        elif type_ == 'index':
            return f'{var_.upper()}[{item}]'
        elif type_ == 'key':
            return f'{var_.upper()}["{item}"]'
        elif type_ == 'attribute':
            return f'{var_.upper()}.{item}'
        elif type_ == 'variable':
            return f'{var_.upper()}[{item.upper()}]'
        else:
            raise ValueError('cant create variable reference')

    def _create_header(self):
        imports = []
        for k in self._build_order:
            if 'getter' in self.cf[k]:
                module = '.'.join(self.cf[k]['getter'].split('.')[:-1])
                if f'import {module}' not in imports:
                    imports.append(f'import {module}')
        return '\n'.join(imports) + '\n'

    def python(self):
        sections = [self._create_header(), self._parameters_to_python()]
        for k in self._build_order:
            sections.append(self._build_to_python(k))
        return '\n'.join(sections)

    def _build_to_python(self, k):
        paragraph = self.cf[k]
        python_  = f"""{k.upper()} = """
        if 'getter' in paragraph:
            python_ += paragraph['getter'] + '(\n'
        else:
            raise NotImplementedError
        for arg in paragraph.get('args', {}):
            if isinstance(paragraph['args'][arg], str) and '$' in paragraph['args'][arg]:
                variable_type = self._determine_getter(paragraph['args'][arg])
                python_expression = \
                    self._variable_reference_to_python(*variable_type)
                python_ += f'    {arg}={python_expression},\n'
            else:
                python_ += f'    {arg}={json.dumps(paragraph["args"][arg])},\n'
        python_ += ')\n'
        return python_

    @property
    def explicit_cf(self):
        return {
            "options": self.parameters,
            "builds": self.explicit_builds,
            "root": self.root,
        }

    def _update_cf(self, cf, parent_cf):
        if isinstance(parent_cf, str):
            with open(parent_cf) as f:
                parent_cf = yaml.load(f)
        assert 'root' in parent_cf or 'root' in cf
        if 'root' in cf:
            parent_cf['root'] = cf['root']
        if 'options' not in parent_cf:
            parent_cf['options'] = {}
        if 'parameters' not in parent_cf:
            parent_cf['parameters'] = []
        parent_cf['parameters'].extend(cf.get('parameters', []))
        parent_cf['options'].update(cf.get('options', {}))
        parent_cf['builds'].update({
            k: v for k, v in cf['builds'].items() if k not in parent_cf['builds']
        })
        for k in parent_cf['builds']:
            if k in cf['builds']:
                if 'args' not in parent_cf['builds'][k]:
                    parent_cf['builds'][k]['args'] = {}
                if parent_cf['builds'][k]['getter'] == cf['builds'][k]['getter']:
                    parent_cf['builds'][k]['args'].update(
                        cf['builds'][k].get('args', {})
                    )
                else:
                    parent_cf['builds'][k] = cf['builds'][k]

        print(json.dumps(parent_cf, indent=2))
        return parent_cf

    def _get_paragraph_variables(self, paragraph):
        v = []
        lookup = {}
        if 'getter' in paragraph and paragraph['getter'].startswith('$'):
            lookup['getter'] = self._determine_getter(paragraph['getter'])
            v.append(lookup['getter'][0])
        lookup['args'] = {}
        if 'args' in paragraph:
            for key, value in paragraph.get('args', {}).items():
                if isinstance(value, str) and value.startswith('$'):
                    lookup['args'][key] = self._determine_getter(value)
                    v.append(lookup['args'][key][0])
        return sorted(list(set(v))), lookup

    @staticmethod
    def _import_item(path):
        path = path.split('.')
        module = '.'.join(path[:-1])
        function = path[-1]
        return getattr(importlib.import_module(module), function)

    @staticmethod
    def _get_default_values(f):
        p = inspect.signature(f).parameters
        return {k: p[k].default for k in p if p[k].default != inspect._empty}

    def _build_leaf(self, paragraph, paragraph_name, do_build=True):
        self._build_order.append(paragraph_name)

        if 'args' not in paragraph:
            paragraph['args'] = {}

        if not self.quiet:
            print(f'importing {paragraph["getter"]}')
        getter = self._import_item(paragraph['getter'])
        defaults = self._get_default_values(getter)
        defaults_not_specified = \
            {k: v for k, v in defaults.items() if k not in paragraph['args']}
        self.explicit_builds[paragraph_name] = paragraph.copy()
        self.explicit_builds[paragraph_name]['args'].update(defaults_not_specified)
        if self.debug is not None and self.debug == paragraph_name:
            print(f'!!!entering building debug: debug={self.debug}!!!')
            print(paragraph)
            import pdb; pdb.set_trace()
        if do_build:
            try:
                return getter(**paragraph['args'])
            except Exception as e:
                # This allows jumping into the error with the debugger
                raise Exception(
                    f'something went wrong in building {paragraph_name}'
                ).with_traceback(e.__traceback__) from e
        else:
            return f'#{paragraph_name}'

    @staticmethod
    def _determine_getter(value):
        """
        >>> Builder._determine_getter('$test[12]')
        ('test', 'index', 12)
        >>> Builder._determine_getter("$test['abc']")
        ('test', 'key', 'abc')
        >>> Builder._determine_getter("$test[$foo]")
        ('test', 'variable', 'foo')
        >>> Builder._determine_getter("$test.bla")
        ('test', 'attribute', 'bla')
        >>> Builder._determine_getter('$test')
        ('test', 'normal', None)
        """
        patterns = [
            r"^\$([a-zA-Z0-9_]+)\[([0-9]+)\]",
            r"^\$([a-zA-Z0-9_]+)\[\'([^']+)\'\]",
            r"^\$([a-zA-Z0-9_]+)\[\$(.*)\]",
            r"^\$([a-zA-Z0-9_]+)\.([a-zA-Z_]+)",
            r"^\$([a-zA-Z0-9_]+)$",
        ]
        types_ = ['index', 'key', 'variable', 'attribute', 'normal']
        match = re.match('|'.join(patterns), value)
        if match is None:
            raise Exception(f'invalid variable reference {value}')
        groups = match.groups()
        i = next(i for i, x in enumerate(groups[::2]) if x is not None)
        type_ = types_[i]
        item = None
        if type_ != 'normal':
            item = groups[2 * i + 1]
        if item is not None and item.isnumeric():
            item = int(item)
        return groups[2 * i], type_, item

    def __getitem__(self, item):
        try:
            value = self.parameters[item]
        except KeyError:
            try:
                value = self.built[item]
            except KeyError:
                raise NotBuiltError
        return value

    def _retrieve_variable(self, manifest, do_build=True):
        key = manifest[0]
        type_ = manifest[1]
        lookup = manifest[2]
        value = self[key]
        if type_ == 'variable':
            lookup = self[lookup]

        if type_ == 'normal':
            pass
        elif type_ in {'key', 'index', 'variable'}:
            try:
                if isinstance(value, str) and value.startswith('#') and not do_build:
                    value = value + f'[{lookup}]'
                else:
                    value = value[lookup]
            except TypeError as e:
                if not do_build:
                    return
                raise e
        elif type_ == 'attribute':
            try:
                if isinstance(value, str) and value.startswith('#') and not do_build:
                    value = f'{value}.{lookup}'
                else:
                    value = getattr(value, lookup)
            except AttributeError as e:
                if not do_build:
                    return
                raise e
        else:
            raise NotImplementedError
        return value

    def _build_steps(self, steps, do_build=True):
        for step in steps:
            self._build_from_root(step, do_build=do_build)

    def _build_from_root(self, paragraph, do_build=True):
        paragraph_value = copy.deepcopy(self.cf[paragraph])
        if 'steps' in paragraph_value:
            return self._build_steps(paragraph_value['steps'])
        variables = self._get_paragraph_variables(paragraph_value)[1]
        dependencies = []
        if variables:
            if 'getter' in variables:
                dependencies.append(variables['getter'])
                try:
                    paragraph_value['getter'] = self._retrieve_variable(variables['getter'],
                                                                        do_build=do_build)
                except NotBuiltError:
                    self.built[variables['getter'][0]] = \
                        self._build_from_root(variables['getter'][0], do_build=do_build)
                    paragraph_value['getter'] = self._retrieve_variable(variables['getter'],
                                                                        do_build=do_build)

            for k, v in variables['args'].items():
                dependencies.append(v)
                try:
                    paragraph_value['args'][k] = self._retrieve_variable(v, do_build=do_build)
                except NotBuiltError:
                    self.built[v[0]] = \
                        self._build_from_root(v[0], do_build=do_build)
                    paragraph_value['args'][k] = self._retrieve_variable(v, do_build=do_build)

        for k in dependencies:
            if k[0] in self.cf and f'\t{k[0]} -> {paragraph}\n' not in self.G.body:
                try:
                    argument_name = next(x for x in variables.get('args', {})
                                         if variables.get('args', {})[x] == k)
                    self.G.edge(k[0], paragraph, label=argument_name)
                except StopIteration:
                    self.G.edge(k[0], paragraph)

        built = self._build_leaf(paragraph_value, paragraph, do_build=do_build)
        self.built[paragraph] = built
        return built

    def build_table(self):
        header = '| variable | constructor |\n --- | --- |\n'
        for k in self.cf:
            if 'getter' in self.cf[k]:
                header += f'| {k} | `{self.cf[k]["getter"]}` |\n'
        return header

    def print(self, path_=None):
        if path_ is None:
            print(self)
            print('-' * len(str(self)))
            from IPython.display import Markdown, display
            display(Markdown(self.build_table()))
            return self.G
        else:
            self.G.format = 'png'
            with open(path_ + '.table.md', 'w') as f:
                f.write(self.build_table())
            self.G.render(path_)

    def build(self, target=None, do_build=True):
        self._build_order = []
        if target is None:
            target = self.root
        return self._build_from_root(target, do_build=do_build)


def build(
    config,
    target=None,
    strict=False,
    dry_run=False,
    debug=None,
    save=True,
    **parameters,
):
    """
    Build function recursively based on "config"

    :param config: config path
    :param target: build only: config["builds"]["<target>"]
    :param verbose: toggle to True for verbose output
    :param **parameters: specified parameters for build

    For more details see "tenen.builder.Builder"
    """
    if config.endswith('.yaml'):
        with open(config) as f:
            config = yaml.load(f)
    elif config.endswith('.json'):
        with open(config) as f:
            config = json.load(f)
    else:
        raise Exception('only .json and .yaml file extensions supported for configs')
    if strict:
        for k in config.get('parameters', {}):
            assert k in parameters, f'missing required parameter "{k}"'
    builder = Builder(config, debug=debug, **parameters)
    if 'experiment' in parameters and os.path.exists(f'models/{parameters["experiment"]}') and save:
        with open(f'models/{parameters["experiment"]}/explicit_cf.json', 'w') as f:
            f.write(json.dumps(builder.explicit_cf, indent=2).replace('#', '$'))
    if not dry_run:
        output = builder.build(target=target)
    else:
        output = None
    return output, builder, builder.explicit_cf
