import dataclasses
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QGroupBox, QVBoxLayout, QStackedWidget,
    QTabWidget, QSizePolicy)
from .datawidgets import type2Widget
from typing import Dict, Union, Optional, get_type_hints


__all__ = [
    "DataclassWidget",
    "StackedDataclassWidget",
    "TabDataclassWidget",
]


@dataclasses.dataclass
class _DefaultDataclass:
    """
    Default empty dataclass for uninitialized :class:`DataclassWidget`.
    """
    pass


class DataclassWidget(QGroupBox):
    """
    Widget which represents the fields of dataclass type.

    Standard way to construct this widget is by :meth:`fromDataclass`
    class method.

    Subclass may redefine :meth:`field2Widget` method to change the
    subwidget constructed by the field. Every subwidget must have
    ``dataValue()`` method which returns the current value,
    ``dataValueChanged`` signal which emits the changed value,
    and ``setDataValue()`` slot which updates the current value.

    :meth:`dataValue` returns the current states of the widgets as
    dataclass instance. :meth:`setDataValue` updates the current states of
    the widgets with dataclass instance.

    Examples
    ========

    Widgets are automatically generated from type annotations. Nested
    dataclasses are recursively constructed.

    >>> from dataclasses import dataclass
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from typing import Tuple
    >>> from dataclass2PySide6 import DataclassWidget
    >>> @dataclass
    ... class DataClass1:
    ...     a: Tuple[int, Tuple[bool, int]]
    >>> @dataclass
    ... class DataClass2:
    ...     x: str
    ...     y: DataClass1
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     widget = DataclassWidget.fromDataclass(DataClass2)
    ...     geometry = widget.screen().availableGeometry()
    ...     widget.resize(geometry.width() / 3, geometry.height() / 2)
    ...     widget.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP
    """

    dataValueChanged = Signal()

    @classmethod
    def fromDataclass(cls, datacls: type) -> "DataclassWidget":
        """
        Construct the widget using the fields from the dataclass.

        Parameters
        ==========

        datacls
            Dataclass type object

        """
        obj = cls()
        obj._dataclass_type = datacls
        fields = dataclasses.fields(datacls)
        annots = get_type_hints(datacls.__init__)
        for f in fields:
            f.type = annots[f.name]
        obj._widgets = {f.name: obj.field2Widget(f) for f in fields}
        obj.initWidgets()
        obj.initUI()
        return obj

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dataclass_type = _DefaultDataclass
        self._widgets = {}

    def field2Widget(self, field: dataclasses.Field) -> QWidget:
        """Return a widget for *field*."""
        if dataclasses.is_dataclass(field.type):
            widget = type(self).fromDataclass(field.type)
        else:
            widget = type2Widget(field.type)
        widget.setDataName(field.name)

        default = field.default
        if default != dataclasses.MISSING:
            widget.setDataValue(default)

        return widget

    def dataclassType(self) -> type:
        """Dataclass type which is used to construct *self*."""
        return self._dataclass_type

    def dataName(self) -> str:
        return self.title()

    def setDataName(self, name: str):
        self.setTitle(name)

    def widgets(self) -> Dict[str, QWidget]:
        """
        Sub-widgets which represent the fields of :meth:`dataclassType`.
        """
        return self._widgets

    def initWidgets(self):
        """Initialize the widgets in :meth:`widgets`."""
        for widget in self.widgets().values():
            widget.dataValueChanged.connect(self.emitDataValueChanged)

    def initUI(self):
        """Initialize the UI with :meth:`widgets`."""
        layout = QVBoxLayout()
        for widget in self.widgets().values():
            layout.addWidget(widget)
        self.setLayout(layout)

    def emitDataValueChanged(self):
        try:
            self.dataValue()
            self.dataValueChanged.emit()
        except (TypeError, ValueError):
            pass

    def dataValue(self) -> object:
        """
        Return the current state of widgets as dataclass instance.

        Returns
        =======

        data
            Dataclass instance

        """
        args = {name: w.dataValue() for (name, w) in self.widgets().items()}
        data = self.dataclassType()(**args)
        return data

    def setDataValue(self, data: object):
        """
        Apply the dataclass instance to data widgets states.

        Parameters
        ==========

        data
            Dataclass instance or dict

        """
        for name, w in self.widgets().items():
            if isinstance(data, dict):
                if not name in data.keys():
                    continue
                val = data[name]
            else:
                val = getattr(data, name)
            w.setDataValue(val)


class StackedDataclassWidget(QStackedWidget):
    """
    Stacked dataclass widgets.

    Use :meth:`addDataclass` to construct and add the widget for the
    dataclass. Use :meth:`indexOf` to get the index of the widget for
    giten dataclass.

    If data value of any dataclass widget is changed,
    :attr:`dataValueChanged` signal is emitted.

    Examples
    ========

    >>> from dataclasses import dataclass
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from dataclass2PySide6 import StackedDataclassWidget
    >>> @dataclass
    ... class DataClass1:
    ...     a: int
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     widget = StackedDataclassWidget()
    ...     widget.addDataclass(DataClass1)
    ...     geometry = widget.screen().availableGeometry()
    ...     widget.resize(geometry.width() / 3, geometry.height() / 2)
    ...     widget.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP

    """

    dataValueChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._dataclasses: Dict[type, int] = {}

    def addWidget(self, w: QWidget):
        # force size policy to make ignore the size of hidden widget
        w.setSizePolicy(
            QSizePolicy.Ignored,
            QSizePolicy.Ignored
        )
        super().addWidget(w)

    def setCurrentIndex(self, index: int):
        old_widget = self.currentWidget()
        if old_widget is not None:
            old_widget.setSizePolicy(
                QSizePolicy.Ignored,
                QSizePolicy.Ignored
            )
        new_widget = self.widget(index)
        if new_widget is not None:
            new_widget.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Preferred
            )
            new_widget.adjustSize()
        super().setCurrentIndex(index)
        self.adjustSize()

    def setCurrentWidget(self, w: QStackedWidget):
        old_widget = self.currentWidget()
        if old_widget is not None:
            old_widget.setSizePolicy(
                QSizePolicy.Ignored,
                QSizePolicy.Ignored
            )
        if w is not None:
            w.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Preferred
            )
            w.adjustSize()
        super().setCurrentWidget(w)
        self.adjustSize()

    def addDataclass(self, dcls: type, name: Optional[str] = None):
        """Construct and add the :class:`DataclassWidget`"""
        if name is None:
            name = dcls.__name__
        widget = DataclassWidget.fromDataclass(dcls)
        widget.setDataName(name)
        self.addWidget(widget)
        self._dataclasses[dcls] = self.indexOf(widget)
        widget.dataValueChanged.connect(self.emitDataValueChanged)

    def indexOf(self, arg__1: Union[type, QWidget]) -> int:
        """
        Returns the index of the given dataclass or ``widget``. Return
        -1 if it not exists in ``StackedDataclassWidget``.
        """
        if dataclasses.is_dataclass(arg__1):
            if not isinstance(arg__1, type):
                dcls = type(arg__1)
            else:
                dcls = arg__1
            return self._dataclasses.get(dcls, -1)
        return super().indexOf(arg__1)

    def emitDataValueChanged(self):
        try:
            self.currentWidget().dataValue()
            self.dataValueChanged.emit()
        except (TypeError, ValueError):
            pass


class TabDataclassWidget(QTabWidget):
    """
    Tabbed dataclass widgets.

    Use :meth:`addDataclass` to construct and add the widget for the
    dataclass. Use :meth:`indexOf` to get the index of the widget for
    giten dataclass.

    If data value of any dataclass widget is changed,
    :attr:`dataValueChanged` signal is emitted.s

    Examples
    ========

    >>> from dataclasses import dataclass
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from dataclass2PySide6 import TabDataclassWidget
    >>> @dataclass
    ... class DataClass1:
    ...     a: int
    >>> @dataclass
    ... class DataClass2:
    ...     b: int
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     widget = TabDataclassWidget()
    ...     widget.addDataclass(DataClass1, "data1")
    ...     widget.addDataclass(DataClass2, "data2")
    ...     geometry = widget.screen().availableGeometry()
    ...     widget.resize(geometry.width() / 3, geometry.height() / 2)
    ...     widget.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP

    """
    dataValueChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._dataclasses: Dict[type, int] = {}

    def addTab(self, widget: QWidget, *args):
        # force size policy to make ignore the size of hidden widget
        widget.setSizePolicy(
            QSizePolicy.Ignored,
            QSizePolicy.Ignored
        )
        super().addTab(widget, *args)

    def setCurrentIndex(self, index: int):
        old_widget = self.currentWidget()
        if old_widget is not None:
            old_widget.setSizePolicy(
                QSizePolicy.Ignored,
                QSizePolicy.Ignored
            )
        new_widget = self.widget(index)
        if new_widget is not None:
            new_widget.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Preferred
            )
            new_widget.adjustSize()
        super().setCurrentIndex(index)
        self.adjustSize()

    def setCurrentWidget(self, w: QStackedWidget):
        old_widget = self.currentWidget()
        if old_widget is not None:
            old_widget.setSizePolicy(
                QSizePolicy.Ignored,
                QSizePolicy.Ignored
            )
        if w is not None:
            w.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Preferred
            )
            w.adjustSize()
        super().setCurrentWidget(w)
        self.adjustSize()

    def addDataclass(self, dcls: type, label: str):
        """Construct and add the :class:`DataclassWidget`"""
        widget = DataclassWidget.fromDataclass(dcls)
        self.addTab(widget, label)
        self._dataclasses[dcls] = self.indexOf(widget)
        widget.dataValueChanged.connect(self.emitDataValueChanged)

    def indexOf(self, arg__1: Union[type, QWidget]) -> int:
        """
        Returns the index of the given dataclass or ``widget``. Return
        -1 if it not exists in ``TabDataclassWidget``.
        """
        if dataclasses.is_dataclass(arg__1):
            if not isinstance(arg__1, type):
                dcls = type(arg__1)
            else:
                dcls = arg__1
            return self._dataclasses.get(dcls, -1)
        return super().indexOf(arg__1)

    def emitDataValueChanged(self):
        try:
            self.currentWidget().dataValue()
            self.dataValueChanged.emit()
        except (TypeError, ValueError):
            pass
