from inspect import getfile
from os.path import join
from tkinter import Tk
from tkinter import ttk as Widgets

Widgets.Frame()


class Window(Tk):
    def __init__(self, Caption=None, Size=None, Position=None, MinSize=None, MaxSize=None, Resizable=None, Center=True,
                 LoadThemes=True):
        Tk.__init__(self)
        self.SetDisplay(False)
        if Caption is not None:
            self.SetCaption(Caption)
        if Size is not None:
            self.SetSize(Size)
        if Position is not None:
            self.SetPosition(Position)
        if MinSize is not None:
            self.SetMinSize(MinSize)
        if MaxSize is not None:
            self.SetMaxSize(MaxSize)
        if Resizable is not None:
            self.SetResizable(Resizable)
        if Center:
            self.Center()
        if LoadThemes:
            self.LoadThemes()
        self.SetDisplay(True)

    def SetCaption(self, Caption):
        self.title(Caption)

    def SetSize(self, Size):
        self.geometry('{}x{}'.format(*Size))
        self.update()

    def SetPosition(self, Position):
        self.geometry('+{}+{}'.format(*Position))
        self.update()

    def SetMinSize(self, MinSize):
        self.minsize(*MinSize)

    def SetMaxSize(self, MaxSize):
        self.maxsize(*MaxSize)

    def SetResizable(self, Resizable):
        self.resizable(*Resizable)

    def SetDisplay(self, Display):
        if Display:
            self.deiconify()
        else:
            self.withdraw()

    def SetTheme(self, Group, Type):
        Type = Type.lower()
        Group = Group.upper()
        if Group == 'AZURE':
            self.tk.call('set_azure_theme', Type)
        if Group == 'FOREST':
            self.tk.call('set_forest_theme', Type)
        elif Group == 'SUN VALLEY':
            self.tk.call('set_sun_valley_theme', Type)

    def LoadThemes(self):
        CurrentPath = getfile(Window)
        CurrentPath = '\\'.join(CurrentPath.split('\\')[0:-1])
        AzureThemePath = join(CurrentPath, 'AzureTheme', 'Azure.tcl')
        ForestThemePath = join(CurrentPath, 'ForestTheme', 'Forest.tcl')
        SunValleyThemePath = join(CurrentPath, 'SunValleyTheme', 'SunValley.tcl')
        self.tk.call('source', AzureThemePath)
        self.tk.call('source', ForestThemePath)
        self.tk.call('source', SunValleyThemePath)

    def Center(self):
        Width, Height = self.winfo_width(), self.winfo_height()
        ScreenWidth, ScreenHeight = self.winfo_screenwidth(), self.winfo_screenheight()
        self.SetPosition((((ScreenWidth - Width) // 2), (ScreenHeight - Height) // 2))

    @staticmethod
    def SetFrame(Frame):
        Frame.pack(fill='both', expand=True)
