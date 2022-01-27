from packaging import version
from abc import abstractmethod
from typing import (List, Any, Optional)

import bokeh
import bokeh.models
import bokeh.layouts
from bokeh.layouts import column

from shyft.dashboard.base import constants
from shyft.dashboard.base.app import LayoutComponents, Widget
from shyft.dashboard.base.ports import (States, Sender, StatePorts, Receiver)


class SelectorViewBase(Widget):
    """
    The select view base class can be used to define custom selector views for the selector presenter.

    (For an custom select view see class SelectTwoView)
    """

    def __init__(self, logger=None) -> None:
        super().__init__(logger=logger)
        self.send_selection = Sender(parent=self, name='send selection of view', signal_type=List[str])
        self.receive_options = Receiver(parent=self, name='receive options to show in view', func=self._receive_options,
                                        signal_type=List[str])
        self.receive_selection = Receiver(parent=self, name='receive selection to show in view',
                                          func=self._receive_selection, signal_type=List[str])
        self.state_ports = StatePorts(parent=self, _receive_state=self._receive_state)
        self.state = States.ACTIVE

    @property
    @abstractmethod
    def layout_components(self) -> LayoutComponents:
        """
        Property to return all layout.dom components of an visualisation app
        such that they can be arranged by the parent layout obj as
        desired.

        Returns
        -------
        dict
            layout_components as:
                    {'widgets': [],
                     'figures': []}

        """
        pass

    @abstractmethod
    def _receive_options(self, new_options: List[str]) -> None:
        """
        List of new options to view

        Parameters
        ----------
        new_options
            List of new options
        """
        pass

    @abstractmethod
    def _receive_selection(self, new_values: List[str]) -> None:
        """
        Set new selection to show in the view view!
        Without triggering the callback, i.e. send selection!

        Parameters
        ----------
        new_values:
            List of new values(s)
        """
        pass

    @abstractmethod
    def _receive_state(self, state: States) -> None:
        """
        Receive state, this should be able to handle all states defiened by States!

        Parameters
        ----------
        state:
            state variable
        """
        pass

    @property
    @abstractmethod
    def width(self) -> int:
        pass

    @width.setter
    @abstractmethod
    def width(self, width: int) -> None:
        pass

    @property
    @abstractmethod
    def layout(self) -> bokeh.models.LayoutDOM:
        pass


def calculate_layout_width(width, padding):
    if width is None or padding is None:
        return None

    return width + padding


class TwoSelect(SelectorViewBase):

    def __init__(self,
                 *,
                 title: Optional[str] = None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 text_height: Optional[int] = None,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger: Optional = None) -> None:
        super().__init__(logger=logger)

        self._default = ''
        self._title = title
        self._options: List[str] = []
        text_height = text_height or constants.text_height
        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode
        layout_width = calculate_layout_width(width, padding)

        # Keep title sizing mode fixed so it stays "connected" as expected to the first Select-field.
        # This mimics the behaviour of setting a title on the TwoSelect without experiencing
        # different Select-fields sizes as a side-effect.
        self._two_select_title = bokeh.models.Div(text=title, height=text_height)

        self._select1 = bokeh.models.Select(width=width, height=height)
        self._select1.disabled = False
        self._select1.on_change('value', self._on_change_select1)
        self._update_select1 = self.update_value_factory(self._select1, 'value')

        self._select2 = bokeh.models.Select(width=width, height=height)
        self._select2.disabled = False
        self._select2.on_change('value', self._on_change_select2)
        self._update_select2 = self.update_value_factory(self._select2, 'value')

        columns = [self._select1, self._select2]

        if title:
            columns.insert(0, self._two_select_title)

        self._layout = bokeh.layouts.column(children=columns,
                                            sizing_mode=sizing_mode, width=layout_width, height=height)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} '{self._title}'"

    @property
    def layout(self) -> bokeh.models.LayoutDOM:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self._select1, self._select2],
                'figures': []}

    def _on_change_select1(self, attr, old, new) -> None:
        # update options of the other selector except default value
        self._select2.options = [o for o in self._options if o != new or o == self._default]
        self.send_selection([new, self._select2.value])

    def _on_change_select2(self, attr, old, new) -> None:
        # update options of the other selector except default value
        self._select1.options = [o for o in self._options if o != new or o == self._default]
        # send selection to callback
        self.send_selection([self._select1.value, new])

    def _receive_options(self, new_options: List[str]) -> None:
        """
        List of new options to view

        Parameters
        ----------
        new_options:
            List of new options
        """
        self._default = new_options[0]
        self._options = new_options
        self._select1.options = new_options.copy()
        self._select2.options = new_options.copy()

    def _receive_selection(self, new_values: List[str]) -> None:
        """
        Set new values of the view!
        Without triggering the callback, i.e. send selection!

        Parameters
        ----------
        new_values:
            List of new values(s)
        """
        if len(new_values) == 0:
            new_values = [self._default, self._default]
        if len(new_values) == 1:
            new_values = [new_values[0], self._default]
        if new_values[0] == new_values[1]:
            new_values = [new_values[0], self._default]
        self._update_select1(new_values[0])
        self._select2.options = [o for o in self._options if o != new_values[0] or o == self._default]
        self._update_select2(new_values[1])
        self._select1.options = [o for o in self._options if o != new_values[1] or o == self._default]

    def _receive_state(self, state: States) -> None:
        """
        Receive state, this should be able to handle all states defiened by States!

        Parameters
        ----------
        state:
            state variable
        """
        if state != self.state:
            self.state = state
            self.state_ports.send_state(state)
        if state == States.LOADING:
            self.disabled = True
            self._two_select_title.update(text=': '.join([self._title, 'loading ...']))
        elif state == States.PROCESSING:
            self.disabled = True
            self._two_select_title.update(text=': '.join([self._title, 'processing ...']))
        elif state == States.INVALID:
            self.disabled = False
            self._two_select_title.update(text=': '.join([self._title, 'invalid']))
        elif state == States.READY:
            self.disabled = False
            self._two_select_title.update(text=self._title)
        elif state == States.ACTIVE:
            self.disabled = False
            self._two_select_title.update(text=self._title)
        elif state == States.DEACTIVE:
            self.disabled = True
            self._two_select_title.update(text=self._title)
        else:
            self.logger.error(f"ERROR: {self.__class__.__name__} - unknown state '{state}' received")

    @property
    def disabled(self) -> bool:
        return self._select1.disabled and self._select2.disabled

    @disabled.setter
    def disabled(self, disabled: bool) -> None:
        self._select1.disabled = disabled
        self._select2.disabled = disabled

    @property
    def width(self) -> int:
        return self._select1.width

    @width.setter
    def width(self, width: int) -> None:
        self._select1.width = width
        self._select2.width = width


class FilterMultiSelect(SelectorViewBase):

    def __init__(self,
                 *,
                 title: str,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 sizing_mode: str = None,
                 size: int = 10,
                 padding: int = None,
                 filter_after_enter_is_pressed: bool = False,
                 case_sensitive: bool = False,
                 logger: Optional = None) -> None:
        super().__init__(logger=logger)

        self.case_sensitive = case_sensitive

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode
        layout_width = calculate_layout_width(width, padding)

        bkwargs = dict(width=width, height=height, size=size, sizing_mode=sizing_mode)
        self.send_event_message = Sender(parent=self, name="TS selector event messenger", signal_type=str)

        self._multi_select = bokeh.models.MultiSelect(**bkwargs)
        self._multi_select.on_change('value', self._on_change_select)
        self._update_select = self.update_value_factory(self._multi_select, 'value')

        self._filter_input = bokeh.models.TextInput(title=title, name="filter_input", width=width)
        value = 'value'
        if not filter_after_enter_is_pressed:
            value = 'value_input'

        self._filter_input.on_change(value, self._filter_input_change)

        self._title = title
        self._current_filter = None

        self._layout = bokeh.layouts.column(self._filter_input,
                                            self._multi_select,
                                            height=height,
                                            width=layout_width)

    @property
    def layout(self) -> bokeh.layouts.LayoutDOM:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self._filter_input, self._multi_select],
                'figures': []}

    def _on_change_select(self, attr, old, new) -> None:
        self.send_selection(new)

    def _filter_input_change(self, attr, old, new) -> None:

        self._current_filter = new
        self._filtered_options = self._filter_options()

        self._multi_select.options = self._filtered_options.copy()

    def _filter_options(self) -> List[str]:

        if self._current_filter is None:
            return self._options
        if self.case_sensitive:
            return [option for option in self._options if self._current_filter in option]
        else:
            return [option for option in self._options if self._current_filter.lower() in option.lower()]

    def _receive_options(self, new_options: List[str]) -> None:
        """
        List of new options to view

        Parameters
        ----------
        new_options:
            List of new options
        """
        self._default = new_options[0]
        self._options = new_options
        self._filtered_options = self._filter_options()
        self._multi_select.options = self._filtered_options.copy()

    def _receive_selection(self, new_values: List[str]) -> None:
        """
        Set new values of the view!
        Without triggering the callback, i.e. send selection!

        Parameters
        ----------
        new_values:
            List of new values(s)
        """
        self._update_select(new_values)

    def _receive_state(self, state: States) -> None:
        """
        Receive state, this should be able to handle all states defined by States!

        Parameters
        ----------
        state:
            state variable
        """
        if state != self.state:
            self.state = state
            self.state_ports.send_state(state)
        if state == States.LOADING:
            self.disabled = True
            self._filter_input.update(title=': '.join([self._title, 'loading ...']))
        elif state == States.PROCESSING:
            self.disabled = True
            self._filter_input.update(title=': '.join([self._title, 'processing ...']))
        elif state == States.INVALID:
            self.disabled = False
            self._filter_input.update(title=': '.join([self._title, 'invalid']))
        elif state == States.READY:
            self.disabled = False
            self._filter_input.update(title=self._title)
        elif state == States.ACTIVE:
            self.disabled = False
            self._filter_input.update(title=self._title)
        elif state == States.DEACTIVE:
            self.disabled = True
            self._filter_input.update(title=self._title)
        else:
            self.logger.error(f"ERROR: {self.__class__.__name__} - unknown state '{state}' received")

    @property
    def disabled(self) -> bool:
        return self._multi_select.disabled and self._filter_input.disabled

    @disabled.setter
    def disabled(self, disabled: bool) -> None:
        self._multi_select.disabled = disabled
        self._filter_input.disabled = disabled

    @property
    def width(self) -> int:
        return self._multi_select.width

    @width.setter
    def width(self, width: int) -> None:
        self._multi_select.width = width
        self._filter_input.width = width


class BokehViewBase(SelectorViewBase):

    def __init__(self,
                 *,
                 title: str,
                 bokeh_model: bokeh.models,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger: Optional = None,
                 title_model: Optional[Any] = None,
                 title_attribute: Optional[str] = None,
                 show_state_title: bool = True,
                 **bkwargs) -> None:
        super().__init__(logger=logger)

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        bkwargs.update(dict(width=width, height=height, sizing_mode=sizing_mode))
        self._bokeh_view = bokeh_model(**bkwargs)
        self._title_model = title_model or self._bokeh_view
        self._title_attribute = title_attribute or 'title'
        self._bokeh_view.disabled = False
        self._layout = bokeh.layouts.column(self._bokeh_view,
                                            width=calculate_layout_width(width, padding), sizing_mode=sizing_mode)
        self.state: States = States.ACTIVE
        self._default: str = ''
        self._title: str = title or ''
        self._title_model.update(**{self._title_attribute: self._title})
        self._show_state_title = show_state_title

    @property
    def layout(self) -> bokeh.layouts.LayoutDOM:
        return self._layout

    def __repr__(self) -> str:
        return f"{self._bokeh_view.__class__.__name__} '{self._title}'"

    def _receive_state(self, state: States) -> None:
        """
        Receive state, this should be able to handle all states defiened by States!

        Parameters
        ----------
        state:
            state variable
        """
        if state != self.state:
            self.state = state
            self.state_ports.send_state(state)
        if state == States.LOADING:
            self.disabled = True
            if self._show_state_title:
                self._title_model.update(**{self._title_attribute: ': '.join([self._title, 'loading ...'])})
        elif state == States.PROCESSING:
            self.disabled = True
            if self._show_state_title:
                self._title_model.update(**{self._title_attribute: ': '.join([self._title, 'processing ...'])})
        elif state == States.INVALID:
            self.disabled = False
            if self._show_state_title:
                self._title_model.update(**{self._title_attribute: ': '.join([self._title, 'invalid'])})
        elif state == States.READY:
            self.disabled = False
            if self._show_state_title:
                self._title_model.update(**{self._title_attribute: self._title})
        elif state == States.ACTIVE:
            self.disabled = False
            if self._show_state_title:
                self._title_model.update(**{self._title_attribute: self._title})
        elif state == States.DEACTIVE:
            self.disabled = True
            if self._show_state_title:
                self._title_model.update(**{self._title_attribute: self._title})
        else:
            self.logger.error(f"ERROR: {self.__class__.__name__} - unknown state '{state}' received")

    @property
    def disabled(self) -> bool:
        return self._bokeh_view.disabled

    @disabled.setter
    def disabled(self, disabled: bool) -> None:
        self._bokeh_view.disabled = disabled

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self._bokeh_view],
                'figures': []}

    @property
    def width(self) -> int:
        return self._bokeh_view.width

    @width.setter
    def width(self, width: int) -> None:
        self._bokeh_view.width = width

    @abstractmethod
    def _receive_options(self, new_options: List[str]) -> None:
        pass

    @abstractmethod
    def _receive_selection(self, new_values: List[str]) -> None:
        pass


class Select(BokehViewBase):

    def __init__(self,
                 *,
                 title: Optional[str] = None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger: Optional = None,
                 show_state_title: bool = True,
                 **bkwargs) -> None:

        super().__init__(title=title, bokeh_model=bokeh.models.Select, width=width, height=height,
                         padding=padding, sizing_mode=sizing_mode,
                         logger=logger, show_state_title=show_state_title, **bkwargs)

        self._bokeh_view.on_change('value', self._on_change_select)
        self._update_select = self.update_value_factory(self._bokeh_view, 'value')

    def _on_change_select(self, attr, old, new) -> None:
        self.send_selection([new])

    def _receive_options(self, new_options: List[str]) -> None:
        """
        List of new options to view

        Parameters
        ----------
        new_options:
            List of new options
        """
        self._default = new_options[0]
        self._bokeh_view.options = new_options.copy()

    def _receive_selection(self, new_values: List[str]) -> None:
        """
        Set new values of the view!
        Without triggering the callback, i.e. send selection!

        Parameters
        ----------
        new_values:
            List of new values(s)
        """
        if len(new_values) == 0:
            self._update_select(self._default)
        else:
            self._update_select(new_values[0])


class MultiSelect(BokehViewBase):

    def __init__(self,
                 *,
                 title: str,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger: Optional = None,
                 show_state_title: bool = True,
                 **bkwargs) -> None:
        super().__init__(title=title, bokeh_model=bokeh.models.MultiSelect, height=height, width=width, padding=padding,
                         sizing_mode=sizing_mode, logger=logger, show_state_title=show_state_title, **bkwargs)

        self._bokeh_view.on_change('value', self._on_change_select)
        self._update_select = self.update_value_factory(self._bokeh_view, 'value')

    def _on_change_select(self, attr, old, new) -> None:
        # bokeh returns list of str
        self.send_selection(new)

    def _receive_options(self, new_options: List[str]) -> None:
        """
        List of new options to view

        Parameters
        ----------
        new_options:
            List of new options
        """
        self._default = new_options[0]
        self._bokeh_view.options = new_options.copy()

    def _receive_selection(self, new_values: List[str]) -> None:
        """
        Set new values of the view!
        Without triggering the callback, i.e. send selection!

        Parameters
        ----------
        new_values:
            List of new values(s)
        """
        if len(new_values) == 0:
            self._update_select([self._default])
        else:
            self._update_select(new_values)


class AutocompleteInput(BokehViewBase):

    def __init__(self,
                 *,
                 title: str,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger: Optional = None,
                 placeholder: Optional[str] = None,
                 keep_text_value: bool = True,
                 show_state_title: bool = True,
                 **bkwargs) -> None:
        bkwargs.update(dict(placeholder=placeholder or ''))

        super().__init__(title=title, bokeh_model=bokeh.models.AutocompleteInput, width=width, height=height,
                         padding=padding, sizing_mode=sizing_mode, logger=logger, show_state_title=show_state_title,
                         **bkwargs)

        self.keep_text_value = keep_text_value
        self.options: List[str] = []
        self._bokeh_view.on_change('value', self._on_change_select)
        self._update_select = self.update_value_factory(self._bokeh_view, 'value')
        self._bokeh_view.placeholder = placeholder or ''

    def _on_change_select(self, attr, old, new) -> None:
        temp_text_value = new
        # n_test = [n.lower() for n in new.split()]
        # if all(n in self.options for n in n_test):
        n_test = [option for option in self.options if new in option.lower()]
        if new in self.options:
            self.send_selection([new])
        elif n_test:
            self.send_selection(n_test)
        elif self.keep_text_value:
            self._update_select(temp_text_value)
        else:
            self._update_select('')

    def _receive_options(self, new_options: List[str]) -> None:
        """
        List of new options to view

        Parameters
        ----------
        new_options:
            List of new options
        """
        self._default = new_options[0]
        # self.options = [o.lower() for o in new_options[1:]]
        self.options = [o for o in new_options[1:]]
        self._bokeh_view.completions = new_options[1:]

    def _receive_selection(self, new_values: List[str]) -> None:
        """
        Set new values of the view!
        Without triggering the callback, i.e. send selection!

        Parameters
        ----------
        new_values:
            List of new values(s)
        """
        if len(new_values) == 0:
            self._update_select(self._default)
        else:
            self._update_select(new_values[0])


class GroupBokehViewBase(BokehViewBase):

    def __init__(self, *,
                 title: str,
                 bokeh_model,
                 width: Optional[int]=None,
                 height: Optional[int]=None,
                 text_height: Optional[int] = None,
                 padding: Optional[int]=None,
                 sizing_mode: Optional[str]=None,
                 logger: Optional=None,
                 show_state_title: bool=True,
                 **bkwargs) -> None:
        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode
        text_height = text_height or constants.text_height
        layout_width = calculate_layout_width(width, padding)
        self._title_div = bokeh.models.Div(text=title or "", height=text_height)

        super().__init__(title=title, bokeh_model=bokeh_model, width=width, height=height,
                         logger=logger, sizing_mode=sizing_mode, title_model=self._title_div, title_attribute='text',
                         show_state_title=show_state_title, **bkwargs)

        self.options: List[str] = []
        self._update_select = self.update_value_factory(self._bokeh_view, 'active')

        columns = [self._bokeh_view]

        if title:
            columns.insert(0, self._title_div)

        self._layout = bokeh.layouts.column(columns, width=layout_width,
                                            height=height, sizing_mode=sizing_mode)

    @property
    def layout(self) -> bokeh.layouts.LayoutDOM:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self._title_div, self._bokeh_view],
                'figures': []}

    def _receive_options(self, new_options: List[str]) -> None:
        """
        List of new options to view

        Parameters
        ----------
        new_options
        """
        self._default = new_options[0]
        self.options = new_options[1:]
        self._bokeh_view.labels = new_options[1:]

    @abstractmethod
    def _receive_selection(self, new_values: List[str]) -> None:
        pass


class RadioGroupBokehViewBase(GroupBokehViewBase):

    def __init__(self,
                 *,
                 title: Optional[str]=None,
                 bokeh_model,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 padding: Optional[int] = None,
                 text_height: Optional[int] = None,
                 sizing_mode: Optional[str]=None,
                 logger: Optional=None,
                 show_state_title=True,
                 **bkwargs) -> None:

        super().__init__(title=title, bokeh_model=bokeh_model, width=width, height=height, text_height=text_height,
                         padding=padding, sizing_mode=sizing_mode,
                         logger=logger, show_state_title=show_state_title, **bkwargs)
        self._bokeh_view.on_change('active', self._on_change_select)

    def _receive_selection(self, new_values: List[str]) -> None:
        """
        Set new values of the view!
        Without triggering the callback, i.e. send selection!

        Parameters
        ----------
        new_values: List of new values(s)
        """
        if len(new_values) == 0 or new_values[0] not in self.options:
            self._update_select(None)
        else:
            self._update_select(self.options.index(new_values[0]))

    def _on_change_select(self, attr, old, new) -> None:
        # bokeh returns int
        if new in range(len(self.options)):
            self.send_selection([self.options[new]])


class RadioButtonGroup(RadioGroupBokehViewBase):
    def __init__(self, *,
                 title: Optional[str]=None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 text_height: Optional[int] = None,
                 padding: Optional[int]=None,
                 sizing_mode: Optional[str]=None,
                 logger=None,
                 **bkwargs) -> None:
        bokeh_model = bokeh.models.RadioButtonGroup

        super().__init__(title=title, width=width, height=height, text_height=text_height,
                         bokeh_model=bokeh_model, padding=padding,
                         sizing_mode=sizing_mode, logger=logger, **bkwargs)


class RadioGroup(RadioGroupBokehViewBase):
    def __init__(self, *,
                 title: Optional[str]=None,
                 width: Optional[int]=None,
                 height: Optional[int]=None,
                 text_height: Optional[int]=None,
                 padding: Optional[int]=None,
                 sizing_mode: Optional[str]=None,
                 logger=None,
                 **bkwargs) -> None:
        bokeh_model = bokeh.models.RadioGroup

        super().__init__(title=title, width=width, height=height, text_height=text_height, bokeh_model=bokeh_model,
                         padding=padding, sizing_mode=sizing_mode, logger=logger, **bkwargs)


class CheckboxGroupBokehViewBase(GroupBokehViewBase):

    def __init__(self, *,
                 title: Optional[str]=None,
                 bokeh_model,
                 width: Optional[int]=None,
                 height: Optional[int]=None,
                 text_height: Optional[int] = None,
                 padding: Optional[int]=None,
                 sizing_mode: Optional[str]=None,
                 logger: Optional=None,
                 show_state_title: bool=True,
                 **bkwargs) -> None:
        super().__init__(title=title, bokeh_model=bokeh_model, width=width, height=height,
                         text_height=text_height, padding=padding, sizing_mode=sizing_mode,
                         logger=logger, show_state_title=show_state_title, **bkwargs)
        self._bokeh_view.on_change('active', self._on_change_select)

    def _receive_selection(self, new_values: List[str]) -> None:
        """
        Set new values of the view!
        Without triggering the callback, i.e. send selection!

        Parameters
        ----------
        new_values: List of new values(s)
        """
        if len(new_values) == 0:
            if version.parse(bokeh.__version__) < version.Version("2.3.0"):
                self._update_select(None)
            else:
                self._update_select([])
        else:
            active = [self.options.index(v) for v in new_values if v in self.options]
            self._update_select(active)

    def _on_change_select(self, attr, old, new) -> None:
        # bokeh returns List[int]
        if new and max(new) in range(len(self.options)):
            selected = [self.options[i] for i in new]
            self.send_selection(selected)
        else:
            self.send_selection([])


class CheckboxGroup(CheckboxGroupBokehViewBase):
    def __init__(self, *,
                 title: Optional[str]=None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 text_height: Optional[int] = None,
                 logger=None,
                 **bkwargs) -> None:
        bokeh_model = bokeh.models.CheckboxGroup
        super().__init__(title=title, width=width, height=height,
                         text_height=text_height, bokeh_model=bokeh_model, logger=logger, **bkwargs)


class CheckboxButtonGroup(CheckboxGroupBokehViewBase):
    def __init__(self, *,
                 title: Optional[str] = None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 text_height: Optional[int] = None,
                 logger=None,
                 **bkwargs) -> None:
        bokeh_model = bokeh.models.CheckboxButtonGroup
        super().__init__(title=title,  width=width, height=height,
                         text_height=text_height, bokeh_model=bokeh_model, height_policy='min', logger=logger, **bkwargs)


class TextInput(Widget):
    """
    A text input widget to get a text input and send it onward via a port.

    The TextInput widget reads a string from the user, which then will be passed to the TextInputPresenter via the
    send_text_input port.
    """
    def __init__(self,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 padding: Optional[int] = None,
                 title: str = "Text input",
                 sizing_mode: Optional[str] = None,
                 logger: Optional = None,
                 **kwargs) -> None:
        """
        Constructor.

        :param width: The width of the widget.
        :param height: The height of the widget.
        :param title: The title of the widget.
        :param padding: Padding.
        :param sizing_mode: Sizing mode (options: "fixed", "stretch_both", "scale_width", "scale_height", "scale_both").
        :param logger: A logger
        :param kwargs:
        """
        super().__init__(logger=logger)

        sizing_mode = sizing_mode or constants.sizing_mode
        padding = padding or constants.widget_padding

        kwargs['title'] = title
        kwargs['width'] = width
        kwargs['height'] = height
        kwargs['value'] = ''
        self.text_input = bokeh.models.TextInput(**kwargs)
        self.text_input.on_change('value', self.on_change)
        self._layout = column(self.text_input, width=calculate_layout_width(width, padding), height=height, sizing_mode=sizing_mode)
        self.send_text_input = Sender(parent=self, name='send text input', signal_type=str)
        self.state_port = StatePorts(parent=self, _receive_state=self._receive_state)
        self.state = States.ACTIVE

    @property
    def layout(self) -> bokeh.models.LayoutDOM:
        """
        The layout of the widget.
        :return: self._layout
        """
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        """
        Returns the components contained in the layout.
        :return: Dict of components (widgets and figures)
        """
        return {'widgets': [self.text_input], 'figures': []}

    def on_change(self, attr, old, new):
        """
        Sends input value (a string) with the connection port (self.send_text_input).

        :param attr: a sting ('value')
        :param old: the previous string
        :param new: the new string
        """
        self.send_text_input(new)

    def _receive_state(self, state: States) -> None:
        """
        Receives a state.

        :param state: a State object
        """
        if state == self.state:
            return
        if state == States.ACTIVE:
            self.state = state
        elif state == States.DEACTIVE:
            self.state = state
            self.state_port.send_state(state)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)
