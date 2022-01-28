import os
import shutil

from kabaret import flow
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict

from .departments import Department
from .maputils import (
    GenericItemMap,
    CreateItemAction,
    CreateGenericItemAction,
    ClearMapAction,
)
from .kitsu import KitsuAsset, KitsuMap, UpdateItemsKitsuSettings


class CreateAssetAction(CreateGenericItemAction):
    """
    Adds an asset to a map given its name.
    """

    _map = flow.Parent()

    asset_name = flow.Param("").ui(label="Name")

    def needs_dialog(self):
        return True

    def run(self, button):
        if button == "Cancel":
            return

        item = self._map.add(self.asset_name.get())

        if item is None:
            msg = self.message.get()
            msg += "\n<h3>Could not create asset <i>{}</i>...</h3>".format(
                self.asset_name.get()
            )
            msg += "\nSee logs for details"
            self.message.set(msg)

            return self.get_result(close=False)

        self._map.touch()


class AssetDepartments(flow.Object):

    model = flow.Child(Department).ui(expanded=True)
    rig = flow.Child(Department).ui(expanded=True)


class Asset(KitsuAsset):
    """
    Abstraction of an asset.
    """

    ICON = ("icons.flow", "asset")

    _assets = flow.Parent()

    settings = flow.Child(ContextualView).ui(hidden=True)
    description = flow.Param("")

    departments = flow.Child(AssetDepartments).ui(expanded=True)

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(asset_name=self.name())


class Assets(GenericItemMap):
    """
    Map of assets.
    """

    ICON = ("icons.flow", "bank")

    item_prefix = "Asset"

    create_asset = flow.Child(CreateAssetAction)

    with flow.group("Kitsu"):
        update_kitsu_settings = flow.Child(UpdateItemsKitsuSettings)

    @classmethod
    def mapped_type(cls):
        return Asset

    def _fill_row_cells(self, row, item):
        row["Name"] = item.name()
        row["Description"] = item.description.get()

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            # return dict(path="LIB", file_category="LIB")
            return dict(file_category="LIB")


class AssetFamily(flow.Object):

    _asset_type = flow.Parent(2)

    description = flow.Param("")
    assets = flow.Child(Assets)

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(asset_family=self.name().lower())


class AssetFamilies(flow.Map):

    create_asset_family = flow.Child(CreateItemAction)

    @classmethod
    def mapped_type(cls):
        return AssetFamily


class AssetType(flow.Object):

    _lib = flow.Parent()

    description = flow.Param("")
    asset_families = flow.Child(AssetFamilies)

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(asset_tpye=self.name().lower())


class AssetTypes(flow.Map):

    create_asset_type = flow.Child(CreateItemAction)

    @classmethod
    def mapped_type(cls):
        return AssetType


class AssetLib(flow.Object):

    asset_types = flow.Child(AssetTypes)

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(file_category="LIB")


# Dependencies
# ----------------------


class DropAssetAction(flow.ConnectAction):
    """
    Adds an asset dependency in a map by drag-and-dropping an Asset.
    """

    _map = flow.Parent()

    def accept_label(self, objects, urls):
        asset_objects = list(filter(lambda obj: isinstance(obj, Asset), objects))
        return super(DropAssetAction, self).accept_label(asset_objects, urls)

    def _add_asset(self, asset):
        asset_ref = self._map.add(asset.name())
        asset_ref.set(asset)

    def run(self, objects, urls):
        for obj in objects:
            self._add_asset(obj)

        self._map.touch()


class AssetDependency(flow.values.Ref):
    """
    Abstraction of an asset dependency.
    """

    ICON = ("icons.flow", "casting")

    SOURCE_TYPE = Asset


class AssetDependencies(flow.Map):
    """
    Map of asset dependencies.
    """

    ICON = ("icons.flow", "casting")

    drop_asset = flow.Child(DropAssetAction)
    clear_map = flow.Child(ClearMapAction)

    @classmethod
    def mapped_type(cls):
        return AssetDependency

    def columns(self):
        return ["Name", "Description"]

    def row(self, item):
        _, row = super(AssetDependencies, self).row(item)
        asset = item.get()

        return asset.oid(), row

    def _fill_row_cells(self, row, item):
        asset = item.get()
        row["Name"] = asset.id.get()
        row["Description"] = asset.description.get()
