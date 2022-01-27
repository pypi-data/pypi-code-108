import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

try:
    from ckanext.metaexport.interfaces import IMetaexport
except ImportError:
    IMetaexport = None

from . import cli, interfaces, views, helpers
from .logic import action


class Iso19115Plugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(interfaces.IIso19115, inherit=True)

    if IMetaexport:
        plugins.implements(IMetaexport, inherit=True)

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
        tk.add_resource("assets", "iso19115")

    # IMetaexport
    def register_metaexport_format(self):
        from . import formatter

        return dict(iso19115=formatter.Iso19115())

    def register_data_extractors(self, formatters):
        formatters.get("iso19115").set_data_extractor(_data_extractor)

    # ITemplateHelpers
    def get_helpers(self):
        return helpers.get_helpers()


def _data_extractor(pkg_id):
    return tk.get_action("iso19115_package_show")({}, {"id": pkg_id})
