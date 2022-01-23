from pathlib import Path

import pkg_resources


class TemplateRegistry:
    def __init__(self):
        self.mapping = {}
        for ep in reversed(sorted(
                pkg_resources.iter_entry_points('oarepo_model_builder.templates'),
                key=lambda ep: ep.name)):
            loaded_package = ep.load()
            base_path = Path(loaded_package.__file__).parent.absolute()
            for k, v in loaded_package.TEMPLATES.items():
                self.mapping[k] = base_path.joinpath(v)

    def get_template(self, template_key, settings):
        # try to get the template key from settings
        path = settings.python.templates.get(template_key, self.mapping.get(template_key, None))
        if not path:
            raise AttributeError(f'Template with key {template_key} has not been found')
        if isinstance(path, str):
            path = Path(path).absolute()
        if path.exists():
            with path.open() as f:
                return f.read()
        raise AttributeError(f'Template with key {template_key} has not been found, file at path {path} does not exist')


templates = TemplateRegistry()
