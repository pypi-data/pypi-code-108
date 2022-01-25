 



from PySide2 import QtWidgets
from ciomax.sections.collapsible_section import CollapsibleSection
from ciopath.gpath_list import PathList
from pymxs import runtime as rt
 

class ExtraAssetsSection(CollapsibleSection):
    ORDER = 65

    def __init__(self,dialog):
        super(ExtraAssetsSection, self).__init__(dialog,"Extra Assets")

        # Buttons
        self.button_layout = QtWidgets.QHBoxLayout()

        for button in [
            {"label": "Clear", "func": self.clear},
            {"label": "Remove selected", "func": self.remove_selected},
            {"label": "Browse files", "func": self.browse_files},
            {"label": "Browse directory", "func": self.browse_dir},
        ]:

            btn = QtWidgets.QPushButton(button["label"])
            btn.setAutoDefault(False)
            btn.clicked.connect(button["func"])
            self.button_layout.addWidget(btn)

        self.content_layout.addLayout(self.button_layout)

        # List
        self.list_component = QtWidgets.QListWidget()
        self.list_component.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_component.setFixedHeight(140)
        self.content_layout.addWidget(self.list_component)
 
    def add_paths(self, *paths):
        # use a PathList to deduplicate.
        path_list = PathList(*self.entries())
        path_list.add(*paths)
        self.list_component.clear()
        self.list_component.addItems([p.fslash() for p in path_list])


    def entries(self):
        result = []
        for i in range(self.list_component.count() ):
            result.append(self.list_component.item(i).text())
        return result

    def clear(self):
        self.list_component.clear()
        self.dialog.store.set_assets([])

    def remove_selected(self):
        model = self.list_component.model()
        for row in sorted([index.row() for index in self.list_component.selectionModel().selectedIndexes()], reverse=True):
            model.removeRow(row)

        self.dialog.store.set_assets( self.entries() )

    def browse_files(self):
        result = QtWidgets.QFileDialog.getOpenFileNames(
            parent=None, caption="Select files to upload")
        if len(result) and len(result[0]):
            self.add_paths(*result[0])
            self.dialog.store.set_assets( self.entries() )

    def browse_dir(self):
        result = QtWidgets.QFileDialog.getExistingDirectory(
            parent=None, caption="Select a directory to upload")
        if result:
            self.add_paths(result)
            self.dialog.store.set_assets( self.entries() )

    def populate_from_store(self):
        store = self.dialog.store
        super(ExtraAssetsSection, self).populate_from_store(store )
        
        self.list_component.addItems(store.assets())

    def resolve(self, expander, **kwargs):
        """
        Compose the output_paths submission sub-object.

        Consists of: 
            amendments = kwargs["amendments"]["upload_paths"]
            self.entries =  Extra assets added manually by the customer.
            AssetManager.GetAssets() = 3ds Max native asset scraper.
            scenefile  = This scene file, even though we may not need it.

        Returns list of paths with forward slashes.
        """
        amendments = kwargs.get("amendments", {}).get("upload_paths", [])
        path_list = PathList()
        path_list.add(*self.entries())

        num_max_assets = rt.AssetManager.getNumAssets()
        max_assets = [rt.AssetManager.getAssetByIndex(i).getFullFilePath() for i in range(1,num_max_assets+1)]

        for asset in max_assets + amendments:
            try:
                path_list.add(asset)
            except ValueError:
                pass

        scenefile =  expander.evaluate("<scenefile>")
        path_list.add(scenefile)

        # in place expand glob characters (although, currently we don't have any)
        path_list.glob()

        return  {"upload_paths":  [p.fslash() for p in path_list]}
 