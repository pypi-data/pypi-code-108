import tkinter
from tkinter.ttk import Combobox
from traceback import format_exc


class AutocompleteCombobox(Combobox):
        def __init__(self, source_tablename=None, default_value=None, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.all_lists = []
                self.list_changed = False
                self.start_list = []
                self.default_value = default_value
                self.source_tablename = source_tablename
                if default_value:
                        self.set_default_value()

        def get_source_tablename(self):
                return self.source_tablename

        def set_default_value(self, *args, **kwargs):
                if self.default_value != None:
                        self.set(self.default_value)

        def get(self, no_default=False, *args, **kwargs):
                """ Если включен режим no_default, будет возвращаться None, если значение Comobobox остался по умолчанию """
                value =  super(AutocompleteCombobox, self).get()
                if no_default and value == self.default_value:
                        return None
                else:
                        return value

        def set_completion_list(self, completion_list):
                """Use our completion list as our drop down selection menu, arrows move through menu."""
                self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
                self.start_list = self._completion_list
                self._hits = []
                self._hit_index = 0
                self.position = 0
                self.bind('<Any-KeyRelease>', self.handle_keyrelease)
                self['values'] = self._completion_list  # Setup our popup menu

        def set_completion_list_demo(self, completion_list):
                """Use our completion list as our drop down selection menu, arrows move through menu."""
                self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
                #self.bind('<Any-KeyRelease>', self.handle_keyrelease)
                self.start_list = self._completion_list
                self['values'] = self._completion_list  # Setup our popup menu

        def autocomplete(self, delta=0):
                """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
                if delta: # need to delete selection otherwise we would fix the current position
                        self.delete(self.position, tkinter.END)
                        print('delta')
                else: # set position to end so selection starts where textentry ended
                        self.position = len(self.get())
                # collect hits
                _hits = []
                for element in self._completion_list:
                        if element.lower().startswith(self.get().lower()): # Match case insensitively
                                _hits.append(element)
                if not self.list_changed:
                        self.start_list = self._completion_list
                        self.list_changed = True
                self.all_lists.append(self._completion_list)
                if len(_hits) > 0:
                        self.set_completion_list_demo(_hits)
                # if we have a new hit list, keep this in mind
                if _hits != self._hits:
                        self._hit_index = 0
                        self._hits=_hits
                # only allow cycling if we are in a known hit list
                if _hits == self._hits and self._hits:
                        self._hit_index = (self._hit_index + delta) % len(self._hits)
                # now finally perform the auto completion
                if self._hits:
                        self.delete(0,tkinter.END)
                        print('hits-', self._hits[self._hit_index])
                        self.insert(0,self._hits[self._hit_index])
                        self.select_range(self.position,tkinter.END)
                        print('hits')

        def set_start_list(self):
                self.set_completion_list_demo(self.start_list)

        def handle_keyrelease(self, event):
                """event handler for the keyrelease event on this widget"""
                if event.keysym == "BackSpace":
                        self.delete(self.index(tkinter.INSERT), tkinter.END)
                        self.position = self.index(tkinter.END)
                        print('back')
                        print('all_lists', self.all_lists)
                        try:
                                #print(self._completion_list)
                                self.set_completion_list_demo(self.all_lists.pop(-1))
                        except IndexError:
                                self.set_start_list()
                                print('trying pop from empty list')
                                print(format_exc())
                if event.keysym == "Left":
                        if self.position < self.index(tkinter.END): # delete the selection
                                self.delete(self.position, tkinter.END)
                        else:
                                self.position = self.position-1 # delete one character
                                self.delete(self.position, tkinter.END)
                        print('here contact')
                if event.keysym == "Right":
                        self.position = self.index(tkinter.END) # go to end (no selection)
                if event.keysym == '??' or len(event.keysym) == 1:
                        self.autocomplete()
                # No need for up/down, we'll jump to the popup
                # list at the position of the autocompletion


def test(test_list):
        """Run a mini application to test the AutocompleteEntry Widget."""
        root = tkinter.Tk(className='AutocompleteCombobox')

        combo = AutocompleteCombobox(root)
        combo.set_completion_list(test_list)
        combo.pack()
        combo.focus_set()
        # I used a tiling WM with no controls, added a shortcut to quit
        root.bind('<Control-Q>', lambda event=None: root.destroy())
        root.bind('<Control-q>', lambda event=None: root.destroy())
        root.mainloop()

if __name__ == '__main__':
        test_list = ('АБВ', 'ВБС', 'Альянс групп', 'Юпитер', 'Озон', 'Тестовая организация', 'Soda', 'Strawberry' )
        test(test_list)
