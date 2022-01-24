try:
    from accpac import UI, UIGridColumn, Finder, showMessageBox
    from extools.view import exview
    from extools.view.errors import ExViewRecordDoesNotExist
    from extools.message import logger_for_module
    from pprint import pformat
except ImportError as e:
    UI = object


class OptfieldMultiColumnUI(UI):
    """Optfield Column UI adds a column populated with a optional field value.

    :param optf_datasource: Optional field datasource name.
    :type optf_datasource: str
    :param grid_control_name: Name of the grid control to add a column to.
    :type grid_control_name: str
    :param columns: Columns to create
    :type columns: dict

    To use the OptfieldMultiColumn UI, create a new Screen script that initializes
    an instance of the class, passing the column configuration as a dictionary.

    Below is an example of adding two columns, *Warranty* and *Warranty
    Period*, to the O/E Order Entry grid, that is populated with the WARRANTY
    optional field for the line.

    .. code-block:: python

        # OE1100
        from accpac import *
        from extools.ui.optfield_column import OptfieldMultiColumnUI

        COLUMNS = {
            "Warranty": {
                'optional_field': 'WARRANTY',
                'default': False,
                'editable': False,
                'hijack': 'LOCATION'
            },
            "Warranty Period": {
                'optional_field': 'WARRANTYPRD',
                'default': "60 Days",
                'editable': True,
                'hijack': 'ITEM',
            },

        OPTF_DATASOURCE = "dsOEORDDO"
        GRID_CONTROL = "avlOEORDDdetail1"

        def main(*args, **kwargs):
            OptfieldMultiColumnUI(OPTF_DATASOURCE, GRID_CONTROL, COLUMNS)
    """
    def __init__(self, optf_datasource, grid_control_name, columns):
        UI.__init__(self)
        self.log = logger_for_module('extools.ui')
        self.log.debug("OptfieldMultiColumnUI({}, {}, {})".format(
            optf_datasource, grid_control_name, pformat(columns)))
        self.columns = columns
        self.dsoptf = self.openDataSource(optf_datasource)
        self.grid_control_name = grid_control_name
        self.finder_fields = {}
        self.default = ""

        self.createScreen()

    def optional_field_is_validated(self, optional_field):
        with exview("CS0011", seek_to={
                "OPTFIELD": optional_field}) as optf:
            if int(optf.validate):
                return True
        return False

    def onGridFinder(self, field_name, caption):
        if caption in self.finder_fields:
            finder = Finder()
            finder.viewID = "CS0012"
            finder.displayFields = "2"
            finder.returnFields = "2"
            finder.filter = 'OPTFIELD="{}"'.format(self.finder_fields[caption])
            finder.onOK = self.finder_ok
            finder.onCancel = self.finder_cancel
            finder.show(self)

    def finder_ok(self, e):
        self.grid.endEdit(e)

    def finder_cancel(self):
        self.grid.preventFinder()

    def is_valid(self, optional_field, value):
        try:
            with exview("CS0012", seek_to={
                    "OPTFIELD": optional_field,
                    "VALUE": value, }) as exv:
                return True
        except ExViewRecordDoesNotExist:
            pass
        return False

    def createScreen(self):
        grid = self.getHostControl(self.grid_control_name)
        self.grid = grid

        for caption, config in self.columns.items():

            col = UIGridColumn()
            col.caption = caption
            col.hasFinder = False

            if self.optional_field_is_validated(config['optional_field']):
                col.hasFinder = True
                self.finder_fields[caption] = config['optional_field']

            col.isEditable = config['editable']
            grid.addColumn(col, config['hijack'])

        grid.setOnGetText(self.onGridGetText)
        grid.setOnBeginEdit(self.onGridBeginEdit)
        grid.setOnAfterEdit(self.onGridAfterEdit)
        if self.finder_fields:
            grid.setOnFinder(self.onGridFinder)

        grid.refreshData()
        self.show()

    def onGridGetText(self, e):
        self.log.debug("onGridGetText for {} {}".format(
                e.caption, pformat(self.columns.keys())))
        if e.caption in self.columns:
            self.dsoptf.put("OPTFIELD", self.columns[e.caption]['optional_field'])
            r = self.dsoptf.read()
            if r != 0:
                e.value = self.default
            else:
                e.value = self.dsoptf.get("VALUE")
            self.log.debug("got value {} [{}]".format(e.value, r))
        return e

    def onGridBeginEdit(self, e):
        self.log.debug("onGridBeginEdit for {} {}".format(
                e.caption, pformat(self.columns.keys())))
        if e.caption in self.columns.keys():
            e.datatype = "TEXT"
            e.width = 60
            e = self.onGridGetText(e)
            self.log.debug("got value {}".format(e.value))
        return e

    def onGridAfterEdit(self, e):
        self.log.debug("onGridAfterEdit for {} {}".format(
                e.caption, self.columns.keys()))
        if e.caption in self.columns.keys():
            optional_field = self.columns[e.caption]['optional_field']
            if self.optional_field_is_validated(optional_field):
                if not self.is_valid(optional_field, e.value):
                    showMessageBox("{} is not a valid choice for {}.".format(
                        e.value, e.caption))
                    e.value = ""
                    return
            self.set_optional_field_to(optional_field, e.value)
        return e

    def set_optional_field_to(self, optional_field, value):
        self.dsoptf.put("OPTFIELD", optional_field)
        r = self.dsoptf.read()
        if r != 0:
            self.dsoptf.dsrecordgenerate()
            self.dsoptf.dsput("OPTFIELD", optional_field)
            self.dsoptf.dsput("VALUE", value)
            self.dsoptf.dsinsert()
        else:
            self.dsoptf.dsput("VALUE", value)
            self.dsoptf.dsupdate()
        self.log.debug("set_optional_field_to({}, {}) complete.".format(
            optional_field, value))