# tk common color chooser dialogue
#
# this module provides an interface to the native color dialogue
# available in Tk 4.2 and newer.
#
# written by Fredrik Lundh, May 1997
#
# fixed initialcolor handling in August 1998
#

#
# options (all have default values):
#
# - initialcolor: color to mark as selected when dialog is displayed
#   (given as an RGB triplet or a Tk color string)
#
# - parent: which window to place the dialog on top of
#
# - title: dialog title
#

from tkinter.commondialog import Dialog


#
# color chooser class

class Chooser(Dialog):
    "Ask for a color"

    command = "tk_chooseColor"

    def _fixoptions(self):
        try:
            # make sure initialcolor is a tk color string
            color = self.options["initialcolor"]
            if isinstance(color, tuple):
                # assume an RGB triplet
                self.options["initialcolor"] = "#%02x%02x%02x" % color
        except KeyError:
            pass

    def _fixresult(self, widget, result):
        # result can be somethings: an empty tuple, an empty string or
        # a Tcl_Obj, so this somewhat weird check handles that
        if not result or not str(result):
            return None, None # canceled

        # to simplify application code, the color chooser returns
        # an RGB tuple together with the Tk color string
        r, g, b = widget.winfo_rgb(result)
        return (r/256, g/256, b/256), str(result)


#
# convenience stuff

def askcolor(color = None, **options):
    "Ask for a color"

    if color:
        options = options.copy()
        options["initialcolor"] = color

    return Chooser(**options).show()

套路 询问颜色(颜色=空, **选项):
    """弹出对话框供用户选择颜色.
    
    选项有两个:

    标题: 颜色对话框的标题, 默认值取决于操作系统.

    父窗口: 颜色对话框位于哪个窗口之上, 默认为主窗口.
    """
    如果 颜色:
        选项 = 选项.复制()
        选项["initialcolor"] = 颜色

    如果 '标题' 在 选项:
        选项['title'] = 选项['标题']
        删 选项['标题']

    如果 '父窗口' 在 选项:
        选项['parent'] = 选项['父窗口']
        删 选项['父窗口']

    返回 Chooser(**选项).show()


# --------------------------------------------------------------------
# test stuff

if __name__ == "__main__":
    print("color", askcolor())
