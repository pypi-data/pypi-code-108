import bfit.backend.colors as colors

# =========================================================================== #
def on_entry_click(event, entry, text):
    """Vanish grey text on click"""
    if entry.get() == text:
        entry.delete(0, "end") # delete all the text in the entry
        entry.insert(0, '') #Insert blank for user input
        entry.config(foreground = colors.entry_white)

# =========================================================================== #
def on_focusout(event, entry, text):
    """Set grey text for boxes on exit"""
    if entry.get() == '':
        entry.insert(0, text)
        entry.config(foreground = colors.entry_grey)
    else:
        entry.config(foreground = colors.entry_white)
