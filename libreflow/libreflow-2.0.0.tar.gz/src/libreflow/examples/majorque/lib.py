import os

from kabaret import flow
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict

from libreflow import baseflow
from .departments import Department


class AssetDepartments(flow.Object):
    design = flow.Child(Department).ui(expanded=True)
    cycle = flow.Child(Department).ui(expanded=True)


class Asset(baseflow.lib.Asset):

    departments = flow.Child(AssetDepartments).ui(expanded=True)

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/episodes/all/assets/%s"
                % (self.root().project().kitsu_url.get(), self.kitsu_id.get())
            )


class Assets(baseflow.lib.Assets):

    _asset_type = flow.Parent()

    create_asset = flow.Child(baseflow.maputils.SimpleCreateAction)
    clear_map = flow.Child(baseflow.maputils.ClearMapAction).ui(hidden=True)
    with flow.group("Kitsu"):
        update_kitsu_settings = flow.Child(baseflow.film.UpdateItemsKitsuSettings)

    @classmethod
    def mapped_type(cls):
        return Asset

    def columns(self):
        return ["Asset"]

    def _fill_row_cells(self, row, item):
        row["Asset"] = item.name()

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return self._asset_type.get_default_contextual_edits(context_name)


class AssetType(flow.Object):

    _asset_types = flow.Parent()
    assets = flow.Child(Assets).ui(expanded=True)
    settings = flow.Child(ContextualView).ui(hidden=True)

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(asset_type=self.name())


class AssetTypes(flow.Map):

    create_asset_type = flow.Child(baseflow.maputils.SimpleCreateAction)
    clear_asset_types = flow.Child(baseflow.maputils.ClearMapAction)

    @classmethod
    def mapped_type(cls):
        return AssetType


class AssetLib(flow.Object):

    asset_types = flow.Child(AssetTypes).ui(expanded=True)

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(file_category="LIB")
