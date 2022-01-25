"""This module contains the GUI for settings"""
import os
import webbrowser
from functools import partial
from tkinter import Tk, Frame, RIGHT
from tkinter import ttk
from tkinter.colorchooser import askcolor
from tkinter.filedialog import askdirectory

from talk1.talk1 import talk

from Magic import usergui, theme, history, indexer, export_import, popups, tkinterlib
from Magic.tkinterlib import TButton, TLabel, TLabelFrame


def setting_page(event = "", username: str = "", state: bool = True) -> None:
    """GUI for the settings page"""

    def usr_page(event = "") -> None:
        """To call the add user page GUI"""
        talk("Please add a new user")
        usergui.user_page()

    settings = Tk()
    bg_colour = theme.read_theme()[0]
    tkinterlib.tkinter_initialise(settings, x = 500, y = 300, top = 0)

    # ...title bar...
    # for title bar refer https://stackoverflow.com/questions/23836000/can-i-change-the-title-bar-in-tkinter
    def move_window(event) -> None:
        """To move the title bar according with the button motion"""
        settings.geometry(f"+{event.x_root}+{event.y_root}")

    title_bar = Frame(settings, bg = bg_colour, bd = 4)
    title_bar.pack(fill = "x")
    tab = ttk.Notebook(settings)
    tab.pack(fill = "both")
    # different frames for tabs
    settings_tab, theme_tab, history_tab, about_tab, indexer_tab, contact_tab = Frame(settings, bg = bg_colour), Frame(settings, bg = bg_colour), Frame(
        settings, bg = bg_colour), Frame(settings, bg = bg_colour), Frame(settings, bg = bg_colour), Frame(settings, bg = bg_colour)

    # General Tab
    TButton(settings_tab, text = "Add User", command = usr_page).pack(fill = "x")
    TButton(settings_tab, text = "Delete User", command = usergui.deleteuser).pack(fill = "x")
    TButton(settings_tab, text = "Reset Elsa", command = popups.resetelsapopup).pack(fill = "x")
    #  Import/Export Tab
    TButton(settings_tab, text = "Export Data", command = export_import.export).pack(fill = "x")
    TButton(settings_tab, text = "Import Data", command = export_import.import_data).pack(fill = "x")

    # Theme tab
    def new_background_colour(event = "") -> None:
        """To add the background colour"""
        color = askcolor()
        bg_colour, text_color, button_colour = theme.read_theme()
        if color[1] is not None: theme.theme_writer(color[1], text_color, button_colour)

    def font_colour(event = "") -> None:
        """To add the font colour"""
        color = askcolor()
        bg_colour, text_color, button_colour = theme.read_theme()
        if color[1] is not None: theme.theme_writer(bg_colour, color[1], button_colour)

    def new_button_colour(event = "") -> None:
        """To add the button colour"""
        color = askcolor()
        bg_colour, text_color, button_colour = theme.read_theme()
        if color[1] is not None: theme.theme_writer(bg_colour, text_color, color[1])

    TButton(theme_tab, text = "Background Colour", command = new_background_colour).pack(fill = "x")
    TButton(theme_tab, text = "Font Colour", command = font_colour).pack(fill = "x")
    TButton(theme_tab, text = "Button color", command = new_button_colour).pack(fil = "x")

    # History Tab
    TButton(history_tab, text = "Show History", command = partial(history.user_read, username = username)).pack(fill = "x")
    TButton(history_tab, text = "Clear History", command = partial(history.clear_history, name = username)).pack(fill = "x")
    # About Tab
    version, ab = TLabelFrame(about_tab, text = "Version"), TLabelFrame(about_tab, text = "Created By")
    TLabel(version, text = "Elsa 1.1").pack()
    version.pack()
    ab.pack()
    # Name labels
    TLabel(ab, text = "Austin Bert").pack()
    TLabel(ab, text = "Elizabeth Jaison").pack()
    TLabel(ab, text = "George Rahul").pack()

    # Indexer Tab
    def folderlabels() -> None:
        """To display the additional folders to be indexed in the GUI"""
        try:
            folders = indexer.read_indexer_folders()
            for folder in folders:
                foldername = folder.split("/")[-1] if len(folder.split("/")[-1]) != 0 else folder.split("/")[0]
                TLabel(indexer_tab, text = foldername).pack()
        except: pass

    def folderchooser() -> None:
        """To choose a new folder that should be indexed"""
        folderpath = askdirectory()
        indexer.add_indexer_folders(path = folderpath)
        settings.destroy()
        setting_page()

    TButton(indexer_tab, text = "Add a folder", command = folderchooser).pack()

    # ....Reset/indexerpathlib.....
    def resetindexercache() -> None:
        """To reset the indexed data and rebuild it"""
        talk("Reseted the cache")
        os.remove((os.getcwd() + "/resources/ indexer.elsa"))
        print("'indexer.elsa' is removed")
        # files will be re - indexed when settings page is quit

    TButton(indexer_tab, text = "Reset Indexer Cache", command = resetindexercache).pack()
    TLabel(indexer_tab, text = "Additional Indexed folders").pack()
    folderlabels()
    # Contact Us Tab
    TButton(contact_tab, text = "Contact Us", command = lambda: webbrowser.open("https://github.com/georgerahul24")).pack()
    TButton(contact_tab, text = "Report a bug", command = lambda: webbrowser.open("https://github.com/georgerahul24/Viraver1.1/issues/new")).pack()
    # Packing the tabs
    settings_tab.pack(fill = "both")
    theme_tab.pack(fill = "both")
    history_tab.pack(fill = "both")
    about_tab.pack(fill = "both")
    indexer_tab.pack(fill = "both")
    tab.add(settings_tab, text = "Settings")
    tab.add(theme_tab, text = "Theme")
    tab.add(history_tab, text = "History")
    tab.add(about_tab, text = "About")
    tab.add(indexer_tab, text = "Indexer")
    tab.add(contact_tab, text = "Contact Us")

    # Close Button
    def quitsettings(event = "") -> None:
        """To quit the settings page"""
        settings.destroy()
        indexer.index_files()
        tkinterlib.reset_colors()

    TButton(title_bar, text = "x", command = quitsettings).pack(side = RIGHT)
    # Moving Titlebar
    title_bar.bind("<B1-Motion>", move_window)
    settings.mainloop()
