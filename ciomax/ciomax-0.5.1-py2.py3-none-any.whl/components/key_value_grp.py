from PySide2 import QtWidgets, QtCore

from ciomax.components import widgets




class KeyValueHeaderGrp(QtWidgets.QWidget):
    """A header row"""
    def __init__(self, **kwargs):
        super(KeyValueHeaderGrp, self).__init__()
        self.scale_factor = self.logicalDpiX() / 96.0
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        self.add_button = QtWidgets.QPushButton("Add")
        self.add_button.setFixedWidth(40 * self.scale_factor)
        self.add_button.setAutoDefault(False)

        self.key_header = QtWidgets.QPushButton(kwargs.get("key_label", "Key"))
        policy = self.key_header.sizePolicy()
        policy.setHorizontalStretch(2)
        self.key_header.setSizePolicy(policy)
        self.key_header.setEnabled(False)
        self.key_header.setAutoDefault(False)

        self.value_header = QtWidgets.QPushButton(
            kwargs.get("value_label", "Value"))
        policy = self.value_header.sizePolicy()
        policy.setHorizontalStretch(3)
        self.value_header.setSizePolicy(policy)
        self.value_header.setEnabled(False)
        self.value_header.setAutoDefault(False)

        layout.addWidget(self.add_button)
        layout.addWidget(self.key_header)
        layout.addWidget(self.value_header)

        if kwargs.get("checkbox_label") is not None:
            self.excl_header = QtWidgets.QPushButton(
                kwargs.get("checkbox_label", "Active"))
            self.excl_header.setFixedWidth(40 * self.scale_factor)
            self.excl_header.setEnabled(False)
            self.excl_header.setAutoDefault(False)
            layout.addWidget(self.excl_header)
        else:
            layout.addSpacing(45 * self.scale_factor)


class KeyValuePairGrp(QtWidgets.QWidget):
    """A single row"""
    delete_pressed = QtCore.Signal(QtWidgets.QWidget)

    def __init__(self, do_checkbox):
        super(KeyValuePairGrp, self).__init__()
        self.scale_factor = self.logicalDpiX() / 96.0
        layout = QtWidgets.QHBoxLayout()
        self.willBeRemoved = False
        self.checkbox = None
        self.setLayout(layout)
        self.delete_button = QtWidgets.QPushButton("X")
        self.delete_button.setFixedWidth(40* self.scale_factor)
        self.delete_button.setAutoDefault(False)
        self.delete_button.clicked.connect(self.delete_me)

        self.key_field = QtWidgets.QLineEdit()
        policy = self.key_field.sizePolicy()
        policy.setHorizontalStretch(2)
        self.key_field.setSizePolicy(policy)
 
        self.value_field = QtWidgets.QLineEdit()
        policy = self.value_field.sizePolicy()
        policy.setHorizontalStretch(3)
        self.value_field.setSizePolicy(policy)


        layout.addWidget(self.delete_button)
        layout.addWidget(self.key_field)
        layout.addWidget(self.value_field)

        if do_checkbox:
            self.checkbox = QtWidgets.QCheckBox()
            self.checkbox.setFixedWidth(40* self.scale_factor)
            layout.addWidget(self.checkbox)
        else:
            layout.addSpacing(45* self.scale_factor)

    def delete_me(self):
        self.delete_pressed.emit(self)


class KeyValueGrpList(QtWidgets.QWidget):
    """The list of KeyValuePairGrps"""

    edited = QtCore.Signal()


    def __init__(self, **kwargs):
        super(KeyValueGrpList, self).__init__()

        self.has_checkbox = kwargs.get("checkbox_label") is not None

        self.header_component = KeyValueHeaderGrp(**kwargs)
        self.content_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.content_layout)

        self.content_layout.addWidget(self.header_component)

        self.entries_component = QtWidgets.QWidget()
        self.entries_layout = QtWidgets.QVBoxLayout()
        self.entries_component.setLayout(self.entries_layout)
        self.content_layout.addWidget(self.entries_component)

        self.header_component.add_button.clicked.connect(self.add_entry)
        # self.header_component.add_button.clicked.connect(self.something_changed)

    def set_entries(self, entry_list):
        if self.has_checkbox:
            for row in  entry_list:
                self.add_entry(key=row[0], value=row[1], check=row[2])
        else:
            for row in  entry_list:
                self.add_entry(key=row[0], value=row[1])

    def add_entry(self, key="", value="", check=False):
        entry = KeyValuePairGrp(self.has_checkbox)
        entry.key_field.setText(key)
        entry.value_field.setText(value)
        if self.has_checkbox:
            entry.checkbox.setChecked(check)

        self.entries_layout.addWidget(entry)
        
        entry.delete_pressed.connect(remove_widget)
        entry.delete_pressed.connect(self.something_changed)
        entry.key_field.editingFinished.connect(self.something_changed)
        entry.value_field.editingFinished.connect(self.something_changed)
        if self.has_checkbox:
            entry.checkbox.stateChanged.connect(self.something_changed)

    def something_changed(self):
        self.edited.emit()


    def entry_widgets(self):
        return [e for e in self.entries_component.children() if e.metaObject().className() == "KeyValuePairGrp" and not e.willBeRemoved ]

    def entries(self):
        result = []
        for widget in self.entry_widgets():
            key = widget.key_field.text().strip()
            value = widget.value_field.text().strip()
            if key and value:
                if self.has_checkbox:
                    checked = widget.checkbox.isChecked()   
                    result.append([key, value, checked])
                else:
                    result.append([key, value])
        return result

    def clear(self):
        for entry in self.entries():
            remove_widget(entry)



@QtCore.Slot(QtWidgets.QWidget)
def remove_widget(widget):
    #  Since the widget is not deleted immediately, the call straight after this
    #  function which calls KeyValueGrpList.entries() and then updates the
    #  store, needs to know which widgets are left. If it simply gets children
    #  of the parent, it will include this widget. By setting willBeRemoved, we
    #  can check it in KeyValueGrpList.entry_widgets() and then igfnore unwanted
    #  widgets when saving to the store.
    widget.willBeRemoved = True
    widget.layout().removeWidget(widget)
    widget.deleteLater()
