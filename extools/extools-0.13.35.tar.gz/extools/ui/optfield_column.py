try:
    from accpac import UI, UIGridColumn, Finder, showMessageBox
    from extools.view import exview
    from extools.view.errors import ExViewRecordDoesNotExist
except ImportError as e:
    UI = object

class OptfieldColumnUI(UI):
    """Optfield Column UI adds a column populated with a optional field value.

    :param caption: Column caption.
    :type caption: str
    :param optional_field: the name of the data source field.
    :type optional_field: str
    :param optf_datasource: Optional field datasource name.
    :type optf_datasource: str
    :param grid_control_name: Name of the grid control to add a column to.
    :type grid_control_name: str
    :param hijack: Existing grid column to hijack.
    :type hijack: str
    :param default: Default value for the field.
    :type default: object
    :param editable: Allow field to be edited?
    :type editable: bool

    To use the OptfieldColumn UI, create a new Screen script that initializes
    an instance of the class, customizing it with the arguments.

    Below is an example of adding a column, *Warranty*, to the O/E Order
    Entry grid, that is populated with the WARRANTY optional field for the
    line.

    .. code-block:: python

        # OE1100
        from accpac import *
        from extools.ui.optfield_column import OptfieldColumnUI

        CAPTION = "Warranty"
        OPTFIELD = "WARRANTY"
        OPTF_DATASOURCE = "dsOEORDDO"
        GRID_CONTROL = "avlOEORDDdetail1"
        HIJACK_COLUMN = "ITEM"

        def main(*args, **kwargs):
            OptfieldColumnUI(CAPTION, OPTFIELD, OPTF_DATASOURCE, GRID_CONTROL,
                             HIJACK, default="", editable=True)
    """
    def __init__(self, caption, optional_field,
                 optf_datasource, grid_control_name,
                 hijack="ITEM", default="", editable=False):
        UI.__init__(self)
        self.caption = caption
        self.optional_field = optional_field
        self.default = default
        self.editable = editable

        self.dsoptf = self.openDataSource(optf_datasource)

        self.grid_control_name = grid_control_name
        self.hijack = hijack

        self.createScreen()

    def optional_field_is_validated(self):
        with exview("CS0011", seek_to={
                "OPTFIELD": self.optional_field}) as optf:
            if int(optf.validate):
                return True
        return False

    def on_grid_finder(self, field_name, caption):
        if caption == self.caption:
                finder = Finder()
                finder.viewID = "CS0012"
                finder.displayFields = "2"
                finder.returnFields = "2"
                finder.filter = 'OPTFIELD="{}"'.format(self.optional_field)
                finder.onOK = self.finder_ok
                finder.onCancel = self.finder_cancel
                finder.show(self)

    def finder_ok(self, e):
        self.grid.endEdit(e)

    def finder_cancel(self):
        self.grid.preventFinder()

    def is_valid(self, value):
        try:
            with exview("CS0012", seek_to={
                    "OPTFIELD": self.optional_field,
                    "VALUE": value, }) as exv:
                return True
        except ExViewRecordDoesNotExist:
            pass
        return False

    def createScreen(self):
        grid = self.getHostControl(self.grid_control_name)
        self.grid = grid

        col = UIGridColumn()
        col.caption = self.caption
        col.hasFinder = False

        if self.optional_field_is_validated():
            col.hasFinder = True

        col.isEditable = self.editable
        grid.addColumn(col, self.hijack)

        grid.setOnGetText(self.onGridGetText)
        grid.setOnBeginEdit(self.onGridBeginEdit)
        grid.setOnAfterEdit(self.onGridAfterEdit)
        if self.optional_field_is_validated():
            grid.setOnFinder(self.on_grid_finder)

        grid.refreshData()
        self.show()

    def onGridGetText(self, e):
        if e.caption == self.caption:
            self.dsoptf.put("OPTFIELD", self.optional_field)
            r = self.dsoptf.read()
            if r != 0:
                e.value = self.default
            else:
                e.value = self.dsoptf.get("VALUE")

    def onGridBeginEdit(self, e):
        if e.caption == self.caption:
            e.datatype = "TEXT"
            e.width = 60
            self.onGridGetText(e)

    def onGridAfterEdit(self, e):
        if e.caption == self.caption:
            if self.optional_field_is_validated():
                if not self.is_valid(e.value):
                    showMessageBox("{} is not a valid choice for {}.".format(
                        e.value, e.caption))
                    e.value = ""
                    return
            self.set_optional_field_to(e.value)

    def set_optional_field_to(self, value):
        self.dsoptf.put("OPTFIELD", self.optional_field)
        r = self.dsoptf.read()
        if r != 0:
            self.dsoptf.dsrecordgenerate()
            self.dsoptf.dsput("OPTFIELD", self.optional_field)
            self.dsoptf.dsput("VALUE", value)
            self.dsoptf.dsinsert()
        else:
            self.dsoptf.dsput("VALUE", value)
            self.dsoptf.dsupdate()
