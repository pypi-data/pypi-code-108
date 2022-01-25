"""
A generic Key/Value table widget.

This widget encapsulates functionality to maintain a list of key value pairs
with an optional checkbox for each entry. 

The list has a header row with an Add button and each list entry has a delete
button. Add and delete functionality is fully self contained.

The "edited" signal is emitted in the following circumstances: 
* When the key or value of a row is finished editing and both are present. 
* When the checkbox changes value. 
* When a row is deleted.

No signal is emitted when a row is first added with the Add button because it is
added empty.

2 use cases are:

* Extra environment variables.
* Metadata.
"""

# TODO: Subclass the optional checkbox implementation, rather than use has_checkbox.

from PySide2 import QtWidgets, QtCore

CHECKBOX_STYLE = "QCheckBox { margin:0 8px }"
CHECKBOX_WIDTH = 40
CHECKBOX_WIDTH_PLUS = 45


class KeyValueHeaderGrp(QtWidgets.QWidget):
    """A header row"""

    def __init__(self, **kwargs):
        """Create the UI elements for the header."""
        super(KeyValueHeaderGrp, self).__init__()
        layout = QtWidgets.QHBoxLayout()

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
        self.add_button = QtWidgets.QPushButton("Add")
        self.add_button.setFixedWidth(CHECKBOX_WIDTH)
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
            self.excl_header.setFixedWidth(CHECKBOX_WIDTH)
            self.excl_header.setEnabled(False)
            self.excl_header.setAutoDefault(False)
            layout.addWidget(self.excl_header)


class KeyValuePairGrp(QtWidgets.QWidget):
    """A single row"""
    delete_pressed = QtCore.Signal(QtWidgets.QWidget)

    def __init__(self, do_checkbox):
        """Create the UI elements for a single row."""
        super(KeyValuePairGrp, self).__init__()
        layout = QtWidgets.QHBoxLayout()

        self.willBeRemoved = False
        self.checkbox = None
        self.setLayout(layout)
        self.delete_button = QtWidgets.QPushButton("X")
        self.delete_button.setFixedWidth(CHECKBOX_WIDTH)
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
            self.checkbox.setFixedWidth(CHECKBOX_WIDTH)
            self.checkbox.setStyleSheet(CHECKBOX_STYLE)
            layout.addWidget(self.checkbox)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

    def delete_me(self):
        """Delete this row."""
        self.delete_pressed.emit(self)


class KeyValueGrpList(QtWidgets.QWidget):
    """The list of KeyValuePairGrps"""

    edited = QtCore.Signal()

    def __init__(self, **kwargs):
        """Create the list UI"""
        super(KeyValueGrpList, self).__init__()

        self.has_checkbox = kwargs.get("checkbox_label") is not None

        self.header_component = KeyValueHeaderGrp(**kwargs)
        self.content_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.content_layout)

        self.content_layout.addWidget(self.header_component)

        self.entries_component = QtWidgets.QWidget()
        self.entries_layout = QtWidgets.QVBoxLayout()
        self.entries_layout.setSpacing(0)
        self.entries_layout.setContentsMargins(0, 0, 0, 0)

        self.entries_component.setLayout(self.entries_layout)
        self.content_layout.addWidget(self.entries_component)

        self.header_component.add_button.clicked.connect(self.add_entry)

        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.content_layout.addStretch()

    def set_entries(self, entry_list):
        """Set all the entries from scratch.

        entry_list is an array of tuples/arrays, each containing a key, value,
        and optional true false.
        """
        self.clear()
        if not entry_list:
            return
        if self.has_checkbox:
            for row in entry_list:
                self.add_entry(key=row[0], value=row[1], check=row[2])
            return
        for row in entry_list:
            self.add_entry(key=row[0], value=row[1])

    def add_entry(self, key="", value="", check=False):
        """
        Add a single entry.

        Set up events for editing and deletion of entries.
        """
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
        """
        Return the entry widgets.

        See remove_widget() for an explanation of the willBeRemoved property.
        """
        return [e for e in self.entries_component.children() if e.metaObject().className() == "KeyValuePairGrp" and not e.willBeRemoved]

    def entries(self):
        """Extract the values from the widget as a list of lists."""
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
        """Clear out all widgets."""
        for widget in self.entry_widgets():
            remove_widget(widget)


@QtCore.Slot(QtWidgets.QWidget)
def remove_widget(widget):
    #  Since the widget is not deleted immediately, the call straight after this
    #  function which calls KeyValueGrpList.entries() and then updates the
    #  storage knob, needs to know which widgets are left. If it simply gets
    #  children of the parent, it will include this widget. By setting
    #  willBeRemoved, we can check it in KeyValueGrpList.entry_widgets() and
    #  then ignore unwanted widgets when saving to the store.
    widget.willBeRemoved = True
    widget.layout().removeWidget(widget)
    widget.deleteLater()
