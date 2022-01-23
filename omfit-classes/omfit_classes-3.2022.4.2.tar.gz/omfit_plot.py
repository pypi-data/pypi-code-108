from omfit_classes.startup_framework import *
from matplotlib import _pylab_helpers
from matplotlib import rcParams, cm
from omfit_classes.omfit_dmp import OMFITdmp
from omfit_classes.omfit_data import Dataset, DataArray
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk as NavigationToolbar2

# ----------------
# patch method
# ----------------
def _patch(obj, fun):
    """
    Patch a standard module/class with a new function/method.
    Moves original attribute to _original_<name> ONLY ONCE! If done
    blindly you will go recursive when reloading omfit_plot.

    """
    name = fun.__name__.lstrip('_')
    ismod = isinstance(obj, types.ModuleType)
    if hasattr(obj, name) and not hasattr(obj, '_original_' + name):
        orig = getattr(obj, name)
        if ismod:
            setattr(obj, '_original_' + name, orig)  # save copy of original function
        else:
            setattr(obj, '_original_' + name, types.MethodType(orig, obj))  # save copy of original method
    if ismod:
        setattr(obj, name, fun)  # replace with modified method
    else:
        setattr(obj, name, types.MethodType(fun, obj))  # replace with modified method


# ----------------
# modified matplotlib.figure.Figure
# ----------------
class Figure(matplotlib.figure.Figure):
    def __init__(self, *args, **kw):
        matplotlib.figure.Figure.__init__(self, *args, **kw)
        self.cbar_cids = []

    def colorbar(self, mappable, cax=None, ax=None, use_gridspec=True, **kw):
        """
        Customized default grid_spec=True for consistency with tight_layout.\n\n
        """
        cbar = matplotlib.figure.Figure.colorbar(self, mappable, cax=cax, ax=ax, use_gridspec=use_gridspec, **kw)
        drg_cbar = DraggableColorbar(cbar, mappable)
        # save weak reference
        self.cbar_cids.append([drg_cbar.connect(), drg_cbar])
        return cbar

    def printlines(self, filename, squeeze=False):
        """
        Print all data in line pyplot.plot(s) to text file.The x values
        will be taken from the line with the greatest number of
        points in the (first) axis, and other lines are interpolated
        if their x values do not match. Column labels are the
        line labels and xlabel.

        :param filename: Path to print data to
        :type filename: str
        :rtype: bool
        """
        with open(filename, 'w') as f:
            data = []

            # Try to avoid clutter in squeeze
            samettle = True
            sameylbl = True
            if squeeze:
                ylbl = self.get_axes()[0].get_ylabel()
                ttle = self.get_axes()[0].get_title()
                for a in self.get_axes():
                    if a.get_ylabel() != ylbl:
                        sameylbl = False
                    if a.get_title() != ttle:
                        samettle = False
                if samettle:
                    f.write(ttle + '\n\n')
                if sameylbl:
                    f.write('  ylabel = ' + re.sub(r'[ \${}]', '', ylbl) + '\n\n')

            for a in self.get_axes():
                if not a.lines:
                    continue
                if not squeeze:
                    data = []
                    f.write('\n' + a.get_title() + '\n\n')
                    f.write('  ylabel = ' + re.sub(r'[ \${}]', '', a.get_ylabel()) + '\n\n')
                # use x-axis from line with greatest number of pts
                xs = [l.get_xdata() for l in a.lines]
                longest = np.array([len(x) for x in xs]).argmax()
                if not data:
                    data.append(xs[longest])
                    f.write('{0:>25s}'.format(re.sub(r'[ \${}]', '', a.get_xlabel())))
                # label and extrapolate each line
                for line in a.lines:
                    label = re.sub(r'[ \${}]', '', line.get_label())
                    if squeeze and not sameylbl:
                        label = re.sub(r'[ \${}]', '', a.get_ylabel()) + label
                    f.write('{0:>25s}'.format(label))
                    # standard axis
                    x, y = line.get_xdata(orig=False), line.get_ydata(orig=False)
                    if np.any(x != data[0]):
                        fit = interp1d(x, y, bounds_error=False, fill_value=np.nan)
                        data.append(fit(data[0]))
                    else:
                        data.append(y)
                if not squeeze:
                    f.write('\n ')
                    data = np.array(data).T
                    for row in data:
                        row.tofile(f, sep=' ', format='%24.9E')
                        f.write('\n ')
                    f.write('\n')
            if squeeze:
                f.write('\n ')
                data = np.array(data).T
                for row in data:
                    row.tofile(f, sep=' ', format='%24.9E')
                    f.write('\n ')
                f.write('\n')
        print("Wrote lines to " + filename)
        return True

    def dmp(self, filename=None):
        """
        :param filename: file where to dump the h5 file

        :return: OMFITdmp object of the current figure
        """
        if filename is None:
            return OMFITdmp(self)
        else:
            open(filename, 'w').close()
            dmp = OMFITdmp(filename, modifyOriginal=True)
            dmp.from_fig(self)
            return dmp

    def data_managment_plan_file(self, filename=None):
        """
        Output the contents of the figure (self) to a hdf5 file given by filename

        :param filename: The path and basename of the file to save to (the extension is stripped, and '.h5' is added)
                         For the purpose of the GA data managment plan, these files can be uploaded directly to https://diii-d.gat.com/dmp

        :return: OMFITdmp object of the current figure
        """
        if filename is None:
            if isinstance(self.number, str):
                filename = self.number
            else:
                filename = 'Figure_%s' % self.number
        filename = os.path.splitext(filename)[0] + '.h5'
        return self.dmp(filename)

    def savefig(self, filename, saveDMP=True, PDFembedDMP=True, *args, **kw):
        r"""
        Revised method to save the figure and the data to netcdf at the same time

        :param filename: filename to save to

        :param saveDMP: whether to save also the DMP file. Failing to save as DMP does not raise an exception.

        :param PDFembedDMP: whether to embed DMP file in PDF file (only applies if file is saved as PDF)

        :param \*args: arguments passed to the original matplotlib.figure.Figure.savefig function

        :param \**kw: kw arguments passed to the original matplotlib.figure.Figure.savefig function

        :return: Returns dmp object if save of DMP succeded. Returns None if user decided not to save DMP.
        """

        # for backward compatibility
        if 'saveNetCDF' in kw:
            saveDMP = kw.pop('saveNetCDF')
            PDFembedDMP = saveDMP
            printw('`saveNetCDF` keyword is deprecated, use `saveDMP` and `PDFembedDMP` keywords instead')

        # if a file descriptor is passed, then keep going as usual
        if not isinstance(filename, str):
            return matplotlib.figure.Figure.savefig(self, filename, *args, **kw)

        try:
            callbacks_bkp = self.callbacks

            try:
                self.callbacks.process('dpi_changed', self)
            except Exception:
                # Hack required to avoid matplotlib error:
                # AttributeError: 'CallbackRegistry' object has no attribute 'callbacks'
                # see: https://github.com/matplotlib/matplotlib/issues/6048
                class dummy(object):
                    def __getattr__(self, attr):
                        return dummy()

                    def __call__(self, *args, **kw):
                        return dummy()

                self.callbacks = dummy()

            # Let's be smart about making a directory if it doesn't exist
            file_dir, basename = os.path.split(filename)
            if file_dir and not os.path.exists(file_dir):
                os.makedirs(file_dir)
                filename = os.path.sep.join([file_dir, basename])

            # See if this file format should be saved as something else and then converted back

            # Dictionary with instructions for which file types (keys) should initially be saved as other file types
            # (values) before being converted.
            convert_k_with_v = {'.eps': '.pdf', '.ps': '.pdf'}
            extension = os.path.splitext(filename)[1].lower()
            convert = convert_k_with_v.get(extension, None)
            if convert is not None:
                eps_flag = np.array(['', '-eps '])[int(extension == '.eps')]
                file_name = filename.replace(extension, convert)
                path, file_name_root = os.path.split(file_name)
                commands_ = '\n'.join(["cd {:}".format(path), "pdftops {:}{:}".format(eps_flag, file_name)])
                exe = distutils.spawn.find_executable('pdftops')
                if exe is None:
                    file_name = filename
            else:
                exe = None
                commands_ = None
                file_name = filename

            printd('savefig: filename = {}'.format(filename), topic='savefig')
            printd('savefig: extension = {}'.format(extension), topic='savefig')
            printd('savefig: convert = {}'.format(convert), topic='savefig')
            printd('savefig: file_name = {}'.format(file_name), topic='savefig')
            printd('savefig: exe = {}'.format(file_name), topic='savefig')
            printd('savefig: commands_ = {}'.format(commands_), topic='savefig')

            matplotlib.figure.Figure.savefig(self, file_name, *args, **kw)

            if exe is not None:
                printd('savefig: attempting conversion...', topic='savefig')
                subprocess.Popen(commands_, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        finally:
            self.callbacks = callbacks_bkp

        if saveDMP or PDFembedDMP:
            try:
                dmp = self.data_managment_plan_file(filename)
            except Exception as _excp:
                printe('Figure data could not be saved as HDF5: ' + repr(_excp))
                return False
            if extension == '.pdf' and PDFembedDMP:
                try:
                    PDF_set_DMP(filename, dmp=dmp.filename, delete_dmp=not saveDMP)
                except Exception as _excp:
                    printe('Could not embed HDF5 data in PDF figure: ' + repr(_excp))
            return dmp

    def script(self):
        """
        :return: string with Python script to reproduce the figure (with DATA!)
        """
        return self.dmp().script()

    def OMFITpythonPlot(self, filename=None):
        """
        generate OMFITpythonPlot script from figure (with DATA!)

        :param filename: filename for OMFITpythonPlot script

        :return: OMFITpythonPlot object
        """
        if filename is None:
            if isinstance(self.number, str):
                filename = self.number + '.py'
            else:
                filename = 'Figure_%s.py' % self.number
        return self.dmp().OMFITpythonPlot(filename)


pyplot.Figure = Figure
scipy.Figure = Figure
pylab.Figure = Figure

# ----------------
# modified matplotlib functions
# ----------------
OMFITfigureGlobal = {}
OMFITfigureGlobal['copied'] = None
OMFITfigureGlobal['select'] = None

# add support for close('all') and figureNotebooks
def close(which_fig):
    """
    Wrapper for pyplot.close that closes FigureNotebooks when closing 'all'

    """
    if which_fig == 'all':
        for fn in list(_active_FigureNotebooks.keys()):
            _active_FigureNotebooks[fn].close()
        pyplot._original_close('all')

    else:
        if which_fig in _active_FigureNotebooks:
            _active_FigureNotebooks[which_fig].close()
        else:
            pyplot._original_close(which_fig)


close.__doc__ += pyplot.close.__doc__
_patch(pyplot, close)

# savedFigure class
class savedFigure(object):
    def __init__(self, fig):
        for k, ax in enumerate(fig.axes):
            if ax.get_legend() is not None:
                ax.legend().draggable(False)
        self.figurePickle = pickle.dumps(fig)
        for k, ax in enumerate(fig.axes):
            if ax.get_legend() is not None:
                ax.legend().draggable(True)

    def __call__(self):
        return OMFITfigure(pickle.loads(self.figurePickle)).figure


class DraggableColorbar(object):
    def __init__(self, cbar, mappable):
        self.cbar = cbar

        self.mappable = mappable
        self.press = None
        self.cycle = sorted([i for i in dir(cm) if hasattr(getattr(cm, i), 'N')])
        self.index = self.cycle.index(cbar.cmap.name)

    def connect(self):
        """connect to all the events we need"""
        self.cidpress = self.cbar.patch.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.cbar.patch.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.cbar.patch.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        """on button press we will see if the mouse is over us and store some data"""
        if event.inaxes != self.cbar.ax:
            return
        self.press = event.ydata

    def key_press(self, event):
        if event.key == 'down':
            self.index += 1
        elif event.key == 'up':
            self.index -= 1
        if self.index < 0:
            self.index = len(self.cycle)
        elif self.index >= len(self.cycle):
            self.index = 0
        cmap = self.cycle[self.index]
        self.cbar.cmap = cmap
        self.cbar.draw_all()
        self.mappable.set_cmap(cmap)
        self.cbar.get_axes().set_title(cmap)
        self.cbar.patch.figure.canvas.draw()

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if self.press is None:
            return
        if event.inaxes != self.cbar.ax:
            return

        yprev = self.press
        ylim = self.cbar.ax.get_ylim()
        dy = (event.ydata - yprev) / (ylim[1] - ylim[0])
        self.press = event.ydata

        scale = self.cbar.norm.vmax - self.cbar.norm.vmin
        perc = 0.03
        cmin, cmax = self.cbar.ax.get_ylim()

        if event.button == 1:
            self.cbar.norm.vmax -= scale * dy

        if event.button == 3:
            self.cbar.norm.vmin -= scale * dy

        self.cbar.draw_all()
        self.mappable.set_norm(self.cbar.norm)
        self.cbar.patch.figure.canvas.draw()

    def on_release(self, event):
        """on release we reset the press data"""
        self.press = None
        self.mappable.set_norm(self.cbar.norm)
        self.cbar.patch.figure.canvas.draw()

    def disconnect(self):
        """disconnect all the stored connection ids"""
        self.cbar.patch.figure.canvas.mpl_disconnect(self.cidpress)
        self.cbar.patch.figure.canvas.mpl_disconnect(self.cidrelease)
        self.cbar.patch.figure.canvas.mpl_disconnect(self.cidmotion)


# enriched figure
class OMFITfigure(object):  # SortedDict):
    def __init__(self, obj, figureButtons=True):
        # SortedDict.__init__(self)

        self.obj = obj

        self.picked = []
        self.selected = None

        self.popup = None
        self.propWindow = None
        self.event = None

        self.buttons = {}
        self.buttons['enable_on_select'] = []
        self.buttons['disable_on_select'] = []

        self.timeDiscriminant = 0.25
        self.modifier = set()
        self._idPress = None
        self._idRelease = None
        self.buttonLock = False
        self.buttonModifier = []
        self.timePress = 0.0
        self.timeRelease = 0.0
        self.toolbar = None
        self.superzoomed = False
        self.multi = None

        if hasattr(self.obj, 'canvas'):
            self.canvas = self.obj.canvas
        elif hasattr(self.obj, 'figure') and self.obj.figure is not None:
            self.canvas = self.obj.figure.canvas
        elif hasattr(self.obj, 'axes') and self.obj.axes is not None:
            self.canvas = self.obj.axes.figure.canvas
        self.figure = self.canvas.figure

        try:
            self.tkRoot = self.canvas._master
            self.focus = self.tkRoot.focus_get()
        except Exception:
            self.tkRoot = None

        self.obj.shortcuts = SortedDict()
        self.obj.shortcuts['p'] = 'Pan/Zoom'
        self.obj.shortcuts['s'] = 'Save'
        self.obj.shortcuts['f'] = 'Toggle fullscreen'
        self.obj.shortcuts['g'] = 'Toggle grid'
        self.obj.shortcuts['L'] = 'Toggle x axis scale (log/linear)'
        self.obj.shortcuts['l'] = 'Toggle y axis scale (log/linear)'
        self.obj.shortcuts['h'] = 'Home/Reset'
        self.obj.shortcuts['t'] = 'Tight layout'
        self.obj.shortcuts['left'] = 'Back'
        self.obj.shortcuts['right'] = 'Forward'
        self.obj.shortcuts['z'] = 'Zoom-to-rect'
        self.obj.shortcuts['hold x'] = 'Constrain pan/zoom to x axis'
        self.obj.shortcuts['hold y'] = 'Constrain pan/zoom to y axis'
        self.obj.shortcuts['hold CONTROL'] = 'Preserve aspect ratio'

        self._idPress = self.canvas.mpl_connect('key_press_event', self.key_press_callback)
        self._idRelease = self.canvas.mpl_connect('key_release_event', self.key_release_callback)
        self._id_superzoom = self.canvas.mpl_connect('button_press_event', self.superzoom)

        if hasattr(self.obj, 'canvas') and self.tkRoot:
            for k in list(self.tkRoot.children.keys()):
                if isinstance(self.tkRoot.children[k], matplotlib.backend_bases.NavigationToolbar2):
                    self.toolbar = self.tkRoot.children[k]
                    for k, b in list(self.toolbar.children.items()):
                        try:
                            txt = b.config('text')[4]
                        except tk.TclError:
                            continue
                        if txt == 'Save':
                            b.config(command=lambda event=None: self.save_figure(self.toolbar))
                            b.bind('<' + rightClick + '>', lambda event=None: self.save_figure(self.toolbar, PDFembedDMP=None))
                            ToolTip.createToolTip(b, 'Save figure + data (file & embedded)<leftClick>\nSave figure ... <rightClick>')
                        elif txt == 'Pan':
                            b.config(command=lambda event=None: self.pan())
                        elif txt == 'Zoom':
                            b.config(command=lambda event=None: self.zoom())

            self.addOMFITfigureToolbar(figureButtons=figureButtons)

        # self.get() #to activate this (useful for inspection), make the OMFITfigure object as a sortedDict

    def _Button(self, text, file, command, tooltip_text=None):
        file = os.path.join(OMFITsrc, 'extras', 'graphics', file)
        im = tk.PhotoImage(master=self.mytoolbar, file=file)
        b = tk.Button(master=self.mytoolbar, text=text, padx=2, pady=2, command=command, image=im)
        b._ntimage = im
        b.pack(side=tk.LEFT)
        if tooltip_text is None:
            tooltip_text = text
        ToolTip.createToolTip(b, tooltip_text)
        return b

    def addOMFITfigureToolbar(self, figureButtons=True):
        self.mytoolbar = tk.Frame(master=self.tkRoot, height=50, padx=2)

        bt = self._Button("Select", "select.ppm", self.objSelect)

        bt = self._Button("Copy", "copy.ppm", self.objCopy)
        bt.config(state=tk.DISABLED)
        self.buttons['enable_on_select'].append(bt)

        bt = self._Button("Paste", "paste.ppm", self.objPaste)
        bt.config(state=tk.DISABLED)
        self.buttons['enable_on_select'].append(bt)

        bt = self._Button("Trash", "trash.ppm", self.objDelete)
        bt.config(state=tk.DISABLED)
        self.buttons['enable_on_select'].append(bt)

        bt = self._Button("Auto-X", "autoX.ppm", lambda event=None: self.objAutoZoom(None, 'x'))
        bt.config(state=tk.DISABLED)
        self.buttons['enable_on_select'].append(bt)

        bt = self._Button("Auto-Y", "autoY.ppm", lambda event=None: self.objAutoZoom(None, 'y'))
        bt.config(state=tk.DISABLED)
        self.buttons['enable_on_select'].append(bt)

        bt = self._Button("Legend", "legend.ppm", self.objLegend)
        bt.config(state=tk.DISABLED)
        self.buttons['enable_on_select'].append(bt)

        bt = self._Button("Crosshair", "crosshair.ppm", self.crosshair)
        self.buttons['disable_on_select'].append(bt)

        bt = self._Button("Help", "help.ppm", self.help)

        if figureButtons:
            bt = self._Button(
                text='Open PDF <leftClick>\n' + 'Open PDF+Data (embedded) <rightClick>',
                file='pdf.ppm',
                command=lambda event=None: self.openPDF(fig=self.figure.number),
            )
            bt.bind('<' + rightClick + '>', lambda event=None: self.openPDF(fig=self.figure.number, PDFembedDMP=True))

            bt = self._Button(
                text='Email PDF <leftClick>\n' + 'Email... <rightClick>',
                file='mail.ppm',
                command=lambda event=None: self.email(fig=self.figure.number),
            )
            bt.bind('<' + rightClick + '>', lambda event=None: self.email(fig=self.figure.number, ext=None))

            bt = self._Button(
                text='Pin object <leftClick>\n' + 'Pin image <rightClick>',
                file='pin.ppm',
                command=lambda event=None: self.pin(fig=self.figure),
            )
            bt.bind('<' + rightClick + '>', lambda event=None: self.pin(fig=self.figure, savefig=False))

        self.mytoolbar.pack(side=tk.BOTTOM, expand=tk.NO, fill=tk.X)

    def pin(self, event=None, fig=None, savefig=True, PDFembedDMP=True):
        """
        :param savefig: if False, save figure as object,
                        if True, save figure as image.
        """

        location = pickTreeLocation(parent=self.tkRoot)
        if location is None:
            return

        OMFIT.addBranchPath(location)
        location = parseLocation(location)
        item = location[-1]
        location = eval(buildLocation(location[:-1]))

        if savefig:
            from omfit_classes.omfit_path import OMFITpath

            base, ext = os.path.splitext(item)
            if not ext:
                ext = '.pdf'
            location[item] = OMFITpath(base + ext)
            fig.savefig(location[item].filename, saveDMP=False, PDFembedDMP=PDFembedDMP)
            printi('Saved rendered figure to tree.')
        else:
            location[item] = savedFigure(fig)
            printi('Saved object figure to tree.')

        OMFITaux['GUI'].update_treeGUI()

    def email(self, event=None, fig=None, ext='PDF', saveDMP=False, PDFembedDMP=False):

        """
        :param ext: default 'PDF'. figure format, e.g. PDF, PNG, JPG, etc.

        :param saveDMP: default False, save HDF5 binary file
            [might have more data than shown in figure; but can be used for DIII-D Data Management Plan (DMP)]

        :param PDFembedDMP: default False, embed DMP file in PDF
        """

        try:
            filename = os.path.splitext(self.canvas.get_default_filename())[0]
        except Exception:
            filename = 'figure'

        if ext is None:
            from omfit_classes.OMFITx import Dialog

            ext = Dialog(
                message='Please select the desired extension.',
                answers=['PDF', 'PDF+Data (embedded)', 'PDF+Data', 'PNG', 'Cancel'],
                icon='question',
                title='Format selection',
            )
            if ext == 'Cancel':
                return
            elif ext == 'PDF+Data':
                ext = 'PDF'
                saveDMP = True
                PDFembedDMP = False
            elif ext == 'PDF+Data (embedded)':
                ext = 'PDF'
                saveDMP = False
                PDFembedDMP = True
            elif ext == 'PDF':
                saveDMP = False
                PDFembedDMP = False
            elif ext == 'PNG':
                saveDMP = False
                PDFembedDMP = False

        filename += '.' + ext.lower()
        if os.path.exists(OMFITcwd + os.sep + filename):
            os.remove(OMFITcwd + os.sep + filename)
        if fig is not None:
            figure(fig)
        pyplot.savefig(OMFITcwd + os.sep + filename, saveDMP=saveDMP, PDFembedDMP=PDFembedDMP)

        attachments = [OMFITcwd + os.sep + filename]
        if saveDMP:
            attachments += [os.path.splitext(OMFITcwd + os.sep + filename)[0] + '.h5']

        prjname = ''
        if OMFIT.filename:
            prjname = 'Project: ' + OMFIT.filename

        eml = tk.email_widget(
            parent=self.tkRoot,
            fromm=OMFIT['MainSettings']['SETUP']['email'],
            to=OMFIT['MainSettings']['SETUP']['email'],
            subject='OMFIT - Figure: ' + filename,
            message='Attachment: ' + filename + '\n' + '=' * 20 + '\n' + prjname + '\n',
            attachments=attachments,
            title='Email ' + filename,
            use_last_email_to=1,
            quiet=False,
        )
        eml.wait_window(eml)

    def openPDF(self, event=None, fig=None, PDFembedDMP=False):
        try:
            filename = self.canvas.get_default_filename()
        except Exception:
            filename = 'figure.pdf'
        if os.path.exists(OMFITcwd + os.sep + filename):
            os.remove(OMFITcwd + os.sep + filename)
        if isinstance(fig, (pyplot.Figure, OMFITfigure)):
            pass
        elif fig is not None:
            fig = figure(fig)
        else:
            fig = pyplot.gcf()
        fig.savefig(OMFITcwd + os.sep + filename, saveDMP=False, PDFembedDMP=PDFembedDMP)
        import omfit_classes.OMFITx

        omfit_classes.OMFITx.Open(OMFITcwd + os.sep + filename)

    def help(self):
        text = """
-= Select Mode =-
Click        : Select object/axis
Right-Click  : Property selector
Double-Click : Zoom on object
Hold-Click   : Object selector
Control-c    : Copy selected object
Control-v    : Paste selected object
Backspace    : Delete selected object

-= Keyboard shortcuts =-
"""
        for k, v in list(self.obj.shortcuts.items()):
            text += '\n{k:13}: {v}'.format(k=k, v=v)

        printi(text)

    def crosshair(self, force=None):
        if force is not False and (force or self.multi is None) and self.figure.axes:
            # interactive = pyplot.isinteractive()
            axis_bkp = {}
            for ax in self.figure.axes:
                axis_bkp[ax] = ax.get_xlim(), ax.get_ylim()
            # pyplot.ion()
            self.multi = matplotlib.widgets.MultiCursor(self.canvas, self.figure.axes, color='r', lw=1, horizOn=True)
            # pyplot.ioff()
            for ax in self.figure.axes:
                ax.set_xlim(axis_bkp[ax][0])
                ax.set_ylim(axis_bkp[ax][1])
            # pyplot.interactive(interactive)
        elif not force and self.multi is not None:
            self.multi.active = False
            self.canvas.draw_idle()
            self.multi = None

    def get(self, event=None):
        self.update(matplotlib.artist.ArtistInspector(self.obj).properties())

        for k, child in enumerate(self.obj.get_children()):
            self[str(k) + "_" + child.__class__.__name__] = OMFITfigure(child)

    def getObj(self, obj):
        tmp = SortedDict()
        tmp.update(matplotlib.artist.ArtistInspector(obj).properties())

        for item in ['figure', 'axes']:
            if item in tmp:
                del tmp[item]

        del tmp['children']

        for childName in list(tmp.keys()):
            if 'matplotlib' in str(tmp[childName].__class__):
                del tmp[childName]
        return tmp

    def selectAxes(self):
        if hasattr(self.selected, 'axes') and not isinstance(self.selected.axes, list) and self.selected.axes is not None:
            return self.selected.axes
        elif isinstance(self.selected, matplotlib.axes.Axes):
            return self.selected
        elif self.event.inaxes is not None:
            return self.event.inaxes
        else:
            return pyplot.gca()

    def selectPick(self, k):
        self.selected = self.picked[k]
        self.toolbar.set_message('Selected: ' + str(self.selected))

        OMFITfigureGlobal['select'] = self.selected

        # update the pyplot.gca()
        self.figure._axstack.bubble(self.selectAxes())

        self.button_manager(self.event)

    def closePopup(self, event=None):
        '''this function closes the popup'''
        if self.popup is not None:
            self.popup.unbind("<FocusOut>")
            self.popup.unbind("<Escape>")
            self.popup.grab_release()
            self.popup.unpost()
            self.popup.destroy()
            self.popup = None
        if self.focus is not None:
            try:
                self.focus.focus_set()
            except tk.TclError:
                pass

    def poPopup(self, event):
        '''this function creates the popup which can then be populated'''
        top = event.guiEvent.widget

        # enforce only one popup at the time
        self.closePopup()
        self.modifier = set()
        self.popup = tk.Menu(top, tearoff=0)
        self.popup.bind("<FocusOut>", self.closePopup)
        self.popup.bind("<Escape>", self.closePopup)
        self.popup.focus_set()

    def mvPopup(self, event):
        event = event.guiEvent

        self.popup.update_idletasks()

        x = event.x_root
        if event.x_root + self.popup.winfo_reqwidth() > self.popup.winfo_screenwidth():
            x = self.popup.winfo_screenwidth() - self.popup.winfo_reqwidth() - 12
        y = event.y_root
        if event.y_root + self.popup.winfo_reqheight() > self.popup.winfo_screenheight():
            y = self.popup.winfo_screenheight() - self.popup.winfo_reqheight() - 12

        self.popup.post(x, y)
        self.popup.grab_set()

    def button_press_callback(self, event):
        """when a mouse button is pressed"""
        self.closePopup()
        self.closePropwindow()

        if self.active != 'SELECT':
            return
        self.timePress = time.time()
        if not self.buttonLock:
            self.buttonLock = True
            self.buttonModifier = 'long'
            top = event.guiEvent.widget.master
            top.after(int(self.timeDiscriminant * 1000), lambda event=event: self.pick(event))

    def button_release_callback(self, event):
        """when a mouse button is released"""
        if self.active != 'SELECT':
            return
        if time.time() - self.timeRelease < self.timeDiscriminant:
            self.buttonModifier = 'double'
        elif time.time() - self.timePress < self.timeDiscriminant:
            self.buttonModifier = 'single'
        self.timeRelease = time.time()

    def pick(self, event):
        """this fucntion takes care of detecting which object was selected"""
        self.buttonLock = False
        # handling of picking
        self.event = event
        self.picked = self.figure.hitlist(self.event)

        # if `control` was not pressed, remove hidden objects
        if 'control' not in self.modifier:
            L = []
            for h in self.picked:
                if not hasattr(h, 'visible') or (hasattr(h, 'visible') and h.visible):
                    if (
                        h._remove_method != None
                        or isinstance(h, matplotlib.axes.Axes)
                        or isinstance(h, matplotlib.image.AxesImage)
                        or isinstance(h, matplotlib.text.Text)
                    ) and not (isinstance(h, matplotlib.patches.Rectangle)):
                        L.append((h.zorder, h))
            L.sort(key=lambda x: x[0])
            self.picked = [h for zorder, h in L]

        if self.figure in self.picked:
            self.picked.remove(self.figure)
        self.picked.insert(0, self.figure)

        if self.buttonModifier != 'long':
            # if it's a short click then select the first object
            self.selectPick(-1)
        else:
            # ask for selection
            self.poPopup(event)
            for k, choice in enumerate(self.picked):
                # nice description
                if isinstance(choice, matplotlib.axes.Axes):
                    description = 'Axes ' + choice.get_title() + ' ' + choice.get_ylabel() + ' ' + choice.get_xlabel()
                elif isinstance(choice, matplotlib.lines.Line2D) and '_line' in choice.get_label():
                    description = (
                        'Line (c:'
                        + str(choice.get_color())
                        + ' ls:'
                        + str(choice.get_linestyle())
                        + ' lw:'
                        + str(choice.get_linewidth())
                        + ')'
                    )
                else:
                    description = str(choice)
                exec(
                    (
                        'self.popup.add_command(label="""'
                        + str(description)
                        + '""", command=lambda event=None:self.selectPick('
                        + str(k)
                        + '))'
                    ),
                    locals(),
                )
            self.mvPopup(event)

    def closePropwindow(self, event=None):
        """close the properties editing window"""
        if self.propWindow is not None:
            self.propWindow.unbind("<FocusOut>")
            self.propWindow.unbind("<Escape>")
            self.propWindow.grab_release()
            self.propWindow.destroy()
            self.propWindow = None
        if self.focus is not None:
            try:
                self.focus.focus_set()
            except tk.TclError:
                pass

    def selectProperty(self, property):
        """open the properties editing window"""
        # get the property
        text = self.getProperty(property)

        # build the property editor GUI
        top = self.event.guiEvent.widget.master
        self.propWindow = tk.Toplevel(top)
        self.propWindow.withdraw()
        self.propWindow.wm_overrideredirect(1)

        color = "#ffffff"

        # pick a maximum width/height
        wmax = min([max([max(np.array([len(line) for line in text.split('\n')])), 20]), 50])
        hmax = min(text.count('\n') + 1, 11)

        # draw the GUI
        frm = tk.Frame(self.propWindow, relief=tk.SOLID, borderwidth=1)
        frm.grid_columnconfigure(1, weight=1)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        if hmax == 1:
            label = tk.OneLineText(frm, width=wmax)
        else:
            label = tk.ScrolledText(frm, height=hmax)
        label.config(background=color, borderwidth=0, font=OMFITfont('normal', 0, 'Courier'))
        label.grid(column=0, row=0, sticky='nsew', columnspan=2)
        label.insert(1.0, text)
        label.delete('end -1 chars', 'end')
        if '__' not in property:
            tk.Button(frm, text='?', command=lambda event=None: onHelp(self), padx=2, pady=1).grid(column=0, row=1, sticky='nsew')
        tk.Button(frm, text='Update ' + property.strip('_'), command=lambda event=None: onButton(self), padx=2, pady=1).grid(
            column=1, row=1, sticky='nsew'
        )
        label.focus_set()

        # bind functions to the GUI
        def onButton(self, event=None):
            text = label.get(1.0, tk.END).strip()
            self.setProperty(property, text)
            self.closePropwindow()
            # show again the property selection
            self.button_manager(self.event)

        def onEscape(event=None):
            self.closePropwindow()
            # show again the property selection
            self.button_manager(self.event)

        def onFocusOut(event=None):
            self.closePropwindow()

        def onHelp(event=None):
            pyplot.setp(self.selected, property)

        if hmax == 1:
            self.propWindow.bind('<Return>', lambda event=None: onButton(self))
            self.propWindow.bind('<KP_Enter>', lambda event=None: onButton(self))
        self.propWindow.bind(f'<{ctrlCmd()}-Return>', lambda event=None: onButton(self))
        self.propWindow.bind('<Escape>', onEscape)
        self.propWindow.bind('<FocusOut>', onFocusOut)

        # set window location not to fall out of screen
        self.propWindow.update_idletasks()
        event = self.event.guiEvent
        x = event.x_root
        if event.x_root + self.propWindow.winfo_reqwidth() > self.propWindow.winfo_screenwidth():
            x = self.propWindow.winfo_screenwidth() - self.propWindow.winfo_reqwidth() - 12
        y = event.y_root
        if event.y_root + self.propWindow.winfo_reqheight() > self.propWindow.winfo_screenheight():
            y = self.propWindow.winfo_screenheight() - self.propWindow.winfo_reqheight() - 12

        self.propWindow.wm_geometry("+%d+%d" % (x, y))

        # wait for the selection to be made
        self.propWindow.deiconify()
        self.propWindow.wait_window(self.propWindow)

    def getProperty(self, property):
        """retrieve the value of the property as seen by the user"""
        if property == '__legend__':
            text = 'legend(labelspacing=0.2,loc=0)'
        elif property == '__fontSizes__':
            text = ''
        else:
            prop = eval("self.selected.get_" + property + "()")
            if isinstance(prop, str):
                text = re.sub(r'\\', r'\\\\', prop)
                text = re.sub(r'\'', r'\'', text)
                text = re.sub(r'\"', r'\"', text)
                text = '"' + text + '"'
            else:
                text = repr(prop)
        return text

    def setProperty(self, property, text):
        doSet = True
        if property == '__legend__':
            doSet = False
            try:
                # if text is True, False or None
                text = ast.literal_eval(text)
                if text:
                    tmp = pyplot.gca().legend(labelspacing=0.2, loc=0)
                    if isinstance(tmp, matplotlib.legend.Legend):
                        tmp.draggable(state=True)
                else:
                    pyplot.gca().legend_ = None
            except Exception:
                try:
                    tmp = eval("pyplot.gca()." + text)
                    if isinstance(tmp, matplotlib.legend.Legend):
                        tmp.draggable(True)
                except Exception as _excp:
                    printe('Plot legend :' + repr(_excp))
        elif property == '__fontSizes__':
            doSet = False
            set_fontsize(self.obj, text)
        if doSet:
            function = eval("self.selected.set_" + property)
            try:
                function(eval(text))
            except Exception as _excp:
                printe('Plot legend :' + repr(_excp))
        self.canvas.draw_idle()

    def button_manager(self, event):
        # handling of buttons after an element has been selected
        if self.selected is None:
            return

        if event.button == rightClickMPLindex:
            properties = {}
            properties['Line2D'] = [
                'Line',
                [
                    'color',
                    'linewidth',
                    'linestyle',
                    'label',
                    'xdata',
                    'ydata',
                    'marker',
                    'markerfacecolor',
                    'markeredgecolor',
                    'markevery',
                    'markersize',
                    'zorder',
                ],
            ]
            properties['Text'] = ['Text', ['text', 'color', 'size', 'weight', 'rotation', 'position', 'zorder']]
            properties['Axes'] = [
                'Axes',
                ['xlim', 'ylim', 'xticks', 'yticks', 'xlabel', 'ylabel', 'xscale', 'yscale', 'aspect', 'title', 'frame_on', '__legend__'],
            ]
            properties['AxesSubplot'] = ['Axes', properties['Axes'][1]]

            properties['LineCollection'] = ['Line collection', ['linewidth']]
            properties['NonUniformImage'] = ['Image', ['extent', 'clim', 'interpolation']]
            properties['Polygon'] = ['Polygon', ['facecolor', 'linewidth', 'verts', 'linestyle']]
            properties['QuadMesh'] = ['Quad mesh', ['facecolor', 'edgecolors', 'array', 'clim', 'cmap']]
            properties['QuadContourSet'] = [
                'QuadContourSet',
                ['array', 'clim', 'cmap'],
            ]  # contourf actually just stores a list of PathCollections?
            properties['AxesImage'] = ['AxesImage', ['interpolation', 'visible', 'array', 'clim', 'cmap']]
            properties['Colorbar'] = ['Colorbar', ['ticklabels', 'label', 'clim', 'cmap']]  # doesn't show up for some reason

            properties['Figure'] = ['Figure', ['facecolor', 'figwidth', 'figheight', 'dpi', '__fontSizes__']]

            # properties['Rectangle']=['Rectangle',['facecolor','edgecolor','xy']]
            # properties['XAxis']=['X axis',['scale','label_text','units','label_position']]
            # properties['YAxis']=['Y axis',copy.copy(properties['XAxis'][1])]
            # properties['FancyBboxPatch']=['facecolor','edgecolors','width','height','x','y','linestyle','linewidth','verts']

            if self.selected.__class__.__name__ in list(properties.keys()):
                self.poPopup(event)
                self.popup.add_command(label=properties[self.selected.__class__.__name__][0], state=tk.DISABLED)
                self.popup.add_separator()
                for k, choice in enumerate(properties[self.selected.__class__.__name__][1]):
                    exec(
                        (
                            'self.popup.add_command(label="""'
                            + choice.strip('_')
                            + '""", command=lambda event=None:self.selectProperty("'
                            + choice
                            + '"))'
                        ),
                        locals(),
                    )
                self.mvPopup(event)

        elif event.button == 1 and self.buttonModifier == 'double':
            # todo this should use objects clip_box
            if isinstance(self.selected, matplotlib.lines.Line2D):
                Xmin = np.nanmin(self.selected.get_xdata())
                Ymin = np.nanmin(self.selected.get_ydata())
                Xmax = np.nanmax(self.selected.get_xdata())
                Ymax = np.nanmax(self.selected.get_ydata())

                # update zoom
                self.toolbar.set_message('Zoom tight: ' + str(self.selected))
                if self.toolbar._nav_stack.empty():
                    self.toolbar.push_current()
                Xmin0, Xmax0 = self.selectAxes().get_xlim()
                Ymin0, Ymax0 = self.selectAxes().get_ylim()
                if Xmin0 != Xmin or Xmax != Xmax0 or Ymin != Ymin0 or Ymax != Ymax0:
                    self.selectAxes().set_xlim((Xmin, Xmax))
                    self.selectAxes().set_ylim((Ymin, Ymax))
                    self.toolbar.push_current()
                    self.canvas.draw_idle()

    def objDelete(self, event=None):
        try:
            tmp = str(self.selected)
            while self.selected:
                if self.selected.remove():
                    break
                parent = None
                for p in self.picked:
                    if hasattr(p, 'getchildren') and self.selected in p.get_children():
                        parent = p
                        break
                self.selected = parent
            self.toolbar.set_message('Removed: ' + tmp)
            self.canvas.draw_idle()
            pyplot.gca().relim()
        except Exception:
            self.toolbar.set_message(str(self.selected) + "can't be removed")

    def objCopy(self, event=None):
        OMFITfigureGlobal['copied'] = self.selected
        self.toolbar.set_message('Copied: ' + str(self.selected))

    def objLegend(self, event=None):
        if pyplot.gca().legend_ is not None:
            pyplot.gca().legend_ = None
            self.toolbar.set_message('Legend hidden')
        else:
            tmp = pyplot.gca().legend(labelspacing=0.2, loc=0)
            if isinstance(tmp, matplotlib.legend.Legend):
                tmp.draggable(state=True)
                self.toolbar.set_message('Legend shown')
            else:
                self.toolbar.set_message('No labels defined to draw a legend')
        self.canvas.draw_idle()

    def objText(self, event=None):
        pyplot.gca().text(0.5, 0.5, 'text')
        self.canvas.draw_idle()

    def objPaste(self, event=None):
        updated = False
        holdBackup = pyplot.ishold()
        pyplot.hold(True)
        try:

            # --------------------
            # paste Line2D
            # --------------------
            if isinstance(OMFITfigureGlobal['copied'], matplotlib.lines.Line2D):
                tmp = self.getObj(OMFITfigureGlobal['copied'])
                line = pyplot.gca().plot(tmp['xdata'], tmp['ydata'])
                for k in ['xydata', 'transformed_clip_path_and_affine']:
                    del tmp[k]
                setp(line, **tmp)
                updated = True

            # --------------------
            # paste Text
            # --------------------
            elif isinstance(OMFITfigureGlobal['copied'], matplotlib.text.Text):
                tmp = self.getObj(OMFITfigureGlobal['copied'])
                text = pyplot.gca().text(tmp['position'][0], tmp['position'][1], tmp['text'])
                for k in ['transformed_clip_path_and_affine', 'prop_tup', 'bbox_patch']:
                    del tmp[k]
                setp(text, **tmp)
                updated = True

            # --------------------
            # paste LineCollection
            # --------------------
            elif isinstance(OMFITfigureGlobal['copied'], matplotlib.collections.LineCollection):
                tmp = self.getObj(OMFITfigureGlobal['copied'])

                v = [np.squeeze(path.vertices[::2]).tolist() for path in tmp['paths']]
                lastPoint = np.squeeze(tmp['paths'][-1].vertices[-1]).tolist()
                v = np.vstack((v, lastPoint))
                x = np.array(v).T[0, :]
                y = np.array(v).T[1, :]
                points = np.array([x, y]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)
                lc = matplotlib.collections.LineCollection(segments)

                for k in ['transformed_clip_path_and_affine', 'colors', 'transforms', 'paths']:
                    del tmp[k]
                setp(lc, **tmp)
                updated = True

                pyplot.gca().add_collection(lc)

                pyplot.gca().plot(x, y, '.')
                del pyplot.gca().lines[-1]

            if updated:
                self.toolbar.set_message('Pasted: ' + str(OMFITfigureGlobal['copied']))
                self.canvas.draw_idle()
                pyplot.gca().relim()

        except Exception:
            raise

        finally:
            pyplot.hold(holdBackup)

    def objAutoZoom(self, event=None, ax=''):
        enabled = eval("pyplot.gca().get_autoscale" + ax + "_on")

        if self.toolbar._nav_stack.empty():
            self.toolbar.push_current()
        Xmin0, Xmax0 = pyplot.gca().get_xlim()
        Ymin0, Ymax0 = pyplot.gca().get_ylim()

        if not enabled():
            pyplot.gca().autoscale(enable=True, axis=ax, tight=True)
            self.toolbar.set_message('Auto ' + ax.upper() + ' enabled, Tight')

        elif enabled() and pyplot.gca()._tight:
            pyplot.gca().autoscale(enable=True, axis=ax, tight=False)
            self.toolbar.set_message('Auto ' + ax.upper() + ' enabled, Loose')

        else:
            pyplot.gca().autoscale(enable=False)
            self.toolbar.set_message('Auto ' + ax.upper() + ' disabled')

        Xmin1, Xmax1 = pyplot.gca().get_xlim()
        Ymin1, Ymax1 = pyplot.gca().get_ylim()

        if Xmin1 != Xmin0 or Ymin1 != Ymin0 or Xmax1 != Xmax0 or Ymax1 != Ymax0:
            self.toolbar.push_current()
            self.canvas.draw_idle()

    def objSelect(self, event=None, forceDisable=False):
        if self.active == 'SELECT' or forceDisable:
            # if was in in select mode, disable this mode and associcated buttons
            self.active = None
            for button in self.buttons['enable_on_select']:
                button.config(state=tk.DISABLED)
            for button in self.buttons['disable_on_select']:
                button.config(state=tk.NORMAL)
        else:
            # activate select mode and activate my buttons
            self.active = 'SELECT'
            for button in self.buttons['enable_on_select']:
                button.configure(state=tk.NORMAL)
            for button in self.buttons['disable_on_select']:
                button.config(state=tk.DISABLED)
            # select mode disables crossair
            self.crosshair(force=False)

        # unset the press binding in the main toolbar
        if hasattr(self.toolbar, '_idPress') and self.toolbar._idPress is not None:
            self.toolbar._idPress = self.toolbar.canvas.mpl_disconnect(self.toolbar._idPress)
            self.toolbar.mode = ''

        # unset the release binding in the main toolbar
        if hasattr(self.toolbar, '_idRelease') and self.toolbar._idRelease is not None:
            self.toolbar._idRelease = self.toolbar.canvas.mpl_disconnect(self.toolbar._idRelease)
            self.toolbar.mode = ''

        # unset the press binding
        if self._idPress is not None:
            self._idPress = self.toolbar.canvas.mpl_disconnect(self._idPress)

        # unset the release binding
        if self._idRelease is not None:
            self._idRelease = self.toolbar.canvas.mpl_disconnect(self._idRelease)

        # set the bindings
        if self.active:
            self.toolbar._idPress = self.canvas.mpl_connect('button_press_event', self.button_press_callback)
            self.toolbar._idRelease = self.canvas.mpl_connect('button_release_event', self.button_release_callback)
            self.toolbar.mode = 'select/property'
            self.toolbar.canvas.widgetlock(self.toolbar)
        else:
            self.toolbar.canvas.widgetlock.release(self.toolbar)

        # set the navigation toolbar button status
        for a in self.toolbar.canvas.figure.get_axes():
            a.set_navigate_mode(self.active)

        # set the navigation toolbar message
        self.toolbar.set_message(self.toolbar.mode)

    def key_press_callback(self, event):
        # if not event.inaxes: return

        # handle modifier
        if event.key in ['control', 'shift', 'alt']:
            self.modifier.add(event.key)
            printd('Key pressed: ' + '+'.join(self.modifier), topic='figure')
            return

        # --------------------
        # delete
        # --------------------
        if event.key == 'backspace' and self.selected is not None:
            self.objDelete(event)

        # --------------------
        # copy
        # --------------------
        elif 'control' in self.modifier and event.key == 'c':
            self.objCopy(event)

        # --------------------
        # paste
        # --------------------
        elif 'control' in self.modifier and event.key == 'v' and OMFITfigureGlobal['copied'] is not None:
            self.objPaste(event)

        # --------------------
        # tight layout
        # --------------------
        elif event.key == 't':
            self.figure.tight_layout()

    def key_release_callback(self, event):
        if event.key in ['control', 'shift', 'alt'] and event.key in self.modifier:
            self.modifier.remove(event.key)
            printd('Released ' + event.key, topic='figure')

    @staticmethod
    def save_figure(self, saveDMP=True, PDFembedDMP=True, *args):
        # Note that self here is the toolbar

        if saveDMP is None or PDFembedDMP is None:
            from omfit_classes.OMFITx import Dialog

            options = ['Figure', 'Figure + Data (file)', 'Figure + Data (embedded)', 'Figure + Data (file & embedded)', 'Cancel']
            choice = Dialog(message='Please select Data handling', answers=options, icon='question', title='Data export selection')
            if options.index(choice) == 0:
                saveDMP = False
                PDFembedDMP = False
            elif options.index(choice) == 1:
                saveDMP = True
                PDFembedDMP = False
            elif options.index(choice) == 2:
                saveDMP = False
                PDFembedDMP = True
            elif options.index(choice) == 3:
                saveDMP = True
                PDFembedDMP = True
            else:
                return

        self.window.tk.eval("catch {tk_getOpenFile foo bar}")
        self.window.tk.eval("catch {tk_getSaveFile foo bar}")
        try:
            self.window.tk.eval("set ::tk::dialog::file::showHiddenVar 0")
            self.window.tk.eval("set ::tk::dialog::file::showHiddenBtn 1")
        except tk.TclError:
            pass

        filetypes = self.canvas.get_supported_filetypes().copy()
        default_filetype = self.canvas.get_default_filetype()

        # Tk doesn't provide a way to choose a default filetype,
        # so we just have to put it first
        default_filetype_name = filetypes[default_filetype]
        del filetypes[default_filetype]
        sorted_filetypes = sorted(list(filetypes.items()))
        sorted_filetypes.insert(0, (default_filetype, default_filetype_name))

        tk_filetypes = [(name, '*.%s' % ext) for (ext, name) in sorted_filetypes]
        for k, item in enumerate(tk_filetypes):
            if item[1] == '*.pdf':
                tk_filetypes.insert(0, tk_filetypes.pop(k))

        try:
            filename = self.canvas.get_default_filename()
        except Exception:
            filename = 'figure.pdf'
        fname = tkFileDialog.asksaveasfilename(
            master=self.window,
            title='Save figure [Data-file: %s   Data-embedded: %s]' % (saveDMP, PDFembedDMP),
            filetypes=tk_filetypes,
            defaultextension='*.pdf',
            initialdir=OMFITaux['lastBrowsedDirectory'],
            initialfile=os.path.splitext(filename)[0] + '.pdf',
        )

        if not fname:
            return

        else:
            try:
                # This method will handle the delegation to the correct type
                self.canvas.figure.savefig(fname, saveDMP=saveDMP, PDFembedDMP=PDFembedDMP)
                OMFITaux['lastBrowsedDirectory'] = os.path.split(fname)[0]
            except Exception as _excp:
                from omfit_classes.OMFITx import Dialog

                Dialog(title="Error saving file", messge=repr(_excp), icon='error', answers=['Ok'])
                raise

    def pan(self, *args):
        self.objSelect(None, True)
        self.toolbar.pan(*args)

    def zoom(self, *args):
        self.objSelect(None, True)
        self.toolbar.zoom(*args)

    superzoomed = False

    def superzoom(self, event):
        """
        Enlarge or restore the selected axis.
        """
        if not event.button == middleClickMPLindex:
            return

        full_screen_pos = (0.1, 0.1, 0.85, 0.85)

        # if superzoomed, restore the axes
        if self.superzoomed:
            # resize and make axis visible
            for axis in event.canvas.figure.axes:
                axis.set_position(axis._orig_position)
                axis.set_visible(True)

            self.superzoomed = False

            # redraw the canvas
            event.canvas.draw()
            return

        ax = event.inaxes
        # On middle button click in an axis zoom the selected axes

        if ax is not None:

            for axis in event.canvas.figure.axes:
                axis._orig_position = axis.get_position()
            ax.set_position(full_screen_pos)

            # make all other axes invisible and minimize
            for axis in event.canvas.figure.axes:
                if axis is not ax:
                    axis.set_visible(False)
                    axis.set_position([0, 0.01, 0.01, 0.01])

            self.superzoomed = True

            # redraw the canvas
            event.canvas.draw()

    @property
    def active(self):
        if compare_version(matplotlib.__version__, '3.3.0') >= 0:
            return self.toolbar._button_pressed
        else:
            return self.toolbar._active

    @active.setter
    def active(self, value):
        if compare_version(matplotlib.__version__, '3.3.0') >= 0:
            self.toolbar._button_pressed = value
        else:
            self.toolbar._active = value


# hijack pyplot new_figure_manager_given_figure to make windows transient of rootGUI
def _new_figure_manager_given_figure(*args):
    """
    Create a new figure manager instance for the given figure.
    """
    # older versions of Matplotlib
    if len(args) == 2:
        num = args[0]
        figure = args[1]
    # newer versions of Matplotlib
    else:
        cls = args[0]
        num = args[1]
        figure = args[2]
    try:
        _focus = windowing.FocusManager()
    except Exception:
        pass
    if OMFITaux['rootGUI'] is None:
        window = tk.Tk()
    else:
        window = tk.Toplevel(OMFITaux['rootGUI'])
    window.withdraw()

    if tk.TkVersion >= 8.5:
        # put a mpl icon on the window rather than the default tk icon. Tkinter
        # doesn't allow colour icons on linux systems, but tk >=8.5 has a iconphoto
        # command which we call directly. Source:
        # http://mail.python.org/pipermail/tkinter-discuss/2006-November/000954.html

        if hasattr(matplotlib, 'get_data_path'):
            _mpl_data_path = matplotlib.get_data_path()
        else:
            _mpl_data_path = matplotlib.rcParams['datapath']

        try:
            icon_fname = os.path.join(_mpl_data_path, 'images', 'matplotlib.gif')
            icon_img = tk.PhotoImage(file=icon_fname)
        except tk.TclError:
            try:
                icon_fname = os.path.join(_mpl_data_path, 'images', 'matplotlib.ppm')
                icon_img = tk.PhotoImage(file=icon_fname)
            except tk.TclError:
                pass

        try:
            window.tk.call('wm', 'iconphoto', window._w, icon_img)
        except (SystemExit, KeyboardInterrupt):
            # re-raise exit type Exceptions
            raise
        except Exception:
            # log the failure, but carry on
            # verbose.report('Could not load matplotlib icon: %s' % sys.exc_info()[1])
            pass

    canvas = pyplot._backend_mod.FigureCanvasTkAgg(figure, master=window)
    if hasattr(pyplot._backend_mod, 'FigureManagerTk'):
        figManager = pyplot._backend_mod.FigureManagerTk(canvas, num, window)
    else:
        figManager = pyplot._backend_mod.FigureManagerTkAgg(canvas, num, window)
    if OMFITaux['rootGUI'] is not None:
        tk_center(window, OMFITaux['rootGUI'], xoff=(np.mod(num - 1, 20) - 10) * 25, yoff=(np.mod(num - 1, 10) - 5) * 25)
    if OMFITaux['rootGUI'] is not None and OMFITaux['rootGUI'].globalgetvar('figsOnTop'):
        window.transient(OMFITaux['rootGUI'])
    if matplotlib.is_interactive():
        figManager.show()
    return figManager


if hasattr(matplotlib.backends, '_backend_tk'):
    _patch(matplotlib.backends._backend_tk._BackendTk, _new_figure_manager_given_figure)
else:
    _patch(matplotlib.backends.backend_tkagg, _new_figure_manager_given_figure)
_patch(pyplot._backend_mod, _new_figure_manager_given_figure)

# hijack pyplot new_figure_manager to automatically enable OMFITfigure features on newly created figures
def _new_figure_manager(num, figsize=(8, 6), FigureClass=Figure, **kw):
    figureManager = getattr(matplotlib.backends, 'backend_' + matplotlib.backends.backend.lower()).new_figure_manager(
        num, figsize=figsize, FigureClass=FigureClass, **kw
    )

    if OMFITaux['GUI'] is not None and hasattr(figureManager, 'window'):  # attribute may not be defined depending on the matplotlib backend
        global_event_bindings.add(
            'FIGURE: show next figure', figureManager.window, '<Alt-End>', lambda event=None: OMFITaux['GUI'].selectFigure(action='forward')
        )
        global_event_bindings.add(
            'FIGURE: show previous figure',
            figureManager.window,
            '<Alt-Home>',
            lambda event=None: OMFITaux['GUI'].selectFigure(action='reverse'),
        )
        global_event_bindings.add(
            'FIGURE: bring figures to the top',
            figureManager.window,
            '<Alt-Next>',
            lambda event=None: OMFITaux['GUI'].selectFigure(action='lift'),
        )
        global_event_bindings.add(
            'FIGURE: hide all figures', figureManager.window, '<Alt-Prior>', lambda event=None: OMFITaux['GUI'].selectFigure(action='lower')
        )
        global_event_bindings.add('FIGURE: close all figures', figureManager.window, '<Alt-Escape>', lambda event=None: close('all'))
        global_event_bindings.add(
            'FIGURE: close all figures (alternative)', figureManager.window, f'<{ctrlCmd()}-Escape>', lambda event=None: close('all')
        )

    OMFITfigure(figureManager.canvas.figure)

    return figureManager


_patch(pyplot, _new_figure_manager)
_patch(pylab, _new_figure_manager)

# set fewer ticks locators that the matplotlib default
import matplotlib.axis, matplotlib.scale


def _set_my_locators_and_formatters(self, axis):
    # choose the default locator and additional parameters
    if isinstance(axis, matplotlib.axis.XAxis):
        axis.set_major_locator(pyplot.MaxNLocator(nbins=5))
    elif isinstance(axis, matplotlib.axis.YAxis):
        axis.set_major_locator(pyplot.MaxNLocator(nbins=5))
    # copy&paste from the original method
    axis.set_major_formatter(pyplot.ScalarFormatter())
    axis.set_minor_locator(pyplot.NullLocator())
    axis.set_minor_formatter(pyplot.NullFormatter())


matplotlib.scale.LinearScale.set_default_locators_and_formatters = _set_my_locators_and_formatters

# ----------------
# tabbed figures
# ----------------
_active_FigureNotebooks = {}


class FigureNotebook(object):
    """
    Notebook of simple tabs containing figures.

    """

    def __init__(self, nfig=0, name="", labels=[], geometry="710x710", figsize=(1, 1)):
        """
        :param nfig: Number of initial tabs

        :param name: String to display as the window title

        :param labels: Sequence of labels to be used as the tab labels

        :param geometry: size of the notebook

        :param figsize: tuple, minimum maintained figuresize when resizing tabs

        """
        # if not in a framework graphical environment, FigureNotebook will simply open new figures
        if OMFITaux['rootGUI'] is None:
            matplotlib.rcParams['figure.max_open_warning'] = 100
            return

        if isinstance(nfig, str) and not name:
            name = nfig
            nfig = 0
        if not len(_active_FigureNotebooks):
            self.num = num = 1
        else:
            self.num = num = max(_active_FigureNotebooks.keys()) + 1
        _active_FigureNotebooks[self.num] = self
        self.figsize = figsize
        if OMFITaux['rootGUI'] is None:
            self.master = tk.Tk()
        else:
            self.master = tk.Toplevel(OMFITaux['rootGUI'])
        self.master.withdraw()
        self.master.wm_title(name)
        self.master.geometry(geometry)

        if OMFITaux['rootGUI'] is not None:
            tk_center(self.master, OMFITaux['rootGUI'], xoff=(np.mod(num - 1, 20) - 10) * 25, yoff=(np.mod(num - 1, 10) - 5) * 25)
        if OMFITaux['rootGUI'] is not None and OMFITaux['rootGUI'].globalgetvar('figsOnTop'):
            self.master.transient(OMFITaux['rootGUI'])

        # add the Tkinter GUI tab(s)
        self.notebook = ttk.Notebook(self.master)
        self.figures = SortedDict()
        labels = list(labels)
        for i in range(nfig):
            if len(labels) < i + 1:
                key = "Tab {:}".format(i)
            else:
                key = labels[i]
            self.add_figure(label=key)

        # resize notebook figures with main window
        self._update_size()
        self.master.bind('<Configure>', self._update_size)

        # allow keys to change tabs (ctrl-tab,ctrl-shift-tab)
        self.notebook.enable_traversal()

        self.master.protocol('WM_DELETE_WINDOW', self.close)
        if OMFITaux['GUI'] is not None:
            global_event_bindings.add(
                'FIGURE: show next figure', self.master, '<Alt-End>', lambda event=None: OMFITaux['GUI'].selectFigure(action='forward')
            )
            global_event_bindings.add(
                'FIGURE: show previous figure', self.master, '<Alt-Home>', lambda event=None: OMFITaux['GUI'].selectFigure(action='reverse')
            )
            global_event_bindings.add(
                'FIGURE: bring figures to the top',
                self.master,
                '<Alt-Next>',
                lambda event=None: OMFITaux['GUI'].selectFigure(action='lift'),
            )
            global_event_bindings.add(
                'FIGURE: hide all figures', self.master, '<Alt-Prior>', lambda event=None: OMFITaux['GUI'].selectFigure(action='lower')
            )
            global_event_bindings.add('FIGURE: close all figures', self.master, '<Alt-Escape>', lambda event=None: close('all'))
            global_event_bindings.add(
                'FIGURE: close all figures (alternative)', self.master, f'<{ctrlCmd()}-Escape>', lambda event=None: close('all')
            )

        self.master.deiconify()

    def email(self, event=None):
        try:
            filename = self.canvas.get_default_filename()
        except Exception:
            filename = 'figure.pdf'

        if os.path.exists(OMFITcwd + os.sep + filename):
            os.remove(OMFITcwd + os.sep + filename)
        files = self.savefig(OMFITcwd + os.sep + filename)

        attachments = [OMFITcwd + os.sep + filename] + [os.path.splitext(x)[0] + '.h5' for x in files]

        prjname = ''
        if OMFIT.filename:
            prjname = 'Project: ' + OMFIT.filename

        eml = tk.email_widget(
            parent=self.master,
            fromm=OMFIT['MainSettings']['SETUP']['email'],
            to=OMFIT['MainSettings']['SETUP']['email'],
            subject='OMFIT - Figure: ' + filename,
            message='Attachment: ' + filename + '\n' + '=' * 20 + '\n' + prjname + '\n',
            attachments=attachments,
            title='Email ' + filename,
            use_last_email_to=1,
            quiet=False,
        )
        eml.wait_window(eml)

    def openPDF(self, event=None):
        try:
            filename = self.canvas.get_default_filename()
        except Exception:
            filename = 'figure.pdf'
        if os.path.exists(OMFITcwd + os.sep + filename):
            os.remove(OMFITcwd + os.sep + filename)
        self.savefig(OMFITcwd + os.sep + filename)
        import omfit_classes.OMFITx

        omfit_classes.OMFITx.Open(OMFITcwd + os.sep + filename)

    def close(self):
        """Close the FigureNotebook master window or a tab"""
        self.master.destroy()
        if self.num in _pylab_helpers.Gcf.get_all_fig_managers():
            del _pylab_helpers.Gcf.get_all_fig_managers()[self.num]
        if self.num in _active_FigureNotebooks:
            del _active_FigureNotebooks[self.num]

    def add_figure(self, label="", fig=None, **fig_kwargs):
        """
        Return the figure canvas for the tab with the given label, creating a new tab if that label does not yet exist
        """
        # if not in a framework graphical environment, FigureNotebook will simply open new figures
        if OMFITaux['rootGUI'] is None:
            if fig is not None:
                return fig
            if label == '':
                label = None
            fig_kwargs.setdefault('num', label)
            return pyplot.figure(**fig_kwargs)

        if label in self.figures:
            return self.figures[label]
        fig_kwargs['figsize'] = self.figsize
        tab = tk.Frame(self.notebook)
        if not label:
            label = 'Figure {:}'.format(len(self.figures) + 1)
        self.notebook.add(tab, text=label)
        self.notebook.pack()

        # embed the figure - is this the best way to pass the default figsize and kwargs?
        if fig is None:
            fig = Figure(**fig_kwargs)
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        fig.set_canvas(canvas)
        canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        # Add standard toolbar to plot
        toolbar = NavigationToolbar2(canvas, tab)
        toolbar.update()
        canvas._tkcanvas.pack(side='top', fill='both', expand=1)

        # restore default matplotlib hotkeys
        def on_key_press(self, event):
            matplotlib.backend_bases.key_press_handler(event, self.canvas, self.canvas.toolbar)

        fig.on_key_press = types.MethodType(on_key_press, fig)
        fig.canvas.mpl_connect('key_press_event', fig.on_key_press)

        # Add OMFIT toolbar to plot
        tmp = OMFITfigure(fig.canvas.figure, figureButtons=False)
        self.figures[label] = fig
        tab.figure = fig

        # Override save button
        for k, v in list(toolbar.children.items()):
            try:
                txt = v.config('text')[4]
            except tk.TclError:
                continue
            if txt == 'Save':
                v.config(command=lambda event=None: self.save_figure(toolbar, self))
        # Add open pdf button
        bt = tmp._Button(text="Open PDF", file="pdf.ppm", command=self.openPDF)
        # Add email button
        bt = tmp._Button(text="Email", file="mail.ppm", command=self.email)

        return fig

    @staticmethod
    def save_figure(self, _self, *args):
        # Note that self here is the toolbar

        self.window.tk.eval("catch {tk_getOpenFile foo bar}")
        self.window.tk.eval("catch {tk_getSaveFile foo bar}")
        try:
            self.window.tk.eval("set ::tk::dialog::file::showHiddenVar 0")
            self.window.tk.eval("set ::tk::dialog::file::showHiddenBtn 1")
        except tk.TclError:
            pass

        filetypes = self.canvas.get_supported_filetypes().copy()
        default_filetype = self.canvas.get_default_filetype()

        # Tk doesn't provide a way to choose a default filetype,
        # so we just have to put it first
        default_filetype_name = filetypes[default_filetype]
        del filetypes[default_filetype]

        sorted_filetypes = sorted(list(filetypes.items()))
        sorted_filetypes.insert(0, (default_filetype, default_filetype_name))

        tk_filetypes = [(name, '*.%s' % ext) for (ext, name) in sorted_filetypes]

        for k, item in enumerate(tk_filetypes):
            if item[1] == '*.pdf':
                tk_filetypes.insert(0, tk_filetypes.pop(k))

        # adding a default extension seems to break the
        # asksaveasfilename dialog when you choose various save types
        # from the dropdown.  Passing in the empty string seems to
        # work - JDH
        # defaultextension = self.canvas.get_default_filetype()
        defaultextension = '*.pdf'
        try:
            filename = self.canvas.get_default_filename()
        except Exception:
            filename = 'figure.pdf'
        fname = tkFileDialog.asksaveasfilename(
            master=self.window,
            title='Save the figure',
            filetypes=tk_filetypes,
            defaultextension=defaultextension,
            initialdir=OMFITaux['lastBrowsedDirectory'],
            initialfile=os.path.splitext(filename)[0] + '.pdf',
        )

        if not fname:
            return
        else:
            try:
                # This method will handle the delegation to the correct type
                _self.savefig(fname)
                OMFITaux['lastBrowsedDirectory'] = os.path.split(fname)[0]
            except Exception as _excp:
                from omfit_classes.OMFITx import Dialog

                Dialog(title="Error saving file", messge=repr(_excp), icon='error', answers=['Ok'])
                raise

    def subplots(self, nrows=1, ncols=1, label='', **subplots_kwargs):
        """
        Adds a figure and axes using pyplot.subplots. Refer to pyplot.subplots for documentation
        """
        # if not in a framework graphical environment, FigureNotebook will simply open new figures
        if OMFITaux['rootGUI'] is None:
            if label == '':
                label = None
            subplots_kwargs.setdefault('num', label)
            return pyplot.subplots(nrows=nrows, ncols=ncols, **subplots_kwargs)

        original_figure = pyplot.figure

        def figure_wrapper(**fig_kwargs):
            return self.add_figure(label=label, **fig_kwargs)

        # Modify the figure function that subplots will call
        pyplot.figure = figure_wrapper

        # Add an exception catcher so that the original figure
        # function will successfully be reinstated even if this
        # function is passed some bogus arguments
        try:
            fig, ax = pyplot.subplots(nrows=nrows, ncols=ncols, **subplots_kwargs)
        except Exception as _excp:
            print('Unable to create tabbed subplots: %s' % repr(_excp))
            fig = ax = None
        finally:
            pyplot.figure = original_figure

        return fig, ax

    def _update_size(self, event=None):
        """
        Match notebook size to master window.
        """
        self.master.unbind('<Configure>')
        self.notebook.configure(width=self.master.winfo_width())
        self.notebook.configure(height=self.master.winfo_height())
        self.master.bind('<Configure>', self._update_size)

    def draw(self, ntab=None):
        """
        Draw the canvas in the specified tab. None draws all.

        """
        if ntab == None:
            for f in list(self.figures.values()):
                f.canvas.draw()
        else:
            self.figures[list(self.figures.keys())[ntab]].canvas.draw()

    def __getitem__(self, label):
        if is_int(label):
            label = list(self.figures.keys())[label]
        self.notebook.select(self.figures.index(label))
        return self.figures[label]

    def __setitem__(self, label, fig):
        return self.add_figure(label=label, fig=fig)

    def savefig(self, filename='', **kw):
        r"""
        Call savefig on each figure, with its label appended to filename

        :param filename: The fullpath+base of the filename to save

        :param \*kw: Passed to Figure.savefig
        """
        # need to select and draw individual tabs to make sure the figure is rendered correctly
        tmp = self.notebook.select()
        basefn, ext = os.path.splitext(filename)
        from matplotlib.backends.backend_pdf import PdfPages

        files = []
        with PdfPages(basefn + '.pdf') as pdf:
            for k, (l, f) in enumerate(self.figures.items()):
                self.notebook.select(k)
                self.draw(k)
                files.append((basefn + '__' + str(l)).replace(' ', '_') + ext)
                f.savefig(files[-1], **kw)
                pdf.savefig(f)
            self.notebook.select(tmp)
        return files


# ----------------
# modified pyplot functions
# ----------------
def figure(num=None, figsize=None, dpi=None, facecolor=None, edgecolor=None, frameon=True, FigureClass=Figure, **kw):
    return pyplot._original_figure(
        num=num, figsize=figsize, dpi=dpi, facecolor=facecolor, edgecolor=edgecolor, frameon=frameon, FigureClass=FigureClass, **kw
    )


_patch(pyplot, figure)


def colorbar(mappable=None, cax=None, ax=None, use_gridspec=True, **kw):
    """
    Modified pyplot colorbar for default use_gridspec=True.
    """
    cb = pyplot.colorbar(mappable=mappable, cax=cax, ax=ax, use_gridspec=use_gridspec, **kw)
    return cb


colorbar.__doc__ += '\n**ORIGINAL DOCUMENTATION** \n\n' + pyplot.colorbar.__doc__


def _line_downsample(line, npts):
    """
    Downsample line data for increased plotting speed.

    :param  npts : int. Number of data points within axes xlims.

    """
    lims = line.axes.get_xlim()
    if not hasattr(line, '_xinit'):
        line._xinit = line.get_xdata(orig=False) * 1
        line._yinit = line.get_ydata(orig=False) * 1
        # display notification on first downsampling
        # if line._xinit.shape[0] > npts:
        #    printw("Automatic downsampling to {n} points (use axes.set_downsampling to change)".format(n=npts))
    window = (line._xinit >= lims[0]) & (line._xinit <= lims[1])
    # Extend out edge
    window[window.argmax() - 1] = True
    window[window.argmax() + window[window.argmax() :].argmin()] = True
    # Set index based on step
    step = int(line._xinit[window].size / npts) + 1
    index = set(np.r_[0 : len(line._xinit[window]) : step])
    # Set index based on masked values
    index.update(np.where(np.ma.masked_invalid(line._xinit[window]).mask)[0].tolist())
    index.update(np.where(np.ma.masked_invalid(line._yinit[window]).mask)[0].tolist())
    index = sorted(list(index))
    # Show reduced data
    line.set_xdata(line._xinit[window][index])
    line.set_ydata(line._yinit[window][index])


pyplot.matplotlib.lines.Line2D.downsample = _line_downsample


def _hitlist(self, event):
    """
    List the children of the artist which contain the mouse event *event*.
    """
    L = []

    hascursor, info = self.contains(event)
    if hascursor:
        L.append(self)

    for a in self.get_children():
        L.extend(a.hitlist(event))
    return L


pyplot.matplotlib.artist.Artist.hitlist = _hitlist

# support not-object oriented way of adding subsequent subplots after matplotlib v2.2.2
_orig_subplot = pyplot.subplot


def subplot(*args, **kw):
    try:
        fig = pyplot.gcf()
        if args in fig._stored_axes:
            pyplot.sca(fig._stored_axes[args])
        else:
            _orig_subplot(*args, **kw)
            fig._stored_axes[args] = pyplot.gca()
    except AttributeError:
        _orig_subplot(*args, **kw)
        fig._stored_axes = {}
        fig._stored_axes[args] = pyplot.gca()
    return fig._stored_axes[args]


subplot.__doc__ = pyplot.subplot.__doc__
_patch(pyplot, subplot)
_patch(pylab, subplot)


class quickplot(object):
    """
    quickplot plots lots of data quickly

    :param x: x values

    :param y: y values

    :param ax: ax to plot on

    It assumes the data points are dense in the x dimension
    compared to the screen resolution at all points in the plot.
    It will resize when the axes are clicked on.
    """

    def __init__(self, x, y, ax=None):
        self.x = x
        self.y = y
        if ax is None:
            ax = pyplot.gca()
        self.ax = ax
        self.image = None

        self.plot()
        ax.figure.canvas.mpl_connect('button_release_event', lambda event: self.plot())

    def get_ax_size(self):
        fig = self.ax.figure
        bbox = self.ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        width, height = bbox.width, bbox.height
        width *= fig.dpi
        height *= fig.dpi
        return width, height

    def plot(self):  # replot the axes
        # matplotlib.pyplot.pause(.1)
        x = self.x
        y = self.y
        ax = self.ax
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        if self.image != None:
            self.image.remove()

        x, y = (a[(x > xlim[0]) & (x < xlim[1])] for a in (x, y))
        IMAGE_DIMENSIONS = list(map(int, self.get_ax_size()))
        if (IMAGE_DIMENSIONS[0] * 0 + 10000) > (len(x) / 10.0):
            self.image = ax.plot(x, y)[0]
            return

        def fill(vector):
            listO0s = np.where(vector != np.array([0]))[0]

            if len(listO0s) == 0:
                return np.zeros(len(vector))

            first0, last0 = listO0s[[0, -1]]
            return np.concatenate((np.zeros(first0), np.ones(last0 - first0 + 1), np.zeros(len(vector) - last0 - 1)))

        heatmap, xedges, yedges = np.histogram2d(x, y, bins=IMAGE_DIMENSIONS)
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        filled = np.apply_along_axis(fill, 1, heatmap)

        self.image = ax.imshow(
            ########np.ma.masked_where(
            ########    filled == 0,
            ########    filled
            ########).T,
            filled.T,
            extent=extent,
            origin='lower',
            clim=(0, 1e-0),
            aspect='auto',
            cmap='Greys',
            ########cmap = matplotlib.colors.ListedColormap(
            ########    'k',
            ########    N=1
            # ),
            interpolation='nearest',
        )


if __name__ == '__main__':
    pyplot.plot([0, 1], [0, 1])
    pyplot.show()
