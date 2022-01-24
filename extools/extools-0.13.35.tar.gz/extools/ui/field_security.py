"""Field Security UIs

UIs for implementing additional security at the field level.

Use the :py:meth:`extools.ui.field_security.permissions_callback_for_table`
together with the :py:class:`extools.ui.field_security.FieldSecurityCallbackUI`
to quickly apply permissions to pretty much any field on a Sage screen.

.. code-block:: python

    # AP1200
    # Add permissions to AP Vendor Tax Number field

    MY_PERMISSIONS_TABLE = "MYMODULE.MYPERMS"
    '''Table format
    | USER | CANREAD | CANWRITE |'''

    # The tax number field control name from accpacUIInfo
    TAX_NUM_CONTROL = "afecAPVENtaxnbr"
    # The tab control name
    TAB_CONTROL = "SSTab1"
    # The id of the "Invoicing" tab, which has the field.
    TAB_ID = 1

    def main(*args, **kwargs):
        callback = permissions_callback_for_table(
                MY_PERMISSIONS_TABLE, "USER", "CANREAD", "CANWRITE")
        ui = FieldSecurityCallbackUI(
                TAX_NUM_CONTROL, callback, TAB_CONTROL, TAB_ID)
"""
try:
    from accpac import *
except ImportError:
    UI = object

from extools.view import exview
from extools.view.errors import ExViewRecordDoesNotExist

def permissions_callback_for_table(view, user_field, read_field, write_field):
    """Generate a callback that checks a user's permissions in a view.

    Best used with the :py:class:`FieldSecurityCallbackUI`, it will check
    a table containing permissions and return a simple (read, write) pair
    suitable for use as a callback.

    :param view: the view to read from, built-in (OE0520) or custom (MOD.TABLE)
    :type view: str
    :param user_field: the username field in the view.
                       must be a key or browseable field.
    :type user_field: str
    :param read_field: the read permission field name - must be bool.
    :type read_field: str
    :param write_field: the write permission field name - must be bool.
    :type write_field: str
    :returns: func

    """
    def check_permissions(user, control, ds, *args, **kwargs):
        try:
            with exview(view, seek_to={user_field: user}) as exv:
                read = bool(int(exv.get(read_field)))
                write = bool(int(exv.get(write_field)))
                return (read, write)
        except ExViewRecordDoesNotExist:
            pass
        except (ValueError, TypeError):
            pass

        return (False, False)

    return check_permissions

class FieldSecurityCallbackUI(UI):
    """Apply custom permissions to a specific on-screen field.

    :param control: name of the on-screen control.
    :type control: str
    :param callback: callback function to check perms. receives
                     (user, control, ds). callback must return (bool(can_read),
                     bool(can_write)).
    :type callback: func
    :param tab_control: name of the tab control (if applicable).
    :type tab_control: str
    :param tab_id: tab id on which the field appears (if applicable).
    :type tab_id: str
    :param ds_name: name of a ds (i.e. adsOEORDH) to open and pass to callback.
    :type ds_name: str
    """

    def __init__(self, control, callback,
                 tab_control="", tab_id=None, ds_name=""):
        UI.__init__(self)
        self.control = control
        self.callback = callback
        self.tab_control = tab_control
        self.tab_id = tab_id
        self.ds = None
        self.ds_name = ds_name
        self.getControlInfo(control, self.onControlInfo)
        self.show()

    def onControlInfo(self, info):
        # Get the host control.
        self.field = self.getHostControl(self.control)

        if self.ds_name:
            self.ds = openDataSource(self.ds_name)

        if self.tab_control:
            self.tabs = self.getHostControl(self.tab_control)
            self.tabs.setOnClick(self.onTabClick)

        self._apply_permissions()

    def _apply_permissions(self):
        r, w = self.callback(self.control, self.ds)
        if r:
            if w:
                self.field.enable()
            else:
                self.field.disable()
        else:
            self.field.hide()

    def onTabClick(self, tab):
        """On tab change hide or show field based on callback."""
        if tab == self.tab_id:
            if hasattr(self, 'field'):
                self._apply_permissions()
