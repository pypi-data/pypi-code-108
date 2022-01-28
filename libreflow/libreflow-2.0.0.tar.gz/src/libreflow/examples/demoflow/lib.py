from kabaret import flow
from libreflow import baseflow


class Assets(flow.Map):

    _asset_family = flow.Parent()

    create_asset = flow.Child(baseflow.maputils.CreateItemAction)

    # def mapped_names(self, page_num=0, page_size=None):
    #     if isinstance(self._asset_family, AssetFamily):
    #         paths = self._asset_family.paths
    #         formats = self._asset_family.formats
    #         recursive_search = self._asset_family.recursive_search

    @classmethod
    def mapped_type(cls):
        return baseflow.lib.Asset

    def columns(self):
        return ["Asset"]

    def _fill_row_cells(self, row, item):
        row["Asset"] = item.name()


class AddPathAction(flow.Action):

    _asset_search_paths = flow.Parent()

    path = flow.StringParam("")

    def get_buttons(self):
        return ["Add path", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        if self._asset_search_paths.has(self.path.get()):
            raise ValueError(
                "Path '{path}' is already registered in search paths {search_paths_oid}".format(
                    path=self.path.get(), search_paths_oid=self._mng.oid()
                )
            )

        self._asset_search_paths.add(self.path.get())


class AssetSearchPaths(flow.values.OrderedStringSetValue):

    add_path = flow.Child(AddPathAction)


class AddFormatAction(flow.Action):

    _asset_formats = flow.Parent()

    format = flow.StringParam("")

    def get_buttons(self):
        return ["Add format", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        if self._asset_formats.has(self.format.get()):
            raise ValueError(
                "Format '{format}' is already registered in formats {formats_oid}".format(
                    format=self.format.get(), formats_oid=self._mng.oid()
                )
            )

        self._asset_formats.add(self.path.get())


class AssetFormats(flow.values.OrderedStringSetValue):

    add_format = flow.Child(AddFormatAction)


class AssetFamily(flow.Object):

    description = flow.Param("Asset Family Description")

    paths = flow.Param(None, AssetSearchPaths)
    formats = flow.Param(None, AssetFormats)
    recursive_search = flow.BoolParam(False)

    assets = flow.Child(Assets)


class AssetFamilies(flow.Map):

    create_asset_family = flow.Child(baseflow.maputils.CreateItemAction)

    @classmethod
    def mapped_type(cls):
        return AssetFamily


class AssetType(flow.Object):

    description = flow.Param("Asset Type Description")
    asset_families = flow.Child(AssetFamilies)


class AssetTypes(flow.Map):

    create_asset_type = flow.Child(baseflow.maputils.CreateItemAction)

    @classmethod
    def mapped_type(cls):
        return AssetType


class AssetLib(flow.Object):

    asset_types = flow.Child(AssetTypes)
