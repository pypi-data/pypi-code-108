# Created by matveyev at 23.02.2021

from copy import deepcopy
from xml.etree import cElementTree as ET

from PyQt5 import QtCore, QtGui

import onlinexml_editor.headers as headers # device_headers, online_headers, possible_headers

device_view_role = QtCore.Qt.UserRole + 1

check_column = 1
type_column = 2


# ----------------------------------------------------------------------
class Node(object):

    def __init__(self, parent, info=None, parent_info=None, row=-1):

        self.parent = parent

        self.part_of_serial_device = isinstance(parent, SerialDeviceNode)
        self.children = []
        self.headers = []

        if info is not None:
            if isinstance(info, dict):
                self.info = info
            else:
                self.info = deepcopy(info.attrib)
                for child in info:
                    if child.tag not in ['group', 'serial_device', 'single_device']:
                        self.info[child.tag] = child.text
        else:
            self.info = {}

        if self.parent is not None:
            self.parent_info = parent.info
        else:
            self.parent_info = {}

        if parent_info is not None:
            self.parent_info = parent_info
            self.part_of_serial_device = True

        all_attribs = list(self.info.keys()) + list(self.parent_info.keys())
        for name in headers.device_headers:
            if name in all_attribs:
                self.headers.append(name)

        for name in all_attribs:
            if name not in self.headers:
                self.headers.append(name)
            if name not in headers.possible_headers:
                headers.possible_headers.append(name)

        if self.parent is not None:
            self.parent.add_child(self, row)

    # ----------------------------------------------------------------------
    def _refill_headers(self):
        self.headers = []
        all_headers = []
        for child in self.children:
            all_headers += child.headers

        all_headers = list(set(all_headers))

        for name in headers.device_headers:
            if name in all_headers:
                self.headers.append(name)

        for name in all_headers:
            if name not in self.headers:
                self.headers.append(name)

    # ----------------------------------------------------------------------
    def add_child(self, child, row=-1):
        if row == -1:
            self.children.append(child)
        else:
            self.children.insert(row, child)
        child.parent = self
        self._refill_headers()

    # ----------------------------------------------------------------------
    def remove_child(self, row):
        del self.children[row]
        self._refill_headers()

    # ----------------------------------------------------------------------
    @property
    def row(self):
        if self.parent is None:
            return 0
        return self.parent.children.index(self)

    # ----------------------------------------------------------------------
    @property
    def child_item_count(self):
        return len(self.headers)

    # ----------------------------------------------------------------------
    @property
    def child_count(self):
        return len(self.children)

    # ----------------------------------------------------------------------
    def child(self, row):
        try:
            return self.children[row]
        except IndexError:
            return None

    # ----------------------------------------------------------------------
    def data(self, column, role):

        if role >= device_view_role:
            role -= device_view_role
            key = self.parent.headers[column].lower()
        else:
            key = headers.online_headers[column].lower()

        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            if key in self.info:
                return self.info[key]
            elif self.part_of_serial_device:
                if key in self.parent_info:
                    return self.parent_info[key]
            elif key == 'device':
                return self.class_name()
            else:
                return ''

        elif role == QtCore.Qt.FontRole:
            my_font = QtGui.QFont()
            if self.check_status() != QtCore.Qt.Unchecked:
                my_font.setBold(True)
            else:
                my_font.setItalic(True)
            return my_font

        elif role == QtCore.Qt.ForegroundRole:
            if not self.check_status() != QtCore.Qt.Unchecked:
                return QtGui.QColor(QtCore.Qt.gray)
            else:
                return QtCore.QVariant()

        elif role == QtCore.Qt.CheckStateRole:
            if column == check_column:
                return self.check_status()
            else:
                return QtCore.QVariant()

    # ----------------------------------------------------------------------
    def set_data(self, column, data, role):

        data_to_set = None

        if role >= device_view_role:
            role -= device_view_role
            key = self.parent.headers[column].lower()
        else:
            key = headers.online_headers[column].lower()

        if role == QtCore.Qt.EditRole:
            data_to_set = data

        elif role == QtCore.Qt.CheckStateRole:
            if data:
                if self.check_status():
                    data_to_set = 'no'
                else:
                    data_to_set = 'yes'
            else:
                data_to_set = 'no'

        if data_to_set is None:
            return False

        if key in self.info:
            self.info[key] = data_to_set
        elif self.part_of_serial_device:
            if key in self.parent_info:
                self.parent_info[key] = data_to_set

        return True

    # ----------------------------------------------------------------------
    def flags(self, column):

        if column == check_column:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
        elif column == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | \
                   QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsEditable
        elif column == type_column and not isinstance(self, DeviceNode):
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    # ----------------------------------------------------------------------
    def is_activated(self):

        if 'active' in self.info:
            active = self.info['active'] == 'yes'
        else:
            active = True

        if self.parent is not None:
            active *= self.parent.is_activated()

        return active

    # ----------------------------------------------------------------------
    def is_all_active(self):
        if 'active' in self.info:
            all_active = self.info['active'] == 'yes'
        else:
            all_active = True

        for child in self.children:
            all_active *= child.is_all_active()

        return all_active

    # ----------------------------------------------------------------------
    def check_status(self):
        if self.is_activated():
            return QtCore.Qt.Checked
        else:
            return QtCore.Qt.Unchecked

    # ----------------------------------------------------------------------
    def deactivate(self):
        self.info['active'] = 'no'
        for device in self.children:
            device.parent_deactivated(False)

    # ----------------------------------------------------------------------
    def class_name(self):
        return ''

    # ----------------------------------------------------------------------
    def class_type(self):
        return ''

    # ----------------------------------------------------------------------
    def accept_add(self):
        return False

    # ----------------------------------------------------------------------
    def get_my_path(self):
        return self.parent.get_my_path() + '/' + self.data(headers.device_headers.index('name'), QtCore.Qt.DisplayRole)

    # ----------------------------------------------------------------------
    def filter_row(self, search_value):
        for value in self.info.values():
            if search_value in value:
                return True
        if self.part_of_serial_device:
            for value in self.parent_info.values():
                if search_value in value:
                    return True
        return False

    # ----------------------------------------------------------------------
    def accept_paste(self, clipboard):

        def _check_serial_device(info):
            equal = True
            for child in clipboard:
                if child.tag not in ['name', 'device', 'sardananame']:
                    if child.tag in info:
                        equal *= child.text == info[child.tag]
                    else:
                        equal = False

            return equal

        def _get_cut_device():
            device = ET.Element('single_device', attrib=clipboard.attrib)
            for child in clipboard:
                if child.tag == 'device':
                    _make_sub_element('device', child.text, device, '')

            return device

        paste_enabled = False
        device_to_paste = clipboard
        if clipboard is not None:
            # if we have group to paste
            if isinstance(self, GroupNode) or isinstance(self, ConfigurationNode):
                paste_enabled = True

            elif isinstance(self, SerialDeviceNode):
                if _check_serial_device(self.info):
                    paste_enabled = True
                    device_to_paste = _get_cut_device()

        return paste_enabled, device_to_paste

    # ----------------------------------------------------------------------
    def get_converted(self):
        if isinstance(self, SerialDeviceNode):
            new_device = ET.Element('group',
                              attrib={'name': self.info['name'],
                                      'active': self.info['active'],
                                      'comment': self.info['comment']})

            for child in self.children:
                child.get_data_to_copy(new_device)
        else:
            new_device = ET.Element('serial_device',
                                    attrib={'name': self.info['name'],
                                            'active': self.info['active'],
                                            'comment': self.info['comment']})

            for key, value in self.children[0].info.items():
                if key not in ['device', 'name', 'comment', 'active', 'sardananame']:
                    _make_sub_element(key, value, new_device, '')

            for child in self.children:
                device = ET.SubElement(new_device, 'single_device',
                                       attrib={'name': child.info['name'],
                                               'active': child.info['active'],
                                               'comment': child.info['comment']})
                _make_sub_element('device', child.info['device'], device, '')
                if 'sardananame' in child.info:
                    _make_sub_element('sardananame', child.info['sardananame'], device, '')

        return new_device

    # ----------------------------------------------------------------------
    def can_be_converted(self):
        can_be_converted, caption = False, ''

        if isinstance(self, SerialDeviceNode):
            can_be_converted, caption = True, 'Convert to group'
        elif isinstance(self, GroupNode):
            if len(self.children):
                can_be_converted = True
                caption = 'Convert to serial device'
                if isinstance(self.children[0], DeviceNode):
                    properties = dict(self.children[0].info)
                    for key in ['sardananame', 'device', 'name', 'comment', 'active']:
                        if key in properties:
                            del properties[key]

                    for child in self.children[1:]:
                        if isinstance(child, DeviceNode):
                            for key, value in properties.items():
                                if key in child.info:
                                    can_be_converted *= value == child.info[key]
                                else:
                                    can_be_converted = False
                        else:
                            can_be_converted = False
                else:
                    can_be_converted = False

        return can_be_converted, caption

    # ----------------------------------------------------------------------
    def _get_device(self, parent):
        if parent is None:
            return ET.Element(self.class_type().lower(),
                              attrib={'name': self.info['name'],
                                      'active': self.info['active'],
                                      'comment': self.info['comment']})
        else:
            return ET.SubElement(parent, self.class_type().lower(),
                                 attrib={'name': self.info['name'],
                                         'active': self.info['active'],
                                         'comment': self.info['comment']})

    # ----------------------------------------------------------------------
    def get_data_to_copy(self, parent=None):
        me = self._get_device(parent)
        for name, value in self.info.items():
            _make_sub_element(name, value, me, '')

        if isinstance(self, DeviceNode) and self.part_of_serial_device:
            for name, value in self.parent_info.items():
                _make_sub_element(name, value, me, '')
        else:
            for child in self.children:
                child.get_data_to_save(me, '')

        return me

    # ----------------------------------------------------------------------
    def get_data_to_save(self, parent_device=None, depth=''):
        property_element = None
        new_device = self._get_device(parent_device)
        new_device.text = '\n' + depth + '\t'

        for name, value in self.info.items():
            property_element = _make_sub_element(name, value, new_device, depth)

        device = None
        for child in self.children:
            device = child.get_data_to_save(new_device, depth + '\t')

        if device is not None:
            device.tail = '\n' + depth
        elif property_element is not None:
            property_element.tail = '\n' + depth

        new_device.tail = '\n' + depth

        return new_device

    # ----------------------------------------------------------------------
    def get_data_to_export(self):

        new_device = ET.Element('device')
        new_device.text = "\n\t"
        property_element = ET.SubElement(new_device, 'name')
        property_element.text = self.info['name']
        property_element.tail = "\n\t"

        for name, value in self.info.items():
            property_element = _make_sub_element(name, value, new_device)

        if self.part_of_serial_device:
            for name, value in self.parent_info.items():
                property_element = _make_sub_element(name, value, new_device)

        if property_element is not None:
            property_element.tail = '\n'

        new_device.tail = '\n'

        return new_device


# ----------------------------------------------------------------------
class DeviceNode(Node):

    # ----------------------------------------------------------------------
    def class_type(self):
        return 'single_device'

    # ----------------------------------------------------------------------
    def export_devices(self, dev_list):
        if self.is_activated():
            dev_list.append(self)


# ----------------------------------------------------------------------
class GroupNode(Node):

    # ----------------------------------------------------------------------
    def class_name(self):
        return 'Group'

    # ----------------------------------------------------------------------
    def class_type(self):
        return 'group'

    # ----------------------------------------------------------------------
    def check_status(self):

        if not self.is_activated():
            return QtCore.Qt.Unchecked
        else:
            all_active = True
            for device in self.children:
                all_active *= device.is_all_active()
            if all_active:
                return QtCore.Qt.Checked
            else:
                return QtCore.Qt.PartiallyChecked

    # ----------------------------------------------------------------------
    def export_devices(self, dev_list):
        for children in self.children:
            children.export_devices(dev_list)

    # ----------------------------------------------------------------------
    def accept_add(self):
        return True


# ----------------------------------------------------------------------
class SerialDeviceNode(GroupNode):

    # ----------------------------------------------------------------------
    def class_name(self):
        return 'Serial device'

    # ----------------------------------------------------------------------
    def class_type(self):
        return 'serial_device'

    # ----------------------------------------------------------------------
    def accept_add(self):
        return True


# ----------------------------------------------------------------------
class ConfigurationNode(GroupNode):

    # ----------------------------------------------------------------------
    def get_my_path(self):
        return self.info['name']

    # ----------------------------------------------------------------------
    def class_name(self):
        return 'Configuration'

    # ----------------------------------------------------------------------
    def class_type(self):
        return 'configuration'

    # ----------------------------------------------------------------------
    def get_all_activated_devices(self):
        dev_list = []
        for child in self.children:
            child.export_devices(dev_list)

        return dev_list

    # ----------------------------------------------------------------------
    def accept_add(self):
        return True


# ----------------------------------------------------------------------
def _make_sub_element(name, value, parent, depth=''):
    property_element = None
    if name not in ['active', 'name', 'comment']:
        property_element = ET.SubElement(parent, name)
        property_element.text = value
        property_element.tail = "\n" + depth + "\t"
    return property_element