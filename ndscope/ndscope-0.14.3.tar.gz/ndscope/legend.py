from qtpy.QtCore import Qt, QRectF
from qtpy.QtGui import QFont, QColor, QBrush, QPen
from qtpy.QtWidgets import QGraphicsLinearLayout, QGraphicsRectItem, QGraphicsSimpleTextItem
import pyqtgraph as pg


class Legend(pg.GraphicsWidget, pg.GraphicsWidgetAnchor):
    """
    This class is a replacement for the pyqtgraph LegendItem class.
    It uses layouts to manage the spacing in response to changes in the font size.
    It also changes the sample trace image from a line to a rectangle for higher visibility.
    """
    def __init__(self):
        super().__init__()
        self.setFlag(self.ItemIgnoresTransformations)
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.setLayout(self.layout)
        self.item_list = []
        self.font = QFont()
        self.text_color = QColor('gray')
        self.offset = (10, 10)

    def addItem(self, item, name):
        """Adds an entry to the legend."""
        label = RectTextItem()
        color = item.opts['pen'].color()
        label.setRectColor(QColor(color))
        label.setText(name)
        label.setTextColor(self.text_color)
        label.setFont(self.font)
        self.item_list.append((item, label))
        self.layout.addItem(label)

    def removeItem(self, item):
        """Removes an entry from the legend."""
        for sample, label in self.item_list:
            if sample is item or label.text() == item:
                self.item_list.remove((sample, label))
                self.layout.removeItem(label)

    def setFont(self, font):
        """Sets the font of the text of the entries in the legend."""
        self.font = font
        for sample, label in self.item_list:
            label.setFont(self.font)

    def setTextColor(self, color):
        """Sets the color of the text of the entries in the legend."""
        self.text_color = color
        for sample, label in self.item_list:
            label.setTextColor(self.text_color)

    def paint(self, painter, option, widget):
        """Paints the rectangle behind the legend."""
        painter.setPen(QPen(QColor(128, 128, 128, 128)))
        painter.setBrush(QBrush(QColor(128, 128, 128, 32)))
        painter.drawRect(self.boundingRect())

    def setOffset(self, offset):
        """Sets the offset position relative to the parent."""
        self.offset = offset
        offset = pg.Point(self.offset)
        anchorx = 1 if offset[0] <= 0 else 0
        anchory = 1 if offset[1] <= 0 else 0
        anchor = (anchorx, anchory)
        self.anchor(itemPos=anchor, parentPos=anchor, offset=offset)

    def setParentItem(self, parent):
        """Sets the parent."""
        ret = pg.GraphicsWidget.setParentItem(self, parent)
        if self.offset is not None:
            offset = pg.Point(self.offset)
            anchorx = 1 if offset[0] <= 0 else 0
            anchory = 1 if offset[1] <= 0 else 0
            anchor = (anchorx, anchory)
            self.anchor(itemPos=anchor, parentPos=anchor, offset=offset)
        return ret

    def hoverEvent(self, ev):
        ev.acceptDrags(Qt.LeftButton)

    def mouseDragEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            ev.accept()
            dpos = ev.pos() - ev.lastPos()
            self.autoAnchor(self.pos() + dpos)


class RectTextItem(pg.GraphicsWidget):
    """
    This class represents an entry in the legend.
    It holds a rectangle the color of the trace next to a text string label for the trace."
    """
    def __init__(self):
        super().__init__()
        self.rect_item = RectItem()
        self.simple_text_item = SimpleTextItem()
        self.layout = QGraphicsLinearLayout()
        self.layout.addItem(self.rect_item)
        self.layout.setAlignment(self.rect_item, Qt.AlignVCenter)
        self.layout.addItem(self.simple_text_item)
        self.layout.setAlignment(self.simple_text_item, Qt.AlignVCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    # If the simple text item emitted a signal each time its size changed, this 
    # signal could be connected to a slot to update the size of the rect item, 
    # and then the setText and setFont methods could be removed.
    def setText(self, text):
        """Sets the text."""
        self.simple_text_item.setText(text)
        self.rect_item.setRect(QRectF(0, 0, self.simple_text_item.height(), self.simple_text_item.height()))

    def setFont(self, font):
        """Sets the font of the text."""
        self.simple_text_item.setFont(font)
        self.rect_item.setRect(QRectF(0, 0, self.simple_text_item.height(), self.simple_text_item.height()))

    # Convenience functions

    def setRectColor(self, color):
        """Sets the color of the rectangle."""
        self.rect_item.setColor(color)

    def text(self):
        """Returns the text."""
        return self.simple_text_item.text()

    def setTextColor(self, color):
        """Sets the color of the text."""
        self.simple_text_item.setColor(color)


class RectItem(pg.GraphicsWidget):
    """This class represents the rectangle in an entry in the legend."""
    def __init__(self):
        super().__init__()
        self.rect_item = QGraphicsRectItem()
        self.setGraphicsItem(self.rect_item)
        self.rect_item.setBrush(QBrush(Qt.SolidPattern))

    def sizeHint(self, which, constraint):
        return self.rect_item.boundingRect().size()

    def setGeometry(self, rect):
        self.rect_item.setPos(rect.topLeft())

    # Convenience functions

    def setRect(self, rect):
        """Sets the size of the rectangle."""
        self.rect_item.setRect(rect)
        self.updateGeometry()

    def setColor(self, color):
        """Sets the color of the rectangle."""
        pen = self.rect_item.pen()
        pen.setColor(color)
        self.rect_item.setPen(pen)
        brush = self.rect_item.brush()
        brush.setColor(color)
        self.rect_item.setBrush(brush)


class SimpleTextItem(pg.GraphicsWidget):
    """This class represents the text in an entry in the legend."""
    def __init__(self):
        super().__init__()
        self.simple_text_item = QGraphicsSimpleTextItem()
        self.setGraphicsItem(self.simple_text_item)
        self.simple_text_item.setBrush(QBrush(Qt.SolidPattern))

    def sizeHint(self, which, constraint):
        return self.simple_text_item.sceneBoundingRect().size()

    def setGeometry(self, rect):
        self.simple_text_item.setPos(rect.topLeft())

    def height(self):
        """Returns the height of the text."""
        return self.simple_text_item.sceneBoundingRect().height()

    # Convenience functions

    def setText(self, text):
        """Sets the text."""
        self.simple_text_item.setText(text)
        self.updateGeometry()

    def text(self):
        """Returns the text."""
        return self.simple_text_item.text()

    def setFont(self, font):
        """Sets the font of the text."""
        self.simple_text_item.setFont(font)
        self.updateGeometry()

    def setColor(self, color):
        """Sets the color of the text."""
        pen = self.simple_text_item.pen()
        pen.setColor(color)
        self.simple_text_item.setPen(pen)
        brush = self.simple_text_item.brush()
        brush.setColor(color)
        self.simple_text_item.setBrush(brush)
