"""Provides class the represents a Template in the application"""

# system imports
from datetime import date, datetime

# 3rd party imports
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class Template():
    """
    Represents a template file in the _templates directory.
    It knows how to render itself using Jinja2.

    Arguments:
        config -- Config instance
        filesystem -- Filesystem instance
        name -- string name of the template

    Attributes:
        config -- Config instance
        filesystem -- Filesystem instance
        template_path -- Path object to root template dir
        env -- Environment instance for Jinja2
        name -- string template name
    """

    EXTENSION = '.md'
    extra_vars = {}

    def __init__(self, config, filesystem, name):
        self.config = config
        self.filesystem = filesystem
        self.template_path = self.filesystem.get_templates_base_path()
        self.env = Environment(loader=FileSystemLoader(str(self.template_path)))
        self.name = name

    def get_path(self):
        """Get the pathlib.Path object for this template"""
        return self.filesystem.get_templates_base_path() / self.name

    def get_name(self):
        """Get the string name of this template"""
        return self.name

    def render(self, extra_vars=None):
        """Render this template with jinja2 and return the resulting template as a string"""
        variables = dict(self.get_variables())
        if extra_vars is not None:
            variables.update(extra_vars)
        try:
            template = self.env.get_template(self.name + self.EXTENSION)
            return template.render(**variables)
        except TemplateNotFound:
            print(f'Template "{self.name}" not found.')
            return ''

    def set_extra_vars(self, variables):
        """Set extra variables to be sent to the template when its rendered

        Arguments:
            variables -- dict of variables to pass to template
        """
        self.extra_vars = variables

    def get_default_variables(self): #pylint: disable=no-self-use
        """Get the global default variables available to all templates"""
        now = datetime.now()
        today = date.today()
        return {
            'now': now,
            'today_iso': today.isoformat(),
            'now_iso': now.isoformat(timespec='seconds'),
            'today_long': today.strftime('%A, %B %d, %Y'),
            'now_long': now.strftime('%A, %B %d, %Y %I:%M %p')
        }

    def get_config_variables(self):
        """Get the variables that are defined in the config file"""
        return self.config.get('template_vars', {}) or {}

    def get_variables(self):
        """Get a dict of all variables to be passed to the template"""
        variables = dict(self.get_default_variables())
        variables.update(self.get_config_variables())
        variables.update(self.extra_vars)
        return variables


def get_all_templates(config, filesystem):
    """Get a list of Template objects for all templates in the notebook"""
    templates = [Template(config, filesystem, child.stem)
        for child in filesystem.get_templates_base_path().glob('*.md')]

    return sorted(templates, key=lambda template: template.get_name().lower())
