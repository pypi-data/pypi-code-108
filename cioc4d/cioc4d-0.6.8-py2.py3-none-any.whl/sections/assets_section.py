import os
import c4d
from cioc4d.sections.collapsible_section import CollapsibleSection
from cioc4d.widgets.button_row import ButtonRow
from cioc4d.widgets.path_widget import PathWidget
from ciopath.gpath_list import GLOBBABLE_REGEX, PathList
from ciopath.gpath import Path
from cioc4d import const as k

BG_COLOR = c4d.Vector(0.2, 0.2, 0.2)


class AssetsSection(CollapsibleSection):
    ORDER = 200

    def __init__(self, dialog):
        self.path_list_grp_id = None
        self.pathlist = PathList()
        self.path_widgets = []
        super(AssetsSection, self).__init__(dialog, "Extra Assets", collapse=True)

    def build(self):

        self.button_row = ButtonRow(
            self.dialog, "Clear List", "Browse File", "Browse Directory", label="Actions"
        )

        self.scroll_id = self.dialog.register()
        self.path_list_grp_id = self.dialog.register()

        scroll_grp = self.dialog.ScrollGroupBegin(
            id=self.scroll_id,
            flags=c4d.BFH_SCALEFIT,
            inith=100,
            scrollflags=c4d.SCROLLGROUP_VERT | c4d.SCROLLGROUP_HORIZ,
        )

        if scroll_grp:
            grp = self.dialog.GroupBegin(
                id=self.path_list_grp_id,
                flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
                title="",
                cols=1,
                groupflags=0,
            )
            if grp:
                self.dialog.GroupBorderSpace(2, 2, 2, 2)

            self.dialog.GroupEnd()  # main
        self.dialog.GroupEnd()  # scroll

        self.dialog.SetDefaultColor(self.path_list_grp_id, c4d.COLOR_BG, BG_COLOR)

    def populate_from_store(self):
        store = self.dialog.store
        self.pathlist = PathList(*(store.assets()))
        self._update_widgets()

    def save_to_store(self):
        store = self.dialog.store
        store.set_assets([p.fslash() for p in self.pathlist])
        store.commit()

    @property
    def clear_button_id(self):
        return self.button_row.button_ids[0]

    @property
    def browse_file_button_id(self):
        return self.button_row.button_ids[1]

    @property
    def browse_directory_button_id(self):
        return self.button_row.button_ids[2]

    def on_plugin_message(self, widget_id, msg):

        # clear list button
        if widget_id == self.clear_button_id:
            self.clear_entries()
        # browse file
        elif widget_id == self.browse_file_button_id:
            fn = c4d.storage.LoadDialog(flags=c4d.FILESELECT_LOAD)
            self.add_entry(fn)
        # browse dir
        elif widget_id == self.browse_directory_button_id:
            fn = c4d.storage.LoadDialog(flags=c4d.FILESELECT_DIRECTORY)
            self.add_entry(fn)
        else:
            # delete one entry button
            path_widget = next(
                (widget for widget in self.path_widgets if widget.delete_btn_id == widget_id), None
            )
            if path_widget:
                self.remove_entry(path_widget.get_value())

    def clear_entries(self):
        self.pathlist = PathList()
        self._update_widgets()
        self.save_to_store()

    def add_entry(self, entry):
        self.pathlist.add(entry)
        self._update_widgets()
        self.save_to_store()

    def remove_entry(self, entry):
        self.pathlist.remove(entry)
        self._update_widgets()
        self.save_to_store()

    def _update_widgets(self):
        self.path_widgets = []
        self.dialog.LayoutFlushGroup(self.path_list_grp_id)
        for path in self.pathlist:
            self.path_widgets.append(PathWidget(self.dialog, path=path.fslash()))
        self.dialog.LayoutChanged(self.path_list_grp_id)

    def resolve(self, expander, **kwargs):

        if not kwargs.get("with_assets"):
            return {
                "upload_paths": "Assets are only shown here if you use the Show Assets button above."
            }
        try:
            result = self.get_upload_paths()
            return {"upload_paths": result}
        except ValueError as ex:
            pass

        return {"upload_paths": str(ex)}

    def get_upload_paths(self):
        return sorted([p.fslash() for p in self.get_assets_path_list()])

    def get_assets_path_list(self):

        document = c4d.documents.GetActiveDocument()
        docpath = document.GetDocumentPath()
        path_list = PathList(*self.pathlist)

        # Called remove_missing here because its cheaper to do it while the list
        # is small. The scraped assets have an exists field anyway.
        path_list.remove_missing()

        docfile = Path(os.path.join(docpath, document.GetDocumentName())).fslash()
        path_list.add(docfile)

        for fn in [a["filename"] for a in self.get_all_scraped_assets()]:
            if not fn or not fn.strip():
                continue
            if Path(fn).relative:
                fn = os.path.join(docpath, fn)
            if os.path.exists(fn):
                path_list.add(fn)

        path_list.glob()
        return path_list

    @staticmethod
    def get_all_scraped_assets():
        """
        Return all scraped asset objects. Dont rmove missing
        """
        document = c4d.documents.GetActiveDocument()

        if k.C4D_VERSION < 22:
            return c4d.documents.GetAllAssets(document, False, "")
        else:
            asset_list = []
            success = c4d.documents.GetAllAssetsNew(
                document, False, "", flags=c4d.ASSETDATA_FLAG_WITHCACHES, assetList=asset_list
            )
            if success == c4d.GETALLASSETSRESULT_FAILED:
                raise ValueError("c4d.GetAllAssetsNew gave an error.")
            else:
                return asset_list
