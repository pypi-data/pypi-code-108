""" extention of tk.OptionMenu which takes of pairs of (value, text)
"""

import tkinter as tk


class CodedOptionMenu(tk.OptionMenu):
    """ extention of tk.OptionMenu which takes of pairs of (value, text)
    """
    def __init__(self, master, options=[], **kw):
        '''
        options is list of (value, text), where
            text is shown in widget, value is use for set() and get()
        '''
        self.cv = tk.StringVar(master)

        tk.OptionMenu.__init__(self, master, self.cv, self.cv.get(), **kw)
        # if kw includes 'command' pass it
        self.set_new_option(options, command=kw.get('command', None))

    def set(self, v):
        self.cv.set(self.v_to_text[v])

    def get(self):
        return self.text_to_v[self.cv.get()]

    def get_nostatechk(self):
        return self.get()

    def clear(self):
        pass

    def setup_optionparam(self, options):
        """initialize self.v_to_text, self.text_to_v, and self.texts
        """
        self.v_to_text = {}
        self.text_to_v = {}
        self.texts = []
        for v, t in options:
            self.v_to_text[v] = t
            self.text_to_v[t] = v
            self.texts.append(t)

    def set_new_option(self, options, command=None):
        """delete current options and set new options. variable does not change"""
        self['menu'].delete(0, tk.END)
        # create new textoption and translation tables
        self.setup_optionparam(options)

        # register self.text as menu, see source of Tkinter.OptionMenu.__init__
        for v in self.texts:
            self['menu'].add_command(
                label=v,
                command=tk._setit(self.cv, v, command))

    def validate(self):
        return None

    def enable(self):
        self.config(state=tk.NORMAL)

    def disable(self):
        self.config(state=tk.DISABLED)

    def is_disabled(self):
        return self.cget('state') == tk.DISABLED


def _demo():
    app = tk.Tk()

    code_opt_menu = CodedOptionMenu(
            app,
            options=[
                (1, '1:one'),
                (2, '2:two')])
    # set default value
    code_opt_menu.set(2)

    code_opt_menu.pack()

    # get button
    def on_getbutton():
        print(code_opt_menu.get())

    getbutton = tk.Button(app, text='get', command=on_getbutton)
    getbutton.pack()

    app.mainloop()


if __name__ == '__main__':
    _demo()
