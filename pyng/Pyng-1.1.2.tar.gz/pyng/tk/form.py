#!/usr/bin/python
"""
    form.py                          Nat Goodspeed
    Copyright (C) 2017               Nat Goodspeed

NRG 2017-10-26
"""
from __future__ import absolute_import

# derived from   http://www.python-course.eu/tkinter_entry_widgets.php
# with help from http://effbot.org/tkinterbook/text.htm
try:
    # Python 3
    import tkinter as tk
except ImportError:
    # Python 2
    import Tkinter as tk
from .__init__ import center, WINDOW_TITLE, BULLET

class Canceled(Exception):
    pass

class Field(object):
    """
    Instantiate a label plus entry field on a row of the Form.
    Subclass must define the specific entry field (get_widget()) plus the
    set() and get() methods.
    """
    def __init__(self, parent, desc, init, label_width):
        # get the row number of the next empty row
        row = parent.grid_size()[1]
        lab = tk.Message(parent, width=label_width, text=desc, anchor='w')
        lab.grid(row=row, column=0, sticky='EW')
        self.widget = self.get_widget(parent)
        self.set(init)
        self.widget.grid(row=row, column=1, sticky='EW')
        # make it so the entry field(s) expand when the dialog is resized
        parent.grid_columnconfigure(1, weight=1)

    def bind(self, *args, **kwds):
        """forward a bind() command to the enclosed widget"""
        self.widget.bind(*args, **kwds)

    def set(self, data):
        # If data is None, it means blank the field. This is useful for a
        # field whose displayed/delivered value is something other than string
        # (such as int), to indicate a value that's actually missing.
        self._set("" if data is None else data)

    def validate(self):
        """
        Specific Field subclasses might override, e.g. to convert an entered
        value to int or some such. In general, call get(), massage the string
        as desired and return the value you want in the output dict -- or
        raise a relevant exception.
        """
        return self.get()

class ShortField(Field):
    """tk.Entry with appropriate set() and get() methods"""
    def get_widget(self, parent):
        return tk.Entry(parent)

    def _set(self, data):
        self.widget.delete(0, tk.END)
        self.widget.insert(0, data)

    def get(self):
        return self.widget.get()

class IntField(ShortField):
    """ShortField that delivers an int"""
    def validate(self):
        # allow field to be left empty; default to 0
        return int(self.get() or 0)

class FloatField(ShortField):
    """ShortField that delivers a float"""
    def validate(self):
        # allow field to be left empty
        return float(self.get() or 0)

class PasswordField(ShortField):
    """ShortField that hides echo characters"""
    def get_widget(self, parent):
        return tk.Entry(parent, show=BULLET)

class KeyValueField(ShortField):
    """
    ShortField that presents editable description field.
    For this Field subclass, set() accepts a pair tuple, and get() and
    validate() return a pair tuple.
    """
    def __init__(self, parent, desc, init, label_width):
        # row number of the next empty row
        row = parent.grid_size()[1]
        self.key = tk.Entry(parent)
        self.key.grid(row=row, column=0, sticky='EW')
        self.widget = self.get_widget(parent)
        self.widget.grid(row=row, column=1, sticky='EW')
        self.set(init or ("", ""))

    def set(self, data):
        key, value = data or ("", "")
        self.key.delete(0, tk.END)
        self.key.insert(0, key)
        self.widget.delete(0, tk.END)
        self.widget.insert(0, value)

    def get(self):
        return (self.key.get(), self.widget.get())

    def bind(self, *args, **kwds):
        self.key.bind(*args, **kwds)
        self.widget.bind(*args, **kwds)

class MultiLineField(Field):
    """tk.Text with appropriate set() and get() methods"""
    # When we have at least one Text field, binding <Return> is
    # contraindicated: every time we try to enter a newline in the Text field,
    # it fires the bound method!
    def bind(self, what, *args, **kwds):
        if what != "<Return>":
            self.widget.bind(what, *args, **kwds)

    def get_widget(self, parent):
        ent = tk.Text(parent)
        ent.config(height=6)
        return ent

    def _set(self, data):
        self.widget.delete(1.0, tk.END)
        self.widget.insert(tk.END, data)

    def get(self):
        return self.widget.get("1.0", tk.END)

class Message(Field):
    """
    Put a text-wrapped message spanning both columns of the Form, e.g. for an
    explanation or for an error message. For this case, 'desc' is ignored.
    """
    def __init__(self, parent, desc, init, label_width):
        self.parent = parent
        # row number of next empty row
        row = parent.grid_size()[1]
        # want to be able to update the Message text
        self.text = tk.StringVar()
        # specify width only to override Message's default behavior of trying
        # to preserve aspect ratio; leave text centered (no anchor='w')
        self.msg = tk.Message(parent, width=label_width, textvariable=self.text)
        self.msg.grid(row=row, column=0, columnspan=2, sticky='EW')
        # this is needed to let the Message adapt to the width of the Form,
        # even initially
        self.msg.bind("<Configure>",
                      lambda event: self.msg.config(width=event.width))
        self.set(init)

    def _set(self, data):
        self.text.set(data)
        ##self.parent.update()

    def get(self):
        return self.text.get()

    def bind(self, *args, **kwds):
        # no input field; suppress base-class bind() functionality
        pass

class CheckboxField(Field):
    """
    Use a Tkinter Checkbutton, but use same label/field pair as the rest.
    """
    def get_widget(self, parent):
        self.checked = tk.IntVar()
        # Checkbutton wants to present the checkbox on the left and text on
        # the right, and by default the text is centered. But to be harmonious
        # with our Form layout, use empty text so we get just the checkbox
        # itself, aligned in column 1 with the rest of our input fields.
        return tk.Checkbutton(parent, text="", variable=self.checked)

    def set(self, data):
        self.checked.set(1 if data else 0)

    def get(self):
        return self.checked.get()

class Form(tk.Tk):
    """
    Build a data-entry dialog by constructing this class, calling its add()
    method with some number of input fields and then calling finish(). This
    suspends the caller while the user ponders the dialog (Tk.mainloop()
    call). The dialog contains the requested labels and fields, plus OK and
    Cancel buttons. Once the user clicks either of those, the Form instance
    destroys itself. The finish() method returns a dict of field keys and
    user-entered values -- or an empty dict for Cancel.
    """
    def __init__(self, title, init={}, topmost=True):
        """
        title:   the title text for the dialog
        init:    a dict-like object containing initial values for fields
        topmost: whether the Form stays on top of other windows

        Any initial entries in 'init' will be used to fill fields added with
        self.add().
        """
        self.output = init.copy()

        tk.Tk.__init__(self)
        # Use the grid manager
        self.grid()
        ##self.geometry('??x??')
        self.title(title)
        # try to ensure this won't coyly hide behind other windows
        if topmost:
            try:
                self.wm_attributes("-topmost", 1)
            except Exception as err:
                # Documentation indicates that -topmost is platform-specific
                pass

        self.fields = {}
        self.set_focus_gen = self.set_focus_first_field()
        # run the generator up to the first yield
        next(self.set_focus_gen)

    def add(self, key, field_class, desc, init=None):
        """
        e.g.
        add('bday', ShortField, 'Date of Birth')
        """
        # If caller doesn't explicitly pass an init value, fetch it from
        # self.output. Passing the same dict to successive calls will
        # therefore populate the dialog with previously-entered data.
        if init is None:
            init = self.output.get(key, "")
        field = field_class(self, desc, init, 150)
        # If this is the first field with a widget, set focus there.
        self.set_focus_gen.send(field)
        self.fields[key] = field

    def set_focus_first_field(self):
        while True:
            field = (yield)
            try:
                widget = field.widget
            except AttributeError:
                # keep looping until the first field that *does* have a widget
                continue
            break
        # set focus to the first field
        widget.focus_set()
        # now just ignore all subsequent fields
        while True:
            yield

    def finish(self):
        """
        Suspends the caller until the user responds to the dialog.

        Returns empty dict for Cancel, populated dict for OK.

        The keys of the dict are the keys for the various Fields passed to
        add(). The corresponding values are taken either from the init dict
        passed to our constructor, or as overridden by the user.
        """
        for field in self.fields.values():
            field.bind('<Return>', self.OK)
            field.bind('<Escape>', self.cancel)

        self.error_message = Message(self, "", "", 150)

        # get the row number of the last empty row
        row = self.grid_size()[1]
        # Use a separate Frame for the buttons so they don't have to be
        # aligned with the labels and entry fields.
        bframe = tk.Frame(self)
        # odd use case -- but if the dialog is stretched vertically, let the
        # buttons track the bottom edge
        self.grid_rowconfigure(row, weight=1)
        bframe.grid(row=row, columnspan=2, sticky='ES')
        for column, button in enumerate(self.action_buttons(bframe)):
            # since these buttons have bframe as parent, their row and column
            # numbers are within that very local grid, unrelated to the row
            # and column numbers of the whole dialog
            button.grid(row=0, column=column, sticky='E')

        center(self)

        self.mainloop()

        return self.output

    def action_buttons(self, parent):
        """
        Override this to specify your own set of action buttons at the
        bottom-right of the Form dialog. Naturally, a custom button may engage
        a new subclass method.
        """
        return [
            tk.Button(parent, text='OK', command=self.OK),
            tk.Button(parent, text='Cancel', command=self.cancel),
            ]

    def OK(self, e=None):
        # collect data into self.output; collect errors into self.error_message
        if not self.collect():
            # if all went well (no errors), we're done
            self.destroy()

    def collect(self):
        """
        Collect data into self.output, validating each Field by calling its
        individual validate() method. Moreover, validate the combined result
        by calling Form.validate(). Collect any resulting errors into a list
        of error messages. Set self.error_message accordingly, and return that
        list. If it's empty, there were no errors: success.
        """
        errors = []

        # Update all output keys from the get() of each Field.
        for key, field in self.fields.items():
            try:
                self.output[key] = field.validate()
            except Exception as err:
                errors.append('%s: %s' % (key, err))

        # call validate() to check through self.output
        try:
            error = self.validate()
        except Exception as err:
            # unify the cases: extract the message string from the exception
            error = str(err)

        # Unless validate() (successfully) returned None, treat as an error.
        if error:
            errors.append(str(error))

        # Set error_message even when there are no errors: in that case, we
        # want to clear it.
        self.error_message.set('\n'.join(errors))
        # show caller
        return errors

    def validate(self):
        """
        Override this to examine self.output and either return a message or
        throw an exception. If it returns None, it means 'no error' and
        finish() returns. If it returns an error message or throws an
        exception, the message is displayed and the Form remains.
        """
        return None

    def cancel(self, e=None):
        # Caller can tell user hit Cancel by the empty output dict.
        self.output.clear()
        self.destroy()

def display_form(title, *fields, **kwds):
    """
    Present the user with an input form and wait. Returns a dict. If the user
    clicks Cancel, the dict is empty. If the user clicks OK, there should be a
    dict entry for each defined field (see below).

    title is the dialog title text.

    fields is any number of tuples of the form:
    (key, field_class, desc)

    where:

    key will be used to retrieve the field's value from the returned dict;

    field_class is one of ShortField, PasswordField or MultiLineField (a Field
    subclass);

    desc is the label text for that input field.

    If you pass init={some dict}, that dict will be used to populate the
    initial values of each field. Otherwise the input fields will be empty.
    Thus, you may redisplay the form dialog multiple times, passing the dict
    returned from the previous call as the init= for the next call.
    """
    # old-style keyword-only param
    init = kwds.pop("init", {})
    form = Form(title, init)
    for field_def in fields:
        form.add(*field_def)
    return form.finish()

def getpws(*tuples, **kwds):
    """
    Pass any number of (key, desc) pair tuples, where each 'desc' is the
    user-visible prompt text for one of the requested passwords. Returns a
    dict whose keys are the 'key' values from each pair, and whose values are
    the passwords entered by the user -- or raises Canceled.

    You can prepopulate the password fields by passing an init= dict with keys
    matching (a subset of) the 'key's from the pairs you pass.
    """
    result = display_form(WINDOW_TITLE,
                          *((key, PasswordField, desc) for key, desc in tuples),
                          **kwds)
    if not result:
        raise Canceled("Prompt for %s canceled" %
                       ", ".join(desc.rstrip().rstrip(':') for key, desc in tuples))
    return result

if __name__ == '__main__':
    from pprint import pprint
##  data = dict(first=True)
##  while data:
##      data.pop("first", None)
##      data = display_form("Personal Questions",
##                          ("expl", Message, "",
##                           "Please enter the requested information. "
##                           "Take your time. Do it right. Wrap the text."),
##                          ("name", ShortField, "Name"),
##                          ("age",  ShortField, "Age"),
##                          ("bbpw", PasswordField, "bitbucket password for code author"),
##                          init=data)
##      pprint(data)

    class ValidatedForm(Form):
        def __init__(self):
            Form.__init__(self, "Fill Me, Fill Me")
            self.add("expl", Message, "", "Enter all requested information.")
            self.add("name", ShortField, "Name")
            self.add("age",  IntField,   "Age")
            self.add("exp2", Message, "", "Enter platform information below.")
            self.add(0, KeyValueField, "", ("mac64", ""))
            self.add(1, KeyValueField, "", ("", ""))
            self.add("exp3", Message, "", "and now just to expand the default size")
            self.add("work", ShortField, "Occupation")
            self.add("play", ShortField, "Hobbies")
            self.add("addr", ShortField, "Address")
            self.add("wed", CheckboxField, "Married?", 1)
            self.add("kids", CheckboxField, "Dependents?")
            self.add("email", ShortField, "Email Address")
            self.tries = 0

        def validate(self):
            if self.tries < 2:
                self.tries += 1
                return "Oh noes, try %s failed!" % self.tries

    pprint(ValidatedForm().finish())
