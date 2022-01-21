import sys
import json
import os.path
import subprocess
import re
import shlex
import copy

import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox

from .contrib.bundlepmw import Pmw

from . import tktool
from . import guidata
from . import gui_root as _root
from . import to_marlowe
from . import profile
from . import json_conv
from . import layoutmode

from . import spawn_diag

import logging
logger = logging.getLogger(__name__)

from . import logconsole


def spawn_marlowe(master, marlowe_data_path):
    """spawn marlowe
    master, master Tk app or Frame
    marlowe_data_path path and filename for marlowe input data which
        includes '.dat' extension
    """
    profile_config = profile.load()

    bname = os.path.basename(marlowe_data_path)
    marlowe_workdir = os.path.dirname(marlowe_data_path)

    # usually marlowe in put data has .dat suffix
    # input argument is truncated .dat extension
    datext = re.compile(r'\.dat$')

    marlowe_input = datext.sub('', bname)

    # query setup marlowe
    # command line which used previously
    # file dump succeeded, save lastdir in the profile
    marlowe_command = profile_config.get('marlowe_command', 'marlowe "{input}"')
    marlowe_shellexec = profile_config.get('marlowe_shellexec', True)

    query = spawn_diag.SpawnDialog(
        master, title='run marlowe program',
        cmdline=marlowe_command, input=marlowe_input, workdir=marlowe_workdir,
        shell=marlowe_shellexec)

    if query.result is not None:
        # save result
        profile_config['marlowe_command'] = query.result['command']
        profile_config['marlowe_shellexec'] = query.result['shellexec']
        profile.update(profile_config)

        # spawn program
        c = query.result['command'].format(input=marlowe_input)
        logger.info('executing: ' + c)
        p = subprocess.Popen(shlex.split(c),
                             cwd=marlowe_workdir,
                             shell=query.result['shellexec'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stdout:
            logger.info(stdout)
        if stderr:
            logger.warn(stdout)
        logger.info('finished: ' + c)


def run():
    # test profile data
    try:
        # profile_config = profile.load()
        profile.load()
    except profile.Error as e:
        tkinter.messagebox.showerror('error on loding profile data',
                                     'error on loding profile data.\n\n' + e)
        sys.exit(2)
    except Exception as e:
        tkinter.messagebox.showerror('error on loding profile data',
                                     'error on loding profile data.\n\n' + str(e))
        sys.exit(2)

    app = tk.Tk()
    Pmw.initialise(app)

    # setup gui
    root = _root.Root(app)
    root.bind_with_balloonhelp(Pmw.Balloon(app))
    root.pack(side=tk.TOP)

    # gui layout
    layoutvar = tk.IntVar(app)
    layoutvar.set(guidata.default['gui_layout'])
    root.layout(layoutvar.get())

    # menubar
    menu = tk.Menu(app)
    app.configure(menu=menu)

    # file
    menufile = tk.Menu(menu, tearoff=False)
    menu.add_cascade(label='File', underline=0, menu=menufile)

    def set_data(d):
        """set guidata and layoutmode
        d is data compatible to guidata.default
        """
        root.set(d['root'])
        layoutvar.set(d['gui_layout'])
        layout_action()

    def get_data():
        """get guidata and layoutmode
        returns a data compatible to guidata.default
        """
        d = copy.deepcopy(guidata.default)
        d['root'] = root.get()
        d['gui_layout'] = layoutvar.get()
        return d

    # file - load
    def load_action():
        profile_config = profile.load()
        fname = tkinter.filedialog.askopenfilename(
            title='Load json file',
            defaultextension='.json',
            initialdir=profile_config['lastdir'],
            filetypes=[('JSON', '*.json'), ('All', '*')])
        if fname:
            with open(fname, 'rt', encoding='utf-8') as stream:
                # load json format
                d = json.load(stream)

                # check version of data and solve it
                d = guidata.solve_version(d)

                # translate json acceptable to native form
                d = json_conv.param_from_json(d)

                set_data(d)

                # load successed save lastdir
                profile_config['lastdir'] = os.path.dirname(fname)
                profile.update(profile_config)

    menufile.add_command(label='Load .json', underline=0, command=load_action)

    # file - save and run
    def save_and_run_action():
        class VExecption(Exception):
            def __init__(self, err):
                Exception.__init__(self)
                self.err = err

        try:
            err = root.validate()
            if err:
                raise VExecption(err)
            d = get_data()
        except VExecption as e:
            tkinter.messagebox.showerror(
                'Validation error',
                'validation error, save is aborted.\n\n'+tktool.error.format_errorstruct(e.err))
            return
        except Exception as e:
            tkinter.messagebox.showerror(
                'exception error', 'exception received, save is aborted.\n'+e)
            return

        profile_config = profile.load()

        fname = tkinter.filedialog.asksaveasfilename(
            title='Save MARLOWE input file',
            initialfile='*.dat',
            initialdir=profile_config['lastdir'],
            filetypes=[('MARLOWE input', '*.dat'), ('All', '*')])
        if fname:
            # create json_name and jsont_name

            # 0. remove existing .json
            if fname[-len('.dat'):] == '.dat':
                json_name = fname[:-len('.dat')] + '.json'
            else:
                json_name = fname + '.json'
            jsont_name = json_name + '.t'

            if os.path.exists(json_name):
                os.unlink(json_name)

            # 1. dump .json.t

            with open(jsont_name, 'wt', encoding='utf-8') as stream:
                d_json = json_conv.param_to_json(d)
                json.dump(d_json, stream, indent=2, sort_keys=True)

            # 2. save as marlowe data format
            with open(fname, 'wt') as stream:
                to_marlowe.to_marlowe(d, stream)

            # 3. rename .json.temp to .json
            os.rename(jsont_name, json_name)

            # file dump succeeded, save lastdir in the profile
            profile_config['lastdir'] = os.path.dirname(fname)
            profile.update(profile_config)

            spawn_marlowe(app, fname)

    menufile.add_separator()
    menufile.add_command(label='Save and Run', underline=0, command=save_and_run_action)

    # data for debugging
    menudata = tk.Menu(menu, tearoff=True)
    menu.add_cascade(label='Data', underline=0, menu=menudata)

    # data - show data
    def get_action():
        logger.info(root.get())
    menudata.add_command(label='Dump to Console', underline=0, command=get_action)

    # data - validate
    def val_action():
        err = root.validate()
        if err:
            tktool.error.show_as_messagebox(err)
    menudata.add_command(label='Validate', underline=0, command=val_action)
    menudata.add_separator()

    # data - clear data
    def clear_action():
        root.clear()
    menudata.add_command(label='Clear', underline=0, command=clear_action)

    # data - set example data
    # def set_action():
    #    set_data(guidata.app_example)
    # menudata.add_command(label='Set Example', 0, command=set_action)

    # layout
    menulayout = tk.Menu(menu, tearoff=False)
    menu.add_cascade(label='Layout', underline=0, menu=menulayout)

    def layout_action():
        mode = layoutvar.get()
        root.layout(mode)

    for v, label in layoutmode.modes:
        labeltext = '{0:d}: {1:s}'.format(v, label)
        menulayout.add_radiobutton(label=labeltext, underline=0,
                                   variable=layoutvar, value=v, command=layout_action)

    # logconsole
    # logwin = logconsole.getLogConsoleWindow('marlowe_ui')
    logconsole.getLogConsoleWindow('marlowe_ui')

    # set default data
    set_data(guidata.default)

    app.mainloop()
