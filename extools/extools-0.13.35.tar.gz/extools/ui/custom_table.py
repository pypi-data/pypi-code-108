"""Custom Table UI

A simple UI for any custom table.  Simply point this UI class at any table
and it will render the fields for you.

If poplar_screenperms is installed, a permission code can be provided to
control access to the screen or its fields.
"""


try:
    from accpac import *
    # from accpac import (UI, showMessageBox, openView, getProgramKey,
    #                     showError, ui_command, FT_INT, FT_LONG,
    #                     PixelsToTwipsX, FT_DATE, FT_TIME, Finder, )
    from poplar_screenperms.screen_permission_ui import ScreenPermissionUI
    parent = ScreenPermissionUI
except ImportError as e:
    UI = object
    parent = UI

class CustomTableUI(parent):
    """CustomTableUI Class

    Create a new custom UI for the given table and permissions code.

    :param tablename: Custom Table name
    :type tablename: str
    :param permcode: Permissions code
    :type permcode: str


    .. code-block:: python

        from extools.ui.custom_table import CustomTableUI

        TABLENAME = "MYTABLE"
        PERMISSION_CODE = "VIMYTA"

        def main(*args, **kwargs):
            CustomTableUI(TABLENAME, PERMISSION_CODE)
    """

    def __init__(self, tablename, permcode):
        super().__init__()

        self.canEdit = True
        self.nid = 0
        self.ds = None
        self.host_controls = {}
        self.datasources = {}
        self.tablename = tablename
        self.permcode = permcode
        if self.tablename:
            self.createScreen()
            if self.permcode and hasattr(self, 'set_program'):
                self.set_program(self.permcode)
        else:
            showMessageBox("Table not set for custom UI.")
            self.closeUI()

    def createScreen(self):

        self.onClose = self.onBtnClose_Click
        self.keyFields = []
        v = openView("VI0011") # VICUSTH
        v.put("TABLENAME", self.tablename)
        if v.read() != 0:
            showMessageBox("Failed to read table {}.".format(self.tablename))
            self.closeUI()
            return
        desc = v.get("DESC")
        if desc == "":
            desc = v.get("TABLENAME")
        self.title = desc
        self.loadTable(self.tablename)
        self.ds.onAfterOpen = self.ds_onAfterOpen

        self.addButtons()
        self.show()

    def ds_onAfterOpen(self):
        self.ds.fireEvents = False
        b = False
        for n in range(1, 10):
            f = "KEY" + str(n)
            f = getProgramKey(f, "").strip()
            if f != "":
                b = True
                self.ds.put(self.ds.fieldByPosition(n-1).name, f)
        self.ds.fireEvents = True
        if b == True:
            self.ds.read()
            self.ds.refreshFields()

    def addButtons(self):
        self.removeControl("btnAdd")
        self.removeControl("btnDelete")
        self.removeControl("btnClose")

        if self.canEdit == True:

            btnid = "btnAdd"
            btn = self.addButton(btnid, "&Add")
            btn.top = -150 - btn.height
            btn.width = 1065
            btn.onClick = self.onBtnSave_Click
            btn.disable()
            self.btnSave = btn
            self.host_controls[btnid] = btn

            btnid = "btnDelete"
            btn = self.addButton(btnid, "&Delete...")
            btn.top = self.btnSave.top
            btn.width = 1065
            btn.left = self.btnSave.left + self.btnSave.width + 80
            btn.onClick = self.onBtnDelete_Click
            btn.disable()
            self.btnDelete = btn
            self.host_controls[btnid] = btn

        btnid = "btnClose"
        btn = self.addButton(btnid, "&Close")
        btn.top = -150 - btn.height
        btn.width = 1065
        btn.left = -btn.width - 150
        btn.onClick = self.onBtnClose_Click
        self.btnClose = btn
        self.host_controls[btnid] = btn

    def loadTable(self, tableName):
        parent = self
        self.ds = self.openDataSource(tableName)
        self.ds.onBefore = self.ds_onBefore
        self.ds.onAfter = self.ds_onAfter
        self.nid = 1

        v = openView("VI0013") # VICUSTK
        v.order(1) # TABLENAME, KEYNUM
        v.put("TABLENAME", tableName)
        v.put("KEYNUM", 1)
        v.read()
        self.keyFields = []
        for n in range(1, 10):
            f = "FIELD" + str(n)
            f = v.get(f).strip()
            if f != "":
                self.keyFields.append(f.upper())

        v = openView("VI0012") # VICUSTD
        v.browse("TABLENAME=" + tableName)
        top = 165

        while v.fetch() == 0:
            fid = "x{}{}".format(self.nid, v.get("FIELD"))
            f = parent.addUIField(fid)
            f.fieldName = v.get("FIELD")
            f.dataSource = self.ds
            f.width = 5000
            f.top = top
            f.ftable = ""
            f.ffield = ""
            f.ffilter = ""
            f.lookup = ""
            f.myfec = None
            f.labelWidth = 120
            top += f.height + 75

            if v.get("DATATYPE") == 1: # Text
                if v.get("SIZE") >= 30:
                    f.width = 7000
            elif v.get("DATATYPE") == 9: # bool (displays as a checkbox)
                f.borderStyle = 0
                f.labelWidth = 0

            if f.fieldName.upper() == self.keyFields[0]:
                f.onClick = self.fecKeyField_click
                f.hasFinder = True
                f.hasArrows = True
                f.hasNew = self.canEdit
                f.width += PixelsToTwipsX(23*6)

            if (v.get("FTABLE").strip() != "") and (v.get("FFIELD").strip() != ""):
                f.hasFinder = True
                m = EnhancedFieldControl(self, f)
                f.ftable = v.get("FTABLE").strip()
                f.ffield = v.get("FFIELD").strip()
                f.ffilter = v.get("FFILTER").strip()
                f.lookup = v.get("LOOKUP").strip()
                f.myfec = m
                f.myfec.fview = None
                if (f.lookup != ""):
                    lbl = self.addLabel("lblLookup" + f.id)
                    lbl.width = 3000
                    lbl.top = f.top + 50
                    lbl.left = f.width + 500
                    f.lbl = lbl
            self.host_controls[fid] = f
        self.addButtons()
        try:
            self.show()
        except Exception as e:
            showMessageBox("Failed to setup screen: {}".format(e), exc_info=True)

    def onBtnClose_Click(self):
        self.CheckSaveRecord(self.onBtnClose_Click_part2)

    def onBtnClose_Click_part2(self, bProceed):
        if bProceed == True:
            self.closeUI()
        else:
            self.abortClose()

    def onBtnSave_Click(self):
        self.saveRecord()

    def onBtnDelete_Click(self):
        self.message("Are you sure you want to delete this record?", "Delete?",
                     "QUESTION", "YESNO", self.onBtnDelete_confirmed)

    def onBtnDelete_confirmed(self, r):
        if r == "YES":
            self.ds.fireEvents = False
            self.ds.delete()
            self.ds.fireEvents = True
            self.NewHeaderLoaded()

    def isKeyField(self, fieldName):
        return fieldName.upper() in self.keyFields

    def ds_onBefore(self, e, fieldName, value):
        if e.startswith("GO") or e in ["FETCH", "INIT", ]:
            self.CheckSaveRecord()
        elif e == "DELETE":
            self.message("Confirm delete", "Delete?", "QUESTION",
                         "YESNO", self.onConfirmDelete)

    def onConfirmDelete(self, r):
        if r != "YES":
            ui_command("return", "ABORT")

    def ds_onAfter(self, e, fieldName, value):
        if e.startswith("GO") or e in ["FETCH", "INIT", "READ", "DELETE",
                                       "INSERT", "UPDATE", "POST"]:
            self.NewHeaderLoaded()
            self.ds.refreshFields()
        elif e == "PUT":
            if self.isKeyField(fieldName):
                self.OnDocumentNumberChanged()
            self.UpdateLookupLabel(fieldName)
        elif e == "OPEN":
            self.UpdateButtons()

    def OnDocumentNumberChanged(self):
        if self.ds.exists() == 1:
            self.ds.read()
            self.ds.refreshFields()
        else:
            self.ds.fireEvents = False
            values = []
            for k in self.keyFields:
                values.append(self.ds.get(k))
            self.ds.order(0)
            self.ds.recordGenerate()
            n = 0
            for v in values:
                if isinstance(v, str) == False:
                    self.ds.put(self.keyFields[n], v)
                elif v.strip() != "":
                    self.ds.put(self.keyFields[n], v)
                n += 1
            self.ds.fireEvents = True
        self.NewHeaderLoaded()

    def CheckSaveRecord(self, cb=None):
        if self.UnsavedChangesExist() == False:
            if cb != None:
                cb(True)
            return
        if cb == None:
            self.csrCb = self.csr_default
        else:
            self.csrCb = cb
        self.message("Save changes?", "Record has been modified", "QUESTION", "YESNOCANCEL", self.onConfirmSave)

    def csr_default(self, bProceed):
        if bProceed == False:
            ui_command("return", "ABORT")

    def saveRecord(self):
        if not self.ds.exists():
            return self.ds.insert()
        else:
            return self.ds.update()

    def onConfirmSave(self, r):
        if r == "YES":
            if self.saveRecord() != 0:
                self.csrCb(False)
            else:
                self.csrCb(True)
        elif r == "CANCEL":
            self.csrCb(False)
        else:
            self.csrCb(True)

    def UnsavedChangesExist(self):
        if self.canEdit == False:
            return False
        if self.ds == None:
            return False
        if self.ds.dirty() != 0:
            return True
        return False

    def NewHeaderLoaded(self):
        self.UpdateButtons()
        self.UpdateLookupLabels()

    def UpdateButtons(self):
        if self.canEdit == False:
            return
        if self.ds.exists() == 0:
            self.btnSave.setCaption("&Add")
            self.btnDelete.disable()
        else:
            self.btnSave.setCaption("&Save")
            self.btnDelete.enable()

        for k in self.keyFields:
            if str(self.ds.get(k)).strip() == "":
                self.btnSave.disable()
                return
        self.btnSave.enable()

    def fecKeyField_click(self, btnType):
        if btnType == 4:
            finder = Finder()
            finder.viewID = self.ds.rotoID
            finder.onOK = self.name_finder_ok
            finder.onCancel = self.name_finder_cancel
            if len(self.keyFields) > 1:
                finder.returnFields = ""
                for n in range(1, len(self.keyFields)+1):
                    finder.returnFields = finder.returnFields + str(n) + ","
                finder.returnFields = finder.returnFields[0:-1]
            # TODO - what fields to show
            finder.show(self)

    def name_finder_ok(self, e):
        self.finderValue = e
        self.CheckSaveRecord(self.name_finder_ok_part2)

    def name_finder_ok_part2(self, bProceed):
        if bProceed == False:
            ui_command("return", "1")
            return
        self.ds.fireEvents = False
        if len(self.keyFields) > 1:
            for n in range(0, len(self.keyFields)):
                f = self.ds.fieldByName(self.keyFields[n])
                if ((f.type == FT_INT) or (f.type == FT_LONG)):
                    self.ds.put(self.keyFields[n], int(self.finderValue[n]))
                elif f.type == FT_DATE:
                    # value will be YYYYMMDDhhnnss00
                    self.ds.put(self.keyFields[n], self.finderValue[n][0:8])
                elif f.type == FT_TIME:
                    # value will be YYYYMMDDhhnnss00
                    self.ds.put(self.keyFields[n], self.finderValue[n][8:8+8])
                else:
                    self.ds.put(self.keyFields[n], self.finderValue[n])
        else:
            f = self.ds.fieldByName(self.keyFields[0])
            if ((f.type == FT_INT) or (f.type == FT_LONG)):
                self.ds.put(self.keyFields[0], int(self.finderValue))
            else:
                self.ds.put(self.keyFields[0], self.finderValue)
        self.ds.fireEvents = True
        self.ds.read()
        ui_command("return", "4")

    def name_finder_cancel(self):
        ui_command("return", "1")

    # Update the lookup labels for all field-edit controls that have finders.
    def UpdateLookupLabels(self):
        for f in self.controls:
            if f.type == "EDIT":
                if f.hasFinder == True:
                    self.UpdateLookupLabel(f.fieldName)

    def UpdateLookupLabel(self, fname):
        f = self.getFieldControlByName(fname)
        if f == None:
            return
        if f.hasFinder != True:
            return
        if f.ftable == "" or f.lookup == "":
            return
        fvalue = self.ds.get(fname)
        if fvalue == None or fvalue == "":
            f.lbl.setText("")
            return
        if f.myfec.fview == None:
            f.myfec.fview = openView(f.ftable)
        v = f.myfec.fview
        desc = ""
        if v != None:
            v.recordClear()
            filter = f.myfec.calcFinderFilter().strip()
            if filter != "":
                filter = "(" + filter + ") AND "
            filter = filter + f.ffield + "=\"" + fvalue + "\""
            v.browse(filter)
            if v.fetch() == 0:
                desc = v.get(f.lookup).strip()
        f.lbl.setText(desc)

    def getFieldControlByName(self, fname):
        for f in self.controls:
            if f.type == "EDIT":
                if f.fieldName.strip() == fname.strip():
                    return f
        return None

class EnhancedFieldControl:
    def __init__(self, ui, fec):
        self.ui = ui
        self.fec = fec
        fec.onClick = self.click

    def click(self, btnType):
        if btnType == 4:
            finder = Finder()

            ftable = self.fec.ftable
            if ftable.find(".") != -1:
                vVICUSTH = openView("VI0011", 0)
                vVICUSTH.order(0) # TABLENAME
                vVICUSTH.put("TABLENAME", ftable)
                if vVICUSTH.read() == 0:
                    ftable = vVICUSTH.get("VIEWID")
            finder.viewID = ftable

            v = openView(self.fec.ftable, 99)
            if v == None:
                showError("Could not open '" + self.fec.ftable + "'")
                return
            if v.fieldByName(self.fec.ffield) == None:
                showError("Field '" + self.fec.ffield + "' does not exist in table '" + self.fec.ftable + "'")
                return
            finder.filter = self.calcFinderFilter()
            finder.returnFields = str(v.fieldByName(self.fec.ffield).index)
            finder.onOK = self.finder_ok
            finder.onCancel = self.finder_cancel
            finder.show(self.ui)

    def calcFinderFilter(self):
        filter = self.fec.ffilter
        if filter == "":
            return ""
        ds = self.ui.ds
        n = ds.fields()
        for i in range(0, n-1):
            vf = ds.fieldByPosition(i)
            filter = filter.replace("{" + vf.name + "}", str(ds.get(vf.name)))
        return filter

    def finder_ok(self, e):
        f = self.ui.ds.fieldByName(self.fec.fieldName)
        if ((f.type == FT_INT) or (f.type == FT_LONG)):
            self.ui.ds.put(self.fec.fieldName, int(e))
        else:
            self.ui.ds.put(self.fec.fieldName, e)
        ui_command("return", "4")

    def finder_cancel(self):
        ui_command("return", "1")
