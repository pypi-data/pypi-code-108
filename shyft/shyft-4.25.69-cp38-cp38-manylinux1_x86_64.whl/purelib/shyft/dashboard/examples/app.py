from bokeh.models import Toggle, LayoutDOM

from shyft.dashboard.base.app import LayoutComponents, Widget

"""
Test to exemplify self.update_value_factory of Widget base class
"""


class MyApp(Widget):

    def __init__(self):
        super().__init__()
        # bokeh layout dom, widget
        self.toggle_button = Toggle(label='My toggle button')
        # add callback to toggel.active attribute
        self.toggle_button.on_click(self.on_click_toggle)
        # create update value factory which does not trigger the callback
        self.set_toggle_state = self.update_value_factory(self.toggle_button, 'active')

    @property
    def layout(self) -> LayoutDOM:
        return self.toggle_button

    @property
    def layout_components(self) -> LayoutComponents:
        """
        Returns
        =======
        dict layout_components as:
                    {'widgets': [],
                     'figures': []}
        """
        return {'widgets': [self.toggle_button], 'figures': []}

    @staticmethod
    def on_click_toggle(new):
        if new:
            print("'Toggle activated'\n")
        else:
            print("'Toggle not activated'\n")


#Test the app
my_app = MyApp()
print("\nactivate the toggle (mimik web interface), should print out 'Toggle activated':")
my_app.toggle_button.active = True

print("\ndeactivate toggle with value factory, should print out nothing, because callback is triggered")
my_app.set_toggle_state(False)

print("\nactivate toggle with value factory, should print out nothing, because callback is triggered")
my_app.set_toggle_state(True)

print("\ndeactivate the toggle (mimik web interface), should print out 'Toggle not activated'")
my_app.toggle_button.active = False
