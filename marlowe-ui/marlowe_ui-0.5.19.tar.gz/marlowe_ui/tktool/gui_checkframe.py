import tkinter as tk

from ..contrib.bundlepmw import Pmw

import logging

logger = logging.getLogger(__name__)

from .. import layoutmode
from .. import balloonhelp

from . import codedoptionmenu


class CheckButtonFrame(tk.Frame):
    def __init__(self, master, gui, example=None):
        """setup test window,
            1. put gui frame
            2. put action buttons,
               - set_example (FrameClass.set())
               - get (FrameClass.get())
               - clear (FrameClass.clear())
               - validate (FrameClass.validate())
               - enable (FrameClass.enable())
               - disable (FrameClass.disable())
               - layoutmode (if FrameClass.layout())
                 this option is avaliable when FrameClass is derived from
                 layoutmode.LayoutModeImplement()
               - balloonhelp (if FrameClass.bind_with_balloonhelp() exists)
                 this option is available FrameClass is derived from
                 balloonhelp.BalloonHelpImplement()
        """
        tk.Frame.__init__(self, master)

        self.gui = gui

        # set default
        def set_action():
            self.gui.set(example)
        setbtn = tk.Button(self, text='set example', command=set_action)
        setbtn.pack(side=tk.LEFT, pady=2)

        # get
        def get_action():
            logger.info(self.gui.get())

        getbtn = tk.Button(self, text='get', command=get_action)
        getbtn.pack(side=tk.LEFT, pady=2)

        # get_nostatechk
        def get_nostatechk_action():
            logger.info(self.gui.get_nostatechk())

        getbtn = tk.Button(self, text='get_nostatechk', command=get_nostatechk_action)
        getbtn.pack(side=tk.LEFT, pady=2)

        # clear
        def clear_action():
            self.gui.clear()

        clearbtn = tk.Button(self, text='clear', command=clear_action)
        clearbtn.pack(side=tk.LEFT, pady=2)

        # validate
        def validate_action():
            logger.info(self.gui.validate())

        validatebtn = tk.Button(self, text='validate', command=validate_action)
        validatebtn.pack(side=tk.LEFT, pady=2)

        # enable
        def enable_action():
            self.gui.enable()
        enablebtn = tk.Button(self, text='enable', command=enable_action)
        enablebtn.pack(side=tk.LEFT, pady=2)

        # disable
        def disable_action():
            self.gui.disable()
        disablebtn = tk.Button(self, text='disable', command=disable_action)
        disablebtn.pack(side=tk.LEFT, pady=2)

        # change layoutmode
        if isinstance(self.gui, layoutmode.LayoutModeImplement):
            def layout_action(v):
                mode = layout.get()
                self.gui.layout(mode)
            layout = codedoptionmenu.CodedOptionMenu(
                self, layoutmode.modes, command=layout_action)
            tk.Label(self, text='Layout:').pack(side=tk.LEFT, padx=(2, 0), pady=2)
            layout.pack(side=tk.LEFT, padx=(0, 2), pady=2)
            layout.set(0)


def gui_checkframe(master, FrameClass, example=None):
    """setup test window,
        1. put gui frame
        2. put action buttons,
           - set_example (FrameClass.set())
           - get (FrameClass.get())
           - clear (FrameClass.clear())
           - validate (FrameClass.validate())
           - enable (FrameClass.enable())
           - disable (FrameClass.disable())
           - layoutmode (if FrameClass.layout())
             this option is avaliable when FrameClass is derived from
             layoutmode.LayoutModeImplement()
           - balloonhelp (if FrameClass.bind_with_balloonhelp() exists)
             this option is available FrameClass is derived from
             balloonhelp.BalloonHelpImplement()
    """

    gui = FrameClass(master)
    gui.pack(side=tk.TOP)

    buttonframe = CheckButtonFrame(master, gui, example)
    buttonframe.pack(side=tk.TOP)

    # balloon help
    if isinstance(gui, balloonhelp.BalloonHelpImplement):
        balloon = Pmw.Balloon(master)
        gui.bind_with_balloonhelp(balloon)
