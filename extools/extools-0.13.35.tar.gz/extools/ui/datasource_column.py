try:
    from accpac import UI, UIGridColumn
except ImportError as e:
    UI = object


class DatasourceColumnUI(UI):
    """Datasource Column UI adds a column populated with a datasource field.

    The datasource does not need to be the same datasource as

    :param caption: Column caption.
    :type caption: str
    :param grid_ds: Data source name.
    :type ds: str
    :param grid_control_name: Name of the grid control to add a column to.
    :type grid_control_name: str
    :param hijack: Existing grid column to hijack.
    :type hijack: str
    :param field: the name of the data source field.
    :type field: str

    To use the DatasourceColumn UI, create a new Screen script that initializes
    an instance of the class, customizing it with the arguments.

    Below is an example of adding a column, *Unit Conversion* to the O/E Order
    Entry grid, that is populated with the unit conversion for the line.

    .. code-block:: python

        # OE1100
        from accpac import *
        from extools.ui.datasource_column import DatasourceColumnUI

        CAPTION = "Unit Conversion"
        DATASOURCE = "adsOEORDD"
        GRID_CONTROL = "avlOEORDDdetail1"
        HIJACK_COLUMN = "ITEM"
        FIELD = "UNITCONV"

        def main(*args, **kwargs):
            DatasourceColumnUI(CAPTION, DATASOURCE, GRID_CONTROL,
                             HIJACK, FIELD)
    """
    def __init__(self, caption, ds, grid_control_name,
                 hijack, gettext_callback):
        UI.__init__(self)
        self.caption = caption
        self.ds = self.openDataSource(ds)
        self.grid_control_name = grid_control_name
        self.hijack = hijack
        self.field = field

        self.createScreen()

    def createScreen(self):
        grid = self.getHostControl(self.grid_control_name)
        self.grid = grid

        col = UIGridColumn()
        col.caption = self.caption
        col.hasFinder = False
        col.isEditable = False
        grid.addColumn(col, self.hijack)

        grid.setOnGetText(self.onGridGetText)
        self.show()
        grid.refreshData()

    def onGridGetText(self, e):
        if e.caption == self.caption:
            e = self.ds.get(self.field)
