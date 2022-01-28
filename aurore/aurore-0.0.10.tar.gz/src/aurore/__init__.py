
__version__ = "0.0.10"

def load(*args,include='ccorp',include_dirs=None,**kwds):
    if include == 'ccorp':
        from .ccorp_include import YAML
        yaml = YAML(typ='safe', pure=True)
        yaml.allow_duplicate_keys = True
        yaml.include_dirs = include_dirs
        return yaml.load(*args, **kwds)

    elif include=='ruamel':
        from .ruamel_include import YAML, yaml_include, my_compose_document
        yaml = YAML(typ='safe', pure=True)
        yaml.Composer.compose_document = my_compose_document
        yaml.default_flow_style = False
        yaml.Constructor.add_constructor("!include", yaml_include)

        return yaml.load(*args, **kwds)



