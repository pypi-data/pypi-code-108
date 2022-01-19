"""
Components/DropdownItem
=======================

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/dropdown-item.png
    :align: center

Usage
-----

.. code-block:: python

    from kivy.lang import Builder

    from kivymd.app import MDApp

    KV = '''
    Screen

        MDDropDownItem:
            id: drop_item
            pos_hint: {'center_x': .5, 'center_y': .5}
            text: 'Item'
            on_release: self.set_item("New Item")
    '''


    class Test(MDApp):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.screen = Builder.load_string(KV)

        def build(self):
            return self.screen


    Test().run()

.. seealso::

    `Work with the class MDDropdownMenu see here <https://kivymd.readthedocs.io/en/latest/components/menu/index.html#center-position>`_
"""

__all__ = ("MDDropDownItem",)

import os
from typing import NoReturn

from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget

from kivymd import uix_path
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.boxlayout import MDBoxLayout

with open(
    os.path.join(uix_path, "dropdownitem", "dropdownitem.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class _Triangle(ThemableBehavior, Widget):
    pass


class MDDropDownItem(
    ThemableBehavior,
    FakeRectangularElevationBehavior,
    ButtonBehavior,
    MDBoxLayout,
):
    text = StringProperty()
    """
    Text item.

    :attr:`text` is a :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    current_item = StringProperty()
    """
    Current name item.

    :attr:`current_item` is a :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    font_size = NumericProperty("16sp")
    """
    Item font size.

    :attr:`font_size` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `'16sp'`.
    """

    def on_text(self, instance_drop_down_item, text_item: str) -> NoReturn:
        self.ids.label_item.text = text_item

    def set_item(self, name_item: str) -> NoReturn:
        """Sets new text for an item."""

        self.ids.label_item.text = name_item
        self.current_item = name_item
