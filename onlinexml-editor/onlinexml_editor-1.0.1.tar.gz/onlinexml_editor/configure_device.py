# Created by matveyev at 26.01.2021

import xml.etree.cElementTree as ET

from PyQt5 import QtWidgets, QtCore

from onlinexml_editor.gui.new_device_ui import Ui_AddDevice
from onlinexml_editor.property_widget import PropertyWidget
from onlinexml_editor.devices_class import SerialDeviceNode, GroupNode


class ConfigureDevice(QtWidgets.QDialog):

    # ----------------------------------------------------------------------
    def __init__(self, parent, options):
        super(ConfigureDevice, self).__init__(parent)

        self._ui = Ui_AddDevice()
        self._ui.setupUi(self)

        self._common_properties_grid = QtWidgets.QGridLayout(self._ui.common_properties)
        self._common_property_widgets = {}

        self._personal_properties_grid = QtWidgets.QGridLayout(self._ui.personal_properties)
        self._personal_property_widgets = {}

        self._last_ind = 0

        self.new_device = {}

        self._ui.fr_common_properties.setVisible(False)
        self._ui.fr_personal_properties.setVisible(False)

        self._ui.cmb_type.currentTextChanged.connect(self._change_device_type)
        self._ui.cmd_add_common_property.clicked.connect(lambda: self._add_property('common'))
        self._ui.cmd_add_personal_property.clicked.connect(lambda: self._add_property('personal'))

        if options['new']:
            self.new_device = True
            self._part_of_serial = options['part_of_serial']
            if not self._part_of_serial:
                self._ui.cmb_type.addItems(['group', 'serial_device', 'single_device'])
            else:
                self._ui.cmb_type.addItem('single_device')
                self._ui.fr_personal_properties.setVisible(True)
                self._add_property('personal', 'device', '', True)
        else:
            self._ui.cmb_type.addItem(options['device'].class_type())
            self._ui.cmb_type.setEnabled(False)

            self.new_device = False
            self.edited_device = options['device']
            self._sub_device = options['sub_device']

            self._part_of_serial = False

            if isinstance(self.edited_device, SerialDeviceNode) or isinstance(self.edited_device, GroupNode):
                if isinstance(self.edited_device, SerialDeviceNode):
                    self._part_of_serial = True
                    self._ui.fr_common_properties.setVisible(True)
                    for key, value in self.edited_device.info.items():
                        if key not in ['active', 'comment', 'name']:
                            self._add_property('common', key, value, False)

                if self._sub_device is None:
                    self._ui.le_name.setText(self.edited_device.info['name'])
                    self._ui.le_comment.setText(self.edited_device.info['comment'])
                else:
                    device = self.edited_device.children[self._sub_device]
                    self._ui.fr_personal_properties.setVisible(True)
                    self._ui.le_name.setText(device.info['name'])
                    self._ui.le_comment.setText(device.info['comment'])

                    for key, value in device.info.items():
                        if key not in ['active', 'comment', 'name']:
                            self._add_property('personal', key, value, False)

            else:
                self._ui.fr_personal_properties.setVisible(True)
                self._ui.le_name.setText(self.edited_device.info['name'])
                self._ui.le_comment.setText(self.edited_device.info['comment'])
                for key, value in self.edited_device.info.items():
                    if key not in ['active', 'comment', 'name']:
                        self._add_property('personal', key, value, False)

            self._bild_view()

    # ----------------------------------------------------------------------
    def accept(self):
        name = self._ui.le_name.text()
        while name == '':
            name, okPressed = QtWidgets.QInputDialog.getText(self, "Get device name", "Name:",
                                                             QtWidgets.QLineEdit.Normal, "")
            if not okPressed:
                self.reject()

        if self.new_device:
            self._make_new_device(name)
        else:
            self._modify_device()

        super(ConfigureDevice, self).accept()

    # ----------------------------------------------------------------------
    def _make_new_device(self, name):
        type = self._ui.cmb_type.currentText()
        self.new_device = ET.Element(type, {'name': name, 'active': 'no', 'comment': self._ui.le_comment.text()})

        if type in ['serial_device', 'single_device']:

            if type == 'serial_device':
                container = self._common_property_widgets
            else:
                container = self._personal_property_widgets

            for widget in container.values():
                valid, name, value = widget.get_data()
                if valid:
                    property_element = ET.SubElement(self.new_device, name)
                    property_element.text = value

    # ----------------------------------------------------------------------
    def _modify_device(self):
        name = self._ui.le_name.text()
        while name == '':
            name, okPressed = QtWidgets.QInputDialog.getText(self, "Get device name", "Name:",
                                                             QtWidgets.QLineEdit.Normal, "")
            if not okPressed:
                self.reject()

        if isinstance(self.edited_device, SerialDeviceNode) or isinstance(self.edited_device, GroupNode):
            if isinstance(self.edited_device, SerialDeviceNode):
                _refill_device(self.edited_device, self._common_property_widgets)

            if self._sub_device is None:
                self.edited_device.info['comment'] = self._ui.le_comment.text()
                self.edited_device.info['name'] = name
            else:
                device = self.edited_device.children[self._sub_device]
                _refill_device(device, self._personal_property_widgets)
                device.info['comment'] = self._ui.le_comment.text()
                device.info['name'] = name

        else:
            _refill_device(self.edited_device, self._personal_property_widgets)
            self.edited_device.info['comment'] = self._ui.le_comment.text()
            self.edited_device.info['name'] = name

        super(ConfigureDevice, self).accept()

    # ----------------------------------------------------------------------
    def _change_device_type(self, text):
        self._common_property_widgets = {}
        if text in ['group', 'configuration']:
            self._ui.fr_common_properties.setVisible(False)
            self._ui.fr_personal_properties.setVisible(False)
        elif text == 'serial_device':
            self._ui.fr_common_properties.setVisible(True)
            self._ui.fr_personal_properties.setVisible(False)
        else:
            self._ui.fr_common_properties.setVisible(False)
            self._ui.fr_personal_properties.setVisible(True)

        self._bild_view()

    # ----------------------------------------------------------------------
    def _add_property(self, type, name='', value='', doRefresh=True):

        if self._part_of_serial and type == 'personal':
            if name == '':
                name = 'sardananame'
            if name in ['device', 'sardananame']:
                new_property = PropertyWidget(self, self._last_ind, name, value, True)
            else:
                return
        else:
            new_property = PropertyWidget(self, self._last_ind, name, value)

        new_property.delete_me.connect(self._delete_property)
        if type == 'common':
            self._common_property_widgets[self._last_ind] = new_property
        else:
            self._personal_property_widgets[self._last_ind] = new_property

        self._last_ind += 1

        if doRefresh:
            self._bild_view()

    # ----------------------------------------------------------------------
    def _delete_property(self, ind):

        if ind in self._common_property_widgets:
            del self._common_property_widgets[ind]
        else:
            del self._personal_property_widgets[ind]

        self._bild_view()

    # ----------------------------------------------------------------------
    def _bild_view(self):

        for container, widgets in zip([self._ui.common_properties, self._ui.personal_properties],
                                      [self._common_property_widgets, self._personal_property_widgets]):
            layout = container.layout()
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                if item:
                    w = layout.itemAt(i).widget()
                    if w:
                        layout.removeWidget(w)
                        w.setVisible(False)

            QtWidgets.QWidget().setLayout(container.layout())
            layout = QtWidgets.QVBoxLayout(container)

            for widget in widgets.values():
                widget.setVisible(True)
                layout.addWidget(widget, alignment=QtCore.Qt.AlignTop)
            layout.addStretch()


# ----------------------------------------------------------------------
def _refill_device(device, widgets):
    keys = list(device.info.keys())
    for key in ['name', 'comment', 'active']:
        keys.remove(key)
    for key in keys:
        del device.info[key]

    for widget in widgets.values():
        valid, name, value = widget.get_data()
        if valid:
            device.info[name] = value