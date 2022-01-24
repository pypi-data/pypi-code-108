try:
    from accpac import UI, Finder, ui_command, OpenFileDialog
except ImportError:
    UI = object
    Finder = object
    pass


class ExUI(UI):
    """An enhanced UI class for extender.

    ``ExUI`` adds additional helpers to the standard Extender UI class.
    """

    # Custom control constants
    BUTTON_WIDTH = 1065
    BUTTON_SPACE = 150

    # Button Types
    FINDER_BUTTON_TYPE = 4

    FILE_DIALOG_FILTERS = {
            "excel": ("Microsoft Excel File (*.xls, *.xlsx)"
                      "|*.xls*|All Files (*.*)|*.*",)
            }

    def __init__(self, title="exui"):
        super().__init__()
        self.title = title

    def finder_on_click_for(self, view, ok_callback, cancel_callback,
                            _filter="", display_fields="1", return_fields="1"):
        """Build a callback to execute on finder button click.

        :param view: The view name (either custom or built in) to find across.
        :type view: str
        :param ok_callback: Callback to execute on user OK
        :type ok_callback: func
        :param cancel_callback: Callback to execute on user cancel
        :type cancel_callback: func
        :param _filter: Filter to apply to finder records.
        :type _filter: str
        :param display_fields: fields to display in finder
        :type display_fields: str (comma separated indexes)
        :param return_fields: fields to display in finder
        :type return_fields: str (comma separated indexes)
        :returns: finder_on_click callback function
        """

        def finder_on_click(btnType):
            """On finder button click, open finder modal."""
            if btnType == self.FINDER_BUTTON_TYPE:
                finder = Finder()
                finder.viewID = view
                finder.onOK = ok_callback
                finder.onCancel = cancel_callback

                finder.filter = _filter
                finder.displayFields = display_fields
                finder.returnFields = return_fields
                finder.show(self)

        return finder_on_click

    def input_with_button(self, caption, callback, default="", label="Button"):
        """Create a compound field with an input field and a button::

                     +-------------------------+  +----------+
            caption  | <input field>           |  | <button> |
                     +-------------------------+  +----------+

        :param caption: input field caption
        :type caption: str
        :param callback: callback function for the button
        :type callback: function
        :param default: default value for the input field
        :type default: str
        :param label: label for the button
        :type label: str
        :returns: (input_field, button)
        :rtype: (accpac.UIField, accpac.UIButton)

        To create a file browse input and button:

        .. code-block:: python

            file_path_fld, file_browse_btn = self.input_with_button(
                    "File", self.on_browse_click, label="Browse")
        """

        # Create labeled text input field
        _id = caption.title().replace(" ", "")
        f = self.addUIField("fileField" + _id)
        f.controlType = "EDIT"
        f.size = 250
        f.width = 5000
        f.labelWidth = 60
        f.caption = caption
        f.hasFinder = False
        if default:
            f.setValue(default)

        # Add the browse button.
        bb = self.addButton("btn{}".format(_id), label)
        bb.top = f.top
        bb.width = self.BUTTON_WIDTH
        bb.left = f.left + f.width + self.BUTTON_SPACE
        bb.onClick = callback

        f.btn = bb

        return (f, bb)

    def get_browse_click_callback(self, field, title="Select File", _filter=""):
        """Create the browse button callback in a closure to pass the field."""
        def onBrowseClickCallback():
            dialog = OpenFileDialog()
            dialog.title = title
            dialog.filter = _filter
            dialog.onOK = self.get_file_ok_callback(field)
            dialog.show(self)

        return onBrowseClickCallback

    def get_file_ok_callback(self, field):
        """Create the File OK callback in a closure to pass the field."""
        def onFileOkCallback(value):
            field.setValue(value)
            ui_command("return", "4")

        return onFileOkCallback
