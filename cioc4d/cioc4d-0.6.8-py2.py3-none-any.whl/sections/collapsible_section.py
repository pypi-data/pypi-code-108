
"""
Collapsible Group is a base class for each stacked section of UI 
"""

import c4d

TOGGLE_W = 100
TOGGLE_X = 11
TOGGLE_Y = 7

TOGGLE_DIST = 5
DEFAULT_TEXT = 191/255.0
COLLAPSED_COLOR = c4d.Vector(0.5, DEFAULT_TEXT, 1)
EXPANDED_COLOR = c4d.Vector(1, DEFAULT_TEXT, DEFAULT_TEXT)
DEFAULT_COLOR = c4d.Vector(DEFAULT_TEXT, DEFAULT_TEXT, DEFAULT_TEXT)

class CollapsibleSection(object):
    """
    Provide a titled collapsible section of UI.

    C4Ds own fold flag has been broken for years. This class abstracts away the
    mechanics required to expand and collapse the contained UI.

    By using this as a section base class we get other benefits, like
    consistency of look and feel, event handling, and introspection. 
    """

    @property
    def ORDER(self):
        """
        Subclasses must provide their place in the stacking order. 

        Values can be sparse: e.g. 10, 20, 30.
        """
        raise NotImplementedError

    def __init__(self, dialog, title, collapse=False, override_color=None):
        """
        Initialize the section. 

        Call the derived class build method, which places specific widgets
        inside the inner group.
        """
        self.group_id = None
        self.vis_group_id = None
        self.separator_id = None
        self.collapsed = None
        self.title = title
        self.dialog = dialog
        self._store_affectors = []

        self._collapsed_color=override_color or COLLAPSED_COLOR
        self._expanded_color=override_color or EXPANDED_COLOR

        # Build the UI
        if not self._begin_group():
            return
        self.build()
        self._end_group()

        self.collapse() if collapse else self.expand()

    def build(self):
        """
        Derived class overrides build. 

        Places widgets.
        """
        return NotImplementedError
 

    def populate_from_store(self):
        """
        Get values from the store to populate this section.

        Values may be saved from a previous session, or defaults if the session
        is new.
        """
        pass

    def save_to_store(self):
        """Called when something changes that we want to save."""
        pass


    def on_plugin_message(self, widget_id, msg):
        """
        Handle events from this plugin.
        """
        pass

    def on_core_message(self, msg_id, msg):
        """
        Handle core events from c4d.
        """
        pass

    def on_message(self, msg_id, msg):
        """
        Handle other messages from c4d.

        We detect mouse events in order to collapse/expand. If a subclass
        implements on_message(), it should be sure to call this base class
        method too. 
        """
        if msg_id == c4d.BFM_INPUT:
            self.on_mouse_click(msg)

    def _begin_group(self):
        """
        Set up the collapsible group structure.

        The outer group displays the clickable label and border. The inner group
        is hidable and contains all subclass widgets.

        TODO: convert to contextmanager
        """
        self.group_id = self.dialog.register()
        title = self.get_titled_toggle()

        # OUTER
        grp = self.dialog.GroupBegin(
            id=self.group_id,
            flags=c4d.BFH_SCALEFIT,
            title=title,
            rows=1,
            cols=1,
            groupflags=0)
        if not grp:
            return

        self.dialog.GroupBorderSpace(4, 4, 4, 4)
        self.dialog.GroupBorder(c4d.BORDER_WITH_TITLE | c4d.BORDER_ROUND)

        # must add an element here (with ID) to prevent a bug where an empty
        # rounded border grp doesn't know how to display properly
        self.separator_id = self.dialog.register()
        self.dialog.AddStaticText(self.separator_id, c4d.BFH_SCALEFIT, inith=4)

        # INNER
        self.vis_group_id = self.dialog.register()
        grp = self.dialog.GroupBegin(
            id=self.vis_group_id,
            cols=1,
            flags=c4d.BFH_SCALEFIT,
            groupflags=0)
        if not grp:
            return

        self.dialog.SetDefaultColor(
            self.vis_group_id, c4d.COLOR_TEXT,   DEFAULT_COLOR)

        return True

    def _end_group(self):
        """End the above groups."""
        self.dialog.GroupEnd()
        self.dialog.GroupEnd()

    def get_titled_toggle(self):
        """Construct label."""
        toggler = "+" if self.collapsed else "-"

        return "{} {}".format(toggler, self.title)

    def on_mouse_click(self, msg):
        """
        Determine if mouse click was on the label.

        If so, toggle collapse/expand
        """
        mousex = msg.GetInt32(c4d.BFM_INPUT_X)
        mousey = msg.GetInt32(c4d.BFM_INPUT_Y)
        group_dim = self.dialog.GetItemDim(self.group_id)
        y = (group_dim["y"]+TOGGLE_Y) - mousey
        if abs(y) > TOGGLE_DIST:
            return
        x = (group_dim["x"]+TOGGLE_X) - mousex
        if x > TOGGLE_DIST:
            return
        x = mousex - (group_dim["x"]+TOGGLE_X + TOGGLE_W)
        if x > TOGGLE_DIST:
            return
        self.toggle()

    def collapse(self):
        """
        Set section to collapsed.

        Hide inner group, but show the spacer so that the outer group has
        something to keep it from bugging out. 

        Change the color to night.
        """
        self.dialog.HideElement(self.vis_group_id, True)
        self.dialog.HideElement(self.separator_id, False)
        self.collapsed = True
        self.dialog.SetString(self.group_id, self.get_titled_toggle())
        self.dialog.SetDefaultColor(
            self.group_id, c4d.COLOR_TEXT,   self._collapsed_color)
        self.dialog.LayoutChanged(self.group_id)
        self.on_collapse()
        return self.collapsed

    def expand(self):
        """
        Set section to expanded.

        Show inner group, but hide the spacer so that it doesn't add extra
        unwanted space while group is expanded. 

        Change the color to day.
        """
        self.dialog.HideElement(self.vis_group_id, False)
        self.dialog.HideElement(self.separator_id, True)

        self.collapsed = False
        self.dialog.SetString(self.group_id, self.get_titled_toggle())
        self.dialog.SetDefaultColor(
            self.group_id, c4d.COLOR_TEXT,   self._expanded_color)
        self.dialog.LayoutChanged(self.group_id)
        self.on_expand()
        return self.collapsed

    def toggle(self):
        """Flip expand/collapsed state """
        return self.expand() if self.collapsed else self.collapse()

    def on_collapse(self):
        pass

    def on_expand(self):
        pass

    def resolve(self, expander, **kwargs):
        return {}

    def get_preview_affectors(self):
        """
        Return widget IDs that should trigger the Preview panel to update.
        """
        return []


    def set_store_affectors(self):
        """
        Save widget IDs that trigger store update.

        These will most likely be the same affectors that trigger a preview. If
        they are not, then override this method.
        """
        self._store_affectors = self.get_preview_affectors()
  
  