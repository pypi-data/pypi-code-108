import tkinter as tk
import tkinter.scrolledtext
import tkinter.simpledialog

import io
import copy

from .tktool import codedoptionmenu

from . import vpar_moliere

import logging
logger = logging.getLogger(__name__)

param_default = {
    'type': 'None',  # ['None', 'Moliere']
    'moliere_param': vpar_moliere.param_default
    }

param_example = {
    'type': 'Moliere',
    'moliere_param': vpar_moliere.param_example
    }


# param['moliere_param']['BPAR'] contains tuple key, so
# this should be tranlated for json output
def param_to_json(native_param):
    """translate native parameter to json assecptable form"""
    d = copy.deepcopy(native_param)
    if 'moliere_param' in d:
        d['moliere_param'] = vpar_moliere.param_to_json(d['moliere_param'])
    return d


def param_from_json(json_param):
    """translate json acceptable data to native form"""
    d = copy.deepcopy(json_param)
    if 'moliere_param' in d:
        d['moliere_param'] = vpar_moliere.param_from_json(d['moliere_param'])
    return d


class MoliereDialog(tkinter.simpledialog.Dialog):
    def __init__(self, master, param, title=None):
        self.param = param
        tkinter.simpledialog.Dialog.__init__(self, master, title)

    def body(self, master):
        self.moliere = vpar_moliere.VparMoliere(master)
        self.moliere.pack()
        self.moliere.set(self.param)

    def apply(self):
        self.result = self.moliere.get()


class Vpar(tk.Frame):
    paramframe_gridparams = {
        'row': 1,
        'column': 0,
        'columnspan': 2,
        'sticky': tk.NSEW
        }

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # tk.Label(self, text='&VPAR:', justify=tk.RIGHT).grid(row=0, column=0, sticky=tk.W) # noQA

        # options
        options = [
            ('None', 'no customization'),
            ('Moliere', 'Moliere model')]
        self.option = codedoptionmenu.CodedOptionMenu(self, options, command=self.onselect)
        self.option.config(anchor=tk.W, width=20)
        self.option.grid(row=0, column=0, sticky=tk.EW)

        # configure button
        self.configure = tk.Button(self, text='configure')
        self.configure.grid(row=0, column=1)

        # make option column expandable
        self.grid_columnconfigure(0, weight=1)

        # summary textbox
        self.summary = tkinter.scrolledtext.ScrolledText(
            self,
            bg='gray', width=1, height=1)
        self.summary.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.summary.config(state=tk.DISABLED)

        # initialize contents
        self.param = None
        self.clear()

    def update_summarytext(self):
        self.summary.config(state=tk.NORMAL)
        self.summary.delete(1.0, tk.END)

        tbuf = io.StringIO()
        if self.param['type'] == 'None':
            tbuf.write('# no params')
        elif self.param['type'] == 'Moliere':
            # format BPAR parameter
            bpar = self.param['moliere_param']['BPAR']
            tbuf.write('# moliere BPAR, print only non-zero value\n')
            for ij in sorted(bpar.keys()):
                if bpar[ij] != 0.0:
                    tbuf.write('BPAR{0} = {1:f}\n'.format(ij, bpar[ij]))

        self.summary.insert(tk.END, tbuf.getvalue())
        self.summary.config(state=tk.DISABLED)

    def onselect(self, val):
        if val == 'no customization':
            self.configure.config(state=tk.DISABLED)
            self.param['type'] = self.option.get()
        elif val == 'Moliere model':
            self.configure.config(state=tk.NORMAL)
            self.configure.config(command=self.config_moliere)
            self.param['type'] = self.option.get()
        self.update_summarytext()

    def config_moliere(self):
        # popup dialog
        param = self.param.get('moliere_param', param_default['moliere_param'])
        dialog = MoliereDialog(
            self, param,
            title='VPAR for Moliere Interatomic Model')

        if dialog.result:
            self.param['moliere_param'] = dialog.result
            self.update_summarytext()

    def set(self, d):
        self.param = copy.deepcopy(param_default)
        if 'type' in d:
            self.param['type'] = d['type']
        if 'moliere_param' in d:
            self.param['moliere_param'] = copy.deepcopy(d['moliere_param'])
        # update option and force call onselect
        self.option.set(self.param['type'])
        self.onselect(self.option.v_to_text[self.param['type']])
        # update summary
        self.update_summarytext()

    def clear(self):
        self.set(param_default)

    def get(self):
        return self.param
