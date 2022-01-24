try:
    from accpac import UI, UIGridColumn
except ImportError as e:
    UI = object

from extools.message import logger_for_module

class CallbackColumnUI(UI):
    """Callback Column UI adds a column to a grid populated with a callback.

    :param ds: Data source name.
    :type ds: str
    :param grid_control_name: Name of the grid control to add a column to.
    :type grid_control_name: str
    :param fields: a list of dictionaries containing the field definitions.
    :type fields: [{'caption': str, 'hijack': str, 'callback': function}, ...]

    To use the CallbackColumn UI, create a new Screen script that instantiates
    an instance of the class, customizing it with the arguments.

    Below is an example of adding a column, *Qty in Ea.* to the O/E Order Entry
    grid, that is populated with the quantity ordered in eaches, regardless of
    the line's Unit of Measure.

    .. code-block:: python

        # OE1100
        from accpac import *
        from extools.ui.callback_column import CallbackColumnUI

        DATASOURCE = "adsOEORDD"
        GRID_CONTROL = "avlOEORDDdetail1"

        def quantity_in_eaches_callback(event, datasource):
            qty = datasource.get("QTYORDERED")
            if qty:
                return qty * datasource.get("UNITCONV")
            return 0

        fields = [{
            'caption': "Qty in Ea.",
            'hijack': 'ITEM',
            'callback': quantity_in_eaches_callback
        },]

        def main(*args, **kwargs):
            CallbackColumnUI(DATASOURCE, GRID_CONTROL, fields)
    """
    def __init__(self, ds, grid_control_name, fields):
        UI.__init__(self)
        self.log = logger_for_module('extools.ui', key='callback_column')
        self.ds = self.openDataSource(ds)
        self.grid_control_name = grid_control_name
        self.fields = fields
        self.callbacks_by_caption = {}

        self.log.debug("starting callback column ui: {}, {}, {}".format(
                ds, grid_control_name, fields))

        self.createScreen()

    def createScreen(self):
        grid = self.getHostControl(self.grid_control_name)
        self.grid = grid

        for field in self.fields:
            col = UIGridColumn()
            col.caption = field['caption']
            col.hasFinder = False
            col.isEditable = False
            grid.addColumn(col, field['hijack'])
            grid.setOnGetText(self.onGridGetText)
            self.callbacks_by_caption[field['caption']] = field['callback']
            self.log.debug("added column {} [{}]".format(
                col.caption, field['hijack']))

        self.show()
        grid.refreshData()

    def onGridGetText(self, e):
        if e.caption in self.callbacks_by_caption:
            e = self.callbacks_by_caption[e.caption](e, self.ds)
