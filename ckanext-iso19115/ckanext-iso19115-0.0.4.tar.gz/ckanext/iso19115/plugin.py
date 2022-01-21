import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

from . import cli, interfaces, views
from .logic import action


class Iso19115Plugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(interfaces.IIso19115, inherit=True)

    # IActions
    def get_actions(self):
        return action.get_actions()

    # IClick
    def get_commands(self):
        return cli.get_commands()

    # IBlueprint
    def get_blueprint(self):
        return views.get_blueprints()

    # IConfigurer
    def update_config(self, config):
        tk.add_template_directory(config, "templates")
