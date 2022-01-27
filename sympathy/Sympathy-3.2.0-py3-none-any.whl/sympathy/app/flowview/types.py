# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from typing import Type

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

from .. import signals
from .. import user_commands
from .. import flow
from .. import themes
from . import grid


class BaseHoverHighlighter(QtCore.QObject):
    """
    An interface for all highlighter_cls used in HighlightableElementViews.
    """

    highlight_on = QtCore.Signal()
    highlight_off = QtCore.Signal()

    def __init__(self, element_view: 'HighlightableElementViewInterface'):
        super().__init__()
        self._element_view = element_view
        # TODO: not used really today, but can be used, for example, to
        #  enable/disable highlighting globally as a setting.
        self._enabled = True
        self._highlighted = False

    def init(self):
        self._element_view.setAcceptHoverEvents(True)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, state):
        self._enabled = state
        self._element_view.setAcceptHoverEvents(self._enabled)

    @property
    def highlighted(self):
        return self._highlighted

    @highlighted.setter
    def highlighted(self, state):
        self._highlighted = state
        if state and self.enabled:
            self.highlight_on.emit()
        else:
            self.highlight_off.emit()


class PropertyAnimationHoverHighlighter(BaseHoverHighlighter):

    def __init__(self, element_view: 'HighlightableElementViewInterface'):
        super().__init__(element_view)
        self._init_highlight_state_machine()

    def _init_highlight_state_machine(self):
        # We use a state machine for highlighting the port when the mouse
        # passes over
        self._state_machine = QtCore.QStateMachine()
        self._normal_state = QtCore.QState(self._state_machine)
        self._highlighted_state = QtCore.QState(self._state_machine)

        # The Normal to Highlighted state transition
        self._normal_to_highlight = self._normal_state.addTransition(
            self.highlight_on, self._highlighted_state)
        self._anim_to_highlight = self._normal_to_highlight_state()
        self._normal_to_highlight.addAnimation(self._anim_to_highlight)
        self._highlighted_state.entered.connect(
            self._anim_to_highlight.start)

        # The Highlighted back to Normal state transition
        self._highlight_to_normal = self._highlighted_state.addTransition(
            self.highlight_off, self._normal_state)
        self._anim_to_normal = self._highlight_to_normal_state_animation()
        self._highlight_to_normal.addAnimation(self._anim_to_normal)
        self._normal_state.entered.connect(self._anim_to_normal.start)

        self._state_machine.setInitialState(self._normal_state)
        self._state_machine.start()

    def _highlight_to_normal_state_animation(self):
        animation = QtCore.QPropertyAnimation(self._element_view, b'scale')
        return animation

    def _normal_to_highlight_state(self):
        animation = QtCore.QPropertyAnimation(self._element_view, b'scale')
        return animation


class ScaleAnimationHoverHighlighter(PropertyAnimationHoverHighlighter):

    def _highlight_to_normal_state_animation(self):
        animation = QtCore.QPropertyAnimation(self._element_view, b'scale')
        animation.setDuration(125)
        curve_scale = QtCore.QEasingCurve(QtCore.QEasingCurve.OutBack)
        curve_scale.setOvershoot(4.0)
        animation.setEasingCurve(curve_scale)
        animation.setEndValue(1.0)
        return animation

    def _normal_to_highlight_state(self):
        animation = QtCore.QPropertyAnimation(self._element_view, b'scale')
        animation.setDuration(125)
        curve_scale = QtCore.QEasingCurve(QtCore.QEasingCurve.OutBack)
        curve_scale.setOvershoot(4.0)
        animation.setEasingCurve(curve_scale)
        animation.setEndValue(1.5)
        return animation


class GraphicsEffectHoverHighlighter(BaseHoverHighlighter):

    def __init__(self, element_view: 'HighlightableElementViewInterface'):
        super().__init__(element_view)
        self._effect = QtWidgets.QGraphicsColorizeEffect()
        theme = themes.get_active_theme()
        self._effect.setColor(theme.connection_highlight_color)
        self._effect.setStrength(0.5)
        self._effect.setEnabled(False)

    def init(self):
        super().init()
        self._element_view.setGraphicsEffect(self._effect)

        self.highlight_on.connect(self._set_effect_enabled)
        self.highlight_off.connect(self._set_effect_disabled)

    def _set_effect_enabled(self):
        self._effect.setEnabled(True)

    def _set_effect_disabled(self):
        self._effect.setEnabled(False)


class BorderHoverHighlighter(BaseHoverHighlighter):

    def __init__(self, element_view: 'HighlightableElementViewInterface'):
        super().__init__(element_view)
        self._highlight_layer = self._element_view._highlight_layer

    def init(self):
        super().init()
        self.highlight_on.connect(self._set_effect_enabled)
        self.highlight_off.connect(self._set_effect_disabled)

    def _set_effect_enabled(self):
        self._highlight_layer.setVisible(True)

    def _set_effect_disabled(self):
        self._highlight_layer.setVisible(False)


class ElementViewInterface(object):
    """An interface for all views of flow elements."""

    def __init__(self, model, *args, **kwargs):
        self._model = model
        self._signals = signals.SignalHandler()
        super().__init__(*args, **kwargs)

    @property
    def model(self):
        """flow.* model corresponding to the view."""
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    def remove(self):
        """Remove the view from the scene."""
        self._signals.disconnect_all(self._model)


class HighlightableElementViewInterface(ElementViewInterface):
    hover_highlighter_cls: BaseHoverHighlighter = BaseHoverHighlighter

    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self._hover_highlighter = None

    def _init_highlighter(self):
        self.set_hover_highlighter()
        self._hover_highlighter.init()

    def set_hover_highlighter(
            self, highlighter_cls: Type[BaseHoverHighlighter] = None):

        if highlighter_cls is None:
            highlighter_cls = self.hover_highlighter_cls
        self._hover_highlighter = highlighter_cls(element_view=self)

    def hoverEnterEvent(self, event):
        if (self._hover_highlighter is not None
                    and self._hover_within_bounding_rect(event)):
                self._hover_highlighter.highlighted = True

    def _hover_within_bounding_rect(self, event):
        return self.boundingRect().contains(event.pos())

    def hoverMoveEvent(self, event):
        if self._hover_highlighter is not None:
            if self._hover_within_bounding_rect(event):
                self._hover_highlighter.highlighted = True
            else:
                self._hover_highlighter.highlighted = False

    def hoverLeaveEvent(self, event):
        if self._hover_highlighter is not None:
            self._hover_highlighter.highlighted = False


class MovableElementViewInterface(HighlightableElementViewInterface,
                                  QtWidgets.QGraphicsObject):
    """Interface for all views of flow elements that can be independently moved
    around.
    """

    cut_requested = QtCore.Signal(ElementViewInterface)
    copy_requested = QtCore.Signal(ElementViewInterface)
    delete_requested = QtCore.Signal(ElementViewInterface)
    mouse_pressed = QtCore.Signal()
    mouse_released = QtCore.Signal()

    hover_highlighter_cls = BorderHoverHighlighter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init()
        self.__init_actions()
        self._init_highlighter()
        self._init_move_state_machine()

    def __init(self):
        self._old_position = QtCore.QPointF()
        size = self._model.size
        self._bounding_rect = QtCore.QRectF(0, 0, size.width(), size.height())
        self.set_position(self._model.position)

        self._outline = QtGui.QPainterPath()
        self._selection_layer = SelectionLayer(
            outline=self._outline, parent=self)
        self._selection_layer.setVisible(False)
        self._highlight_layer = SelectionLayer(
            outline=self._outline,
            options={"z-value": 11,
                     "border-color": "border_color",
                     "brush-color": "border_color",
                     "brush-alpha": 50},
            parent=self)
        self._highlight_layer.setVisible(False)

        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)

        self._signals.connect(
            self._model,
            self._model.position_changed[QtCore.QPointF],
            self.set_position)

    def __init_actions(self):
        theme = themes.get_active_theme()
        self._copy_action = self._create_action(
            'Copy', self._copy_requested, icon=theme.copy)
        self._cut_action = self._create_action(
            'Cut', self._cut_requested, icon=theme.cut)
        self._delete_action = self._create_action(
            'Delete', self._delete_requested, icon=theme.delete)
        self._show_info_action = self._create_action(
            'Properties', self._show_info_requested)

    def _create_action(self, text, slot, icon=None):
        action = QtWidgets.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(icon))
        action.triggered.connect(slot)
        return action

    def _init_move_state_machine(self):
        self._move_state_machine = QtCore.QStateMachine(self)
        self._state_nonmoving = QtCore.QState(self._move_state_machine)
        self._state_moving = QtCore.QState(self._move_state_machine)
        self._state_nonmoving.addTransition(
            self.mouse_pressed, self._state_moving)
        self._state_moving.addTransition(
            self.mouse_released, self._state_nonmoving)
        self._move_state_machine.setInitialState(self._state_nonmoving)
        self._move_state_machine.start()

        self._state_moving.entered.connect(self._start_move)
        self._state_moving.exited.connect(self._finish_move)

    def _copy_requested(self):
        self.copy_requested.emit(self)

    def _cut_requested(self):
        self.cut_requested.emit(self)

    def _delete_requested(self):
        self.delete_requested.emit(self)

    def position(self):
        return self.pos()

    @QtCore.Slot(QtCore.QPointF)
    def set_position(self, pos):
        self.setPos(pos)

    @QtCore.Slot()
    def _start_move(self):
        if len(self.scene().selectedItems()) > 1 and self.isSelected():
            for item in self.scene().selectedItems():
                if isinstance(item, MovableElementViewInterface):
                    item.start_move_individual()
        else:
            self.start_move_individual()

    @QtCore.Slot()
    def _finish_move(self):
        if self._old_position == self.position():
            return

        cmds = []
        for item in self.scene().selectedItems():
            if isinstance(item, MovableElementViewInterface):
                cmds.append(item.finish_move_individual())
        self._model.flow.undo_stack().push(
            user_commands.MacroCommand(cmds, text='Moving group'))

    def _set_bounding_rect(self, rect):
        self.prepareGeometryChange()
        self._selection_layer.set_bounding_rect(rect)
        self._bounding_rect = rect

    def boundingRect(self):
        return self._bounding_rect

    def start_move_individual(self):
        self._old_position = self.position()

    def finish_move_individual(self):
        return user_commands.MoveElementCommand(
            self._model, self._old_position, self.position())

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            self._selection_layer.setVisible(value)
        elif change == QtWidgets.QGraphicsItem.ItemPositionChange:
            return grid.instance().snap_to_grid(value)
        elif (change == QtWidgets.QGraphicsItem.ItemPositionHasChanged and
              value != self.position()):
            cmd = user_commands.MoveElementCommand(
                self._model, self._model.position, value)
            self._model.flow.undo_stack().push(cmd)
            return value
        return super().itemChange(change, value)

    def set_this_z(self):
        """Implement in subclass if ordering is wanted (when moving objects).
        It shall set z for itself and its subelements (like ports) so that
        they are on top of everything when dragged.
        """
        pass

    def set_other_z(self):
        """Implement in subclass if ordering is wanted (when moving objects).
        It shall set z for itself and its subelements so that it is on top
        of everything when selected, except the item which the cursor is on.
        """
        pass

    def reset_z(self):
        """Implement in subclass if ordering is wanted (when moving objects).
        It shall set z for itself and its subelements to its default value.
        """
        pass

    def _set_selected_z(self):
        self._reset_all_z()
        for item in self.scene().selectedItems():
            if isinstance(item, MovableElementViewInterface):
                item.set_other_z()

    def _reset_all_z(self):
        for item in self.scene().items():
            if isinstance(item, MovableElementViewInterface):
                item.reset_z()

    def mousePressEvent(self, event):
        self._reset_all_z()
        self._set_selected_z()
        self.set_this_z()
        self.mouse_pressed.emit()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.mouse_released.emit()
        super().mouseReleaseEvent(event)

    @QtCore.Slot()
    def _show_info_requested(self):
        raise NotImplementedError('Not implemented for interface')

    def set_cursor(self, cursor=None):
        self.scene().flow_view().set_item_cursor(cursor)

    def remove(self):
        self.set_cursor(None)
        super().remove()


class SelectionLayer(QtWidgets.QGraphicsItem):
    """The blue layer that is painted on top of items when they are
    selected.
    """

    def __init__(self, outline, options: dict = None, parent=None):
        super().__init__(parent=parent)

        if options is None:
            options = {}

        self._outline = outline
        self.setZValue(options.get('z-value', 10))
        self.prepareGeometryChange()
        self._bounding_rect = parent.boundingRect()
        theme = themes.get_active_theme()

        border_width = options.get("border-with", 3.0)
        border_color = getattr(
            theme, options.get("border-color", "selection_color"))
        self._pen = QtGui.QPen(border_color, border_width)
        brush_color = getattr(
            theme, options.get("brush-color", "selection_color"))
        brush_color = QtGui.QColor(brush_color)
        brush_color.setAlpha(options.get("brush-alpha", 100))
        self._brush = QtGui.QBrush(brush_color)

    def set_outline(self, outline):
        self._outline = outline

    def set_bounding_rect(self, rect):
        self.prepareGeometryChange()
        self._bounding_rect = rect

    def boundingRect(self):
        return self._bounding_rect

    def paint(self, painter, options, widget=None):
        painter.save()
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawPath(self._outline)
        painter.restore()


def filter_nodes(element_list):
    """Helper for finding ElementViewInterface's whose models are nodes."""
    return [
        element for element in element_list
        if flow.Type.is_port_manager(element)]


def filter_nodes_to_model(element_list):
    return [
        element.model for element in element_list
        if element.model.type in flow.Type.main_types]


def filter_elements_to_model(element_list):
    return [
        element.model for element in element_list
        if element.model.type in (
            flow.Type.Node, flow.Type.FlowInput, flow.Type.FlowOutput,
            flow.Type.Flow, flow.Type.Connection)]


def filter_element_views(element_list):
    """Helper for finding GraphicItems's that are ElementViewInterface's."""
    return [element for element in element_list
            if isinstance(element, ElementViewInterface)]


def filter_element_views_to_model(element_list):
    return [
        element.model for element in element_list
        if isinstance(element, ElementViewInterface)]


def get_label(text):
    label = QtWidgets.QLabel(text)
    label.setTextInteractionFlags(
        QtCore.Qt.TextSelectableByMouse | QtCore.Qt.TextSelectableByKeyboard)
    return label
