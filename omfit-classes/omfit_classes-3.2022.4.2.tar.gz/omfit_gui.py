import time

t_start_omfit_gui = time.time()
import omfit_tree
from omfit_tree import *
from omfit_tree import _OMFITpython, _OMFITnoSave, _lock_OMFIT_preferences
from omfit_classes.utils_base import _streams
from utils_widgets import _defaultFont
import utils_tk
from omfit_classes.omfit_python import help
from collections.abc import Callable as CollectionsCallable
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

print('Loading OMFIT GUI...')

# ---------------------
# Git and splash screen
# ---------------------
def splash(rootGUI, onCloseFunction=None):
    # get list of installed packages
    installed_packages = check_installed_packages()

    # build GUI
    width = 500

    t_start_splash_GUI = time.time()

    def destroy():
        top.destroy()
        if onCloseFunction:
            onCloseFunction()

    top = tk.Toplevel()
    top.withdraw()
    top.wm_transient(rootGUI)
    top.wm_title('')

    txtheader = tk.StringVar()

    frm = ttk.Frame(top)
    frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=20, pady=10)
    logo = ttk.Label(master=frm, text='OMFIT', font=OMFITfont('bold', 10), width=width + 100)
    logo.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
    try:
        im = tk.PhotoImage(master=frm, file=os.path.join(OMFITsrc, 'extras', 'graphics', 'OMFIT_logo_color.gif'))
        logo.configure(image=im)
        logo._ntimage = im
    except Exception:
        pass
    ttk.Label(frm, text='One Modeling Framework for Integrated Tasks', font=OMFITfont('bold', 2)).pack(
        side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=20, pady=10
    )
    if 'conda' in sys.version.lower():
        ttk.Label(frm, text='Powered by python installed by conda').pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=20, pady=10)

    def doSomething():
        tab_selected = notebook.tab(notebook.tabs().index(notebook.select()))['text']
        for k in tab:
            tab[k].pack_forget()
        if tab_selected in tab:
            tab[tab_selected].pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

    tab = {}
    notebook = ttk.Notebook(frm)
    notebook.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
    notebook.add(ttk.Frame(top), text="What's new")
    notebook.add(ttk.Frame(top), text='About')
    notebook.add(ttk.Frame(top), text='Users agreement')
    notebook.bind("<<NotebookTabChanged>>", lambda event: doSomething())

    # =================
    tab["About"] = topfrm = ttk.Frame(frm)
    txt = tk.ScrolledText(topfrm, wrapButton='char', wrap='none', font=OMFITfont(family='Courier'))
    txt.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
    s = 'System'.ljust(22) + ': %s\n\n' % (' '.join(platform.uname()))
    s += 'Python'.ljust(22) + ': %s\n\n' % sys.executable
    s += 'Installation type'.ljust(22) + ': %s\n\n' % (['PERSONAL', 'PUBLIC'][os.path.exists(os.sep.join([OMFITsrc, '..', 'public']))])
    s += 'Repository'.ljust(22) + ': %s\n\n' % repo_str
    s += 'OMFIT project'.ljust(22) + ': %s\n\n' % str(OMFIT.filename)
    s += 'OMFIT project size'.ljust(22) + ': %s\n\n' % str(sizeof_fmt(OMFIT.filename))
    s += 'Memory usage'.ljust(22) + ': %s\n\n' % memuse()
    for _n, _k in enumerate(installed_packages_summary_as_text(installed_packages).split('\n')):
        s += ['', 'Installed packages'][_n == 0].ljust(22) + ': %s\n' % _k
    s += '\n'
    from omfit_classes.startup_framework import _OMFIT_important_directories

    for _k in _OMFIT_important_directories:
        s += _k.ljust(22) + ': %s\n\n' % eval(_k)
    txt.insert(1.0, s)

    # =================
    tab["Users agreement"] = topfrm = ttk.Frame(frm)
    with open(OMFITsrc + os.sep + '..' + os.sep + 'LICENSE.rst', 'r') as _f:
        motd = _f.read()
    txt = tk.ScrolledText(topfrm, wrapButton='word', wrap='word')
    txt.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
    txt.insert(1.0, motd.strip())

    # =================
    tab["What's new"] = topfrm = ttk.Frame(frm)
    if repo is None:

        ttk.Label(topfrm, text='WARNING!', font=OMFITfont('bold', 10)).pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        motd = (
            "This installation of OMFIT is not running from a git repository!?\n"
            "(or perhaps your git installation is not working properly)\n\n"
            "OMFIT should always be run from a git repository so that you "
            "can keep it up-to-date and contribute to it's development :)\n\n"
            "Have you read the OMFIT user agreement?"
        )

        ttk.Label(topfrm, text=motd.strip(), wraplength=width).pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

    else:
        topfrm.grid_rowconfigure(1, weight=1)
        topfrm.grid_columnconfigure(0, weight=1)
        yscrollbar = ttk.Scrollbar(topfrm)
        yscrollbar.grid(row=1, column=1, sticky=tk.N + tk.S + tk.W)
        canvas = tk.Canvas(topfrm, bd=0, yscrollcommand=yscrollbar.set)
        canvas.grid(row=1, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        yscrollbar.config(command=canvas.yview)
        taskGUIframeInterior = ttk.Frame(canvas)
        taskGUIframeInterior.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        parentGUI = taskGUIframeInterior
        interior_id = canvas.create_window(0, 0, anchor=tk.NW, window=taskGUIframeInterior)

        cdate = ''
        commits, messages, authors, dates, tag_commits = repo.get_visible_commits()
        OMFITaux['cframes'] = []
        dates = list(map(float, dates))
        for k, (commit, message_orig, author, date) in enumerate(zip(commits, messages, authors, dates)):
            bgcolor = 'gray95'

            ctype, summary, message, ctype_color = parse_git_message(message_orig, commit, tag_commits)

            if message[0].strip() == summary:
                title = summary.strip()
                text = '\n'.join(message[1:]).strip()
            else:
                title = ''
                text = message_orig.strip()

            if ctype.lower() not in ['hide', 'hidden', 'minor'] and (commit in tag_commits or not re.match("Merge .*", title)):
                _cdate = '\t'
                if cdate != time.strftime("%a, %d %b %Y", time.localtime(date)):
                    _cdate = cdate = time.strftime("%a, %d %b %Y", time.localtime(date))
                    bgcolor = 'gray90'

                cframe = ttk.Frame(parentGUI, relief=tk.RAISED, border=1, cursor="question_arrow")
                cframe.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=2)
                OMFITaux['cframes'].append(cframe)

                tframe = ttk.Frame(cframe)
                tframe.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=5)

                t1frame = ttk.Frame(tframe)
                t1frame.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)

                ctime = time.strftime("%H:%M", time.localtime(date))
                lbl = ttk.Label(
                    t1frame, text=_cdate + '\t' + ctime, justify=tk.LEFT, anchor=tk.W, font=OMFITfont('bold', 0), wraplength=width
                )
                lbl.pack(side=tk.LEFT)

                lbl = ttk.Label(
                    t1frame, text=ctype, justify=tk.RIGHT, anchor=tk.E, font=OMFITfont('bold', 0), wraplength=width, foreground=ctype_color
                )
                lbl.pack(side=tk.RIGHT)

                author = author.strip()
                if commit in tag_commits:
                    pass
                else:
                    lbl = ttk.Label(tframe, text=author, justify=tk.RIGHT, anchor=tk.E, font=OMFITfont('normal', -2), wraplength=width)
                    lbl.pack(side=tk.BOTTOM, expand=tk.NO, fill=tk.X)

                if commit in tag_commits:
                    lbl = ttk.Label(
                        cframe,
                        text=repo.tag.splitlines()[tag_commits.index(commit)],
                        justify=tk.LEFT,
                        anchor=tk.W,
                        font=OMFITfont('bold', 0),
                        wraplength=width,
                    )
                    lbl.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=10)
                else:
                    lbl = ttk.Label(cframe, text=title, justify=tk.LEFT, anchor=tk.W, font=OMFITfont('bold', 0), wraplength=width)
                    lbl.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=10)

                # make commits inspectable
                def traverse_items(item, ki):
                    item.bind('<Button-1>', lambda event, top=top: git_diff_viewer(commits[ki], commits[ki] + '~', parentGUI=top))
                    if hasattr(item, 'winfo_children'):
                        for kid in item.winfo_children():
                            traverse_items(kid, ki)

                traverse_items(cframe, k)

        canvas.update_idletasks()
        top.configure(
            width=taskGUIframeInterior.winfo_reqwidth() + yscrollbar.winfo_width() + 40, height=taskGUIframeInterior.winfo_reqheight()
        )
        canvas.configure(width=taskGUIframeInterior.winfo_reqwidth(), height=300)

        def configure_size():
            canvas.update_idletasks()
            canvas.configure(scrollregion=(0, 0, top.winfo_width() + 40, taskGUIframeInterior.winfo_reqheight()))
            canvas.itemconfigure(
                interior_id, width=top.winfo_width() - 40 - yscrollbar.winfo_width(), height=taskGUIframeInterior.winfo_reqheight()
            )
            canvas.update_idletasks()

        canvas.bind('<Configure>', lambda event: configure_size())

        def mouse_wheel(event):
            # respond to Linux or Windows wheel event
            if event.num == 5 or event.delta == -120:
                canvas.yview('scroll', 1, 'units')
            if event.num == 4 or event.delta == 120:
                canvas.yview('scroll', -1, 'units')

        top.bind("<MouseWheel>", mouse_wheel)
        top.bind("<Button-4>", mouse_wheel)
        top.bind("<Button-5>", mouse_wheel)

    projects = OMFIT.recentProjects()
    if len(projects):

        def open_projects():
            top.destroy()
            OMFITaux['GUI'].loadOMFIT()

        def open_recent_project():
            top.destroy()
            OMFITaux['GUI']._loadOMFITproject(project, persistent_projectID=projects[project].get('persistent_projectID', False))

        projectname = project = list(projects.keys())[0]
        if projectname.endswith('OMFITsave.txt'):
            projectname = os.path.split(projectname)[0]
        projectname = os.path.split(projectname)[1]
        pjFrame = ttk.Frame(top)
        pjFrame.pack(side=tk.TOP, fill=tk.X)
        allProjects = ttk.Button(pjFrame, text='Open project...', command=open_projects)
        allProjects.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH, padx=(20, 5), pady=5)
        lastProject = ttk.Button(pjFrame, text='Open most recent project: ' + projectname, command=open_recent_project)
        lastProject.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH, padx=(5, 20), pady=5)

    def import_modules():
        top.destroy()
        OMFITaux['GUI'].loadOMFIT('module')

    importmodule = ttk.Button(top, text='Import module...', command=import_modules)
    importmodule.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=20, pady=5)
    continueButton = ttk.Button(top, text='Continue to OMFIT >>>', command=destroy)
    continueButton.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=20, pady=5)

    if len(installed_packages['bad']):

        def print_install():
            OMFIT['installed_packages'] = installed_packages
            for line in installed_packages_summary_as_text(installed_packages).split('\n'):
                if '(!)' in line:
                    printe(line)
                else:
                    printw(line)
            if os.path.exists(os.sep.join([OMFITsrc, '..', 'public'])) and OMFIT['MainSettings']['SETUP']['institution'] != 'PERSONAL':
                printi('It appears you are running a PUBLIC OMFIT installation at %s' % OMFIT['MainSettings']['SETUP']['institution'])
                if len(OMFIT['MainSettings']['SETUP']['report_to']):
                    printi(
                        'Please contact %s to have this OMFIT running environment checked and updated\n Or'
                        % ', '.join(tolist(OMFIT['MainSettings']['SETUP']['report_to']))
                    )
                print('file this discrepancy @ https://github.com/gafusion/OMFIT-source/issues ')
                print('Your feedback is critical to help maintain this installation at optimal performance.')
            else:
                printi('It appears you are running your own OMFIT installation')
                printi('Visit https://omfit.io/install.html to learn how to update your envionment')
            OMFITaux['GUI'].update_treeGUI()
            destroy()

        installButton = ttk.Button(
            top, text='WARNING: Outdated OMFIT core Python environment', command=print_install, style='flatwarning.TButton'
        )
        installButton.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=20, pady=5)

    top.bind('<Escape>', lambda event: destroy())
    top.protocol("WM_DELETE_WINDOW", destroy)
    top.update_idletasks()
    top.deiconify()
    top.resizable(width=False, height=False)
    sys.__stdout__.write('Time to load splash screen: %g seconds\n' % (time.time() - t_start_splash_GUI))
    sys.__stdout__.flush()
    return top


def git_diff_viewer(commit1, commit2, git_dir=None, parentGUI=None):
    """
    Open a visual representation of the difference between two git commits of the
        git repo at `git_dir`

    :param commit1: The reference (hash, tag, branch) of commit1 (presented as the later commit)
    :param commit2: The reference (hash, tag, branch) of commit2
    :param git_dir: The root directory of the desired git repo (`None` means the OMFIT repo)

    :return: None
    """
    from omfit_tree import repo

    if git_dir is not None:
        repo = OMFITgit(git_dir)
    diff_str = repo('diff --patch %s..%s' % (commit2, commit1))
    DiffViewer(diff_str, message=repo.get_commit_message(commit1), parentGUI=parentGUI)


def DiffViewer(diff_str, message='', parentGUI=None):
    """
    Present the `diff_str` patch visually, with additions as green, and subtractions as red

    :param diff_str: A string in patch format, of the difference between two strings
    :param message: The string to put as a title (to give context to the diff)
    :param parentGUI: A tk widget, to be used as the parent GUI

    :return: None
    """
    inputDiffText = diff_str.splitlines(True)
    top = tk.Toplevel(parentGUI)
    top.withdraw()
    top.transient(parentGUI)
    top.geometry(str(int(OMFITaux['rootGUI'].winfo_width() * 8.0 / 9.0)) + "x" + str(int(OMFITaux['rootGUI'].winfo_height() * 8.0 / 9.0)))
    top.wm_title('Git Diff commits')

    message = re.sub(r'<<<>>>(.*)<<<>>>', r'\n<<<>>>\1<<<>>>', message)
    ctype = re.findall(r'<<<>>>.*<<<>>>', message, re.MULTILINE | re.DOTALL)
    if len(ctype):
        message = message.replace(ctype[0], '')
    message = message.strip()

    # GUI items
    ttk.Label(top, text=message, font=OMFITfont('bold', 2)).pack()
    text = tk.ScrolledText(top, relief=tk.SOLID, borderwidth=1, font=OMFITfont('normal', 0, 'Courier'), wrap=tk.NONE)
    text.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

    # colors
    text.tag_configure('+', background='DarkSeaGreen1')
    text.tag_configure('-', background='RosyBrown2')
    text.tag_configure('?', background='light blue')
    text.tag_configure(' ', background='white')
    text.tag_configure('/', background='gray85')
    text.tag_configure('@', background='light blue')

    # differences
    offset = 1
    lines = 0
    for item in inputDiffText:
        if item[:3] == '+++' or item[:3] == '---':
            text.insert('end', item, '/')
            lines += 1
        elif item[0] == '+':
            text.insert('end', item[offset:], '+')
            lines += 1
        elif item[0] == '-':
            text.insert('end', item[offset:], '-')
            lines += 1
        elif item[0] == '?':
            for k, c in enumerate(item[offset:]):
                if c in ['-', '+', '^']:
                    text.tag_add('?', str(lines) + '.' + str(k))
        elif item[0] == '@':
            text.insert('end', item, '@')
            lines += 1
        elif item[0].startswith(' ' * offset):
            text.insert('end', item[offset:])
            lines += 1
        else:
            text.insert('end', item)
            lines += 1

    text.config(state=tk.DISABLED)

    top.bind('<Escape>', lambda event: top.destroy())

    top.protocol("WM_DELETE_WINDOW", top.destroy)
    top.update_idletasks()
    tk_center(top, parentGUI)
    top.deiconify()
    top.wait_window(top)


class EditEntryPopup(ttk.Frame):
    """
    Build EditEntryPopup GUI to edit OMFIT tree enties in-line
    """

    def __init__(self, parent, rowid, text, dynamic, **kw):
        ttk.Frame.__init__(self, parent, **kw)

        self.entry = tk.OneLineText(self, **kw)
        self.entry.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
        self.entry.set(text)

        self.controls = ttk.Frame(self)
        self.controls.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)

        self.dynamic = tk.BooleanVar()
        self.dynamic.set(dynamic)
        ck = ttk.Checkbutton(self.controls, text="Dynamic expression", variable=self.dynamic)
        ck.state(['!alternate'])  # removes color box bg indicating user has not clicked it, which may confuse people
        ck.pack(side=tk.LEFT)

        def onReturn():
            tmp = parseLocation('OMFIT' + rowid)
            if not self.entry.get().strip():
                eval(buildLocation(tmp[:-1])).__delitem__(tmp[-1])
            elif self.dynamic.get():
                eval(buildLocation(tmp[:-1]))[tmp[-1]] = eval('OMFITexpression(self.entry.get())')
            else:
                eval(buildLocation(tmp[:-1]))[tmp[-1]] = eval(self.entry.get())
            self.event_generate("<<update_treeGUI>>")
            self.destroy()
            OMFITaux['GUI'].force_tree_focus()
            return 'break'

        def destroy():
            OMFITaux['GUI'].force_tree_focus()
            self.destroy()

        self.entry.focus_force()
        self.entry.bind('<Return>', lambda event: onReturn())
        self.entry.bind('<KP_Enter>', lambda event: onReturn())
        self.entry.bind("<Escape>", lambda event: destroy())


def tree_entry_repr(obj, tp=None):
    """
    returns string representation of OMFIT tree entry

    :param obj: object

    :param tp: externally defined user class (overrides object class)

    :return: string representation of OMFIT tree entry
    """
    if tp is None:
        tp = obj.__class__.__name__
    dynamic = False
    if isinstance(obj, OMFITexpression):
        value = obj.expression
        dynamic = True
    elif isinstance(obj, OMFITwebLink):
        value = repr(obj)
    elif isinstance(obj, str):
        value = repr(obj)
    elif isinstance(obj, OMFITtypes):
        value = tp + '(' + ','.join([_f for _f in [repr(obj.filename), keyword_arguments(obj.__save_kw__())] if _f]) + ')'
    elif isinstance(obj, OMFITosborneProfile):
        value = (
            "OMFITosborneProfile(server="
            + repr(obj.server)
            + ", treename="
            + repr(obj.treename)
            + ", shot="
            + repr(obj.shot)
            + ', time='
            + repr(obj.time)
            + ', runid='
            + repr(obj.runid)
            + ')'
        )
    elif isinstance(obj, (OMFITmds, OMFITmdsValue)):
        value = obj.__class__.__name__ + "(" + keyword_arguments(obj.__save_kw__()) + ")"
    elif isinstance(obj, OMFITrdb):
        value = (
            "OMFITrdb(query=\""
            + obj.query
            + "\", db="
            + repr(obj.db)
            + ", server="
            + repr(obj.server)
            + ", by_column="
            + str(obj.by_column)
            + ")"
        )
    elif isinstance(obj, (OMFITharvest, OMFITharvestS3)):
        value = repr(obj)
    elif isinstance(obj, uncertainties.core.AffineScalarFunc):
        if getattr(obj, 'tag', None):
            value = 'ufloat(nominal_value=%r,std_dev=%r,tag=%r)' % (obj.n, obj.s, getattr(obj, 'tag', None))
        else:
            value = 'ufloat(%r,%r)' % (obj.n, obj.s)
    elif obj is None:
        value = 'None'
    elif isinstance(obj, (OMFITtree, ODS)):
        value = tp + '()'
    else:
        value = repr(obj)
    return value, dynamic


def virtualKeys(f):
    """
    :param f: function to decorate

    :return: decorated function
    """

    @functools.wraps(f)
    def treevirtualKeys(self, *args, **kw):
        bkp = OMFITaux['virtualKeys']
        OMFITaux['virtualKeys'] = True
        try:
            return f(self, *args, **kw)
        finally:
            OMFITaux['virtualKeys'] = bkp

    return treevirtualKeys


# ---------------------
# Main GUI
# ---------------------
class OMFITgui(object):
    def __init__(self, rootGUI):
        self.rootGUI = rootGUI
        self.treeGUI = None
        self.popup = None
        self.console = None
        self.lockSave = False

        self.focus = ''
        self.focusRoot = ''
        self.focusRootRepr = ''
        self.linkToFocus = None

        self.rootGUI.copiedName = ''
        self.rootGUI.copiedWhat = ''

        self.browserSearch = ''
        self.opened_closed = {}
        self.opened_closed_bkp = None
        self.match_query = None
        self.search_F3 = 0
        self.searchLocation = None
        self.onlyTree = None
        self.commandBoxNamespace = None
        self.clear_close_button = None
        self.parent_tags = {}
        self.attributes = {}

        self.tabID = 0
        self.focus_view = []
        self.opened_closed_view = []
        self.vScroll_view = []
        self.hScroll_view = []
        self.onlyTree_view = []
        self.notes = None
        self.terminal = None

        self.remoteSelectorVariable = tk.StringVar()
        self.branchSelectorVariable = tk.StringVar()
        self.pushRemoteSelectorVariable = tk.StringVar()
        self.pushBranchSelectorVariable = tk.StringVar()

        self.cmap = default_matplotlib_cmap_cycle
        self.ncmap = 10
        self.x = None
        self.xName = None
        self.y = None
        self.yName = None
        self.z = None
        self.zName = None
        self.normPlotAxis = tk.BooleanVar()
        self.normPlotAxis.set(False)
        self.compoundStyles = tk.BooleanVar()
        self.compoundStyles.set(False)
        self.figsOnTop = tk.BooleanVar(name='figsOnTop')
        self.figsOnTop.set(OMFIT['MainSettings']['SETUP']['GUIappearance']['figures_on_top'])
        self.drag = None
        self.editEntryPopup = None

        self.omfitdebug_logs = tk.StringVar()
        self.omasdebug_logs = tk.StringVar()

        self.command = []
        self.commandActive = 0
        self.commandNames = []
        self.showHidden = False
        self.showHiddenCk = None
        self.showType = True
        self.showTypeCk = None
        self.saveZip = False
        self.lastRunScriptFromGUI = None
        self.autoSaveAlarm = None
        self.autoTouchAlarm = None
        self.memory_history = []

        self.build_OMFIT_GUI()

        self.newProjectModule(interactive=False)

        self.events_treeGUI()
        self.dropdownMenu()

        self.keepAlive()
        self.autoSave()
        self.autoTouch(trigger=False)

        omfit_log('started session', 't_startup=%s' % (time.time() - t_start_omfit_gui))

    def dropdownMenu(self):
        menubar = tk.Menu(self.rootGUI)

        # ---------------------------
        # file
        # ---------------------------
        filemenu = tk.Menu(menubar, tearoff=False)

        def cycle_color():
            top = tk.Toplevel(self.rootGUI)
            top.withdraw()
            top.transient(self.rootGUI)
            top.wm_title('Colormap color cycle')

            ncolors = tk.StringVar()
            ncolors.set(self.ncmap)
            reverse = tk.BooleanVar()
            reverse.set(False)

            def setCmap():
                try:
                    nc = np.linspace(0, 1, max([int(ncolors.get()), 1]))
                except Exception:
                    nc = 1
                a = np.outer(nc, np.ones(1)).T
                axx = fig.add_subplot(111)
                if reverse.get():
                    axx.imshow(a, aspect='auto', cmap=pyplot.get_cmap(cmap.get()).reversed(), origin="lower", interpolation='nearest')
                else:
                    axx.imshow(a, aspect='auto', cmap=pyplot.get_cmap(cmap.get()), origin="lower", interpolation='nearest')
                axx.axis("off")
                fig.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=1.0, hspace=0.0, wspace=1.0)
                fig.canvas.draw()

            try:
                self.ncmap = max([1, int(self.ncmap)])
            except Exception:
                self.ncmap = 10
            if '_r' in self.cmap[-2:]:
                reverse.set(True)
                self.cmap = self.cmap[:-2]

            tab = ttk.Frame(top)
            tab.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=2)
            fig = matplotlib.figure.Figure(figsize=(5, 0.25))
            canvas = FigureCanvasTkAgg(fig, master=tab)
            canvas.draw()
            fig.set_canvas(canvas)
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            cmaps = sorted([m for m in matplotlib.pyplot.colormaps() if not m.endswith("_r")])

            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
            ttk.Label(frm, text='Colormap: ').pack(side=tk.LEFT)
            cmap = ttk.Combobox(frm, state='readonly')
            cmap.bind('<<ComboboxSelected>>', lambda event: setCmap())
            cmap.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
            cmap.configure(values=tuple(cmaps))
            cmap.set(self.cmap)

            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
            ck = ttk.Checkbutton(frm, variable=reverse, command=setCmap, text='Reverse colors order')
            ck.state(['!alternate'])  # removes color box bg indicating user has not clicked it, which may confuse people
            ck.pack(side=tk.LEFT, padx=5, pady=2)

            def default_color(what=None):
                reset = {'fills': ['image.cmap'], 'lines': ['axes.prop_cycle', 'axes.color_cycle', 'lines.cmap']}
                reset[None] = reset['fills'] + reset['lines']
                for item in reset[what]:
                    if item in OMFIT['MainSettings']['SETUP']['PlotAppearance']:
                        del OMFIT['MainSettings']['SETUP']['PlotAppearance'][item]
                if what in ['lines', None]:
                    printi('Reset default colors for lines: ' + str(list(map(str, default_matplotlib_line_cycle))))
                if what in ['fills', None]:
                    printi('Reset default colors for fills: ' + default_matplotlib_cmap_cycle)
                self.update_treeGUI()

            def onReturn(what=None):
                try:
                    self.cmap = cmap.get() + '_r' * reverse.get()
                    if what in ['lines', None]:
                        OMFIT['MainSettings']['SETUP']['PlotAppearance']['lines.cmap'] = (self.cmap, eval(ncolors.get()))
                        printi('Set default colors for lines: ' + self.cmap + ' in ' + ncolors.get() + ' steps')
                    if what in ['blind', None]:
                        OMFIT['MainSettings']['SETUP']['PlotAppearance']['lines.cmap'] = ('blind', 10)
                        printi('Set default colors for lines: color blind')
                    if what in ['fills', None]:
                        OMFIT['MainSettings']['SETUP']['PlotAppearance']['image.cmap'] = self.cmap
                        printi('Set default colors for fills: ' + self.cmap)
                    self.update_treeGUI()
                    if what is None:
                        top.destroy()
                except Exception:
                    raise

            def onEscape():
                top.destroy()

            ttk.Separator(top).pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
            ttk.Label(frm, text='Fills colors ', font=OMFITfont('bold')).pack(side=tk.LEFT)
            frm = ttk.Frame(frm)
            frm.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
            ttk.Button(frm, text='Apply colormap', command=lambda: onReturn(what='fills')).pack(
                side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO
            )
            ttk.Button(frm, text='Default colormap (%s)' % default_matplotlib_cmap_cycle, command=lambda: default_color(what='fills')).pack(
                side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO
            )

            ttk.Separator(top).pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
            ttk.Label(frm, text='Lines colors ', font=OMFITfont('bold')).pack(side=tk.LEFT)
            frm = ttk.Frame(frm)
            frm.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

            frm1 = ttk.Frame(frm)
            frm1.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
            ttk.Label(frm1, text='Number of cycling colors in gradient: ').pack(side=tk.LEFT)
            e1 = ttk.Entry(frm1, textvariable=ncolors, width=30)
            e1.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
            e1.focus_set()
            ttk.Button(frm, text='Gradient color cycle', command=lambda: onReturn(what='lines')).pack(
                side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO
            )
            ttk.Separator(frm).pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
            ttk.Button(frm, text='Default color cycle', command=lambda: default_color(what='lines')).pack(
                side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO
            )
            ttk.Button(frm, text='Color-blind color cycle', command=lambda: onReturn(what='blind')).pack(
                side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO
            )

            top.bind('<KP_Enter>', lambda event: onReturn())
            top.bind('<Escape>', lambda event: onEscape())
            top.bind('<Key>', lambda event: setCmap())

            top.protocol("WM_DELETE_WINDOW", top.destroy)
            top.update_idletasks()
            tk_center(top, self.rootGUI)
            top.deiconify()
            setCmap()
            top.wait_window(top)

        def productivity():
            pyplot.figure(num='OMFIT productivity diagram')
            ax = pyplot.gca()

            x1 = np.linspace(-2, 10, 100)
            x = np.linspace(0, 10, 100)
            ax.plot(x1, x1 * 0.001 + 0.5, 'b', lw=1, label='The usual way  ')
            ax.plot(x, 0.35 * (0.1 ** (0.3 * x) + 2 * np.tanh(x - 5) + 1 + (x > 5) * x * 0.2) + 0.5, 'r', lw=1, label='The OMFIT way')

            ax.set_xlabel('Time   ')
            ax.set_ylabel('Productivity   ')
            ax.set_title('OMFIT users\nevolution of feelings')

            ax.legend(loc=0).set_draggable(True)

            pyplot.annotate("denial", [-2, 0.55], xytext=[-2, 1], arrowprops=dict(facecolor='black', shrink=0.05))
            pyplot.annotate("curiosity", [0.1, 0.55], xytext=[1, 1], arrowprops=dict(facecolor='black', shrink=0.05))
            pyplot.annotate("skepticism", [2.5, 0.2], xytext=[2.5, -0.5], arrowprops=dict(facecolor='black', shrink=0.05))

            pyplot.annotate("excitement", [4.5, 0.45], xytext=[5, 0.2], arrowprops=dict(facecolor='black', shrink=0.05))
            pyplot.annotate("amazement", [5.0, 1], xytext=[7, 1], arrowprops=dict(facecolor='black', shrink=0.05))
            pyplot.annotate("realization", [10, 2.2], xytext=[8, 1.8], arrowprops=dict(facecolor='black', shrink=0.05))

            # excitement

            ax.set_xlim(-1, 10)
            ax.set_ylim(-0.5, 2)

            # XKCDify the axes -- this operates in-place
            XKCDify(ax, xaxis_loc=0.0, yaxis_loc=0.0, xaxis_arrow='+-', yaxis_arrow='+-', expand_axes=True)

        filemenu.add_command(
            label="New project", command=self.newProjectModule, accelerator=global_event_bindings.get('GLOBAL: new project')
        )
        filemenu.add_command(label="Open project...", command=self.loadOMFIT, accelerator=global_event_bindings.get('GLOBAL: open project'))
        filemenu.add_command(label="Save project", command=self.quickSave, accelerator=global_event_bindings.get('GLOBAL: save project'))
        filemenu.add_command(label="Save project as...", command=self.saveOMFITas)
        filemenu.add_command(label="Save remote copy of project...", command=OMFIT.deployGUI)
        filemenu.add_separator()
        filemenu.add_command(label="Compare to project...", command=lambda: self.loadOMFIT(action='compare'))
        filemenu.add_separator()
        filemenu.add_command(
            label="New module...",
            command=lambda: self.newProjectModule('module'),
            accelerator=global_event_bindings.get('GLOBAL: new module'),
        )
        filemenu.add_command(
            label="Import module...",
            command=lambda: self.loadOMFIT('module'),
            accelerator=global_event_bindings.get('GLOBAL: import module'),
        )
        filemenu.add_command(
            label="Reload modules...",
            command=lambda: self.OMFITmodules('reload'),
            accelerator=global_event_bindings.get('GLOBAL: reload module'),
        )
        filemenu.add_command(
            label="Export modules...",
            command=lambda: self.OMFITmodules('export'),
            accelerator=global_event_bindings.get('GLOBAL: export module'),
        )
        filemenu.add_separator()
        filemenu.add_command(label="Load regression script...", command=self.loadOMFITregression)
        filemenu.add_separator()
        filemenu.add_command(label="Reset SSH tunnels, database connections", command=lambda: OMFIT.reset_connections(mds_cache=False))
        filemenu.add_separator()
        filemenu.add_command(label="Preferences...", command=lambda: OMFIT['scratch']['__preferencesGUI__'].run())
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=self.quit_clean, accelerator=global_event_bindings.get('GLOBAL: quit'))

        def update():
            self.force_selection()
            # export/reload modules
            if len(OMFIT.moduleDict()):
                filemenu.entryconfig(10, state=tk.NORMAL)
                filemenu.entryconfig(11, state=tk.NORMAL)
            else:
                filemenu.entryconfig(10, state=tk.DISABLED)
                filemenu.entryconfig(11, state=tk.DISABLED)
            # save
            if OMFIT.filename == '' or not os.access(OMFIT.filename, os.W_OK):
                filemenu.entryconfig(2, state=tk.DISABLED)
            else:
                filemenu.entryconfig(2, state=tk.NORMAL)

        filemenu.config(postcommand=update)
        menubar.add_cascade(label="File", menu=filemenu)

        # ---------------------------
        # edit
        # ---------------------------
        editmenu = tk.Menu(menubar, tearoff=False)

        editmenu.add_command(label="Edit tree entry (Browse) ...", command=self.itemSetup)
        editmenu.add_command(
            label="Edit tree entry (Guided) ...",
            command=lambda: self.itemSetupOld(GUItype='guided'),
            accelerator=global_event_bindings.get('TREE: edit tree entry'),
        )
        editmenu.add_command(
            label="Edit tree entry (Advanced) ...",
            command=lambda: self.itemSetupOld(GUItype='advanced'),
            accelerator=global_event_bindings.get('TREE: edit tree entry'),
        )
        editmenu.add_separator()
        editmenu.add_command(
            label='Copy tree location',
            command=lambda: self.clipboard(what='location'),
            accelerator=global_event_bindings.get('TREE: copy location'),
        )
        editmenu.add_command(
            label='Copy tree location from root',
            command=lambda: self.clipboard(what='root'),
            accelerator=global_event_bindings.get('TREE: copy location from root'),
        )
        editmenu.add_command(
            label='Copy tree location tip',
            command=lambda: self.clipboard(what='tip'),
            accelerator=global_event_bindings.get('TREE: copy location tip'),
        )
        editmenu.add_command(
            label='Copy tree value', command=lambda: self.clipboard(what='value'), accelerator=global_event_bindings.get('TREE: copy value')
        )

        def update():
            self.force_selection()
            # copy
            if not len(self.focus):
                editmenu.entryconfig(4, state=tk.DISABLED)
                editmenu.entryconfig(5, state=tk.DISABLED)
                editmenu.entryconfig(6, state=tk.DISABLED)
            else:
                editmenu.entryconfig(4, state=tk.NORMAL)
                editmenu.entryconfig(5, state=tk.NORMAL)
                editmenu.entryconfig(6, state=tk.NORMAL)

        editmenu.config(postcommand=update)
        menubar.add_cascade(label="Edit", menu=editmenu)

        # ---------------------------
        # plotting
        # ---------------------------
        plotmenu = tk.Menu(menubar, tearoff=False)
        plotmenu.add_command(label="Quick plot", command=self.quickPlotF, accelerator=global_event_bindings.get('TREE: execute/plot'))
        plotmenu.add_command(label="Quick over-plot", command=self.quickPlot, accelerator=global_event_bindings.get('TREE: over plot'))
        plotmenu.add_command(
            label="Set X", command=lambda: self.quickPlotX(action='setX'), accelerator=global_event_bindings.get('TREE: set plot X')
        )
        plotmenu.add_command(
            label="Set Y", command=lambda: self.quickPlotX(action='setY'), accelerator=global_event_bindings.get('TREE: set plot Y')
        )
        plotmenu.add_command(
            label="Set Z", command=lambda: self.quickPlotX(action='setZ'), accelerator=global_event_bindings.get('TREE: set plot Z')
        )
        plotmenu.add_command(label="Clear X, Y, Z", command=lambda: self.quickPlotX(action='clear'))
        plotmenu.add_checkbutton(label="Use normalized axis", onvalue=True, offvalue=False, variable=self.normPlotAxis)
        plotmenu.add_separator()
        stylemenu = tk.Menu(plotmenu, tearoff=False)
        plotmenu.add_cascade(label='Plots style', menu=stylemenu)
        plotmenu.add_command(label="Default colors...", command=cycle_color)
        plotmenu.add_separator()
        plotmenu.add_command(label='Spruce up plot...', command=lambda: OMFIT['scratch']['__spruceUpFigures__'].run())

        def update():
            self.force_selection()
            # XYclear (this is copied also in XquickPlot)
            cl_message = []
            if self.x is not None:
                cl_message.append('X')
            if self.y is not None:
                cl_message.append('Y')
            if self.z is not None:
                cl_message.append('Z')
            if len(cl_message):
                plotmenu.entryconfig(5, label="Clear " + ', '.join(cl_message), state=tk.NORMAL)
            else:
                plotmenu.entryconfig(5, label="Clear X, Y, Z", state=tk.DISABLED)

            # Xset and Yset
            if (
                isinstance(self.linkToFocus, np.ndarray)
                and ('s' not in self.linkToFocus.dtype.char.lower())
                and np.sum(np.array(np.array(self.linkToFocus).shape) > 1) == 1
            ) or (
                isinstance(self.linkToFocus, OMFITmdsValue)
                and (hasattr(self.linkToFocus, '_data'))
                and (self.linkToFocus._data is not None)
                and ('s' not in self.linkToFocus.data().dtype.char.lower())
                and np.sum(np.array(self.linkToFocus.data()).shape > 1) == 1
            ):
                plotmenu.entryconfig(4, label="Set as Z", state=tk.NORMAL)
                plotmenu.entryconfig(3, label="Set as Y", state=tk.NORMAL)
                plotmenu.entryconfig(2, label="Set as X", state=tk.NORMAL)
            else:
                plotmenu.entryconfig(4, label="Set as Z", state=tk.DISABLED)
                plotmenu.entryconfig(3, label="Set as Y", state=tk.DISABLED)
                plotmenu.entryconfig(2, label="Set as X", state=tk.DISABLED)

            # QuickPlot
            if (isinstance(self.linkToFocus, np.ndarray) and ('s' not in self.linkToFocus.dtype.char.lower())) or hasattr(
                self.linkToFocus, 'plot'
            ):
                plotmenu.entryconfig(1, label="Quick over plot", state=tk.NORMAL)
                plotmenu.entryconfig(0, label="Quick plot", state=tk.NORMAL)
            else:
                plotmenu.entryconfig(1, label="Quick over plot", state=tk.DISABLED)
                plotmenu.entryconfig(0, label="Quick plot", state=tk.DISABLED)

            # Style
            stylemenu.delete(0, tk.END)

            def defaultStyle():
                matplotlib.rcParams.update(matplotlib.rcParamsDefault)

            def setStyle(stl=None):
                if not self.compoundStyles.get():
                    matplotlib.rcParams.update(matplotlib.rcParamsDefault)
                pyplot.style.use(stl)

            stylemenu.add_command(label='Reset to defaults', command=defaultStyle)
            stylemenu.add_checkbutton(label='Combine styles', onvalue=True, offvalue=False, variable=self.compoundStyles)
            stylemenu.add_command(label='Styles editor ...', command=lambda: OMFIT['scratch']['__styleGUI__'].run())
            stylemenu.add_separator()
            matplotlib.style.core.reload_library()
            styles = {'User': {}, 'OMFIT': {}, 'System': {}}
            for item in sorted(matplotlib.style.available, key=lambda x: x.lower()):
                if os.path.exists(os.sep.join([matplotlib.get_configdir(), 'stylelib', item + '.mplstyle'])):
                    styles['User'][item] = os.sep.join([matplotlib.get_configdir(), 'stylelib', item + '.mplstyle'])
                elif os.path.exists(os.sep.join([OMFITsrc, 'extras', 'styles', item + '.mplstyle'])):
                    styles['OMFIT'][item] = os.sep.join([OMFITsrc, 'extras', 'styles', item + '.mplstyle'])
                else:
                    styles['System'][item] = item
            for grp in ['User', 'OMFIT', 'System']:
                grpstylemenu = tk.Menu(stylemenu, tearoff=False)
                stylemenu.add_cascade(label=grp, menu=grpstylemenu)
                for item in sorted(styles[grp].keys(), key=lambda x: re.sub('[_]', ' ', x).strip().lower()):
                    grpstylemenu.add_command(label=re.sub('[_]', ' ', item).strip(), command=lambda stl=styles[grp][item]: setStyle(stl))

        plotmenu.config(postcommand=update)
        menubar.add_cascade(label="Plot", menu=plotmenu)

        # ---------------------------
        # Figure
        # ---------------------------
        figmenu = tk.Menu(menubar, tearoff=False)

        def setFig(fig):
            pyplot.figure(fig.canvas.figure.number)
            fig.window.lift()
            fig.window.focus_force()
            fig.window.deiconify()

        def centerFig():
            for k, fig in enumerate(matplotlib._pylab_helpers.Gcf.get_all_fig_managers()):
                tk_center(fig.window, OMFITaux['rootGUI'])

        def update():
            while figmenu.entryconfig(0):
                try:
                    figmenu.delete(0)
                except Exception:
                    break
            figmenu.add_command(
                label="Close all",
                command=lambda: close('all'),
                accelerator=global_event_bindings.get('FIGURE: close all figures'),
                state=tk.DISABLED,
            )
            figmenu.add_command(label="Center all", command=centerFig, state=tk.DISABLED)

            def updateFigsOnTopMainSettings():
                OMFIT['MainSettings']['SETUP']['GUIappearance']['figures_on_top'] = self.figsOnTop.get()
                self.update_treeGUI()

            figmenu.add_checkbutton(
                label="Figures on top", onvalue=True, offvalue=False, variable=self.figsOnTop, command=updateFigsOnTopMainSettings
            )
            for k, fig in enumerate(matplotlib._pylab_helpers.Gcf.get_all_fig_managers()):
                if k == 0:
                    figmenu.entryconfig(0, state=tk.NORMAL)
                    figmenu.entryconfig(1, state=tk.NORMAL)
                    figmenu.add_separator()
                    figmenu.add_command(
                        label="Show all",
                        command=lambda: self.selectFigure(action='lift'),
                        accelerator=global_event_bindings.get('FIGURE: show all figures'),
                    )
                    figmenu.add_command(
                        label="Hide all",
                        command=lambda: self.selectFigure(action='lower'),
                        accelerator=global_event_bindings.get('FIGURE: hide all figures'),
                    )
                    if len(matplotlib._pylab_helpers.Gcf.get_all_fig_managers()) > 1:
                        figmenu.add_command(
                            label="Previous",
                            command=lambda: self.selectFigure(action='reverse'),
                            accelerator=global_event_bindings.get('FIGURE: show previous figure'),
                        )
                        figmenu.add_command(
                            label="Next",
                            command=lambda: self.selectFigure(action='forward'),
                            accelerator=global_event_bindings.get('FIGURE: show next figure'),
                        )
                    figmenu.add_separator()
                figmenu.add_command(label=str(TKtopGUI(fig.canvas)._master.wm_title()), command=lambda fig=fig: setFig(fig))

        figmenu.config(postcommand=update)
        menubar.add_cascade(label="Figures", menu=figmenu)

        # ---------------------------
        # OMAS
        # ---------------------------
        omasmenu = tk.Menu(menubar, tearoff=False)

        def browse(ds):
            if 'IMAS data dictionary' not in OMFIT:
                OMFIT.insert(0, 'IMAS data dictionary', ODS(consistency_check=False))
            OMFIT['IMAS data dictionary'].update(omas_info(ds))
            self.update_treeGUI()

        browseimas = tk.Menu(omasmenu, tearoff=False)
        dss = omas.omas_utils.list_structures(imas_version=list(omas.imas_versions)[-1])
        for d in np.unique([ds[0] for ds in dss]):
            browseimas_sub = tk.Menu(browseimas, tearoff=False)
            for ds in [ds for ds in dss if ds.startswith(d)]:
                browseimas_sub.add_command(label=ds, command=lambda ds=ds: browse(ds))
            browseimas.add_cascade(label=d.upper(), menu=browseimas_sub)
        omasmenu.add_cascade(label="Browse data structure", menu=browseimas)

        if hasattr(omas, 'omas_machine') and hasattr(omas.omas_machine, 'reload_machine_mappings'):
            omasmenu.add_command(label="Reload experiment mappings", command=omas.omas_machine.reload_machine_mappings)

        menubar.add_cascade(label="OMAS", menu=omasmenu)

        # ---------------------------
        # Develop
        # ---------------------------
        devmenu = tk.Menu(menubar, tearoff=False)

        devmenu.add_command(
            label="Re-run last script executed",
            command=self.reRunlastRun,
            accelerator=global_event_bindings.get('TREE: re-run last script'),
        )
        devmenu.add_separator()

        omfitdebug = tk.Menu(devmenu, tearoff=False)
        devmenu.add_cascade(label='OMFIT debug', menu=omfitdebug)

        def set_omasdebug(topic):
            os.environ['OMAS_DEBUG_TOPIC'] = topic

        omasdebug = tk.Menu(omasmenu, tearoff=False)
        omasdebug.add_checkbutton(
            label='Quiet all', onvalue='0', variable=self.omasdebug_logs, command=lambda topic='0': set_omasdebug(topic=topic)
        )
        omasdebug.add_checkbutton(
            label='Print all', onvalue='*', variable=self.omasdebug_logs, command=lambda topic='*': set_omasdebug(topic=topic)
        )
        omasdebug.add_separator()
        for topic in sorted(['machine', 'dynamic', 'coordsio', 'cocos']):
            omasdebug.add_checkbutton(
                label=topic, onvalue=topic, variable=self.omasdebug_logs, command=lambda topic=topic: set_omasdebug(topic=topic)
            )
        devmenu.add_cascade(label="OMAS debug", menu=omasdebug)

        def show_memory_history():
            m = np.array(self.memory_history).astype(float)
            fig = figure(num='Memory usage history')
            fig.clf()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot(m[:, 0] - time.time(), m[:, 1] / 2.0 ** 10 / 2.0 ** 10, '.-')
            ax.set_xlabel('Time [s]')
            ax.set_ylabel('Memory [Mb]')

        def connect_to_morti():
            username, server, port = setup_ssh_tunnel(
                "build2.gat.com:8080", OMFIT['MainSettings']['SERVER']['cybele']['server'], allowEmptyServerUsername=True
            )
            openInBrowser(f'http://{server}:{port}')

        devmenu.add_separator()
        devmenu.add_command(label='Manage modules scripts...', command=OMFIT['scratch']['__developerModeGUI__'].run)

        devmenu.add_separator()
        devmenu.add_command(
            label='Show last script error in full format',
            command=self.showError,
            accelerator=global_event_bindings.get('TREE: show last error in full format'),
        )
        devmenu.add_command(
            label="Show last execution diagram",
            command=self.showExecDiag,
            accelerator=global_event_bindings.get('Show last execution diagram'),
        )
        devmenu.add_command(label="Show memory usage history", command=show_memory_history)

        # Open web-browser (with ssh tunnel) to the Jenkins server where OMFIT regressions are run
        if OMFIT['MainSettings']['SERVER']['GA_username'] in ['meneghini', 'smithsp', 'eldond', 'kalling']:
            devmenu.add_separator()
            devmenu.add_command(label="Macmini Omfit Regression Test Invigilator (MORTI)", command=connect_to_morti)

        def set_omfitdebug(topic):
            os.environ['OMFIT_DEBUG'] = topic
            if topic != '0' and topic in OMFITaux['debug_logs']:
                tag_print(''.join(OMFITaux['debug_logs'][topic]), tag='DEBUG')

        def update():
            self.omfitdebug_logs.set(os.environ.get('OMFIT_DEBUG', '0'))
            if self.lastRunScriptFromGUI is None:
                devmenu.entryconfig(0, state=tk.DISABLED)
            else:
                devmenu.entryconfig(0, state=tk.NORMAL)
            # update the debug
            omfitdebug.delete(0, tk.END)
            omfitdebug.add_command(label='Clear logs', command=lambda: OMFITaux['debug_logs'].clear())
            omfitdebug.add_separator()
            omfitdebug.add_checkbutton(
                label='Quiet all', onvalue='0', variable=self.omfitdebug_logs, command=lambda topic='0': set_omfitdebug(topic=topic)
            )
            omfitdebug.add_checkbutton(
                label='Print all', onvalue='-1', variable=self.omfitdebug_logs, command=lambda topic='-1': set_omfitdebug(topic=topic)
            )
            omfitdebug.add_separator()
            for topic in sorted(list(OMFITaux['debug_logs'].keys()), key=lambda x: x.lower()):
                omfitdebug.add_checkbutton(
                    label=topic, onvalue=topic, variable=self.omfitdebug_logs, command=lambda topic=topic: set_omfitdebug(topic=topic)
                )

        devmenu.config(postcommand=update)
        menubar.add_cascade(label="Develop", menu=devmenu)

        # ---------------------------
        # OMAS
        # ---------------------------
        helpmenu = tk.Menu(menubar, tearoff=False)

        helpmenu.add_command(label="Send email feedback", command=self.email_feedback)
        helpmenu.add_separator()
        helpmenu.add_command(label="Help window", command=help, accelerator=global_event_bindings.get('GLOBAL: help window'))
        helpmenu.add_command(label="Online help", command=lambda: openInBrowser('https://omfit.io'))
        helpmenu.add_command(label="Show keyboard shortcuts", command=global_event_bindings.printAll)
        helpmenu.add_separator()
        helpmenu.add_command(label="Splash screen...", command=lambda: splash(self.rootGUI))
        helpmenu.add_command(label="Productivity", command=productivity)

        menubar.add_cascade(label="Help", menu=helpmenu)

        # save for configuration changes later
        self.menubar = menubar
        self.filemenu = filemenu
        self.editmenu = editmenu
        self.plotmenu = plotmenu
        self.figmenu = figmenu
        self.omasmenu = omasmenu
        self.devmenu = devmenu
        self.helpmenu = helpmenu

        # instantiate
        self.rootGUI.config(menu=self.menubar)

    # ------------------
    # TREE GUI
    # ------------------
    def build_OMFIT_GUI(self):
        self.t_start_build_GUI = time.time()

        def toggleShowType():
            self.showType = not self.showType
            if not self.showType:
                self.treeGUI["displaycolumns"] = 'value'
                self.treeGUI.column(
                    "value",
                    width=(self.treeGUI.column("value", option='width') + self.treeGUI.column("type", option='width')),
                    stretch=True,
                )
                self.treeGUI.column("#0", stretch=False)
            else:
                self.treeGUI["displaycolumns"] = ('value', 'type')
                self.treeGUI.column(
                    "value",
                    width=(self.treeGUI.column("value", option='width') - self.treeGUI.column("type", option='minwidth')),
                    stretch=True,
                )
                self.treeGUI.column("type", width=self.treeGUI.column("type", option='minwidth'), stretch=True)
                self.treeGUI.column("#0", stretch=False)
            tmp = self.leftright_pan.sash_coord(0)
            self.treeGUI.update_idletasks()
            self.leftright_pan.sash_place(0, tmp[0], 0)

        def toggleShowHidden():
            self.showHidden = not self.showHidden
            self.update_treeGUI()
            try:
                self.treeGUI.see(parseBuildLocation(parseBuildLocation(self.focus)[:-1]))
                self.treeGUI.update_idletasks()
                self.treeGUI.see(self.focus)
            except Exception:
                pass

        def clearConsole(event):
            def clear(tag):
                OMFITx.clc(tag)
                popup.unpost()

            popup = tk.Menu(self.rootGUI, tearoff=0)
            popup.add_command(label="Clear all", command=lambda: clear(None))
            popup.add_separator()
            popup.add_command(label="Clear OMFIT output (black)", command=lambda: clear('STDOUT'))
            popup.add_command(label="Clear OMFIT error (red)", command=lambda: clear('STDERR'))
            popup.add_command(label="Clear OMFIT warning (orange)", command=lambda: clear('WARNING'))
            popup.add_command(label="Clear OMFIT info (green)", command=lambda: clear('INFO'))
            popup.add_command(label="Clear OMFIT debug (yellow)", command=lambda: clear('DEBUG'))
            popup.add_separator()
            popup.add_command(label="Clear programs output (blue)", command=lambda: clear('PROGRAM_OUT'))
            popup.add_command(label="Clear programs error (purple)", command=lambda: clear('PROGRAM_ERR'))
            popup.add_separator()
            popup.add_command(label="Clear help (pale green)", command=lambda: clear('HELP'))
            popup.add_command(label="Clear history (gray)", command=lambda: clear('HIST'))
            popup.bind("<FocusOut>", lambda event: popup.unpost())
            popup.post(event.x_root, event.y_root)
            popup.focus_set()

        def toggleFollowOutput():
            self.console.follow = not self.console.follow
            if self.console.follow:
                self.ckFollow.state(['selected'])
                self.console.see('end')
            else:
                self.ckFollow.state(['!selected'])

        def toggleWrap1():
            if self.console.configure('wrap')[4].lower() != 'none':
                self.ckWrap1.state(['!selected'])
                self.console.configure(wrap='none')
            else:
                self.ckWrap1.state(['selected'])
                self.console.configure(wrap='char')

        def toggleWrap2():
            doWrap = self.command[self.commandActive].configure('wrap')[4].lower() != 'none'
            for k in range(len(self.command)):
                if doWrap:
                    self.ckWrap2.state(['!selected'])
                    self.command[k].configure(wrap='none')
                else:
                    self.ckWrap2.state(['selected'])
                    self.command[k].configure(wrap='char')

        self.prop_sash = None
        self.prop_sash_lock = False
        self.sash_alarm = None

        def configure_sash():
            # resize sashes while mantaining proportionality
            def _configure_sash():
                if self.sash_alarm:
                    self.rootGUI.after_cancel(self.sash_alarm)
                    self.sash_alarm = None

                self.rootGUI.update_idletasks()
                tmp = (
                    self.rootGUI.winfo_width(),
                    self.rootGUI.winfo_height(),
                    self.leftright_pan.sash_coord(0)[0],
                    self.updown_pan.sash_coord(0)[1],
                )
                if self.prop_sash is None or tmp[0] == self.prop_sash[0] and tmp[1] == self.prop_sash[1]:
                    self.prop_sash = tmp
                else:
                    self.leftright_pan.sash_place(0, int(float(tmp[0]) / self.prop_sash[0] * self.prop_sash[2]), 0)
                    self.updown_pan.sash_place(0, 0, int(float(tmp[1]) / self.prop_sash[1] * self.prop_sash[3]))
                    self.rootGUI.update_idletasks()
                    self.prop_sash = (
                        self.rootGUI.winfo_width(),
                        self.rootGUI.winfo_height(),
                        self.leftright_pan.sash_coord(0)[0],
                        self.updown_pan.sash_coord(0)[1],
                    )

                self.browser_label_text.configure(
                    width=int((self.browserFrame.winfo_width() - self.browser_label_text.winfo_x()) / float(self.deltaw) - 2)
                )

                self.rootGUI.update_idletasks()
                self.prop_sash_lock = False

            if not self.prop_sash_lock:
                self.prop_sash_lock = True
                self.sash_alarm = self.rootGUI.after(250, _configure_sash)

        colorSep = tk.Frame(self.rootGUI, background=OMFITaux['session_color'], height=1)
        mainContent = ttk.Frame(self.rootGUI)
        statusBar = ttk.Frame(self.rootGUI)
        self.rootGUI.grid_rowconfigure(1, weight=1)
        self.rootGUI.grid_columnconfigure(0, weight=1)
        colorSep.grid(row=0, column=0, sticky='nswe')
        mainContent.grid(row=1, column=0, sticky='nswe')
        statusBar.grid(row=2, column=0, sticky='we')

        ttk.Label(statusBar, text='Show:', font=OMFITfont('normal', -2)).pack(side=tk.LEFT)
        self.showHiddenCk = ttk.Checkbutton(statusBar, text='hidden', command=toggleShowHidden, style='small.TCheckbutton')
        self.showHiddenCk.state(['!alternate'])  # removes color box bg indicating user has not clicked it, which may confuse people
        self.showHiddenCk.pack(side=tk.LEFT)
        self.showTypeCk = ttk.Checkbutton(statusBar, text='types', command=toggleShowType, style='small.TCheckbutton')
        self.showTypeCk.state(['!alternate'])  # removes color box bg indicating user has not clicked it, which may confuse people
        self.showTypeCk.pack(side=tk.LEFT)
        if self.showType:
            self.showTypeCk.state(['selected'])
        else:
            self.showTypeCk.state(['!selected'])

        self.statusBarText = tk.StringVar()
        lbl = ttk.Label(statusBar, textvariable=self.statusBarText, font=OMFITfont('normal', -2))

        def copyProjectName():
            if OMFIT.filename:
                self.rootGUI.clipboard_clear()
                self.rootGUI.clipboard_append(OMFIT.filename, type='PRIMARY')
                self.rootGUI.clipboard_append(OMFIT.filename, type='STRING')
                printt('Copied project name: ' + OMFIT.filename)

        lbl.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        lbl.bind('<Button-1>', lambda event: copyProjectName())

        self.rowCol = tk.StringVar()
        self.rowCol.set('Ln:? Col:?'.ljust(20))
        lbl = ttk.Label(statusBar, textvariable=self.rowCol, font=OMFITfont('normal', -2))
        lbl.pack(side=tk.RIGHT, expand=tk.NO, fill=tk.NONE)

        self.memory = tk.StringVar()
        self.memory.set(''.ljust(20))
        lbl = ttk.Label(statusBar, textvariable=self.memory, font=OMFITfont('normal', -2))
        lbl.pack(side=tk.RIGHT, expand=tk.NO, fill=tk.NONE)

        bg = ttk_style.lookup('TFrame', 'background')
        self.leftright_pan = tk.PanedWindow(mainContent, orient=tk.HORIZONTAL, showhandle=1, borderwidth=2, opaqueresize=1, background=bg)
        self.leftright_pan.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.leftright_pan.bind('<Configure>', lambda event: configure_sash())
        self.updown_pan = tk.PanedWindow(self.leftright_pan, orient=tk.VERTICAL, showhandle=1, borderwidth=2, opaqueresize=1, background=bg)
        self.updown_pan.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.updown_pan.bind('<Configure>', lambda event: configure_sash())

        console_label_widget = ttk.Frame(self.rootGUI)
        bf = ttk.Button(console_label_widget, text='?')
        bf.configure(width=int(len(bf.configure('text')[4]) * _GUIappearance['buttons_width_multiplier']))
        bf.pack(side=tk.LEFT)
        ttk.Label(console_label_widget, text='Console ', style='bold.TLabel').pack(side=tk.LEFT)
        b1 = ttk.Button(console_label_widget, text='Clear ...', takefocus=0)
        b1.configure(width=int(len(b1.configure('text')[4]) * _GUIappearance['buttons_width_multiplier']))
        b1.pack(side=tk.LEFT)
        b1.bind("<Button-1>", clearConsole)

        self.wrap1 = tk.IntVar()
        self.ckWrap1 = ttk.Checkbutton(console_label_widget, text='Wrap', variable=self.wrap1, command=toggleWrap1)
        self.ckWrap1.pack(side=tk.LEFT)
        self.follow = tk.IntVar()
        self.ckFollow = ttk.Checkbutton(console_label_widget, text='Follow', variable=self.follow, command=toggleFollowOutput)
        self.ckFollow.pack(side=tk.LEFT)
        console = ttk.LabelFrame(self.updown_pan, labelwidget=console_label_widget)
        console.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH)
        self.console = tk.ConsoleTextGUI(console, width=80, relief=tk.GROOVE, border=0, undo=tk.TRUE, maxundo=10)
        self.console.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        if self.console.follow:
            self.ckFollow.state(['selected'])
        else:
            self.ckFollow.state(['!selected'])
        self.console.configure(wrap='none')
        if self.console.configure('wrap')[4].lower() != 'none':
            self.ckWrap1.state(['selected'])
        else:
            self.ckWrap1.state(['!selected'])
        bf.bind("<Button-1>", lambda event: self.console.search())

        # command box
        command_label_widget = ttk.Frame()
        frm = ttk.Frame(command_label_widget)
        frm.pack(side=tk.TOP, fill=tk.X)
        self.bf = ttk.Button(frm, text='?')
        self.bf.configure(width=int(len(self.bf.configure('text')[4]) * _GUIappearance['buttons_width_multiplier']))
        self.bf.pack(side=tk.LEFT)
        ttk.Label(frm, text='Command box ', justify=tk.LEFT, anchor=tk.W, style='bold.TLabel').pack(side=tk.LEFT)

        def execute():
            return self.command[self.commandActive].execute()

        def clear_and_close():
            if len(self.command[self.commandActive].get()):
                self.command[self.commandActive].clear()
            else:
                self.commandNotebook.unbind("<<NotebookTabChanged>>")
                self.commandNotebook.forget(self.command[self.commandActive])
                self.command.pop(self.commandActive)
                self.commandNames.pop(self.commandActive)
                self.commandNotebook.bind("<<NotebookTabChanged>>", lambda event: self.commandSelect())
                if len(self.command) and self.commandActive == len(self.command):
                    self.commandNotebook.select(self.commandActive - 1)
                else:
                    self.commandNotebook.select(self.commandActive)
                    for c in range(self.commandActive, len(self.command)):
                        self.command[c].name = 'OMFIT command box #%d' % (c + 1)
                        try:
                            if int(self.commandNames[c]) == c + 2:
                                self.commandNames[c] = str(c + 1)
                        except ValueError:
                            continue
            self.commandSelect()

        b1 = ttk.Button(frm, text='Execute', command=execute)
        b1.pack(side=tk.LEFT)
        b1.configure(width=int(len(b1.configure('text')[4]) * _GUIappearance['buttons_width_multiplier']))
        b1 = ttk.Button(frm, text='Clear', command=clear_and_close)
        b1.pack(side=tk.LEFT)
        b1.configure(width=int(len(b1.configure('text')[4]) * _GUIappearance['buttons_width_multiplier']))
        self.clear_close_button = b1
        self.wrap2 = tk.IntVar()
        self.ckWrap2 = ttk.Checkbutton(frm, text='Wrap', variable=self.wrap2, command=toggleWrap2)
        self.ckWrap2.state(['!alternate'])
        self.ckWrap2.pack(side=tk.LEFT)
        ttk.Label(frm, text='').pack(side=tk.LEFT, fill=tk.X)
        frm = ttk.Frame(command_label_widget)
        frm.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(frm, text='Namespace: ').pack(side=tk.LEFT, fill=tk.X)
        self.namespaceComboBox = Combobox(frm, state='readonly', width=100)
        self.namespaceComboBox.bind('<<ComboboxSelected>>', lambda event: self.commandNamespace())
        self.namespaceComboBox.pack(side=tk.LEFT, fill=tk.X)
        self.commandLabelFrame = ttk.LabelFrame(self.updown_pan, labelwidget=command_label_widget)
        self.commandLabelFrame.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH)

        # individual command box editors
        self.commandNotebook = ttk.Notebook(self.commandLabelFrame)
        self.commandNotebook.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        self.commandNotebook.add(ttk.Frame(self.commandLabelFrame), text=' + ')
        self.commandAdd(0)
        self.commandNotebook.bind("<<NotebookTabChanged>>", lambda event: self.commandSelect())

        browser_label_widget = ttk.Frame()

        self.searchButtons = ttk.Frame(browser_label_widget)
        b1 = ttk.Button(self.searchButtons, text='X', command=self.onQuitSearch)
        b1.configure(width=int(len(b1.configure('text')[4]) * _GUIappearance['buttons_width_multiplier']))
        b1.pack(side=tk.LEFT)
        b1 = ttk.Button(self.searchButtons, text='<', command=lambda: self.F3(action='reverse'))
        b1.configure(width=int(len(b1.configure('text')[4]) * _GUIappearance['buttons_width_multiplier']))
        b1.pack(side=tk.LEFT)
        b1 = ttk.Button(self.searchButtons, text='>', command=lambda: self.F3(action='forward'))
        b1.configure(width=int(len(b1.configure('text')[4]) * _GUIappearance['buttons_width_multiplier']))
        b1.pack(side=tk.LEFT)
        self.searchButtons.grid(column=0, row=0, sticky='ew')
        self.searchButtons.grid_remove()

        self.searchButton = ttk.Button(browser_label_widget, text='?', command=self.ctrlF)
        self.searchButton.configure(width=int(len(self.searchButton.configure('text')[4]) * _GUIappearance['buttons_width_multiplier']))
        self.searchButton.grid(column=0, row=0)

        self.browser_label_name = tk.StringVar()
        self.browser_label_name.set('Browser')
        ttk.Label(browser_label_widget, textvariable=self.browser_label_name, style='bold.TLabel').grid(column=1, row=0, sticky='nsew')
        self.browser_label_text = tk.OneLineText(browser_label_widget, percolator=True)
        self.browser_label_text.grid(column=2, row=0, sticky='nsew')
        ttk.Label(browser_label_widget, text=' ').grid(column=3, row=0, sticky='nsew')

        self.browser_label_text.bind('<Return>', lambda event: self.onDoSearch())
        self.browser_label_text.bind('<KP_Enter>', lambda event: self.onDoSearch())
        self.browser_label_text.bind('<Escape>', lambda event: self.onQuitSearch())
        self.browser_label_text.configure(width=10)
        width0 = self.browser_label_text.winfo_reqwidth()
        self.browser_label_text.configure(width=10 + 1)
        width1 = self.browser_label_text.winfo_reqwidth()
        self.deltaw = width1 - width0

        self.browserFrame = ttk.LabelFrame(self.leftright_pan, labelwidget=browser_label_widget)

        # Notebook
        self.notebook = ttk.Notebook(self.browserFrame)
        self.notebook.bind("<<NotebookTabChanged>>", lambda event: self.viewSelect())
        self.notebook.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)

        # scrollable tree
        self.treeGUI = tk.Treeview(self.browserFrame, scrollup=self.display_row_info, selectmode='browse')
        self.treeGUI.frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        self.treeGUI["columns"] = ('value', 'type')
        self.treeGUI.column("#0", minwidth=200, width=200, stretch=False)
        self.treeGUI.column("value", minwidth=150, width=150, stretch=True)
        self.treeGUI.column("type", minwidth=130, width=130, stretch=False)
        self.treeGUI.heading("#0", text="OMFIT")
        self.treeGUI.heading("value", text="Content")
        self.treeGUI.heading("type", text="Data type")
        if self.showType:
            self.treeGUI["displaycolumns"] = ('value', 'type')
        else:
            self.treeGUI["displaycolumns"] = 'value'

        # add views to notebook
        self.addView("View 1")
        self.addView("View 2")
        self.addView("Attrs")
        self.addView("Scratch", "['scratch']")
        self.addView("Command Box", "['commandBox']")
        self.addView("Script Run", "['scriptsRun']")
        self.addView("Main Settings", "['MainSettings']")

        self.notes = askDescription(self.browserFrame, '', label='', showInsertDate=True, showHistorySeparate=False)
        self.notebook.add(ttk.Frame(self.notebook), text='Notes')

        self.help = ttk.Frame(self.browserFrame)
        self._help = omfit_pydocs()
        self._help._buildGUI(parent=self.help, topLevel=False)
        self.help.pack_forget()
        self.notebook.add(ttk.Frame(self.notebook), text='Help')

        self.terminal = ttk.Frame(self.browserFrame)
        self.notebook.add(ttk.Frame(self.notebook), text='Terminal')

        self.rootGUI.protocol("WM_DELETE_WINDOW", self.quit_clean)
        # event handling for calling functions
        self.rootGUI.bind("<<update_treeGUI>>", lambda event: self.update_treeGUI())
        self.rootGUI.bind("<<update_GUI>>", lambda event: self.updateGUI())

        self.rootGUI.bind("<<TreeviewOpen>>", self.TreeviewOpen)
        self.rootGUI.bind("<<TreeviewClose>>", self.TreeviewClose)

        self.leftright_pan.add(self.browserFrame)
        self.leftright_pan.add(self.updown_pan)
        self.updown_pan.add(console)
        self.updown_pan.add(self.commandLabelFrame)
        self.rootGUI.update_idletasks()

        self.leftright_pan.sash_place(0, int(_sgw * 0.618), 0)
        self.leftright_pan.paneconfigure(self.browserFrame, sticky='NSEW')
        self.leftright_pan.paneconfigure(self.updown_pan, sticky='NSEW')
        self.updown_pan.sash_place(0, 0, int(_sgh * (1 - 0.618)))
        self.updown_pan.paneconfigure(console, sticky='NSEW')
        self.updown_pan.paneconfigure(self.commandLabelFrame, sticky='NSEW')
        global_event_bindings.add('GLOBAL: online help', self.rootGUI, '<F1>', lambda event: openInBrowser('https://omfit.io'))
        global_event_bindings.add('GLOBAL: re-run last script', self.rootGUI, '<F5>', lambda event: self.reRunlastRun())
        global_event_bindings.add('GLOBAL: show last error in full format', self.rootGUI, '<F6>', lambda event: self.showError())
        global_event_bindings.add('GLOBAL: last execution diagram', self.rootGUI, '<F7>', lambda event: self.showExecDiag())
        global_event_bindings.add('GLOBAL: new project', self.rootGUI, f'<{ctrlCmd()}-n>', lambda event: self.newProjectModule())
        global_event_bindings.add('GLOBAL: save project', self.rootGUI, f'<{ctrlCmd()}-s>', lambda event: self.quickSave())
        global_event_bindings.add('GLOBAL: open project', self.rootGUI, f'<{ctrlCmd()}-o>', lambda event: self.loadOMFIT())
        global_event_bindings.add('GLOBAL: import module', self.rootGUI, f'<{ctrlCmd()}-I>', lambda event: self.loadOMFIT('module'))
        global_event_bindings.add('GLOBAL: export module', self.rootGUI, f'<{ctrlCmd()}-E>', lambda event: self.OMFITmodules('export'))
        global_event_bindings.add('GLOBAL: reload module', self.rootGUI, f'<{ctrlCmd()}-R>', lambda event: self.OMFITmodules('reload'))
        global_event_bindings.add('GLOBAL: new module', self.rootGUI, f'<{ctrlCmd()}-N>', lambda event: self.newProjectModule('module'))
        global_event_bindings.add('GLOBAL: quit', self.rootGUI, f'<{ctrlCmd()}-q>', lambda event: self.quit_clean())
        global_event_bindings.add(
            'GLOBAL: quit no questions asked', self.rootGUI, f'<{ctrlCmd()}-Q>', lambda event: self.quit_clean(force=True)
        )
        global_event_bindings.add('GLOBAL: help window', self.rootGUI, f'<{ctrlCmd()}-h>', lambda event: help())
        global_event_bindings.add('TREE: search', self.treeGUI, f'<{ctrlCmd()}-f>', lambda event: self.ctrlF())
        global_event_bindings.add('TREE: next entry found', self.treeGUI, '<F3>', lambda event: self.F3(action='forward'))  # Firefox-like
        global_event_bindings.add(
            'TREE: previous entry found', self.treeGUI, '<Shift-F3>', lambda event: self.F3(action='reverse')
        )  # Firefox-like
        global_event_bindings.add(
            'TREE: next entry found (alternative)', self.treeGUI, f'<{ctrlCmd()}-g>', lambda event: self.F3(action='forward')
        )  # Chrome-like
        global_event_bindings.add(
            'TREE: previous entry found (alternative)', self.treeGUI, f'<{ctrlCmd()}-G>', lambda event: self.F3(action='reverse')
        )  # Chrome-like

        global_event_bindings.add('FIGURE: show next figure', self.rootGUI, '<Alt-End>', lambda event: self.selectFigure(action='forward'))
        global_event_bindings.add(
            'FIGURE: show previous figure', self.rootGUI, '<Alt-Home>', lambda event: self.selectFigure(action='reverse')
        )
        global_event_bindings.add('FIGURE: show all figures', self.rootGUI, '<Alt-Prior>', lambda event: self.selectFigure(action='lift'))
        global_event_bindings.add('FIGURE: hide all figures', self.rootGUI, '<Alt-Next>', lambda event: self.selectFigure(action='lower'))
        global_event_bindings.add('FIGURE: close all figures', self.rootGUI, '<Alt-Escape>', lambda event: pyplot.close('all'))
        global_event_bindings.add(
            'FIGURE: close all figures (alternative)', self.rootGUI, f'<{ctrlCmd()}-Escape>', lambda event: pyplot.close('all')
        )

        def screen():
            if platform.system() == 'Darwin':
                wmctrl()
            else:
                utils_tk._winfo_screen(reset=True)
                screen_geometry()
                self.rootGUI.geometry(
                    '%dx%d+%d+%d' % (screen_geometry()[0], screen_geometry()[1], screen_geometry()[2], screen_geometry()[3])
                )

        global_event_bindings.add('GLOBAL: Center OMFIT window to screen', self.rootGUI, '<F8>', lambda event: screen())

        self.rootGUI.bind('<Configure>', lambda event: configure_sash())

        configure_sash()

        # clipboard handling
        self.rootGUI.selection_handle(tk.omfit_sel_handle)

        def lastActivity():
            OMFITaux['lastActivity'] = time.time()

        self.rootGUI.bind_all("<Motion>", lambda event: lastActivity())

        print('Time to build GUI: %g seconds' % (time.time() - self.t_start_build_GUI))

    def events_treeGUI(self):
        # note to self: tags that appear first win over tags appearing later

        # use of lambda function is dictated from the fact that force_selection uses
        # 1) if event is None: the selected item
        # 2) if event!=None: the mouse location written in the event
        # So actions performed by the mouse should be called directly to provide an event
        # whereas actions performed by the keyboard should be called with event=None

        global_event_bindings.add('TREE: execute/plot', self.treeGUI, '<Return>', lambda event: self.run_or_plot(), tag='treeItem')
        global_event_bindings.add(
            'TREE: execute/plot (alternative)', self.treeGUI, '<Double-1>', lambda event: self.run_or_plot(), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: execute/plot (alternative 2)', self.treeGUI, '<KP_Enter>', lambda event: self.run_or_plot(), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: execute/plot ask default variables',
            self.treeGUI,
            f'<{ctrlCmd()}-Return>',
            lambda event: self.run_or_plot(defaultVarsGUI=True),
            tag='treeItem',
        )
        global_event_bindings.add(
            'TREE: execute/plot ask default variables (alternative)',
            self.treeGUI,
            f'<{ctrlCmd()}-Double-1>',
            lambda event: self.run_or_plot(defaultVarsGUI=True),
            tag='treeItem',
        )
        global_event_bindings.add('TREE: over plot', self.treeGUI, '<Shift-Return>', lambda event: self.quickPlot(), tag='treeItem')
        global_event_bindings.add(
            'TREE: over plot (alternative)', self.treeGUI, '<Shift-Double-1>', lambda event: self.quickPlot(), tag='treeItem'
        )

        global_event_bindings.add(
            'TREE: over plot ask default variables',
            self.treeGUI,
            f'<Shift-{ctrlCmd()}-Return>',
            lambda event: self.quickPlot(defaultVarsGUI=True),
            tag='treeItem',
        )
        global_event_bindings.add(
            'TREE: over plot ask default variables (alternative)',
            self.treeGUI,
            f'<Shift-{ctrlCmd()}-Double-1>',
            lambda event: self.quickPlot(defaultVarsGUI=True),
            tag='treeItem',
        )

        global_event_bindings.add('TREE: set plot X', self.treeGUI, '<X>', lambda event: self.quickPlotX(action='setX'), tag="ndarray")
        global_event_bindings.add('TREE: set plot Y', self.treeGUI, '<Y>', lambda event: self.quickPlotX(action='setY'), tag="ndarray")
        global_event_bindings.add('TREE: set plot Z', self.treeGUI, '<Z>', lambda event: self.quickPlotX(action='setZ'), tag="ndarray")
        global_event_bindings.add('TREE: open file', self.treeGUI, '<space>', lambda event: self.openFile(), tag="OMFITpath")
        global_event_bindings.add(
            'TREE: open original file', self.treeGUI, '<Shift-space>', lambda event: self.openFile('original'), tag="OMFITpath"
        )
        global_event_bindings.add('TREE: open web link', self.treeGUI, '<space>', lambda event: self.linkToFocus(), tag="OMFITwebLink")

        global_event_bindings.add(
            'TREE: navigate UP', self.treeGUI, '<KeyRelease-Up>', lambda event: self.force_selection(), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: navigate DOWN', self.treeGUI, '<KeyRelease-Down>', lambda event: self.force_selection(), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: close item', self.treeGUI, '<KeyRelease-Left>', lambda event: self.force_selection(), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: navigate LEFT (close all sub-entries)',
            self.treeGUI,
            '<Shift-Left>',
            lambda event: self.TreeviewClose(all=True),
            tag='treeItem',
        )
        global_event_bindings.add(
            'TREE: open item', self.treeGUI, '<KeyRelease-Right>', lambda event: self.force_selection(), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: copy location', self.treeGUI, f'<{ctrlCmd()}-c>', lambda event: self.clipboard(what='location'), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: copy location from root', self.treeGUI, f'<{ctrlCmd()}-r>', lambda event: self.clipboard(what='root'), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: copy location tip', self.treeGUI, f'<{ctrlCmd()}-t>', lambda event: self.clipboard(what='tip'), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: copy value', self.treeGUI, f'<{ctrlCmd()}-C>', lambda event: self.clipboard(what='value'), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: paste at location', self.treeGUI, f'<{ctrlCmd()}-v>', lambda event: self.clipboard(what='paste'), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: paste inside', self.treeGUI, f'<{ctrlCmd()}-V>', lambda event: self.clipboard(what='pasteInside'), tag='treeItem'
        )

        def showItem(what='print'):
            self.treeGUI.focus()
            if what == 'print':
                printi(self.linkToFocus)
            elif what == 'pprint':
                pprinti(self.linkToFocus)
            elif what == 'repr':
                printi(repr(self.linkToFocus))
            self._update_treeGUI()

        global_event_bindings.add('TREE: print entry', self.treeGUI, '<p>', lambda event: showItem(what='print'), tag='treeItem')
        global_event_bindings.add(
            'TREE: pprint entry', self.treeGUI, f'<{ctrlCmd()}-p>', lambda event: showItem(what='pprint'), tag='treeItem'
        )
        global_event_bindings.add('TREE: repr entry', self.treeGUI, f'<{ctrlCmd()}-P>', lambda event: showItem(what='repr'), tag='treeItem')

        global_event_bindings.add(
            'TREE: quick edit tree entry', self.treeGUI, '<Tab>', lambda event: self.onRowDoubleClick(), tag='editableTreeItem'
        )
        global_event_bindings.add(
            'TREE: edit tree entry', self.treeGUI, '<Shift-Tab>', lambda event: self.itemSetupOld(), tag='editableTreeItem'
        )
        global_event_bindings.add(
            'TREE: edit tree entry (alternative)', self.treeGUI, '<ISO_Left_Tab>', lambda event: self.itemSetupOld(), tag='editableTreeItem'
        )
        global_event_bindings.add('TREE: contextual menu', self.treeGUI, f'<{middleClick}>', self.itemRightClicked, tag='editableTreeItem')
        global_event_bindings.add(
            'TREE: contextual menu (alternative)', self.treeGUI, f'<{rightClick}>', self.itemRightClicked, tag='editableTreeItem'
        )

        global_event_bindings.add(
            'TREE: move entry UP', self.treeGUI, f'<{ctrlCmd()}-u>', lambda event: self.itemMove('Up'), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: move entry DOWN', self.treeGUI, f'<{ctrlCmd()}-d>', lambda event: self.itemMove('Down'), tag='treeItem'
        )
        global_event_bindings.add(
            'TREE: delete entry', self.treeGUI, f'<{ctrlCmd()}-BackSpace>', lambda event: self.itemDelete(), tag='treeItem'
        )
        global_event_bindings.add('TREE: clear entry', self.treeGUI, f'<{ctrlCmd()}-w>', lambda event: self.itemClear(), tag='treeItem')

        self.treeGUI.tag_bind('treeItem_action', '<Button-1>', self.force_selection)
        self.treeGUI.tag_bind('treeItem_action', f'<{rightClick}>', self.force_selection)
        self.treeGUI.tag_bind('treeItem_action', f'<{middleClick}>', self.force_selection)

    def TreeviewOpen(self, all=False):
        focus = self.treeGUI.focus()

        # for pagers we just need to redraw the GUI
        if 'OMFITtreeGUIpager@' in focus:
            self.opened_closed['@'.join(focus.split('@')[:-1]) + '@'] = 1
            self.opened_closed['%'.join(focus.split('%')[:-1])] = 1
            self._update_treeGUI()
            return

        self.force_selection()

        self.opened_closed[focus] = 1

        # dynamically load when expading objects that have not been loaded
        if hasattr(self.linkToFocus, 'dynaLoad') and self.linkToFocus.dynaLoad:
            dynaLoader(self.linkToFocus)

        # perform update_idletasks to make sure get_children gets it right
        self.rootGUI.update_idletasks()

        # Expand all tree subelements
        if all:
            for item in list(self.opened_closed.keys()):
                if item.startswith(focus):
                    self.opened_closed[item] = 1
            self._update_treeGUI()
        else:
            if len(self.treeGUI.get_children(focus)) and self.treeGUI.get_children(focus)[0] == focus + '_':
                self._update_treeGUI()

        # perform update_idletasks to make sure display_row_info gets it
        self.rootGUI.update_idletasks()
        self.display_row_info()
        # perform update_idletasks to display display_row_info changes
        self.rootGUI.update_idletasks()

        self.force_selection(focus)

    def TreeviewClose(self, all=False):
        focus = self.treeGUI.focus()

        # see if it was open or closed
        wasOpen = self.opened_closed.get(focus, 0)
        del self.opened_closed[focus]

        # delete pagers
        if self.opened_closed.get(focus + 'OMFITtreeGUIpager@', 0):
            for item in list(self.opened_closed.keys()):
                if item.startswith(focus + 'OMFITtreeGUIpager@'):
                    del self.opened_closed[item]
            self._update_treeGUI()

        # Collapse all tree subelements
        if all:
            for item in list(self.opened_closed.keys()):
                if item.startswith(focus):
                    del self.opened_closed[item]
            self._update_treeGUI()
            if wasOpen:
                return 'break'

        self.rootGUI.update_idletasks()
        self.force_selection(focus)

    def update_treeGUI(self):
        OMFIT.updateMainSettings()
        self.commandNamespace()

    def commandNamespace(self):
        # manage the namespace selection in the commandBox
        tmp = list(OMFIT.moduleDict().keys())
        tmp.insert(0, '')
        tmp = ['OMFIT' + k for k in tmp]
        tmp.insert(0, '-- Clean namespace --')
        if len(OMFITscriptsDict):
            tmp.insert(0, '-- Merge scriptRun namespace --')
        self.namespaceComboBox.configure(values=tuple(tmp))
        changed = False
        if self.commandBoxNamespace not in self.namespaceComboBox.configure('values')[4]:
            self.commandBoxNamespace = 'OMFIT'
            self.namespaceComboBox.set(self.commandBoxNamespace)
            changed = True

        for k in range(len(self.command)):
            if self.command[k].namespace is None:
                changed = True

        if self.namespaceComboBox.get() != self.commandBoxNamespace or changed:
            if self.namespaceComboBox.get() == '-- Clean namespace --':
                OMFITconsoleDict.clear()

                self.namespaceComboBox.set(self.commandBoxNamespace)
                printi("Command-Box namespace is clean")

            elif self.namespaceComboBox.get() == '-- Merge scriptRun namespace --':
                tmpKeys = list(OMFITscriptsDict.keys())
                OMFITconsoleDict.update(OMFITscriptsDict)
                OMFITscriptsDict.clear()

                self.namespaceComboBox.configure(values=tuple(tmp[1:]))
                self.namespaceComboBox.set(self.commandBoxNamespace)
                printi("Merged scriptRun namespace:" + str(tmpKeys))

            self.commandBoxNamespace = self.namespaceComboBox.get()
            eval(self.commandBoxNamespace)['__placeHolder__'] = SortedDict()
            for k in range(len(self.command)):
                self.command[k].namespace = relativeLocations(eval(self.commandBoxNamespace + "['__placeHolder__']"))
            del eval(self.commandBoxNamespace)['__placeHolder__']

        self.namespaceComboBox.configure(state='normal')
        self.namespaceComboBox.selection_clear()
        self.namespaceComboBox.configure(state='readonly')
        self._update_treeGUI()

    def updateGUI(self):
        OMFITx.UpdateGUI()

    def update_treeGUI_and_GUI(self):
        self.update_treeGUI()
        self.updateGUI()

    @virtualKeys
    def _update_treeGUI(self):

        # save selection and focus
        if self.treeGUI is None:
            return
        selectionWas = self.treeGUI.selection()
        focusWas = self.treeGUI.focus()

        self.parent_tags = {}

        def getkeys(me):
            if hasattr(me, '__tree_keys__'):
                meKeys = me.__tree_keys__()
            else:
                meKeys = []
                if isinstance(me, np.recarray):
                    if me.dtype.names is not None:
                        meKeys = me.dtype.names
                    else:
                        meKeys = list(range(len(me)))
                elif isinstance(me, (list, tuple)):
                    meKeys = list(range(len(me)))
                elif isinstance(me, Dataset):
                    meKeys = list(me.variables.keys())
                elif isinstance(me, DataArray):
                    pass
                elif isinstance(me, pandas.Series):
                    pass
                else:
                    meKeys = list(me.keys())
            return meKeys

        # this update tree should be used when I am sure that the content of the tree has not changed
        def search_traverse(me, myLocation, query):
            if isinstance(query, str):
                query = eval('re.compile(r".*' + query + '.*",re.I)')

            if isinstance(me, dict):
                # normal dictionaries are sorted alphabetically
                # search is done only on dictionaries, not lists, tuples and recarrays
                meKeys = list(me.keys())
                if not isinstance(me, (SortedDict, OrderedDict)):
                    try:
                        meKeys = sorted(sorted(meKeys), key=sortHuman)
                    except TypeError:
                        pass

                for kid in meKeys:
                    if self.showHidden or not re.match(hide_ptrn, str(kid)):
                        kidName = "[" + repr(kid) + "]"
                        entryID = myLocation + kidName
                        meKid = me[kid]

                        # speedup: evaluate expressions only once here
                        if isinstance(meKid, OMFITexpression):
                            meKid = me[kid]._value_()

                        if re.match(query, str(kid)) and not re.search(hide_ptrn, str(kid)):
                            # if you find it in the variable name
                            self.match_query[entryID] = 1
                        elif isinstance(meKid, _OMFITpython) and re.search(query, meKid.read()):
                            # if you find it in the content of a python script
                            self.match_query[entryID] = 3
                        elif isinstance(meKid, str) and re.search(query, str(meKid)):
                            # if you find it in a string
                            self.match_query[entryID] = 2
                        elif (
                            isinstance(meKid, OMFITmdsValue)
                            and hasattr(meKid, '_data')
                            and (isinstance(meKid._data, str) or (np.iterable(meKid._data) and isinstance(meKid._data[0], str)))
                            and re.search(query, str(meKid._data))
                        ):
                            # if you find it in the content of a string MDS+ variable
                            self.match_query[entryID] = 2

                        if isinstance(meKid, dict):
                            search_traverse(meKid, entryID, query)

        def insert_traverse(me, myLocation):
            # meKeys contains the list of strings that lead one level deeper in the GUI graphical representation
            try:
                meKeys = getkeys(me)
            except Exception as _excp:
                if os.environ['USER'] in ['meneghini', 'smithsp']:
                    printt('Tree GUI traverse oddity %s: %s' % (str(myLocation), repr(_excp)))
                return

            # sort simple dictionaries, lists, tuple entries
            if not isinstance(me, (SortedDict, OrderedDict)) and not isinstance(me, (list, tuple)):
                try:

                    def sort_first(x):
                        try:
                            return str(x[0])
                        except (TypeError, IndexError):
                            return x

                    meKeys = sorted(meKeys, key=sort_first)
                    meKeys = sorted(meKeys, key=sortHuman)
                except TypeError:
                    pass

            # generate representation of meKeys
            meKeys = list(map(lambda kid: "[" + repr(kid) + "]", meKeys))

            # additional sub-trees that are not lists or dicts only shown if showHidden
            if self.showHidden:
                if isinstance(me, (Dataset, DataArray)) and hasattr(me, 'attrs') and len(me.attrs):
                    meKeys.extend(list(map(lambda kid: ".attrs[" + repr(kid) + "]", me.attrs.keys())))

            possiblyHidden = True
            if isinstance(me, (list, tuple, np.recarray, Dataset)):
                possiblyHidden = False

            # add pagers
            if len(meKeys) > 1000:
                n = int(10 ** np.floor(np.log10(np.sqrt(len(meKeys)))))
                sections = np.linspace(0, len(meKeys), n + 1).astype(int)
                tmp = []
                for s, (kstart, kend) in enumerate(zip(sections[:-1], sections[1:])):
                    pagerkey = f'OMFITtreeGUIpager@{s}%[{kstart}:{kend}]'
                    if s == 0 or s == n - 1 or self.opened_closed.get(myLocation + pagerkey.split('%')[0], 0):
                        tmp += meKeys[kstart:kend]
                    else:
                        tmp += [pagerkey]
                meKeys = tmp

            # loop over keys
            skipKeys = map(lambda kid: "[" + repr(kid) + "]", ['_OMFITkeyName', '_OMFITparent', '_OMFITcopyOf'])
            for kidName in meKeys:
                if kidName in skipKeys:
                    continue
                entryID = myLocation + kidName

                if kidName.startswith('OMFITtreeGUIpager@'):
                    self.treeGUI.insert(
                        myLocation,
                        tk.END,
                        entryID,
                        text='?',
                        tags=tuple(['pager']),
                        values=tuple(['Expand rows ' + kidName.split('%')[1], '']),
                    )
                    self.treeGUI.insert(entryID, tk.END, entryID + '_', text='dummy', tags=tuple(['dummy']))
                    continue

                if (not possiblyHidden or self.showHidden or not (kidName.startswith("['__") and kidName.endswith("__']"))) and (
                    self.onlyTree is None or self.onlyTree in entryID or entryID in self.onlyTree
                ):
                    try:
                        meKid = eval('me' + kidName)
                    except Exception as _excp:
                        printe('Error with GUI representation of `%s`: %s' % (entryID, repr(_excp)))
                        continue

                    self.treeGUI.insert(myLocation, tk.END, entryID)  # text, tags and values handled via display_row_info()

                    # handle modifyOriginal and readOnly tags
                    if isinstance(meKid, OMFITobject) or isinstance(meKid, OMFITtree):
                        try:
                            if hasattr(meKid, 'modifyOriginal') and meKid.modifyOriginal and hasattr(meKid, 'readOnly') and meKid.readOnly:
                                self.parent_tags[entryID] = 'modifyOriginal_readOnly'
                            elif hasattr(meKid, 'modifyOriginal') and meKid.modifyOriginal:
                                self.parent_tags[entryID] = 'modifyOriginal'
                            elif hasattr(meKid, 'readOnly') and meKid.readOnly:
                                self.parent_tags[entryID] = 'readOnly'
                        except AttributeError as _excp:
                            pass

                    # do not go deeper if dynaLoad
                    if hasattr(meKid, 'dynaLoad') and meKid.dynaLoad:
                        self.treeGUI.insert(
                            entryID,
                            tk.END,
                            entryID + '_',
                            text='',
                            tags=tuple(['OMFITerror']),
                            values=tuple(['Error with dynamic loading', '']),
                        )

                    # if these conditions are true, the object could have a child
                    elif not isinstance(meKid, pandas.Series) and (
                        isinstance(meKid, (dict, np.recarray, list, tuple, Dataset))
                        or (hasattr(meKid, 'keys') and hasattr(meKid, '__getitem__'))
                        or (self.showHidden and isinstance(meKid, (Dataset, DataArray)))
                    ):
                        # if the object is open, go deeper
                        if (entryID in self.opened_closed) and self.opened_closed[entryID] == 1:
                            insert_traverse(meKid, entryID)
                            self.treeGUI.item(entryID, open=1)
                        # the object is not open, make a dummy entry underneath it to make it so that we can expand the tree
                        else:
                            try:
                                meKidKeys = getkeys(meKid)
                                if not inspect.isclass(meKid) and len(meKidKeys):
                                    for item in meKidKeys:
                                        try:
                                            str_item = str(item)
                                        except Exception:
                                            str_item = ''
                                        if self.showHidden or not str_item or not re.match(hide_ptrn, str_item):
                                            self.treeGUI.insert(entryID, tk.END, entryID + '_', text='dummy', tags=tuple(['dummy']))
                                            if entryID in self.opened_closed:
                                                del self.opened_closed[entryID]
                                            break
                                elif entryID in self.opened_closed:
                                    del self.opened_closed[entryID]
                            except Exception as _excp:
                                if entryID in self.opened_closed:
                                    del self.opened_closed[entryID]
                                printt('Issue representing object %s in the OMFIT GUI: %s' % (entryID, repr(_excp)))

        # searching
        if not len(self.browserSearch):
            self.match_query = None
            # restore original opened/closed
            if self.opened_closed_bkp is not None:
                self.opened_closed = self.opened_closed_bkp
            self.opened_closed_bkp = None

        elif self.match_query is None and not len(self.focus):
            self.browserSearch = ''

        elif self.match_query is None:
            self.match_query = OrderedDict()
            self.search_F3 = None

            # force loading of the searched object
            list(eval('OMFIT' + self.searchLocation).keys())

            # prevent search to force dynamic loading
            dynaLoadBkp = OMFITaux['dynaLoad_switch']
            OMFITaux['dynaLoad_switch'] = False
            try:
                # perform the search
                search_traverse(eval('OMFIT' + self.searchLocation), self.searchLocation, self.browserSearch)
                for item in list(self.match_query.keys()):
                    locSteps = parseBuildLocation(item)
                    for k in range(len(locSteps)):
                        location = parseBuildLocation(locSteps[0 : k + 1])
                        if location not in self.match_query:
                            self.match_query[location] = 0

                # open only the tree where the search is done
                if self.opened_closed_bkp is None:
                    self.opened_closed_bkp = self.opened_closed
                self.opened_closed = {}
                tmp = parseBuildLocation(self.searchLocation)
                for k in range(len(tmp) - 1):
                    self.opened_closed[parseBuildLocation(tmp[: k + 1])] = 1

                # open the branches which match the query
                tmp = traverse(eval('OMFIT' + self.searchLocation))
                tmp.insert(0, '')
                for item in tmp:
                    if self.searchLocation + item in self.match_query:
                        self.opened_closed[self.searchLocation + item] = 1
                        # handle dynaload manually (force loading of the matching object)
                        if (
                            hasattr(eval('OMFIT' + self.searchLocation + item), 'dynaLoad')
                            and eval('OMFIT' + self.searchLocation + item).dynaLoad
                        ):
                            try:
                                OMFITaux['dynaLoad_switch'] = True
                                list(eval('OMFIT' + self.searchLocation + item).keys())
                            finally:
                                OMFITaux['dynaLoad_switch'] = False

            except Exception as _excp:
                self.browser_label_text.set(self.browser_label_text.get() + ' ...Wrong syntax...')
                printe('Error updating tree GUI\n' + repr(_excp))

            finally:
                OMFITaux['dynaLoad_switch'] = dynaLoadBkp

        # insert entries in the tree GUI
        for item in self.treeGUI.get_children():
            try:
                self.treeGUI.delete(item)
            except tk.TclError as _excp:
                printe('Error in OMFIT GUI update: ' + repr(_excp))
        if len(self.attributes):
            insert_traverse(self.attributes['dir'], '')
        else:
            insert_traverse(OMFIT, '')
        self.display_row_info()

        # restore selection
        try:
            self.treeGUI.selection_set(selectionWas)  # tkStringEncode is not needed here because already escaped
            self.treeGUI.focus(focusWas)
        except tk.TclError:
            pass

    @virtualKeys
    def display_row_info(self, tree=None):
        if len(self.attributes):
            base = "self.attributes['dir']"
        else:
            base = 'OMFIT'
        for entryID in np.unique([self.treeGUI.identify_row(k) for k in range(0, self.treeGUI.winfo_height(), 1)]):
            if len(entryID) and entryID[-1] == '_':
                continue
            try:
                meKid = eval(base + entryID)
            except Exception:
                continue

            kid = parseLocation(entryID)[-1]

            tags = []
            for pEntryID in self.parent_tags:
                if entryID.startswith(pEntryID):
                    tags.append(self.parent_tags[pEntryID])
            if self.match_query is not None:
                if entryID in self.match_query:
                    if not self.match_query[entryID]:
                        pass
                    elif self.match_query[entryID] == 1:
                        tags.append('queryMatch')
                    elif self.match_query[entryID] == 2:
                        tags.append('queryMatchContent')
                    elif self.match_query[entryID] == 3:
                        tags.append('queryMatchFileContent')
                    else:
                        raise ValueError('queryMatch value not recognized')

            tags, values = itemTagsValues(meKid, showHidden=self.showHidden, treeview=self.treeGUI, parent_tags=tags)

            try:
                if hasattr(meKid, 'dynaLoad') and meKid.dynaLoad:
                    tags.append('dynaLoad')
            except AttributeError as _excp:
                pass

            self.treeGUI.item(entryID, text=treeText(kid, False, -1, False), tags=tuple(tags), values=tuple(values))

    def updateTitle(self):
        title = 'OMFIT  '
        if OMFIT.filename == '':
            statusBar = 'Unsaved project'
        elif OMFIT.filename[-4:] == '.zip':
            statusBar = 'Project saved as: %s  (%s)' % (OMFIT.filename, sizeof_fmt(OMFIT.filename))
            title += '-  ' + OMFIT.projectName() + '  '
        else:
            statusBar = 'Project saved as: %s' % (OMFIT.filename)
            title += '-  ' + OMFIT.projectName() + '  '
        title += '-   '
        title += 'PID ' + str(os.getpid())
        title += ' on ' + platform.uname()[1].split('.')[0]
        if len(repo_str):
            title += '   -  ' + repo_str
        title += '   -  Python %d.%d' % (sys.version_info[0], sys.version_info[1])

        if OMFIT.filename and not os.access(OMFIT.filename, os.W_OK):
            statusBar += '  -  READ ONLY'

        self.rootGUI.wm_title(title)
        self.statusBarText.set(statusBar)

    def onRowDoubleClick(self):
        self.force_selection()

        # close previous popups
        if self.editEntryPopup:
            self.editEntryPopup.destroy()
            self.editEntryPopup = None

        if not self.focus:
            return 'break'

        # get column position info
        x0, y0, width0, height0 = self.treeGUI.bbox(self.focus, '#0')
        x1, y1, width1, height1 = self.treeGUI.bbox(self.focus, '#1')
        if self.showType:
            x2, y2, width2, height2 = self.treeGUI.bbox(self.focus, '#2')
        else:
            width2 = 0

        # y-axis offset
        pady = height0 + 4

        # place Entry popup properly
        text, dynamic = tree_entry_repr(self.linkToFocus)
        self.editEntryPopup = EditEntryPopup(self.treeGUI, self.focus, text=text, dynamic=dynamic)
        self.editEntryPopup.place(x=x1, y=y1 + pady, anchor=tk.W, relwidth=float(width1 + width2) / float(width0 + width1 + width2) * 0.95)

        return 'break'

    def force_tree_focus(self):
        self.treeGUI.focus_force()
        try:
            self.treeGUI.selection_set(tkStringEncode(self.focus))
            self.treeGUI.focus(self.focus)
            self.force_selection()
        except tk.TclError:
            pass

    # ------------------
    # Help
    # ------------------
    def email_feedback(self):
        """
        Provide a GUI to send an email with OMFIT developers' emails pre-filled for convenience
        """
        filename = OMFIT.filename
        if not filename:
            filename = 'unsaved'
        message = '''I noticed that...

Please do the following...

I am sending this from OMFIT version %s running on %s

My project is: %s''' % (
            repo_str,
            socket.gethostname(),
            filename,
        )

        tk.email_widget(
            parent=OMFITaux['rootGUI'],
            fromm=OMFIT['MainSettings']['SETUP']['email'],
            to=','.join(
                list(
                    set(
                        ['meneghini@fusion.gat.com', 'smithsp@fusion.gat.com'] + list(map(str, OMFIT['MainSettings']['SETUP']['report_to']))
                    )
                )
            ),
            cc=OMFIT['MainSettings']['SETUP']['email'],
            subject='OMFIT User Feedback',
            message=message,
            title='Send OMFIT feedback :-)',
            use_last_email_to=2,
            quiet=False,
        )

    # ------------------
    # Search
    # ------------------
    def onDoSearch(self):
        if self.searchLocation is not None:
            self.browserSearch = self.browser_label_text.get()
            self.match_query = None
            self.update_treeGUI()
            global_event_bindings.add('TREE: quit search mode', self.treeGUI, '<Escape>', lambda event: self.onQuitSearch())
            self.treeGUI.focus_set()
            self.F3(action='forward')

    def onQuitSearch(self):
        if self.searchLocation is not None:
            self.browserSearch = ''
            self.searchLocation = None
            self.force_selection()

            # leave active selection open
            if self.focus is not None and len(self.focus) and self.opened_closed_bkp is not None:
                locations = parseBuildLocation(self.focus)
                for k in range(len(locations)):
                    self.opened_closed_bkp[parseBuildLocation(locations[:k])] = 1
                    # clear search and unbind

            self.treeGUI.focus_set()
            self.update_treeGUI()
            try:
                self.treeGUI.see(parseBuildLocation(parseBuildLocation(self.focus)[:-1]))
                self.treeGUI.update_idletasks()
                self.treeGUI.see(self.focus)
            except Exception:
                pass
            self.treeGUI.unbind(OMFIT['MainSettings']['SETUP']['KeyBindings'].setdefault('TREE:_quit_search_mode', '<Escape>'))
            self.searchButtons.grid_remove()
            self.searchButton.grid()

    def ctrlF(self):
        if len(self.focus):
            if self.searchLocation is None:
                self.browser_label_text.set('')

                self.searchLocation = self.focus
                if not isinstance(self.linkToFocus, dict):
                    self.searchLocation = parseBuildLocation(parseBuildLocation(self.focus)[:-1])

            self.force_selection()

            self.browser_label_text.focus_set()
            global_event_bindings.add('TREE: quit search mode', self.treeGUI, '<Escape>', lambda event: self.onQuitSearch())
            self.searchButton.grid_remove()
            self.searchButtons.grid()
        else:
            self.browser_label_name.set('Search')
            self.browser_label_text.set('...Select subtree where to search...')

    def F3(self, action='forward'):
        if self.match_query is not None and len(self.match_query):
            tmp = [key for key in list(self.match_query.keys()) if self.match_query[key] > 0]
            if action != 'forward':
                tmp.reverse()
            breakNext = False
            for item in tmp:
                if breakNext:
                    break
                if self.match_query[item] > 0 and item == self.focus:
                    breakNext = True
            if not breakNext:
                for item in tmp:
                    if self.match_query[item] > 0:
                        break
            self.treeGUI.selection_set(tkStringEncode(item))
            self.treeGUI.focus(item)
            self.focus = item
            self.force_selection()
            self.treeGUI.see(item)

    # ------------------
    # Multiple views
    # ------------------
    def addView(self, name, onlyTree=None):
        self.opened_closed_view.append(copy.deepcopy(self.opened_closed))
        self.focus_view.append(self.focus)
        self.notebook.add(ttk.Frame(self.notebook), text=name)
        self.vScroll_view.append(self.treeGUI.vScroll.get())
        self.hScroll_view.append(self.treeGUI.hScroll.get())
        self.onlyTree_view.append(onlyTree)

    def viewSelect(self):
        self.onQuitSearch()
        self.treeGUI.frame.pack_forget()
        self.notes.frame.pack_forget()
        self.help.pack_forget()
        self.terminal.pack_forget()

        self.attributes = {}
        if self.notebook.tab(self.notebook.tabs().index(self.notebook.select()))['text'] == 'Notes':
            self.notes.frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
            self.notes.frame.focus()

        elif self.notebook.tab(self.notebook.tabs().index(self.notebook.select()))['text'] == 'Help':
            self.help.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
            self.help.focus()
            self._help(self.linkToFocus)
            self._help.e.delete(0, 'end')
            self._help.e.insert(0, self.focusRootRepr)

        elif self.notebook.tab(self.notebook.tabs().index(self.notebook.select()))['text'] == 'Attrs':
            self.treeGUI.frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
            self.focus_view[self.tabID] = self.focus
            self.vScroll_view[self.tabID] = self.treeGUI.vScroll.get()
            self.hScroll_view[self.tabID] = self.treeGUI.hScroll.get()
            # switch
            self.tabID = self.notebook.tabs().index(self.notebook.select())
            # restore
            self.opened_closed = self.opened_closed_view[self.tabID]
            self.onlyTree = None
            # get object attributes
            tmp = {}
            for item in dir(self.linkToFocus):
                try:
                    tmp[item] = getattr(self.linkToFocus, item)
                except Exception as _excp:
                    tmp[item] = _excp
            self.attributes = {
                'focus': self.focus,
                'linkToFocus': self.linkToFocus,
                'focusRoot': self.focusRoot,
                'focusRootRepr': self.focusRootRepr,
                'dir': tmp,
            }
            self.update_treeGUI()
            self.treeGUI.yview_moveto(self.vScroll_view[self.tabID][0])
            self.treeGUI.xview_moveto(self.hScroll_view[self.tabID][0])

        elif self.notebook.tab(self.notebook.tabs().index(self.notebook.select()))['text'] == 'Terminal':
            self.terminal.pack(side=tk.TOP, expand=tk.NO, fill=tk.NONE)
            self.terminal.update_idletasks()
            self.terminal.configure(width=self.browserFrame.winfo_width(), height=self.browserFrame.winfo_height())
            if not hasattr(self.terminal, 'started') or self.terminal.started.poll() is not None:
                if platform.system() == 'Darwin':
                    geo = '10000x10000'
                else:
                    geo = '80x32'
                self.terminal.started = subprocess.Popen(
                    "xterm -ls -into %d -geometry %s -sb" % (self.terminal.winfo_id(), geo), shell=True
                )
            self.terminal.focus()

        else:
            self.treeGUI.frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
            # record
            self.focus_view[self.tabID] = self.focus
            self.vScroll_view[self.tabID] = self.treeGUI.vScroll.get()
            self.hScroll_view[self.tabID] = self.treeGUI.hScroll.get()
            # switch
            self.tabID = self.notebook.tabs().index(self.notebook.select())
            # restore
            self.opened_closed = self.opened_closed_view[self.tabID]
            self.onlyTree = self.onlyTree_view[self.tabID]
            if self.onlyTree is not None:
                self.opened_closed[self.onlyTree] = 1
            self.update_treeGUI()
            self.focus = self.focus_view[self.tabID]
            try:
                self.force_selection(self.focus)
            except Exception:
                self.focus = ''
                self.force_selection(self.focus)
            self.treeGUI.yview_moveto(self.vScroll_view[self.tabID][0])
            self.treeGUI.xview_moveto(self.hScroll_view[self.tabID][0])

    def commandAdd(self, item):

        # command box popup menu
        def ScriptSaveToFile():
            initial = "script" + str(self.commandActive + 1) + ".py"
            location = tkFileDialog.asksaveasfilename(
                initialdir=OMFITaux['lastBrowsedDirectory'],
                initialfile=os.path.split(initial)[1],
                filetypes=[("Python", "*.py"), ('All files', '.*')],
                parent=OMFITaux['rootGUI'],
            )
            if len(location):
                scripttmp = self.command[self.commandActive].get()
                with open(location, "w") as f:
                    f.write(scripttmp)
                printi("Script " + str(self.commandActive + 1) + " saved to " + location)

                dir = os.path.split(location)[0]
                if len(dir) and os.path.exists(dir) and OMFITcwd not in dir:
                    OMFITaux['lastBrowsedDirectory'] = dir

        def ScriptLoadFromFile():
            location = tkFileDialog.askopenfilename(
                initialdir=OMFITaux['lastBrowsedDirectory'], filetypes=[("Python", "*.py"), ('All files', '.*')], parent=OMFITaux['rootGUI']
            )
            if len(location):
                with open(location, 'r') as f:
                    scripttmp = f.read()
                self.command[self.commandActive].set(scripttmp)
                printi("Script " + str(self.commandActive + 1) + " loaded from " + location)

                dir = os.path.split(location)[0]
                if len(dir) and os.path.exists(dir) and OMFITcwd not in dir:
                    OMFITaux['lastBrowsedDirectory'] = dir

        def ScriptSaveToTree():
            def onEscape():
                top.destroy()

            commandActive = self.commandActive
            top = tk.Toplevel(self.rootGUI)
            top.withdraw()
            top.transient(self.rootGUI)
            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)  # , padx=5, pady=5)
            frm.grid_columnconfigure(1, weight=1)
            top.wm_title('Save OMFITpythonTask')

            def onReturn():
                v2 = newLocation.get()
                try:
                    eval(v2)
                    if 'No' == dialog(title='Overwrite ?', message='Overwrite entry?', answers=['Yes', 'No'], parent=top):
                        return
                except Exception:
                    pass
                v2_ = parseBuildLocation(v2)
                v2base = eval('OMFIT' + parseBuildLocation(v2_[:-1]))
                scriptfile = OMFITpythonTask(str(v2_[-1] + ".py"))
                scripttmp = self.command[commandActive].get()
                with open(scriptfile.filename, "w") as f:
                    f.write(scripttmp)
                v2base[v2_[-1]] = scriptfile
                printi("Script " + str(commandActive + 1) + " placed in " + v2)
                top.destroy()
                self.update_treeGUI()

            ttk.Label(frm, text='To: ').grid(row=1, sticky=tk.E)
            newLocation = tk.OneLineText(frm, width=50, percolator=True)
            newLocation.set(self.focusRootRepr)
            e1 = newLocation
            e1.grid(row=1, column=1, sticky=tk.E + tk.W, columnspan=2)
            e1.focus_set()
            top.bind('<Return>', lambda event: onReturn())
            top.bind('<KP_Enter>', lambda event: onReturn())
            top.bind('<Escape>', lambda event: onEscape())
            top.protocol("WM_DELETE_WINDOW", top.destroy)
            top.update_idletasks()
            tk_center(top, self.rootGUI)
            top.deiconify()
            top.wait_window(top)

        def ScriptLoadFromTree():
            with open(self.linkToFocus.filename, "r") as f:
                scripttmp = f.read()
            self.command[self.commandActive].set(scripttmp)
            printi("Script " + str(self.commandActive + 1) + " loaded from " + self.focusRootRepr)

        def RenameTab():
            def onEscape():
                top.destroy()

            commandActive = self.commandActive
            top = tk.Toplevel(self.rootGUI)
            top.withdraw()
            top.transient(self.rootGUI)
            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)  # , padx=5, pady=5)
            frm.grid_columnconfigure(1, weight=1)
            top.wm_title('Rename tab')

            def onReturn():
                v2 = newLocation.get()
                self.commandNames[self.commandActive] = v2
                top.destroy()
                self.update_treeGUI()
                self.commandSelect()

            ttk.Label(frm, text='Name: ').grid(row=1, sticky=tk.E)
            newLocation = tk.OneLineText(frm, width=50, percolator=False)
            newLocation.set(self.commandNames[self.commandActive])
            e1 = newLocation
            e1.grid(row=1, column=1, sticky=tk.E + tk.W, columnspan=2)
            e1.focus_set()
            top.bind('<Return>', lambda event: onReturn())
            top.bind('<KP_Enter>', lambda event: onReturn())
            top.bind('<Escape>', lambda event: onEscape())
            top.protocol("WM_DELETE_WINDOW", top.destroy)
            top.update_idletasks()
            tk_center(top, self.rootGUI)
            top.deiconify()
            top.wait_window(top)

        scriptpopup = tk.Menu(self.leftright_pan, tearoff=0)
        scriptpopup.add_command(label="Load from file", command=ScriptLoadFromFile)
        scriptpopup.add_command(label="Save to file", command=ScriptSaveToFile)
        scriptpopup.add_command(label="Load from tree", command=ScriptLoadFromTree)
        scriptpopup.add_command(label="Save to tree", command=ScriptSaveToTree)
        scriptpopup.add_command(label="Rename tab", command=RenameTab)
        scriptpopup.add_separator()
        # Format style
        def format(item):
            self.command[item].set(omfit_formatter(self.command[item].get()))

        scriptpopup.add_command(label="Style format", command=lambda item=item: format(item=item))
        scriptpopup.add_separator()
        # Copy/paste from https://stackoverflow.com/a/21467986/768675
        scriptpopup.add_command(label="Cut", command=lambda item=item: self.command[item].event_generate('<<Cut>>'))
        scriptpopup.add_command(label="Copy", command=lambda item=item: self.command[item].event_generate('<<Copy>>'))
        scriptpopup.add_command(label="Paste", command=lambda item=item: self.command[item].event_generate('<<Paste>>'))

        def middle_click(item=0):
            try:
                self.command[item].insert('insert', self.command[item].selection_get(selection='PRIMARY'))
            except Exception:
                pass

        scriptpopup.add_command(label="Paste (Middle-click)", command=lambda item=item: middle_click(item=item))

        def update(item=0):
            if self.focus and not isinstance(self.linkToFocus, OMFITpythonGUI) and isinstance(self.linkToFocus, _OMFITpython):
                scriptpopup.entryconfig(2, state=tk.NORMAL)
            else:
                scriptpopup.entryconfig(2, state=tk.DISABLED)
            try:
                self.command[item].selection_get(selection='PRIMARY')
            except Exception:
                scriptpopup.entryconfig(9, state=tk.DISABLED)

        scriptpopup.config(postcommand=lambda item=item: update(item=item))

        def do_scriptpopup(event):
            scriptpopup.post(event.x_root, event.y_root)
            scriptpopup.focus_set()

        scriptpopup.bind("<FocusOut>", lambda event: scriptpopup.unpost())

        self.command.append(
            tk.ConsoleTextGUI(
                self.commandLabelFrame,
                name='OMFIT command box #' + str(item + 1),
                width=80,
                relief=tk.GROOVE,
                border=1,
                OMFITcwd=OMFITcwd,
                OMFITpythonTask=OMFITpythonTask,
                OMFITpythonGUI=OMFITpythonGUI,
                OMFITx=OMFITx,
            )
        )

        doWrap = self.command[self.commandActive].configure('wrap')[4].lower() != 'none'
        if doWrap:
            self.ckWrap2.state(['selected'])
            self.command[item].configure(wrap='char')
        else:
            self.ckWrap2.state(['!selected'])
            self.command[item].configure(wrap='none')

        self.command[item].clearTextOnExecution = False
        self.command[item].interactive()

        self.commandNotebook.forget(self.commandNotebook.tabs()[-1])
        if (item == 0 and len(self.commandNames) == 0) or item != 0:
            self.commandNames.append(str(item + 1))
        self.commandNotebook.add(self.command[item], text=' ' + self.commandNames[-1] + ' ')
        self.commandNotebook.add(ttk.Frame(self.commandLabelFrame), text=' + ')

        # bindings
        self.command[item].bind("<<set-line-and-column>>", lambda event: self.set_line_and_column())
        self.command[item].event_add("<<set-line-and-column>>", "<KeyRelease>", "<ButtonRelease>")
        self.command[item].after_idle(self.set_line_and_column)
        self.command[item].bind(f"<{rightClick}>", do_scriptpopup)

        # bindings for switching between tabs
        def next(*args, **kw):
            tmp = self.commandNotebook.index(self.commandNotebook.select())
            try:
                self.commandNotebook.select(str(int(tmp) + 1))
            except Exception:
                pass
            return 'break'

        def back(*args, **kw):
            tmp = self.commandNotebook.index(self.commandNotebook.select())
            try:
                self.commandNotebook.select(str(int(tmp) - 1))
            except Exception:
                pass
            return 'break'

        global_event_bindings.add('CONSOLE: next tab', self.command[item], f'<{ctrlCmd()}-Prior>', back)
        global_event_bindings.add('CONSOLE: previous tab', self.command[item], f'<{ctrlCmd()}-Next>', next)

        # this should occur only when the OMFIT tree has been initialized
        if 'scratch' in OMFIT:
            self.commandNamespace()

    def commandSelect(self):
        tmp = self.commandNotebook.index(self.commandNotebook.select())

        # if the ` + ` has been pressed
        if tmp == len(self.command):
            self.commandAdd(len(self.command))
            self.commandNotebook.select(tmp)

        # below we handle the tab selection
        if self.commandActive != tmp:
            self.commandActive = tmp
            self.command[self.commandActive].focus()
        for k in range(len(self.command)):
            txt = ' ' + self.commandNames[k]
            if len(self.command[k].get(1.0, tk.END).strip()):
                txt = txt + '*'
            else:
                txt = txt + ' '
            if k == self.commandActive:
                txt = '   %s   ' % (self.commandNames[k])
            self.commandNotebook.tab(k, text=txt)

        # bind the search button to the active commandBox
        self.bf.unbind("<Button-1>")
        self.bf.bind("<Button-1>", lambda event: self.command[self.commandActive].search())

        self.set_line_and_column()

    def set_line_and_column(self):
        line, column = self.command[self.commandActive].index(tk.INSERT).split('.')
        self.rowCol.set(('Ln:%s Col:%s' % (line, column)).ljust(20))
        if not len(self.command[self.commandActive].get()) and len(self.command) > 1:
            self.clear_close_button.configure(text='Close')
        else:
            self.clear_close_button.configure(text='Clear')

    # ------------------
    # TREE ITEM
    # ------------------
    def itemSetupOld(self, GUItype=None):
        self.force_selection()
        self.lastCall = None
        warn_location = [True]

        def destroy():
            top.destroy()
            self.rootGUI.after(100, self.force_tree_focus)

        def onReturn():
            if warn_location[0] and warn_location[0] != location.get():
                try:
                    eval(location.get())
                    allertText.set("Tree location is already in use. Press ENTER again to confirm!")
                    warn_location[0] = location.get()
                    return
                except KeyError:
                    pass
                except Exception as _excp:
                    allertText.set(repr(_excp))
                    return

            v1 = location.get().strip()

            if GUItype == 'advanced':
                v2 = e2text.get(1.0, tk.END)[:-1]
            else:
                v2 = value.get()
            if v1 == v2:
                destroy()
                return
            if isString.get() and v2 != v1:
                v2 = repr(v2)
            if v1.startswith(v2) and v2 != '':
                raise OMFITexception('Attempted recursive reference {} in {}'.format(v2, v1))

            # figure out the namespace
            _special1 = []
            try:
                try:
                    saveOld = eval(v1)
                except KeyError:
                    saveOld = _special1
                finally:
                    setLocation(v1, SortedDict(), globals())
                    namespace = {}
                    namespace.update(globals())
                    namespace.update(relativeLocations(eval(v1)))
            except Exception as _excp:
                allertText.set(repr(_excp))
                return
            finally:
                if saveOld is _special1:
                    d, b = dirbaseLocation(v1)
                    del eval(d)[b]
                else:
                    setLocation(v1, saveOld, namespace)

            # assign the value
            try:
                if not len(v2.strip()):
                    setLocation(v1, OMFITtree(), namespace)
                else:
                    if dynamic_expression.get():
                        setLocation(v1, OMFITexpression(v2), namespace)
                    else:
                        setLocation(v1, eval(v2, namespace), namespace)
                destroy()

            except Exception as _excp:
                allertText.set(repr(_excp))

            finally:
                self.update_treeGUI_and_GUI()

                try:
                    # Try to change lastBrowsedDirectory if it's an OMFIT object
                    # this is to make sure to change lastBrowsedDirectory if the user has typed it in by himself
                    if isinstance(eval(v1), OMFITobject):
                        dir = os.path.split(eval(v1).originalFilename)[0]
                        if len(dir) and os.path.exists(dir) and OMFITcwd not in dir:
                            OMFITaux['lastBrowsedDirectory'] = dir
                except Exception:
                    pass

        def onEvaluate():
            v1 = location.get().strip()

            if GUItype == 'advanced':
                v2 = e2text.get(1.0, tk.END)[:-1]
            else:
                v2 = value.get()
            if isString.get():
                v2 = repr(v2)

            try:
                saveOld = eval(v1)
                namespace = {}
                namespace.update(globals())
                namespace.update(relativeLocations(eval(v1)))
                setLocation(v1, OMFITexpression(v2), namespace)
                tmp = eval(v1)._value_()
                if isinstance(tmp, OMFITexpressionError):
                    printe(tmp.error)
            finally:
                setLocation(v1, saveOld, namespace)

        def onEscape():
            destroy()

        def onClear():
            value.set('')
            e2text.delete('1.0', 'end')

        def onButtonNormal():
            machine = OMFIT['MainSettings']['EXPERIMENT']['device']
            shot = OMFIT['MainSettings']['EXPERIMENT']['shot']
            time = OMFIT['MainSettings']['EXPERIMENT']['time']
            runid = OMFIT['MainSettings']['EXPERIMENT']['runid']

            e2.config(state=tk.NORMAL)
            c1.config(state=tk.NORMAL)
            c2.config(state=tk.DISABLED)
            c2.state(['!selected'])
            c0.state(['!selected'])
            remoteFile.config(state=tk.DISABLED)
            if tp.get() == 'None':
                value.set('None')
            elif tp.get() == 'int':
                value.set('0')
            elif tp.get() == 'float':
                value.set('0.0')
            elif tp.get() == 'complex':
                value.set('(0+0j)')
            elif tp.get() == 'str':
                value.set('""')
            elif tp.get() == 'ufloat':
                value.set('ufloat_fromstr("1+/-0.1")')
            elif tp.get() == 'linspace':
                value.set("np.linspace(0,1,10)")
            elif tp.get() == 'array':
                value.set("np.array([0,0])")
            elif tp.get() == 'matrix':
                value.set("np.matrix([[0,0],[0,0]])")
            elif tp.get() == 'OMFITeqdsk':
                onButtonOMFIT()
                return
            elif tp.get() in ['OMFITmds', 'OMFITmdsValue']:
                printi('----------------')
                if is_device(machine, ('NSTX', 'NSTX-U')):
                    printi('NSTX/NSTX-U MDS+ trees')
                    # fmt: off
                    printi(re.sub('[\[\n\]]', '', str(np.array(
                        ['ACQ_INFO', 'ACTIVESPEC', 'CAMERAS', 'CAMERAS2', 'CLOCK', 'DCPS', 'DERIVED', 'EDGE', 'EFIT', 'EFITRT',
                         'EFITRT_DEV', 'ENGINEERING', 'ENG_DEV', 'FASTMAG', 'FUELING', 'GASPUFFIMGNG', 'LITHIUM', 'LONGSHOT', 'MICROWAVE',
                         'MMWR', 'MSE', 'NBI', 'NSTX_VALID', 'OPERATIONS', 'OPS_PC', 'PARTICLES', 'PASSIVESPEC', 'PROBES', 'PSPEC_PC', 'RF',
                         'SFLIP', 'SHOTMODE', 'SHOTNO', 'UCLA_INTERF', 'USXR', 'WF']))))
                    # fmt: on
                    default_tree = 'EFIT'
                elif is_device(machine, 'DIII-D'):
                    printi('DIII-D MDS+ trees')
                    # fmt: off
                    printi(re.sub('[\[\n\]]', '', str(np.array(
                        ['AOT', 'AOT01...12', 'AVIEWTEST', 'BALOO', 'BATTERY', 'BCI', 'BES', 'BIOFUEL', 'BOLOM', 'BOLPWR', 'CONT01...12',
                         'D3D', 'DCON', 'DDB', 'DSPRED', 'ECE', 'EDGE', 'EFIT', 'EFIT01...20', 'EFITDE', 'EFITRT1', 'EFITRT2', 'EFITS1',
                         'EFITS2', 'EFITnn', 'ELECTRONS', 'FISSION', 'FLUCTUATIONS', 'GAPROF', 'GATO', 'IMAGE', 'IMPCON01', 'IMPCON02',
                         'IMPCONU', 'IONS', 'IRTV', 'ITPA', 'LANGMUIR', 'LIBEAM', 'M3D', 'MHD', 'MICROX', 'MOD', 'MSE', 'MSEFAQ03', 'N/A',
                         'NB', 'NEUTRALS', 'NIMROD', 'ONETWO', 'ONETWO01...12', 'OPERATIONS', 'OT', 'OT01...12', 'PED', 'PEDESTAL',
                         'PERFMON', 'PI', 'PREFERENCES', 'PROFDB', 'PYFIT', 'PYFIT01', 'PYFIT02', 'PYFIT03', 'PYFIT04', 'RF', 'RWM',
                         'SPECTROSCOPY', 'STATIC', 'SURFMN', 'SYNMSE', 'TANGTV', 'TANGTVA', 'TANHFIT', 'TEST', 'TRANSP', 'TRANSP01...12',
                         'TRANSPORT', 'TRANSPTEST', 'TRENDS', 'TRIP3D', 'TSCAL', 'TSRAW', 'WALL', 'ZIPFIT01', 'ZIPFIT02', 'ZIPFITU']))))
                    # fmt: on
                    default_tree = 'ELECTRONS'
                elif is_device(machine, 'AUG'):
                    printi('AUG MDS+ tree')
                    default_tree = None

                print('Machine: ', machine)

                printi(' >> note <<  Use .data(), .units() , .dim_of(0), .units_dim_of(0) to access info of OMFITmdsValue objects')
                printi('----------------')
                if tp.get() == 'OMFITmds':
                    value.set(f"OMFITmds('{machine}', treename='{default_tree}', shot={shot}, subtree='')")
                elif tp.get() == 'OMFITmdsValue':
                    value.set(f"OMFITmdsValue('{machine}', treename='', shot={shot}, TDI='')")
                c1.config(state=tk.DISABLED)
                c1.state(['!selected'])
            elif tp.get() == 'OMFITosborneProfile':
                value.set(
                    "OMFITosborneProfile(server="
                    + repr(machine)
                    + ", treename='PEDESTAL', shot="
                    + repr(shot)
                    + ', time='
                    + repr(time)
                    + ', runid='
                    + repr(runid)
                    + ')'
                )
                c1.config(state=tk.DISABLED)
                c1.state(['!selected'])
            elif tp.get() == 'OMFITrdb':
                printi('----------------')
                printi('`d3drdb` for DIII-D SQL database')
                printi('https://diii-d.gat.com/DIII-D/comp/database/d3drdb/tablelist.php')
                printi('----------------')
                printi("`d3d` for Osborne's SQL database")
                printi('----------------')
                value.set(
                    """OMFITrdb("select * from summaries where shot>150700 and shot<150800 and ip_flat>8E5",db='d3drdb',server='d3drdb',by_column=True)"""
                )
                c1.config(state=tk.DISABLED)
                c1.state(['!selected'])
            elif tp.get() == 'OMFITharvest':
                value.set("OMFITharvest(table=None,limit=None)")
                c1.config(state=tk.DISABLED)
                c1.state(['!selected'])
            elif tp.get() == 'OMFITharvestS3':
                value.set("OMFITharvestS3(table='', limit=None, by_column=True, skip_underscores=True)")
                c1.config(state=tk.DISABLED)
                c1.state(['!selected'])
            elif tp.get() == 'ODS':
                value.set("ODS()")
                c1.config(state=tk.DISABLED)
                c1.state(['!selected'])
            elif tp.get() == 'OMFITwebLink':
                value.set("OMFITwebLink('gafusion.github.io/OMFIT-source/')")
                c1.config(state=tk.DISABLED)
                c1.state(['!selected'])
            elif tp.get() == 'OMFITtoksearch':
                value.set("OMFITtoksearch( [133221], {'ip':TKS_PtDataSignal('ip')}, functions=None, where=None,  return_data='by_shot')")
            elif tp.get() == 'empty':
                value.set('')
                e2.config(state=tk.DISABLED)
            self.lastCall = None

        def onButtonOMFIT():
            e2.config(state=tk.NORMAL)
            c1.config(state=tk.DISABLED)
            c2.config(state=tk.NORMAL)
            c0.state(['!selected'])
            remoteFile.config(state=tk.NORMAL)
            c1.state(['!selected'])
            if len(filename.get()):
                value.set(tp.get() + '("' + filename.get() + '")')
            else:
                value.set(tp.get() + '("")')
            e2.icursor(tk.END)
            e2.xview(tk.END)
            self.lastCall = onButtonOMFIT

        def onFile():
            if GUItype == 'advanced':
                v2 = e2text.get(1.0, tk.END)
            else:
                v2 = value.get()
            v2 = re.sub(r"^[^\(]*\((.*)\)[^\)]*$", r"\1", v2).split(',')
            for k, item in enumerate(v2):
                try:
                    v2[k] = eval(item)
                except Exception:
                    pass
            if len(v2) and len(v2[0]):
                tmp = v2[0]
            else:
                tmp = None

            tmp = OMFITx.remoteFile(top, transferRemoteFile=True, remoteFilename=tmp)
            if tmp is not None:
                e2.config(state=tk.NORMAL)
                c1.config(state=tk.DISABLED)
                c1.state(['!selected'])
                c2.config(state=tk.DISABLED)
                c2.state(['!selected'])
                filename.set(tmp)
                if self.lastCall is not None:
                    self.lastCall()
                e2.icursor(tk.END)
                e2.xview(tk.END)

        def toggleDynamic(TestExpr, c2):
            if not dynamic_expression.get():
                TestExpr.config(state=tk.DISABLED)
                c2.config(state=tk.NORMAL)
                c0.config(state=tk.NORMAL)
            else:
                TestExpr.config(state=tk.NORMAL)
                c2.state(['!selected'])
                c2.config(state=tk.DISABLED)
                c0.state(['!selected'])
                c0.config(state=tk.DISABLED)

        def toggleModifyOriginal(GUItype, tp, value):
            tmp = re.sub(',modifyOriginal=True', '', value.get())
            tmp = re.sub(',modifyOriginal=False', '', tmp)
            if modifyOriginal.get():
                value.set(re.sub(r'\)$', ',modifyOriginal=True)', tmp))
            else:
                value.set(tmp)

        def toggleString():
            tmp = e2.get()
            e2.delete('1.0', 'end')
            e2.set_highlight(not isString.get())
            e2.set(tmp)

            tmp = e2text.get()
            e2text.delete('1.0', 'end')
            e2text.set_highlight(not isString.get())
            e2text.set(tmp)

        if GUItype is None:
            GUItype = 'guided'
            if isinstance(self.linkToFocus, OMFITexpression):
                if re.findall('\n', self.linkToFocus.expression):
                    GUItype = 'advanced'
            else:
                if isinstance(self.linkToFocus, str) and re.findall('\n', str(self.linkToFocus)):
                    GUItype = 'advanced'
                elif isinstance(self.linkToFocus, np.ndarray):
                    GUItype = 'advanced'

        # Tk variables used
        value = tk.StringVar()
        dynamic_expression = tk.BooleanVar()
        isString = tk.BooleanVar()
        modifyOriginal = tk.BooleanVar()
        allertText = tk.StringVar()
        tp = tk.StringVar()
        filename = tk.StringVar()

        # build the GUI
        top = tk.Toplevel(self.rootGUI)
        top.withdraw()
        top.transient(self.rootGUI)

        ttk.Label(top, textvariable=allertText, foreground='red').pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        ttk.Separator(top).pack(side=tk.TOP, padx=5, expand=tk.NO, fill=tk.X)

        MODES = [
            ("Int", "int", 0),
            ("Float", "float", 1),
            ("Complex", "complex", 2),
            ("Uncertainty", "ufloat", 3),
            ("None", "None", 0),
            ("Linspace", "linspace", 1),
            ("Array", "array", 2),
            ("Matrix", "matrix", 3),
            ("----", "----", 0),
            ("Namelist", "OMFITnamelist", 0),
            ("NetCDF", "OMFITnc", 1),
            ("IDL save", "OMFITidlSav", 2),
            ("IDL language", "OMFITidl", 3),
            ("CSV", "OMFITcsv", 0),
            ("ASCII table", "OMFITasciitable", 1),
            ("INI config", "OMFITini", 2),
            ("MATLAB", "OMFITmatlab", 3),
            ("File", "OMFITpath", 0),
            ("ASCII file", "OMFITascii", 1),
            ("Directory", "OMFITdir", 2),
            ("Web link", "OMFITwebLink", 3),
            ("Python pickle", "OMFITpickle", 0),
            ("HDF5", "OMFIThdf5", 1),
            ("Json", "OMFITjson", 2),
            ("bib", "OMFITbibtex", 3),
            ("----", "----", 0),
            ("EQDSK (g,a,m,k,s)", "OMFITeqdsk", 0),
            ("GA code input", "OMFITgacode", 1),
            ("GA input.gacode", "OMFITinputgacode", 2),
            ("TGYRO dir", "OMFITtgyro", 3),
            ("ONETWO statefile", "OMFITstatefile", 0),
            ("ONETWO outone", "OMFIToutone", 1),
            ("Osborne pFile", "OMFITpFile", 2),
            ("Osborne profiles", "OMFITosborneProfile", 3),
            ("NIMROD", "OMFITnimrod", 0),
            ("U-file", "OMFITuFile", 1),
            ("TRANSP namelist", "OMFITtranspNamelist", 2),
            ("OMAS data structure", "ODS", 3),
            ("CHEASE", "OMFITchease", 0),
            ("GATO", "OMFITdskgato", 1),
            ("MARS", "OMFITmars", 2),
            ("----", "----", 0),
            ("MDS+ tree", "OMFITmds", 0),
            ("MDS+ value", "OMFITmdsValue", 1),
            ("SQL database", "OMFITrdb", 2),
            ("HARVEST dB", "OMFITharvestS3", 3),
            ("Toksearch Query", "OMFITtoksearch", 0),
            ("----", "----", 0),
            ("Python task", "OMFITpythonTask", 0),
            ("Python GUI", "OMFITpythonGUI", 1),
            ("Python plot", "OMFITpythonPlot", 2),
            ("Python regression", "OMFITpythonTest", 3),
            ("----", "----", 0),
            ("OMFIT tree", "OMFITtree", 0),
            ("OMFIT collection", "OMFITcollection", 1),
            ("OMFIT module", "OMFITmodule", 2),
            ("OMFIT project", "OMFITproject", 3),
        ]

        if GUItype == 'advanced':
            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, padx=5, expand=tk.NO, fill=tk.X)

            top.wm_title('Setup tree entry (ADVANCED)')
            ttk.Label(frm, text="Entry location: ").pack(side=tk.LEFT)
            e1 = tk.OneLineText(frm, percolator=True)
            location = e1
            e1.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=tk.YES)

            e2 = tk.OneLineText(frm)  # this is just a placeholder
            e2text = tk.ConsoleTextGUI(
                top,
                wrap=tk.NONE,
                undo=tk.TRUE,
                maxundo=-1,
                relief=tk.GROOVE,
                border=1,
                height=12,
                percolator=True,
                font=OMFITfont('normal', 0, 'Courier'),
            )
            e2text.bind(f'<{ctrlCmd()}-Return>', 'break')
            e2text.pack(side=tk.TOP, padx=5, pady=5, expand=tk.YES, fill=tk.BOTH)
            allertText.set("Remember to set `return_variable = ...` to the value you want to assign to the tree entry")

            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            c2 = ttk.Checkbutton(
                frm, text="Modify original file", variable=modifyOriginal, command=lambda: toggleModifyOriginal(GUItype, tp, value)
            )
            c1 = ttk.Checkbutton(frm, text="Dynamic expression", variable=dynamic_expression, command=lambda: toggleDynamic(TestExpr, c2))
            c0 = ttk.Checkbutton(frm, text="is string", variable=isString, command=toggleString)
            c0.state(['!alternate'])  # removes color box bg indicating user has not clicked it
            c1.state(['!alternate'])  # removes color box bg indicating user has not clicked it
            c2.state(['!alternate'])  # removes color box bg indicating user has not clicked it
            c0.pack(side=tk.LEFT, padx=5, pady=5, expand=tk.NO)
            c1.pack(side=tk.LEFT, padx=5, pady=5, expand=tk.NO)
            ttk.Label(frm).pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
            ttk.Button(frm, text="Update", command=onReturn).pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
            TestExpr = ttk.Button(frm, text="Test Expression", command=onEvaluate)
            TestExpr.pack(side=tk.LEFT)
            ttk.Label(frm).pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
            ttk.Button(frm, text="Clear", command=onClear).pack(side=tk.LEFT)

        elif GUItype == 'guided':
            top.wm_title('Setup tree entry (GUIDED)')
            top.resizable(1, 0)

            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, padx=5, expand=tk.NO, fill=tk.X)
            ttk.Label(frm, text="Entry location: ").pack(side=tk.LEFT)
            e1 = tk.OneLineText(frm, percolator=True)
            location = e1
            e1.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, padx=5, expand=tk.NO, fill=tk.X)
            ttk.Label(frm, text="Entry value: ").pack(side=tk.LEFT)
            e2 = tk.OneLineText(frm, width=50, percolator=True)
            value = e2
            e2.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
            e2text = tk.ScrolledText(top)  # this is just a placeholder

            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, padx=5, expand=tk.NO, fill=tk.X)
            ttk.Label(frm).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
            remoteFile = ttk.Button(frm, text="Open file...", command=onFile)
            remoteFile.state(['disabled'])
            remoteFile.pack(side=tk.LEFT)
            ttk.Label(frm).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
            c2 = ttk.Checkbutton(
                frm, text="Modify original file", variable=modifyOriginal, command=lambda: toggleModifyOriginal(GUItype, tp, value)
            )
            c1 = ttk.Checkbutton(frm, text="Dynamic expression", variable=dynamic_expression, command=lambda: toggleDynamic(TestExpr, c2))
            c0 = ttk.Checkbutton(frm, text="is string", variable=isString, command=toggleString)
            c0.state(['!alternate'])  # removes color box bg indicating user has not clicked it
            c1.state(['!alternate'])  # removes color box bg indicating user has not clicked it
            c2.state(['!alternate'])  # removes color box bg indicating user has not clicked it
            if GUItype == 'advanced':
                c0.pack(side=tk.LEFT, padx=5, pady=5, expand=tk.NO)
            c2.pack(side=tk.LEFT, padx=5, pady=5, expand=tk.NO)
            c1.pack(side=tk.RIGHT, padx=5, pady=5, expand=tk.NO)
            dynamic_expression.set(False)
            TestExpr = ttk.Button(frm, text="Test Expression", command=onEvaluate)
            # radio button
            ttk.Separator(top).pack(side=tk.TOP, padx=5, expand=tk.NO, fill=tk.X)
            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            row = 0
            for text, mode, arrange in MODES:
                if mode == '----':
                    rd = ttk.Separator(frm)
                    row = row + 1
                    rd.grid(row=row, column=arrange, sticky=tk.E + tk.W + tk.N + tk.S, columnspan=10)
                else:
                    if (
                        mode in OMFITtypesStr or mode in ['OMFITtree', 'OMFITmodule', 'OMFITproject', 'OMFITtgyro', 'OMFITpickle']
                    ) and mode not in ['OMFITharvestS3']:
                        rd = ttk.Radiobutton(frm, text=text, variable=tp, value=mode, command=onButtonOMFIT)
                    else:
                        rd = ttk.Radiobutton(frm, text=text, variable=tp, value=mode, command=onButtonNormal)
                    if arrange == 0:
                        row = row + 1
                        frm.grid_rowconfigure(0, weight=1)
                    rd.grid(row=row, column=arrange, sticky=tk.W + tk.N)
                    frm.grid_columnconfigure(arrange, weight=1)

        else:
            raise ValueError('GUItype can only be `advanced` or `guided`')

        if self.linkToFocus.__class__.__name__ in OMFITtypesStr:
            tp.set(self.linkToFocus.__class__.__name__)
            c1.state(['!selected'])
            c1.config(state=tk.DISABLED)
        else:
            tp.set(self.linkToFocus.__class__.__name__)

        if self.focusRootRepr:
            location.set(self.focusRootRepr)
        dynamic_expression.set(False)
        value.set('')
        e2text.delete('1.0', 'end')

        modifyOriginal.set(False)
        if hasattr(self.linkToFocus, 'modifyOriginal'):
            modifyOriginal.set(self.linkToFocus.modifyOriginal)

        # setup entries
        if not len(self.focus):
            location.set("OMFIT['test']")
        else:
            tmp = tree_entry_repr(self.linkToFocus, tp.get())
            dynamic_expression.set(tmp[1])
            value.set(tmp[0])
            if isinstance(self.linkToFocus, str) and not isinstance(self.linkToFocus, OMFITexpression):
                if GUItype == 'advanced':
                    isString.set(True)
                    value.set(self.linkToFocus)

        e2text.insert(tk.END, value.get())

        toggleDynamic(TestExpr, c2)
        toggleModifyOriginal(GUItype, tp, value)
        toggleString()

        # last few details
        e2text.focus_set()
        e2.focus_set()
        if GUItype == 'advanced':
            e2text.bind(f'<{ctrlCmd()}-Return>', lambda event: onReturn())
        else:
            top.bind('<Return>', lambda event: onReturn())
            top.bind('<KP_Enter>', lambda event: onReturn())
        top.bind('<Escape>', lambda event: onEscape())

        top.protocol("WM_DELETE_WINDOW", destroy)
        top.update_idletasks()
        tk_center(top, self.rootGUI)
        top.deiconify()
        top.wait_window(top)

    def itemSetup(self):

        # on Return
        warn_location = [True]

        def onReturn():
            if warn_location[0] and warn_location[0] != location.get():
                try:
                    eval(location.get())
                    allertText.set("Tree location is already in use. Press ENTER again to confirm!")
                    warn_location[0] = location.get()
                    return
                except KeyError:
                    pass
                except Exception as _excp:
                    allertText.set(repr(_excp))
                    return

            v1 = location.get().strip()
            v2 = value.get()

            if v1 == v2:
                destroy()
                return
            if v1.startswith(v2) and v2 != '':
                raise OMFITexception('Attempted recursive reference {} in {}'.format(v2, v1))

            # figure out the namespace
            _special1 = []
            try:
                try:
                    saveOld = eval(v1)
                except KeyError:
                    saveOld = _special1
                finally:
                    setLocation(v1, SortedDict(), globals())
                    namespace = {}
                    namespace.update(globals())
                    namespace.update(relativeLocations(eval(v1)))
            except Exception as _excp:
                allertText.set(repr(_excp))
                return
            finally:
                if saveOld is _special1:
                    d, b = dirbaseLocation(v1)
                    del eval(d)[b]
                else:
                    setLocation(v1, saveOld, namespace)

            # assign the value
            try:
                if not len(v2.strip()):
                    setLocation(v1, OMFITtree(), namespace)
                else:
                    if dynamic_expression.get():
                        setLocation(v1, OMFITexpression(v2), namespace)
                    else:
                        setLocation(v1, eval(v2, namespace), namespace)
                top.destroy()

            except Exception as _excp:
                allertText.set(repr(_excp))

            finally:
                self.update_treeGUI_and_GUI()

                try:
                    # Try to change lastBrowsedDirectory if it's an OMFIT object
                    # this is to make sure to change lastBrowsedDirectory if the user has typed it in by himself
                    if isinstance(eval(v1), OMFITobject):
                        dir = os.path.split(eval(v1).originalFilename)[0]
                        if len(dir) and os.path.exists(dir) and OMFITcwd not in dir:
                            OMFITaux['lastBrowsedDirectory'] = dir
                except Exception:
                    pass

        # on Escape
        def onEscape():
            top.destroy()

        # store arguments entered by user
        old_class_name = [None]
        old_class_default_args = {}
        retain_args = {}

        def update_retain_args():
            if old_class_name[0] and re.match('(\w+\(.*\))', value.get()):
                try:
                    tmp = 'inspect.getcallargs(%s.__init__,None,%s)' % (
                        old_class_name[0],
                        re.sub('%s(\(.*\))' % old_class_name[0], r'\1', value.get())[1:-1],
                    )
                    tmp = eval(tmp)
                    for item in tmp:
                        if item in old_class_default_args and (
                            item != 'filename'
                            and tmp[item] != eval(old_class_default_args[item])
                            or (item == 'filename' and tmp[item] not in [eval(old_class_default_args[item]), '', None])
                        ):
                            retain_args[item] = tmp[item]
                except (TypeError, SyntaxError) as _excp:
                    pass

        # populate classes tree
        added = {}

        def insert_entries():
            for item in classesTreeGUI.get_children():
                classesTreeGUI.delete(item)
            flt = re.compile(re.escape(filter_cls.get()), re.I)
            added.clear()
            for k, group in enumerate(['name', 'module', 'description']):
                for cls in classes:
                    cls_name = re.sub(r"\<.*'(.*)'\>", r'\1', str(cls).strip(')('))
                    cls_name = re.sub('^(omfit_tree)\.', '', cls_name)
                    module = '.'.join(cls_name.split('.')[:-1])
                    name = cls_name.split('.')[-1]
                    description = cls.__doc__
                    if description is None:
                        description = ''
                    if re.search(flt, eval(group)) and cls_name not in list(added.values()):
                        classesTreeGUI.insert('', tk.END, cls_name, text=name, values=(re.sub('classes\.', '', module),), tag=tuple())
                        added[name] = cls_name

        # upon class selection
        def selectClass(store_args=True):
            if not len(classesTreeGUI.selection()):
                return

            if store_args:
                update_retain_args()

            if len(classesTreeGUI.selection()):
                cls_name = classesTreeGUI.selection()[0]
                cls = eval(cls_name)
                module = '.'.join(cls_name.split('.')[:-1])
                name = cls_name.split('.')[-1]

                # fill out class description
                descText.configure(state=tk.NORMAL)
                descText.delete('1.0', 'end')
                descText.insert('insert', '+-' + '-' * len(cls_name) + '-+', 'separator')
                descText.insert('insert', '\n| ' + cls_name + ' |', 'separator')
                descText.insert('insert', '\n+-' + '-' * len(cls_name) + '-+\n', 'separator')
                if cls.__doc__:
                    descText.insert('insert', '\n'.join(re.sub('\b.', '', pydoc.render_doc(cls)).split('\n')[1:]).strip())
                descText.configure(state=tk.DISABLED)
                descText.see(1.0)

                args, kw, extra_args, extra_kw = function_arguments(cls.__init__)
                init_args_string = []
                if len(args) > 1:
                    init_args_string = ['%s={%s}' % (x, x) for x in args[1:]]
                for item in retain_args:
                    if item in kw:
                        init_args_string += ['%s={%s}' % (item, item)]
                if show_extra_arguments.get() and len(kw):
                    init_args_string += ['%s={%s}' % (x, x) for x in list(kw.keys())]
                init_args_string = unsorted_unique(init_args_string)
                if name in OMFITtypesStr:
                    for item in ['modifyOriginal', 'readOnly']:
                        if retain_args.get(item, False) or show_extra_arguments.get():
                            init_args_string += ['%s={%s}' % (item, item)]
                init_args_string = ', '.join(init_args_string).strip()
                for item in args[1:]:
                    kw[item] = '_^_%s_^_' % item
                for item in kw:
                    kw[item] = repr(kw[item])
                if name in OMFITtypesStr:
                    for attr in ['modifyOriginal', 'readOnly']:
                        kw[attr] = 'False'
                old_class_default_args.clear()
                old_class_default_args.update(kw)
                for item in retain_args:
                    kw[item] = repr(retain_args[item])
                tmp = (name + '(%s)' % init_args_string).format(**kw)
                for item in args[1:]:
                    tmp = re.sub('\'_\^_%s_\^_\'' % item, '', tmp)
                value.set(tmp)
                old_class_name[0] = name

        # on clicking file button
        def onFile():
            update_retain_args()
            tmp = OMFITx.remoteFile(top, transferRemoteFile=True, remoteFilename=retain_args.get('filename', ''))
            retain_args['filename'] = tmp
            selectClass(store_args=False)
            value.focus_set()

        top = tk.Toplevel(self.rootGUI)
        top.withdraw()
        top.transient(self.rootGUI)

        top.wm_title('Set OMFIT tree entry...')

        allertText = tk.StringVar()
        ttk.Label(top, textvariable=allertText, foreground='red').pack(side=tk.TOP, expand=tk.NO, fill=tk.X)

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        ttk.Label(frm, text='Entry Location: ').pack(side=tk.LEFT, padx=5, pady=5)
        location = tk.OneLineText(frm, percolator=True, width=100)
        location.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)
        location.icursor(tk.END)
        location.xview(tk.END)
        location.set("OMFIT['test']")
        location.bind('<Return>', lambda event: onReturn())
        location.bind('<KP_Enter>', lambda event: onReturn())

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        ttk.Label(frm, text='Value: ').pack(side=tk.LEFT, padx=5, pady=5)
        value = tk.OneLineText(frm, percolator=True)
        value.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)
        value.icursor(tk.END)
        value.xview(tk.END)
        value.set('')
        value.bind('<Return>', lambda event: onReturn())
        value.bind('<KP_Enter>', lambda event: onReturn())

        ttk.Separator(top).pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=5)

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
        frm1 = ttk.Frame(frm)
        frm1.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        text = 'Classes filter: '
        ttk.Label(frm1, text=text).pack(side=tk.LEFT)
        filter_cls = ttk.Entry(frm1)
        filter_cls.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        filter_cls.icursor(tk.END)
        filter_cls.xview(tk.END)
        filter_cls.bind("<Key>", lambda event: classesTreeGUI.after(1, insert_entries))

        remoteFile = ttk.Button(frm1, text="Open file...", command=onFile)
        remoteFile.pack(side=tk.LEFT)

        dynamic_expression = tk.BooleanVar()
        dynamic_expression_ck = ttk.Checkbutton(frm1, text="dynamic expression", variable=dynamic_expression, command=selectClass)
        dynamic_expression_ck.state(['!alternate'])  # removes color box bg indicating user has not clicked it
        dynamic_expression_ck.pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
        show_extra_arguments = tk.BooleanVar()
        show_extra_arguments_ck = ttk.Checkbutton(frm1, text="show all class arguments", variable=show_extra_arguments, command=selectClass)
        show_extra_arguments_ck.state(['!alternate'])  # removes color box bg indicating user has not clicked it
        show_extra_arguments_ck.pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)

        classesTreeGUI = tk.Treeview(frm, height=15, selectmode='browse')
        classesTreeGUI.frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        descText = tk.ScrolledText(frm, width=60, font=OMFITfont('normal', 0, 'Courier'))
        descText.configure(wrap='none')
        descText.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
        descText.tag_configure('historic', foreground='dark slate gray')
        descText.tag_configure('error', foreground='red')
        descText.tag_configure('separator', foreground='blue')
        descText.tag_configure('warning', foreground='dark orange')
        classesTreeGUI["columns"] = '#1'
        classesTreeGUI.column("#0", minwidth=250, stretch=True)
        classesTreeGUI.column("#1", stretch=False)
        classesTreeGUI.heading("#0", text="Class")
        classesTreeGUI.bind('<Button-1>', lambda event: classesTreeGUI.after(10, selectClass))
        classesTreeGUI.bind('<Up>', lambda event: classesTreeGUI.after(10, selectClass))
        classesTreeGUI.bind('<Down>', lambda event: classesTreeGUI.after(10, selectClass))

        classes = sorted(OMFITtypes + OMFITdictypes, key=lambda x: str(x))
        insert_entries()

        top.bind('<Escape>', lambda event: onEscape())

        # if something in the tree was selected
        if self.focusRootRepr:
            location.set(self.focusRootRepr)

            # dynamic expressions
            if isinstance(self.linkToFocus, OMFITexpression):
                dynamic_expression.set(True)
                value.set(self.linkToFocus.expression)

            # other objects
            else:
                # OMFIT classes
                if self.linkToFocus.__class__.__name__ in added:
                    insert_entries()
                    try:
                        classesTreeGUI.selection_set(added[self.linkToFocus.__class__.__name__])
                        classesTreeGUI.see(added[self.linkToFocus.__class__.__name__])
                    except Exception:
                        pass
                    if self.linkToFocus.__class__.__name__ in OMFITtypesStr:
                        for attr in ['filename', 'modifyOriginal', 'readOnly']:
                            if hasattr(self.linkToFocus, attr):
                                retain_args[attr] = getattr(self.linkToFocus, attr)
                    selectClass()  # this sets the value for known classes
                # Do not repr an ODS
                elif isinstance(self.linkToFocus, ODS):
                    value.set('ODS()')
                # not OMFIT classes
                else:
                    filter_cls.delete(0, 'end')
                    value.set(repr(self.linkToFocus))

            # place cursor in value field
            value.focus_set()

        # if nothing in the tree was selected place cursor in class filter field
        else:
            filter_cls.focus_set()

        top.protocol("WM_DELETE_WINDOW", top.destroy)
        top.update_idletasks()
        tk_center(top, self.rootGUI)
        top.deiconify()
        top.wait_window(top)

    def itemClear(self, confirm=False):
        self.force_selection()
        linkToFocus = self.linkToFocus
        if linkToFocus is None or not isinstance(linkToFocus, (dict, list)):
            return
        if confirm:
            if 'No' == dialog(
                title="Clear ?",
                message="Clear "
                + self.focusRootRepr
                + '\n\nTIP: use '
                + global_event_bindings.get('TREE: clear entry')
                + ' for rapid clear',
                answers=['Yes', 'No'],
                parent=self.rootGUI,
            ):
                return
        if isinstance(linkToFocus, dict):
            linkToFocus.clear()
        elif isinstance(linkToFocus, list):
            linkToFocus[:] = []
        self.update_treeGUI_and_GUI()

    def itemDelete(self, confirm=False):
        self.force_selection()

        if confirm:
            if 'No' == dialog(
                title="Delete ?",
                message="Delete "
                + self.focusRootRepr
                + '\n\nTIP: use '
                + global_event_bindings.get('TREE: delete entry')
                + ' for rapid deletion',
                answers=['Yes', 'No'],
                parent=self.rootGUI,
            ):
                return

        parent = buildLocation(parseLocation(self.focusRoot)[:-1])
        if isinstance(eval(parent), list):
            next = self.focus
            exec('%s.pop(%d)' % (parent, parseLocation(self.focusRoot)[-1]))
        else:
            next = self.treeGUI.next(self.focus)
            exec('del ' + self.focusRoot)

        self.update_treeGUI_and_GUI()

        try:
            eval('OMFIT' + next)
        except Exception:
            return

        if len(next):
            self.treeGUI.selection_set(tkStringEncode(next))
            self.treeGUI.focus(next)
        self.force_selection()

    def itemRenameDuplicateCompare(self, action='rename', confirm=False):
        self.force_selection()

        def onEscape():
            top.destroy()

        originalLocation = tk.StringVar()
        originalLocation.set(self.focusRootRepr)
        precision = tk.StringVar()
        precision.set('0.0')
        filename_change = tk.StringVar()
        flatten = tk.BooleanVar()
        flatten.set(0)

        top = tk.Toplevel(self.rootGUI)
        top.withdraw()
        top.transient(self.rootGUI)

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X, padx=5, pady=5)
        frm.grid_columnconfigure(1, weight=1)

        if action == 'rename':
            top.wm_title('Rename/Move entry')
            ttk.Label(frm, text='Rename/Move: ').grid(row=0, sticky=tk.E)

            def onReturn():
                v1 = originalLocation.get().strip()
                v2 = newLocation.get().strip()

                if v1 == v2:
                    printi(v1 + ' and ' + v2 + ' are the same location')

                else:
                    v1_ = parseBuildLocation(v1)
                    v2_ = parseBuildLocation(v2)
                    v1base = eval('OMFIT' + parseBuildLocation(v1_[:-1]))
                    v2base = eval('OMFIT' + parseBuildLocation(v2_[:-1]))
                    if id(v1base) == id(v2base) and isinstance(v1base, SortedDict):
                        # insert in place
                        index = v1base.index(v1_[-1])
                        tmp = v1base.pop(v1_[-1])
                        v2base.insert(index, v2_[-1], tmp)
                    else:
                        # insert
                        tmp = v1base.pop(v1_[-1])
                        v2base[v2_[-1]] = tmp

                    if bool(self.treeGUI.item(re.sub('OMFIT\[', '[', v1), 'open')):
                        self.opened_closed[re.sub('OMFIT\[', '[', v2)] = 1
                    else:
                        self.opened_closed[re.sub('OMFIT\[', '[', v2)] = 0
                    self.update_treeGUI_and_GUI()

                top.destroy()

        elif action == 'duplicate' or action == 'deepcopy':
            top.wm_title('%s entry' % action.title())
            if action == 'duplicate' and hasattr(self.linkToFocus, 'duplicate'):
                ttk.Label(frm, text='Duplicate: ').grid(row=0, sticky=tk.E)
            else:
                ttk.Label(frm, text='Copy: ').grid(row=0, sticky=tk.E)

            def onReturn():
                v1 = originalLocation.get().strip()
                v2 = newLocation.get().strip()
                if action == 'deepcopy' and v1 == v2:
                    printi(v1 + ' and ' + v2 + ' are the same location')
                else:
                    if action == 'duplicate' and hasattr(self.linkToFocus, 'duplicate'):
                        tmp = eval(v1).duplicate(filename_change.get())
                    else:
                        tmp = copy.deepcopy(eval(v1))
                    v1_ = parseBuildLocation(v1)
                    v2_ = parseBuildLocation(v2)
                    v1base = eval('OMFIT' + parseBuildLocation(v1_[:-1]))
                    v2base = eval('OMFIT' + parseBuildLocation(v2_[:-1]))
                    if id(v1base) == id(v2base) and isinstance(v1base, SortedDict):
                        # insert in next place
                        index = v1base.index(v1_[-1])
                        v2base.insert(index + 1, v2_[-1], tmp)
                    else:
                        # insert
                        v2base[v2_[-1]] = tmp

                    if bool(self.treeGUI.item(re.sub('OMFIT\[', '[', v1), 'open')):
                        self.opened_closed[re.sub('OMFIT\[', '[', v2)] = 1
                    else:
                        self.opened_closed[re.sub('OMFIT\[', '[', v2)] = 0
                    self.update_treeGUI_and_GUI()

                top.destroy()

        elif action == 'compare':
            top.wm_title('Compare entry')
            ttk.Label(frm, text='Compare: ').grid(row=0, sticky=tk.E)

            def onReturn():
                v1 = originalLocation.get().strip()
                v2 = newLocation.get().strip()
                try:
                    eval(v2)
                except Exception:
                    raise Exception(v2 + ' does not exists')

                if id(eval(v1)) != id(eval(v2)):
                    if isinstance(eval(v1), SortedDict) and isinstance(eval(v2), SortedDict):
                        top.destroy()
                        diffTreeGUI(
                            eval(v1),
                            eval(v2),
                            thisName='Original in ' + v1,
                            otherName='Compared to ' + v2,
                            resultName='Final result in ' + v1,
                            precision=float(precision.get()),
                            deepcopyOther=True,
                            flatten=flatten.get(),
                        )
                        self.update_treeGUI_and_GUI()
                    elif isinstance(eval(v1), OMFITascii) and isinstance(eval(v2), OMFITascii):
                        top.destroy()
                        diffViewer(
                            self.rootGUI,
                            thisFilename=eval(v1).filename,
                            otherFilename=eval(v2).filename,
                            thisName='Original in ' + v1,
                            otherName='Compared to ' + v2,
                            title=None,
                        )
                    else:
                        top.destroy()
                        printi(v2 + ' is not of type ' + eval(v1).__class__.__name__ + ' and can not be compared')
                else:
                    top.destroy()
                    printi(v1 + ' and ' + v2 + ' are the same object (id:' + str(id(eval(v1))) + ')')

        ttk.Label(frm, text=originalLocation.get()).grid(row=0, column=1, sticky=tk.W)
        ttk.Label(frm, text='        ').grid(row=0, column=2, sticky=tk.E)
        ttk.Label(frm, text='To: ').grid(row=1, sticky=tk.E)
        newLocation = tk.OneLineText(frm, width=50, percolator=True)
        newLocation.set(self.focusRootRepr)
        e1 = newLocation
        e1.grid(row=1, column=1, sticky=tk.E + tk.W, columnspan=2)
        e1.focus_set()

        if action == 'duplicate':
            ttk.Label(frm, text='filename: ').grid(row=2, sticky=tk.E)
            e1 = ttk.Entry(frm, textvariable=filename_change)
            filename_change.set(os.path.split(self.linkToFocus.filename)[1])
            e1.grid(row=2, column=1, sticky=tk.E + tk.W, columnspan=2)

        elif action == 'compare' and isinstance(eval(originalLocation.get()), SortedDict):
            ttk.Label(frm, text='Relative precision: ').grid(row=2, sticky=tk.E)
            e1 = ttk.Entry(frm, textvariable=precision)
            e1.grid(row=2, column=1, sticky=tk.E + tk.W, columnspan=2)
            ttk.Label(frm, text='Flatten: ').grid(row=3, column=0, sticky=tk.E)
            ck = ttk.Checkbutton(frm, variable=flatten, text=' (no merge)')
            ck.state(['!alternate'])  # removes color box bg indicating user has not clicked it
            ck.grid(row=3, column=1, sticky=tk.W, columnspan=1)

        def onReturnConfirm():
            if newLocation.get().strip() != originalLocation.get().strip():
                try:
                    eval(newLocation.get().strip())
                    if 'No' == dialog(
                        title=action + " ?",
                        message='Continue with ' + action + " even if it will overwrite content at " + newLocation.get().strip(),
                        answers=['Yes', 'No'],
                        parent=top,
                    ):
                        return
                except Exception as _excp:
                    pass
            onReturn()

        if confirm:
            top.bind('<Return>', lambda event: onReturnConfirm())
            top.bind('<KP_Enter>', lambda event: onReturnConfirm())
        else:
            top.bind('<Return>', lambda event: onReturn())
            top.bind('<KP_Enter>', lambda event: onReturn())
        top.bind('<Escape>', lambda event: onEscape())

        top.protocol("WM_DELETE_WINDOW", top.destroy)
        top.update_idletasks()
        tk_center(top, self.rootGUI)
        top.deiconify()
        top.wait_window(top)

    def itemMove(self, direction='Down'):
        self.force_selection()
        location = parseBuildLocation(self.focusRootRepr)
        OMFITlocation = [OMFIT]
        for k in range(len(location)):
            OMFITlocation.append(OMFITlocation[k][location[k]])

        if isinstance(OMFITlocation[-2], SortedDict):
            index = OMFITlocation[-2].keyOrder.index(location[-1])
            if direction == 'Up':
                OMFITlocation[-2].moveDown(index)
            else:
                OMFITlocation[-2].moveUp(index)
            self._update_treeGUI()
            self.treeGUI.selection_set(tkStringEncode(self.focus))
            self.treeGUI.focus(self.focus)
            self.force_selection()

    def itemRightClicked(self, event):
        try:
            self.popup.unpost()
            self.popup.destroy()
        except Exception:
            pass

        self.force_selection(event)
        focusRoot = self.focusRoot
        linkToFocus = self.linkToFocus
        focusRootRepr = self.focusRootRepr

        self.popup = tk.Menu(self.rootGUI, tearoff=False)

        def remote_terminal(linkToFocus=None):
            username, server, port = setup_ssh_tunnel(
                linkToFocus['server'], linkToFocus.get('tunnel', ''), forceTunnel=False, forceRemote=True
            )
            command_line = "xterm -e '%s %s -t -t -Y -q -p %s %s@%s'" % (
                sshOptions(),
                controlmaster(username, server, port, linkToFocus['server']),
                port,
                username,
                server,
            )
            subprocess.Popen(command_line, shell=True, stdin=subprocess.PIPE)

        if isinstance(linkToFocus, OMFITmodule):

            def setup_module():
                OMFIT['scratch']['__moduleSetupGUI__'].run(base_override=relativeLocations(linkToFocus))

            self.popup.add_command(label="Setup module...", command=setup_module)
            if len(OMFITmodule.directories(checkIsWriteable=True)):
                self.popup.add_command(
                    label='Manage module scripts...', command=lambda: OMFIT['scratch']['__developerModeGUI__'].run(module_link=linkToFocus)
                )
            self.popup.add_separator()

        elif (
            isinstance(linkToFocus, namelist.NamelistName)
            and eval(buildLocation(parseLocation(focusRoot)[:-1])) is OMFIT['MainSettings']['SERVER']
            and 'server' in linkToFocus
        ):
            self.popup.add_command(
                label="Remote X-terminal", command=lambda linkToFocus=linkToFocus: remote_terminal(linkToFocus=linkToFocus)
            )
            if ''.join(decrypt_credential(linkToFocus['server'])):
                self.popup.add_command(
                    label="Reset password", command=lambda linkToFocus=linkToFocus: reset_credential(linkToFocus['server'])
                )

                def print_OTP(linkToFocus):
                    pwd, otp = decrypt_credential(linkToFocus['server'])
                    if len(otp):
                        import pyotp

                        pwd_otp = pwd + pyotp.TOTP(otp).now()
                    else:
                        pwd_otp = pwd
                    printw(linkToFocus['server'] + ' : ' + pwd_otp)

                self.popup.add_command(label="Display password+OTP", command=lambda linkToFocus=linkToFocus: print_OTP(linkToFocus))
            self.popup.add_separator()

        elif hasattr(linkToFocus, '__popup_menu__'):

            submenues = {}
            for item, value in linkToFocus.__popup_menu__():
                sub = linkToFocus.__class__.__name__
                if '>' in item:
                    sub, item = item.split('>')
                if sub not in submenues:
                    submenues[sub] = tk.Menu(self.popup, tearoff=False)
                    self.popup.add_cascade(label=sub, menu=submenues[sub])
                submenues[sub].add_command(label=item, command=value)
            if len(submenues):
                self.popup.add_separator()

        if isinstance(linkToFocus, OMFITmainSettings):
            self.popup.add_command(label="Save as user default settings", command=lambda: self.configMainSettings(updateUserSettings=True))
            self.popup.add_command(
                label="Save user settings to the cloud", command=lambda: self.configMainSettings(updateUserSettings='S3')
            )
            self.popup.add_separator()
            self.popup.add_command(label="Restore user default settings", command=lambda: self.configMainSettings(restore='diff_user'))
            self.popup.add_command(
                label="Restore installation default settings", command=lambda: self.configMainSettings(restore='diff_skel')
            )
            self.popup.add_command(label="Restore user settings from the cloud", command=lambda: self.configMainSettings(restore='diff_S3'))

            if (
                not os.path.exists(os.sep.join([OMFITsrc, '..', 'public']))
                and OMFIT['MainSettings']['SETUP']['email'] in OMFIT['MainSettings']['SETUP']['report_to']
            ):
                self.popup.add_command(label="Update MainSettings skeleton", command=OMFIT.saveMainSettingsSkeleton)
            self.popup.add_separator()
            self.popup.add_command(label="Copy tree location", command=lambda: self.clipboard(what='location'))

        elif isinstance(linkToFocus, _OMFITnoSave):
            self.popup.add_command(label="Copy tree location", command=lambda: self.clipboard(what='location'))
            if isinstance(linkToFocus, OMFITtmp):
                self.popup.add_command(label="Clean entry", command=lambda: self.itemClear(confirm=True))
                self.popup.add_command(label="Compare/Merge entry...", command=lambda: self.itemRenameDuplicateCompare(action='compare'))

        elif isinstance(linkToFocus, OMFITmdsValue):
            self.popup.add_command(label="Copy tree location", command=lambda: self.clipboard(what='location'))
            self.popup.add_separator()
            self.popup.add_command(label="Fetch data", command=self.runLinkToFocus)
            self.popup.add_command(label="Quick plot", command=self.quickPlotF)
            self.popup.add_command(label="Quick over plot", command=self.quickPlot)

        else:
            self.popup.add_command(label="Edit tree entry...", command=self.itemSetupOld)
            self.popup.add_command(
                label="Move/Rename entry...", command=lambda: self.itemRenameDuplicateCompare(action='rename', confirm=True)
            )
            extra_text = ['', '']
            if not isinstance(linkToFocus, _OMFITpython) and hasattr(linkToFocus, 'duplicate'):
                extra_text = [' (same file reference)', ' (new file reference)']
            if not isinstance(linkToFocus, _OMFITpython):
                self.popup.add_command(
                    label="Deepcopy entry%s..." % extra_text[0],
                    command=lambda: self.itemRenameDuplicateCompare(action='deepcopy', confirm=True),
                )
            if hasattr(linkToFocus, 'duplicate'):
                self.popup.add_command(
                    label="Duplicate entry%s..." % extra_text[1],
                    command=lambda: self.itemRenameDuplicateCompare(action='duplicate', confirm=True),
                )

            self.popup.add_separator()
            if isinstance(linkToFocus, (dict, list)):
                if not isinstance(linkToFocus, OMFITmodule):
                    self.popup.add_command(label="Clean entry...", command=lambda: self.itemClear(confirm=True))
            self.popup.add_command(label="Delete entry...", command=lambda: self.itemDelete(confirm=True))

            # OMFITcollection
            self.popup.add_separator()
            if isinstance(linkToFocus, OMFITcollection):

                def set_selector(selector):
                    linkToFocus.selector = eval(selector)
                    self.update_treeGUI()

                submenu = tk.Menu(self.popup, tearoff=False)
                for k, selector in enumerate(['None', repr('random')] + list(map(repr, linkToFocus.KEYS()))):
                    if k == 2:
                        submenu.add_separator()
                    submenu.add_command(label=selector, command=lambda selector=selector: set_selector(selector))
                self.popup.add_cascade(label="Collection", menu=submenu)
                self.popup.add_command(label='Sort keys', command=self.sort)

            # not OMFITcollection or OMFITcollection with selector!=None
            if not isinstance(linkToFocus, OMFITcollection) or linkToFocus.selector != None:

                if isinstance(linkToFocus, OMFITobject) and linkToFocus.filename is not None and len(linkToFocus.filename):
                    # `Save OMFIT working copy as...` should not be necessary now that .duplicate() GUI accepts filename
                    # self.popup.add_command(label="Save OMFIT working copy as..." , command=self.saveOMFITobjAs)
                    if hasattr(linkToFocus, 'load') and not getattr(linkToFocus, 'dynaLoad', False):
                        self.popup.add_command(label="Reload from file", command=self.reloadOMFITobj)
                    if hasattr(linkToFocus, 'dynaLoad') and not linkToFocus.dynaLoad and hasattr(linkToFocus, 'close'):
                        self.popup.add_command(label="Close", command=self.closeOMFITobj)
                    if isinstance(linkToFocus, OMFITascii):
                        self.popup.add_command(label="Open in editor", command=self.openFile)
                    if isinstance(linkToFocus, _OMFITpython):
                        self.popup.add_command(
                            label="Style format", command=lambda linkToFocus=linkToFocus: linkToFocus.format(verbose=True)
                        )

                    def email(obj):
                        obj.save()
                        filename = os.path.split(obj.filename)[1]
                        prjname = ''
                        if OMFIT.filename:
                            prjname = 'Project: ' + OMFIT.filename
                        tk.email_widget(
                            parent=OMFITaux['rootGUI'],
                            fromm=OMFIT['MainSettings']['SETUP']['email'],
                            to=OMFIT['MainSettings']['SETUP']['email'],
                            subject='OMFIT - Object: ' + filename,
                            message='Attachment: ' + filename + '\n' + '=' * 20 + '\n' + prjname + '\n',
                            attachments=[obj.filename],
                            title='Email ' + filename,
                            use_last_email_to=1,
                            quiet=False,
                        )

                    if linkToFocus.filename and hasattr(linkToFocus, 'save'):
                        self.popup.add_command(label="Email...", command=lambda: email(linkToFocus))

            # compressed/deflated OMFITobjects, OMFITtrees, and OMFITcollections with selector==None
            if (
                isinstance(linkToFocus, OMFITobject)
                or isinstance(linkToFocus, OMFITtree)
                or (isinstance(linkToFocus, OMFITcollection) and linkToFocus.selector == None)
            ):

                def compress_deflate(action):
                    top = tk.Toplevel(self.rootGUI)
                    top.withdraw()
                    top.transient(self.rootGUI)
                    top.wm_title(action + ' ' + focusRootRepr)

                    ttk.Label(top, text='To: ').pack(side=tk.LEFT)
                    var = tk.OneLineText(top, width=50, percolator=True)
                    var.set(focusRootRepr)
                    var.pack(side=tk.LEFT, padx=2, pady=5, fill=tk.X, expand=tk.YES)

                    def onReturn():
                        if action.lower() == 'compress':
                            exec(var.get() + '=OMFITtreeCompressed(' + focusRootRepr + ')', globals(), locals())
                        elif action.lower() == 'deflate':
                            cls = 'OMFITtree'
                            if '__compressed_' in os.path.split(linkToFocus.filename)[1]:
                                cls = os.path.split(linkToFocus.filename)[1].split('__compressed_')[0]
                            exec(var.get() + '=' + cls + '("""' + linkToFocus.filename + '""")', globals(), locals())
                        self.update_treeGUI()
                        top.destroy()

                    def onEscape():
                        top.destroy()

                    var.focus_set()
                    top.bind('<Return>', lambda event: onReturn())
                    top.bind('<KP_Enter>', lambda event: onReturn())
                    top.bind('<Escape>', lambda event: onEscape())

                    top.protocol("WM_DELETE_WINDOW", top.destroy)
                    top.update_idletasks()
                    tk_center(top, self.rootGUI)
                    top.deiconify()
                    top.wait_window(top)

                if isinstance(linkToFocus, OMFITtree):
                    self.popup.add_command(label="Compress...", command=lambda: compress_deflate('Compress'))
                elif isinstance(linkToFocus, OMFITtreeCompressed):
                    self.popup.add_command(label="Deflate...", command=lambda: compress_deflate('Deflate'))

            # deployGUI
            if hasattr(self.linkToFocus, 'deployGUI'):
                self.popup.add_command(label="Deploy as...", command=self.deployOMFITobj)

            # more deploy options if not OMFITcollection or OMFITcollection with selector!=None
            if not isinstance(linkToFocus, OMFITcollection) or linkToFocus.selector != None:
                if not isinstance(linkToFocus, (OMFITtree, _OMFITpython)) and not (
                    hasattr(linkToFocus, 'dynaLoad') and linkToFocus.dynaLoad
                ):
                    self.popup.add_command(label="Deploy as pickle...", command=lambda: self.deployOMFITobj(pickleObject=True))
                if xarray is not None and isinstance(linkToFocus, xarray.Dataset):
                    self.popup.add_command(label="Deploy as NetCDF...", command=self.deployOMFITobj)
                    self.popup.add_separator()
                elif isinstance(linkToFocus, np.ndarray):
                    if isinstance(linkToFocus, np.ndarray):
                        tmp = len(linkToFocus.shape)
                    if tmp in [0, 1, 2]:
                        self.popup.add_command(label="Deploy as ASCII...", command=self.deployOMFITobj)

            # OMFITtree or OMFITcollection with selector==None
            if isinstance(linkToFocus, OMFITtree) or (isinstance(linkToFocus, OMFITcollection) and linkToFocus.selector == None):

                def external_internal(action='internal'):
                    if action == 'internal':
                        tmp = linkToFocus.duplicate(quiet=False)
                        linkToFocus.clear()
                        linkToFocus.update(tmp)
                        linkToFocus.filename = ''
                        linkToFocus.readOnly = False
                        linkToFocus.modifyOriginal = False

                    else:

                        if 'update' not in action:
                            tmp = linkToFocus.duplicateGUI(
                                modifyOriginal='modifyOriginal' in action, readOnly='readOnly' in action, quiet=False
                            )

                        else:
                            filename = linkToFocus.filename

                            if 'readOnly' not in action:
                                tmp = linkToFocus.duplicate(quiet=False)
                                linkToFocus.clear()
                                linkToFocus.update(tmp)
                                linkToFocus.filename = ''
                                linkToFocus.readOnly = False
                                linkToFocus.modifyOriginal = False

                            tmp = linkToFocus.duplicate(
                                filename=filename, modifyOriginal='modifyOriginal' in action, readOnly='readOnly' in action, quiet=False
                            )

                        if tmp is not None:
                            linkToFocus.clear()
                            linkToFocus.update(tmp)
                            linkToFocus.filename = tmp.filename
                            linkToFocus.readOnly = tmp.readOnly
                            linkToFocus.modifyOriginal = tmp.modifyOriginal

                    self.update_treeGUI()

                submenu = tk.Menu(self.popup, tearoff=False)
                if linkToFocus.modifyOriginal or linkToFocus.readOnly:
                    submenu.add_command(label="Save within project", command=lambda: external_internal('internal'))
                    if linkToFocus.modifyOriginal and linkToFocus.readOnly:
                        submenu.add_command(
                            label="Update deploy + modifyOriginal + readOnly",
                            command=lambda: external_internal('modifyOriginal_readOnly_update'),
                        )
                    elif linkToFocus.modifyOriginal:
                        submenu.add_command(
                            label="Update deploy + modifyOriginal", command=lambda: external_internal('modifyOriginal_update')
                        )
                    elif linkToFocus.readOnly:
                        submenu.add_command(label="Update deploy + readOnly", command=lambda: external_internal('readOnly_update'))
                else:
                    submenu.add_command(label="Deploy + modifyOriginal...", command=lambda: external_internal('modifyOriginal'))
                    submenu.add_command(label="Deploy + readOnly...", command=lambda: external_internal('readOnly'))
                    submenu.add_command(
                        label="Deploy + modifyOriginal + readOnly...", command=lambda: external_internal('modifyOriginal_readOnly')
                    )
                self.popup.add_cascade(label='External reference', menu=submenu)
                if isinstance(linkToFocus, OMFITcollection) and linkToFocus.selector is None:
                    self.popup.add_separator()

            # not OMFITcollection or OMFITcollection with selector!=None
            if not isinstance(linkToFocus, OMFITcollection) or linkToFocus.selector != None:
                self.popup.add_separator()

                # to avoid dynamic loading of objects just by right-clicking on them
                if hasattr(linkToFocus, 'dynaLoad') and linkToFocus.dynaLoad:

                    def forceLoad():
                        linkToFocus.load()
                        self.update_treeGUI()
                        self.rootGUI.after(1, lambda: self.itemRightClicked(event))

                    self.popup.add_command(label="Force load", command=forceLoad)
                    self.popup.add_separator()

                # loaded objects
                else:
                    options = 0
                    if isinstance(linkToFocus, SortedDict) or isinstance(linkToFocus, OMFITascii):
                        self.popup.add_command(
                            label="Compare/Merge entry...", command=lambda: self.itemRenameDuplicateCompare(action='compare')
                        )
                        options += 1
                    if hasattr(linkToFocus, 'sort'):
                        self.popup.add_command(label='Sort keys', command=self.sort)
                        options += 1
                    if options:
                        self.popup.add_separator()

                    ods_start, ods_end, path = OMFITaux['GUI'].is_part_of_ods()
                    if ods_start is not None:
                        odspath = buildLocation([str(omas.omas_utils.l2u(path[ods_start:ods_end]))]) + buildLocation([''] + path[ods_end:])
                        self.popup.add_command(
                            label="IMAS data dictionary info", command=lambda odspath=odspath: pprint_imas_data_dictionary_info(odspath)
                        )
                        if not (isinstance(linkToFocus, ODS) and not linkToFocus.location):
                            self.popup.add_separator()

                    if isinstance(linkToFocus, ODS) and not linkToFocus.location:
                        submenues = {}
                        for sub in ['physics', 'plot', 'over plot']:
                            submenues[sub] = tk.Menu(self.popup, tearoff=False)
                            self.popup.add_cascade(label=sub.capitalize(), menu=submenues[sub])
                            for item in dir(linkToFocus):
                                if item.startswith(sub.split(' ')[-1]) and np.any(
                                    [item.startswith(sub.split(' ')[-1] + '_' + k) for k in linkToFocus]
                                ):
                                    lbl = (' '.join(item.split('_')[1:])).capitalize()
                                    func = getattr(linkToFocus, item)
                                    if sub == 'over plot':
                                        _, kw, _, _ = function_arguments(func)
                                        func = _lock_OMFIT_preferences(func)
                                        if 'fig' in kw:
                                            submenues[sub].add_command(label=lbl, command=lambda func=func: func(fig=pyplot.gcf()))
                                        elif 'ax' in kw:
                                            submenues[sub].add_command(label=lbl, command=lambda func=func: func(ax=pyplot.gca()))
                                        else:
                                            submenues[sub].add_command(label=lbl, command=func)
                                    else:
                                        func = _lock_OMFIT_preferences(func)
                                        submenues[sub].add_command(label=lbl, command=func)
                        self.popup.add_separator()

                    elif isinstance(linkToFocus, np.ndarray):
                        if len(linkToFocus.shape) in [1, 2]:
                            self.popup.add_command(label="Quick plot", command=self.quickPlotF)
                            self.popup.add_command(label="Quick over plot", command=self.quickPlot)
                            if len(np.squeeze(linkToFocus).shape) == 1:

                                def n_control_points(interp):
                                    top = tk.Toplevel(self.rootGUI)
                                    top.withdraw()
                                    top.transient(self.rootGUI)
                                    top.wm_title('Number of control points')

                                    npoints = tk.StringVar()
                                    npoints.set(str(max([4, int(linkToFocus.size // 5)])))
                                    ttk.Label(top, text='Number of control points: ').pack(side=tk.LEFT)
                                    e1 = ttk.Entry(top, textvariable=npoints, width=30)
                                    e1.pack(side=tk.LEFT, padx=2, pady=5, fill=tk.X, expand=tk.YES)

                                    def onReturn():
                                        self.quickPlotF(edit=int(npoints.get()), interp=interp)
                                        top.destroy()

                                    def onEscape():
                                        top.destroy()

                                    e1.focus_set()
                                    top.bind('<Return>', lambda event: onReturn())
                                    top.bind('<KP_Enter>', lambda event: onReturn())
                                    top.bind('<Escape>', lambda event: onEscape())

                                    top.protocol("WM_DELETE_WINDOW", top.destroy)
                                    top.update_idletasks()
                                    tk_center(top, self.rootGUI)
                                    top.deiconify()
                                    top.wait_window(top)

                                self.popup.add_command(label="Quick edit - points", command=lambda: self.quickPlotF(edit=1))
                                self.popup.add_command(label="Quick edit - nearest", command=lambda: n_control_points('nearest'))
                                self.popup.add_command(label="Quick edit - linear", command=lambda: n_control_points('linear'))
                                self.popup.add_command(label="Quick edit - pchip", command=lambda: n_control_points('pchip'))
                                self.popup.add_command(label="Quick edit - spline", command=lambda: n_control_points('spline'))
                                self.popup.add_command(label="Quick edit - circular", command=lambda: n_control_points('circular'))
                            self.popup.add_separator()

                    elif hasattr(linkToFocus, 'plot'):
                        self.popup.add_command(label="Quick plot", command=self.quickPlotF)
                        self.popup.add_command(label="Quick over plot", command=self.quickPlot)
                        self.popup.add_command(
                            label="Quick over plot (via defaultVarsGUI)...", command=lambda: self.quickPlot(defaultVarsGUI=True)
                        )
                        self.popup.add_separator()

                    if isinstance(linkToFocus, _OMFITpython) or isinstance(linkToFocus, CollectionsCallable):
                        self.popup.add_command(label="Run()", command=self.runLinkToFocus)
                        self.popup.add_command(
                            label="Run (via defaultVarsGUI)...", command=lambda: self.runLinkToFocus(defaultVarsGUI=True)
                        )
                        self.popup.add_separator()

            self.popup.add_command(label="Copy entry location", command=lambda: self.clipboard(what='location'))
            self.popup.add_command(label="Copy entry location from root", command=lambda: self.clipboard(what='root'))
            self.popup.add_command(label="Copy entry location tip", command=lambda: self.clipboard(what='tip'))
            self.popup.add_command(label="Copy entry value", command=lambda: self.clipboard(what='value'))
            # Failed for smithsp when testing all right-click options
            # if isinstance(linkToFocus,OMFITobject):
            # self.popup.add_command(label="Copy to global clipboard" , command=lambda: self.clipboard(what='S3'))
            self.popup.add_command(label="Paste entry (via memory copy)", command=lambda: self.clipboard(what='paste'))
            if isinstance(linkToFocus, dict):
                self.popup.add_command(label="Paste entry inside (via memory copy)", command=lambda: self.clipboard(what='pasteInside'))
            # Failed for smithsp when testing all right-click options
            # self.popup.add_command(label="Paste from global clipboard" , command=lambda: self.clipboard(what='pasteS3'))

        self.popup.update_idletasks()

        x = event.x_root
        if event.x_root + self.popup.winfo_reqwidth() > self.popup.winfo_screenwidth():
            x = self.popup.winfo_screenwidth() - self.popup.winfo_reqwidth() - 12
        y = event.y_root
        if event.y_root + self.popup.winfo_reqheight() > self.popup.winfo_screenheight():
            y = self.popup.winfo_screenheight() - self.popup.winfo_reqheight() - 12

        self.popup.post(x, y)
        self.popup.focus_set()
        self.popup.update_idletasks()

        def popupFocusOut():
            self.popup.unpost()
            self.popup.destroy()

        self.popup.bind("<FocusOut>", lambda event: popupFocusOut())

    # ------------------
    # GUIs
    # ------------------
    def startOMFITgui(self):
        self.browser_label_text.set('')

        OMFITaux['GUI'] = self
        OMFITaux['rootGUI'] = self.rootGUI
        OMFITaux['treeGUI'] = self.treeGUI
        OMFITaux['console'] = self.console

        OMFITx.CloseAllGUIs()

        for k in range(len(self.opened_closed_view)):
            self.opened_closed_view[k] = {}
        self.opened_closed_bkp = None
        self.viewSelect()
        self.commandSelect()
        self.notes.delete('1.0', 'end')

        self.x = None
        self.xName = None
        self.y = None
        self.yName = None

        self.focus = ''
        self.focusRoot = ''
        self.focusRootRepr = ''
        self.linkToFocus = None

        self.update_treeGUI()
        self.autoSave(trigger=False)
        self.updateTitle()

    def newProjectModule(self, isModule=None, interactive=True):

        self.onQuitSearch()

        if isModule is None:
            if self.lockSave:
                printi('Wait for ' + self.lockSave + ' to finish')
                return

            if interactive:
                answ = dialog(
                    title="Save changes?",
                    message="Save changes to"
                    + (" project:\n\n   " + OMFIT.projectName() + "\n\n" if OMFIT.filename else " current project ")
                    + "before opening a new project?",
                    answers=['Yes', 'No', 'Cancel'],
                    parent=self.rootGUI,
                )
                if answ == 'Cancel':
                    return
                if answ == 'Yes':
                    save_success = self.saveOMFITas()
                    OMFITx.Refresh()
                    if not save_success:
                        return

            pyplot.close('all')
            OMFITx.CloseAllGUIs()
            OMFITx._harvest_experiment_info()
            self.console.delete('1.0', 'end')

            OMFIT.start()

            while len(self.command):
                self.commandNotebook.forget(self.commandNotebook.tabs()[-1])
                self.command.pop()

            self.commandActive = 0
            self.commandBoxNamespace = None

            self.startOMFITgui()

        else:

            def onReturn():
                location = parseLocation(newLocation.get())
                eval(buildLocation(location[:-1]))[location[-1]] = OMFITmodule(None, developerMode=False)
                if moduleID.get().strip('\'"').strip():
                    eval(buildLocation(location[:-1]))[location[-1]]['SETTINGS']['MODULE']['ID'] = moduleID.get().strip('\'"').strip()
                top.destroy()

            def onEscape():
                top.destroy()

            newLocation = tk.StringVar()
            newLocation.set("OMFIT['NEW_MODULE']")
            moduleID = tk.StringVar()
            moduleID.set('')

            top = tk.Toplevel(self.rootGUI)
            top.withdraw()
            top.transient(self.rootGUI)
            top.wm_title('Create new module')

            frm = ttk.Frame(top)
            frm.pack(expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

            ttk.Label(frm, text='Location of the new module').grid(row=0, column=0, sticky=tk.W)
            e2 = ttk.Entry(frm, textvariable=newLocation, width=40)
            e2.grid(row=0, column=1, sticky=tk.E)
            e2.focus_set()
            ttk.Label(frm, text='Module ID').grid(row=1, column=0, sticky=tk.E)
            e1 = ttk.Entry(frm, textvariable=moduleID, width=40)
            e1.grid(row=1, column=1, sticky=tk.E + tk.W, columnspan=2)

            top.bind('<Return>', lambda event: onReturn())
            top.bind('<KP_Enter>', lambda event: onReturn())
            top.bind('<Escape>', lambda event: onEscape())

            top.protocol("WM_DELETE_WINDOW", top.destroy)
            top.update_idletasks()
            tk_center(top, self.rootGUI)
            top.deiconify()
            top.wait_window(top)

        self.update_treeGUI_and_GUI()

    def _save(self, filename=None, zip=None, quiet=False, override_std_out_err=False):

        _streams.backup()

        if override_std_out_err:

            class Redirector(object):
                def __init__(self, q, tag='STDOUT'):
                    self.q = q
                    self.tag = tag

                def write(self, string):
                    self.q.put([string, self.tag])

                def __getattr__(self, attr):
                    return getattr(sys.__stdout__, attr)

            for k in _streams:
                _streams[k] = Redirector(override_std_out_err, k)
            sys.stdout = _streams['STDOUT']
            sys.stderr = _streams['STDERR']

        try:
            if filename is None and len(OMFIT.filename):
                # quick-save
                OMFIT.save(quiet)
                omfit_log('save project', OMFIT.filename)
                OMFITx._harvest_experiment_info()

            elif isinstance(filename, tuple) and len(OMFIT.filename):
                # auto-saves go to OMFITautosaveDir which is in the temporary
                # OMFIT working directory, so that it does not get backed-up
                if not os.path.exists(OMFITautosaveDir):
                    os.makedirs(OMFITautosaveDir)
                if os.path.splitext(OMFIT.filename)[1] == '.zip':
                    filename = os.path.splitext(os.path.split(OMFIT.filename)[1])[0]
                elif os.path.splitext(OMFIT.filename)[1] == '.txt':
                    filename = os.path.split(os.path.split(OMFIT.filename)[0])[1]
                else:
                    raise Exception('Bad OMFIT project filename')
                OMFIT.deploy(OMFITautosaveDir + os.sep + filename + os.sep + 'OMFITsave.txt', zip=False)

                # create symlink to the projectsDir so that users can easily find the auto-saves
                linkdir = os.path.abspath(OMFIT['MainSettings']['SETUP']['projectsDir'].rstrip('/\\')) + os.sep + 'auto-save' + os.sep
                if not os.path.exists(linkdir):
                    os.makedirs(linkdir)
                if os.path.islink(linkdir + os.sep + filename) and os.path.exists(linkdir + os.sep + filename):
                    os.remove(linkdir + os.sep + filename)
                os.symlink(OMFITautosaveDir + os.sep + filename, linkdir + os.sep + filename)

            elif filename is None or not len(filename):
                # this is bad (should never be here)
                raise Exception('OMFIT project filename not set')

            else:
                # save with new name
                OMFIT.saveas(filename, zip)
                omfit_log('save new project', OMFIT.filename)
                OMFITx._harvest_experiment_info()

        except Exception as _excp:
            if override_std_out_err:
                sys.stderr.write(repr(_excp) + '\n\nERROR during save!\n')
            else:
                raise

        finally:
            _streams.restore()

    def _noBlockSave(self, message='save'):
        def saveCheck():
            try:
                # if the user aborted the save
                if self.lockSave == 'abort':
                    finished.set(True)
                    self.rootGUI.update_idletasks()
                    if p.is_alive():
                        os.kill(p.pid, signal.SIGKILL)
                    tag_print('\nsave aborted by user\n', tag='ERROR')
                    error.set('\nsave aborted by user\n')

                # if there is some text in the save
                elif not q.empty():
                    while not q.empty():
                        string, tag = q.get(False)
                        if tag in ['STDOUT', 'INFO']:
                            all_stdout.set(all_stdout.get() + string)
                        else:
                            break

                    # if normal text write it in the status bar and carry-on
                    # NOTE: we do not stop for empty strings on STDERR as this
                    #       may happen when OMFIT is handling warnings internally
                    if tag in ['STDOUT', 'INFO'] or not string:
                        tmp = [_f for _f in string.split('\n') if _f]
                        if len(tmp):
                            self.statusBarText.set(message + ': ' + tmp[-1])
                        self.rootGUI.after(10, saveCheck)
                        self.rootGUI.update_idletasks()

                    # if text on STDERR then stop
                    else:
                        tmp = string
                        while not q.empty():
                            string, tag = q.get(False)
                            if tag not in ['STDOUT', 'INFO']:
                                tmp += string
                        if p.is_alive():
                            os.kill(p.pid, signal.SIGKILL)
                        error.set(tmp)
                        tag_print(tmp, tag=tag)
                        finished.set(True)
                        self.rootGUI.update_idletasks()

                # if we are still saving (the process is still alive)
                elif p.is_alive():
                    self.rootGUI.after(100, saveCheck)

                # if we are still saving (the flag finished is not True)
                elif q.empty() and not finished.get():
                    finished.set(True)
                    self.rootGUI.update_idletasks()

            # should never get here
            except Exception as _excp:
                if p.is_alive():
                    os.kill(p.pid, signal.SIGKILL)
                tag_print('\n' + repr(_excp), tag='ERROR')
                error.set(repr(_excp))
                finished.set(True)
                self.rootGUI.update_idletasks()
                raise

        try:
            finished = tk.BooleanVar()
            finished.set(False)
            error = tk.StringVar()
            error.set('')
            all_stdout = tk.StringVar()
            all_stdout.set('')

            self.lockSave = message
            q = multiprocessing.Queue()
            if message == 'auto-save':
                p = multiprocessing.Process(target=self._save, kwargs={'override_std_out_err': q, 'filename': ()})
            else:
                p = multiprocessing.Process(target=self._save, kwargs={'override_std_out_err': q, 'filename': None})
            with parallel_environment(mpl_backend=False):
                p.start()
            saveCheck()
            self.rootGUI.wait_variable(finished)
            p.join()
            if self.lockSave != 'abort' and message != 'auto-save':
                OMFIT.recentProjects()
                # this needs to be done here because if the save is done in a different process the OMFIT tree does not get updated
                OMFIT['MainSettings']['SETUP']['version'] = repo_active_branch_commit
                OMFIT['MainSettings']['SETUP']['python_environment'] = SortedDict(python_environment())

        finally:
            self.lockSave = False
            self.update_treeGUI()

        return error.get()

    def _abortLockSave(self):
        # do not save when OMFIT_SAVE_DEBUG is simply set to True, or 1 but ok if it is a string
        if safe_eval_environment_variable('OMFIT_DEBUG', False) and not safe_eval_environment_variable('OMFIT_SAVE_DEBUG', False):
            if not isinstance(safe_eval_environment_variable('OMFIT_DEBUG', False), str):
                raise OMFITexception(
                    'Cowardly refusing to save while os.environ["OMFIT_DEBUG"] is on; set os.environ["OMFIT_SAVE_DEBUG"] to "1" to override'
                )

        if self.lockSave == 'abort':
            printi('Abort quicksave already in progress')
            return True
        if self.lockSave:
            tmp = dialog(
                title="Abort %s?" % self.lockSave,
                message="Decide before save is completed...",
                answers=['Abort %s' % self.lockSave, 'Continue %s' % self.lockSave],
                parent=self.rootGUI,
            )
            if tmp == 'Abort %s' % self.lockSave:
                self.lockSave = 'abort'
                self.updateTitle()
            return True
        return False

    def quickSave(self, updateNotes=True):
        # if project was never saved run saveOMFITas
        if not len(OMFIT.filename) or not os.access(OMFIT.filename, os.W_OK):
            self.rootGUI.after(1, self.saveOMFITas)
            return

        # check if self.lockSave is set and if so ask users if they want to abort it
        if self._abortLockSave():
            return

        printi(f'Quick-saving project @ {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')

        abort = tk.BooleanVar()
        abort.set(False)
        if updateNotes:

            def continueSave():
                abort.set(False)
                self.notes.clear()
                self.notes.insert('insert', desc.get(1.0, tk.END))
                OMFIT.prj_options['type'] = re.sub('None', '', prj_type.get())
                OMFIT.prj_options['color'] = re.sub('None', '', prj_color.get())
                OMFIT.prj_options['persistent_projectID'] = persistent_projectID.get()
                top.destroy()

            top = tk.Toplevel(self.rootGUI)
            top.withdraw()
            top.transient(self.rootGUI)

            if os.path.split(OMFIT.filename)[1] == 'OMFITsave.txt':
                projectname = os.path.split(os.path.split(OMFIT.filename)[0])[1]
            else:
                projectname = os.path.splitext(os.path.split(OMFIT.filename)[1])[0]
            top.wm_title('Quick-Save Project:  ' + projectname)

            # project type
            frm1 = ttk.Frame(top)
            frm1.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=5)
            prj_type = tk.StringVar()
            if 'type' in OMFIT.prj_options and OMFIT.prj_options['type'] in OMFIT.prj_options_choices['type']:
                prj_type.set(OMFIT.prj_options['type'])
            else:
                prj_type.set('None')
            ttk.Label(frm1, text='Type: ').pack(side=tk.LEFT, anchor=tk.W)
            for text in ['None'] + OMFIT.prj_options_choices['type']:
                b = ttk.Radiobutton(frm1, text=text, variable=prj_type, value=text)
                b.pack(side=tk.LEFT, anchor=tk.W)

            # project color
            frm1 = ttk.Frame(top)
            frm1.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=5)
            prj_color = tk.StringVar()
            if 'color' in OMFIT.prj_options and OMFIT.prj_options['color'] in list(OMFIT.prj_options_choices['color'].keys()):
                prj_color.set(OMFIT.prj_options['color'])
            else:
                prj_color.set('None')
            ttk.Label(frm1, text='Color code: ').pack(side=tk.LEFT, anchor=tk.W)
            for color_name, color_value in [('None', 'black')] + list(OMFIT.prj_options_choices['color'].items()):
                if color_name == 'None':
                    style = 'TRadiobutton'
                else:
                    style = color_name + '.TRadiobutton'
                    ttk.Style().configure(style, foreground=color_value)
                b = ttk.Radiobutton(frm1, text=color_name, variable=prj_color, value=color_name, style=style)
                b.pack(side=tk.LEFT, anchor=tk.W)

            desc = askDescription(
                top, self.notes.get(1.0, tk.END).strip() + '\n', 'Update project log:', showInsertDate=True, expand=tk.YES
            )
            desc.bind(f'<{ctrlCmd()}-Return>', lambda event: continueSave())

            saveFrame = ttk.Frame(top)
            saveFrame.pack(side=tk.TOP, padx=5, pady=2, expand=tk.NO, fill=tk.X)

            bt = ttk.Button(saveFrame, text="Save in background", command=continueSave)
            bt.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)

            persistent_projectID = tk.BooleanVar()
            persistent_projectID.set(OMFIT.prj_options['persistent_projectID'])
            ck = ttk.Checkbutton(saveFrame, variable=persistent_projectID, text='use same projectID when loading')
            ck.state(['!alternate'])
            ck.pack(side=tk.LEFT)
            ck.var = persistent_projectID
            if persistent_projectID.get():
                ck.state(['selected'])

            def abortSave():
                abort.set(True)
                top.destroy()

            top.bind('<Return>', lambda event: continueSave())
            top.bind('<KP_Enter>', lambda event: continueSave())
            top.bind('<Escape>', lambda event: abortSave())

            top.protocol("WM_DELETE_WINDOW", abortSave)
            top.update_idletasks()
            tk_center(top, self.rootGUI)
            top.deiconify()
            bt.focus_set()
            top.wait_window(top)

        if abort.get():
            printe(f'Aborted quick-save @ {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')

        else:
            self.console.clear('HIST')

            error = self._noBlockSave('quick-save')

            if error:
                printe(
                    '\nQuick-save failed!\n'
                    + '=' * 20
                    + '\n'
                    + error
                    + '\n'
                    + '=' * 20
                    + '\nPlease try again with `File > Save project as`'
                )
            else:
                printi(f'Done with quick-save @ {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')

            self.autoSave(trigger=False)
            self.updateTitle()

    def autoSave(self, trigger=True):
        """
        :param trigger: if False then this is only used to reset the autoSave alarm
        """
        # disable the alarm
        if self.autoSaveAlarm is not None:
            self.rootGUI.after_cancel(self.autoSaveAlarm)
            self.autoSaveAlarm = None

        try:
            if trigger:
                # do not autosave if project was never saved
                if not len(OMFIT.filename):
                    printt('Skip auto-save: this project was never saved')
                    return

                # here only after autosave_minutes have passesd since last auto-save
                # skip autosave if more than autosave_minutes of inactivity
                minutes_inactive = (time.time() - OMFITaux['lastActivity']) / 60.0
                if minutes_inactive > OMFIT['MainSettings']['SETUP']['autosave_minutes']:
                    printt(
                        'Skip auto-save: this project was already auto-saved and there has not been activity for %d minutes'
                        % int(minutes_inactive)
                    )
                    return

                # check if self.lockSave is set and if so ask users if they want to abort it
                if self._abortLockSave():
                    return

                # do the auto-save
                printd('Auto-saving project...', topic='save')
                error = self._noBlockSave('auto-save')

                # error handling
                if error:
                    printe('\nAuto-save failed! Please try again with `File > Save project as`')
                else:
                    printd('Done with auto-save!', topic='save')
                    printt('OMFIT - ' + 'auto-save' + ' - ' + utils_base.now() + " - " + OMFIT.filename)

                # update the statusBarText
                self.updateTitle()

        finally:
            # whatever happens always re-enable the alarm to autosave again in autosave_minutes
            self.autoSaveAlarm = self.rootGUI.after(OMFIT['MainSettings']['SETUP']['autosave_minutes'] * 60 * 1000, self.autoSave)

    def autoTouch(self, trigger=True):
        if self.autoTouchAlarm is not None:
            self.rootGUI.after_cancel(self.autoTouchAlarm)
            self.autoTouchAlarm = None
        self.autoTouchAlarm = self.rootGUI.after(
            int(OMFIT['MainSettings']['SETUP']['autotouch_days'] * 60 * 1000 * 24 * 60), self.autoTouch
        )

        # call autoSave(trigger=False) to reset the autoSave alarm
        if not trigger:
            return

        printd('Auto-touching project...', topic='auto-touch')

        cmd = 'find %s -exec touch {} +' % OMFITsessionDir
        error = os.system(cmd)

        if error:
            printe(
                "\nAuto-touch failed.\nOMFIT regularly touches all the files associated this project to"
                "prevent local systems from designating them as stale and deleting them.\n\n"
                "You might want to save and restart the project/session just to be safe."
            )
        else:
            printd('Done with auto-touch!', topic='auto-touch')
            printt('OMFIT - auto-touch - %s - %s' % (utils_base.now(), OMFIT.filename))

        # reset autosave_minutes since the last successful save
        self.autoTouch(trigger=False)

    def saveOMFITas(self, background=True):
        """
        Start up a GUI with a prompt for project path, filename, type, color

        :param background: Whether to allow saving in the background

        :returns: True or False reflecting whether OMFIT.filename has a value upon exiting this method
        """
        if self._abortLockSave():
            return False

        self.save_success = False

        def onReturn(noBlock=True):
            # generate the save directory
            if not os.path.exists(value1.get().strip()):
                os.makedirs(os.path.abspath(value1.get().strip()))
                printi('Private projects directory has been created: ' + value1.get().strip())

            if not os.access(os.path.abspath(value1.get().strip()), os.W_OK):
                printe('Save failed! You have no write permissions to ' + os.path.abspath(value1.get().strip()))
                return False

            # save
            saveFile = value1.get().strip() + os.sep + value2.get().strip()
            printi(f'Saving project as {saveFile}/OMFITsave.txt')
            printi(f'Saving starts @ {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')

            self.console.clear('HIST')

            self.notes.clear()
            self.notes.insert('insert', desc.get(1.0, tk.END))

            OMFIT.prj_options['type'] = re.sub('None', '', prj_type.get())
            OMFIT.prj_options['color'] = re.sub('None', '', prj_color.get())
            OMFIT.prj_options['persistent_projectID'] = persistent_projectID.get()

            # blocking or non-blocking save as
            if noBlock:
                top.destroy()

                # set OMFIT filename and zip
                if self.saveZip:
                    OMFIT.filename = saveFile + '.zip'
                else:
                    OMFIT.filename = saveFile + os.sep + 'OMFITsave.txt'
                OMFIT.zip = self.saveZip

                # non-blocking save
                error = self._noBlockSave('quick-save')

                if error:
                    printe(
                        '\nQuick-save failed!\n'
                        + '=' * 20
                        + '\n'
                        + error
                        + '\n'
                        + '=' * 20
                        + '\nPlease try again with `File > Save project as`'
                    )
                else:
                    printi(f'Done with quick-save @ {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
                self.save_success = True

            else:
                self._save(filename=saveFile + os.sep + 'OMFITsave.txt', zip=self.saveZip)

                printi(f'Project saved @ {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')

                # update recent projects
                OMFIT.recentProjects()

                # update the GUI
                self.update_treeGUI()
                top.destroy()
                self.save_success = True

            self.autoSave(trigger=False)
            self.updateTitle()

        def onEscape():
            top.destroy()

        def onButtonDir():
            tmp = tkFileDialog.askdirectory(initialdir=value1.get().strip(), parent=top)
            if len(tmp):
                value1.set(tmp)
            e1.icursor(tk.END)
            e1.xview(len(value1.get()))

        def onButtonFile():
            filetypes = [('OMFIT save', 'OMFITsave.txt'), ('OMFIT save', '*.zip'), ('All files', '.*')]
            if self.saveZip:
                filetypes.insert(0, filetypes.pop(1))
            tmp = tkFileDialog.askopenfilename(initialdir=value1.get().strip(), filetypes=filetypes, parent=top)
            if len(tmp):
                filename = os.path.split(tmp)[1]
                dirname = os.path.split(tmp)[0]
                if os.path.splitext(filename)[1] == '.zip':
                    filename = os.path.splitext(filename)[0]
                    ck.state(['selected'])
                    self.saveZip = True
                else:
                    filename = os.path.split(dirname)[1]
                    dirname = os.path.split(dirname)[0]
                    ck.state(['!selected'])
                    self.saveZip = False
                value1.set(dirname)
                value2.set(filename)

            e1.icursor(tk.END)
            e1.xview(len(value1.get()))

        value1 = tk.StringVar()
        value2 = tk.StringVar()

        top = tk.Toplevel(self.rootGUI)
        top.withdraw()
        top.transient(self.rootGUI)
        top.wm_title('Save project as...')

        # past directories
        projects = OMFIT.recentProjects(only_read=True)
        if projects is None:
            projects = []
        projects = [re.sub(os.sep + 'OMFITsave.txt', '', x) for x in projects]
        projectsDir = [os.path.abspath(OMFIT['MainSettings']['SETUP']['projectsDir'].rstrip('/\\'))]
        for prj in projects:
            if os.path.split(prj)[0] not in projectsDir:
                projectsDir.append(os.path.split(prj)[0])
        projectsDir = unsorted_unique(projectsDir)
        projectsDir = tuple(projectsDir)

        # directory selection
        dirFrame = ttk.Frame(top)
        dirFrame.pack(side=tk.TOP, padx=5, expand=tk.NO, fill=tk.X)
        ttk.Label(dirFrame, text='Save to directory:').pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
        e1 = ttk.Entry(dirFrame, textvariable=value1, width=50)
        e1 = ttk.Combobox(dirFrame, state='normal', textvariable=value1, values=projectsDir)
        e1.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        e1.icursor(tk.END)
        e1.xview(len(value1.get()))
        dirButton = ttk.Button(dirFrame, text="Directory lookup", command=onButtonDir)
        dirButton.pack(side=tk.LEFT)

        # filename selection
        nameFrame = ttk.Frame(top)
        nameFrame.pack(side=tk.TOP, padx=5, expand=tk.NO, fill=tk.X)
        ttk.Label(nameFrame, text="Project name : ").pack(side=tk.LEFT)
        e2 = ttk.Entry(nameFrame, textvariable=value2)
        e2.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        e2.icursor(tk.END)
        e2.xview(tk.END)
        fileButton = ttk.Button(nameFrame, text="File lookup", command=onButtonFile)
        fileButton.pack(side=tk.LEFT)

        # set directory and filename
        if OMFIT.filename != '':
            tmp = os.path.splitext(OMFIT.filename)[0]
            if os.path.split(tmp)[1] == 'OMFITsave':
                tmp = os.path.split(tmp)[0]
            if os.access(os.path.split(tmp)[0], os.W_OK):
                value1.set(os.path.split(tmp)[0])
            else:
                value1.set(projectsDir[0])
            value2.set(os.path.split(tmp)[1])
        else:
            value1.set(projectsDir[0])
            value2.set(utils_base.now("%Y-%m-%d_%H_%M"))

        # project type
        frm1 = ttk.Frame(top)
        frm1.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=5)
        prj_type = tk.StringVar()
        if 'type' in OMFIT.prj_options and OMFIT.prj_options['type'] in OMFIT.prj_options_choices['type']:
            prj_type.set(OMFIT.prj_options['type'])
        else:
            prj_type.set('None')
        ttk.Label(frm1, text='Type: ').pack(side=tk.LEFT, anchor=tk.W)
        for text in ['None'] + OMFIT.prj_options_choices['type']:
            b = ttk.Radiobutton(frm1, text=text, variable=prj_type, value=text)
            b.pack(side=tk.LEFT, anchor=tk.W)

        # project color
        frm1 = ttk.Frame(top)
        frm1.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=5)
        prj_color = tk.StringVar()
        if 'color' in OMFIT.prj_options and OMFIT.prj_options['color'] in list(OMFIT.prj_options_choices['color'].keys()):
            prj_color.set(OMFIT.prj_options['color'])
        else:
            prj_color.set('None')
        ttk.Label(frm1, text='Color code: ').pack(side=tk.LEFT, anchor=tk.W)
        for color_name, color_value in [('None', 'black')] + list(OMFIT.prj_options_choices['color'].items()):
            if color_name == 'None':
                style = 'TRadiobutton'
            else:
                style = color_name + '.TRadiobutton'
                ttk.Style().configure(style, foreground=color_value)
            b = ttk.Radiobutton(frm1, text=color_name, variable=prj_color, value=color_name, style=style)
            b.pack(side=tk.LEFT, anchor=tk.W)

        desc = askDescription(top, self.notes.get(1.0, tk.END).strip() + '\n', 'Project log:', showInsertDate=True, expand=tk.YES)
        desc.bind(f'<{ctrlCmd()}-Return>', lambda event: onReturn(noBlock=True))

        saveFrame = ttk.Frame(top)
        saveFrame.pack(side=tk.TOP, padx=5, pady=2, expand=tk.NO, fill=tk.X)
        if background:
            ttk.Button(saveFrame, text="Save in background", command=lambda: onReturn(noBlock=True)).pack(
                side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5
            )
        ttk.Button(saveFrame, text="Save", command=lambda: onReturn(noBlock=False)).pack(
            side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5
        )

        def toggleSaveZip():
            self.saveZip = not self.saveZip

        ck = ttk.Checkbutton(saveFrame, text='as .zip', command=toggleSaveZip)
        ck.state(['!alternate'])
        ck.pack(side=tk.LEFT)
        self.saveZip = OMFIT.zip
        if OMFIT.zip:
            ck.state(['selected'])
        else:
            ck.state(['!selected'])

        persistent_projectID = tk.BooleanVar()
        persistent_projectID.set(OMFIT.prj_options['persistent_projectID'])
        ck = ttk.Checkbutton(saveFrame, variable=persistent_projectID, text='use same projectID when loading')
        ck.state(['!alternate'])
        ck.pack(side=tk.LEFT)
        ck.var = persistent_projectID
        if persistent_projectID.get():
            ck.state(['selected'])

        top.bind('<Return>', lambda event: onReturn())
        top.bind('<KP_Enter>', lambda event: onReturn())
        top.bind('<Escape>', lambda event: onEscape())
        desc.focus_set()

        top.protocol("WM_DELETE_WINDOW", top.destroy)
        top.update_idletasks()
        tk_center(top, self.rootGUI)
        top.deiconify()
        top.wait_window(top)

        # Return save_success status
        return self.save_success

    def _loadOMFITproject(self, filename, persistent_projectID=False):
        self.newProjectModule(interactive=False)
        self.update_treeGUI()

        OMFIT.load(filename, persistent_projectID=persistent_projectID)

        omfit_log('load project', OMFIT.filename)
        OMFIT.recentProjects()

        commands = OMFIT.prj_options['commands']
        commandNames0 = OMFIT.prj_options['commandNames']
        if not commandNames0:
            commandNames0 = []
        for k in range(len(commandNames0) + 1, len(commands) + 1):
            commandNames0.append(str(k))

        self.commandNames = []
        if isinstance(commands, list):
            k = -1
            for kk in range(len(commands)):
                if len(commands[kk].strip()):
                    k += 1
                if len(self.command) < (k + 1):
                    self.commandAdd(k)
                    self.commandNames[k] = commandNames0[kk]
                else:
                    self.commandNames.append(commandNames0[kk])
                self.command[k].insert(1.0, commands[kk].rstrip() + '\n')
        elif isinstance(commands, str):
            self.command[0].insert(1.0, commands)
            self.commandNames.append('1')
        self.commandNotebook.select(self.commandNotebook.tabs()[0])

        self.namespaceComboBox.set(OMFIT.prj_options['namespace'])

        notes = OMFIT.prj_options['notes']
        self.notes.clear()
        self.notes.insert('insert', notes.strip() + '\n')

        console = OMFIT.prj_options['console']
        if len(console):
            tag_print('\n', tag='HIST')
            tag_print('+------------------------------+', tag='HIST')
            tag_print('| BELOW IS WHAT YOU WERE DOING |', tag='HIST')
            tag_print('+------------------------------+', tag='HIST')
            try:
                tag_print(str(console.strip().encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')), tag='HIST')
            except UnicodeEncodeError:
                tag_print('Unable to read history', tag='HIST')
            tag_print('+------------------------------+', tag='HIST')
            tag_print('| ABOVE IS WHAT YOU WERE DOING |', tag='HIST')
            tag_print('+------------------------------+', tag='HIST')
            tag_print('\n', tag='HIST')

        dir = os.path.abspath(OMFIT['MainSettings']['SETUP']['projectsDir'].rstrip('/\\')) + os.sep + 'auto-save' + os.sep
        if dir in os.path.abspath(OMFIT.filename) or OMFITautosaveDir in os.path.abspath(OMFIT.filename):
            OMFIT.filename = ''
        self.updateTitle()

        self.update_treeGUI()

    def loadOMFIT(self, isModule=None, action='load'):

        if not isModule and self.lockSave:
            printi('Wait for ' + self.lockSave + ' to finish')
            return

        def onReturn(isModule, action):
            top.update_idletasks()
            # ======================
            # LOAD/COMPARE PROJECT
            # ======================
            if not isModule:
                if not os.path.exists(value1.get().strip()) or os.path.isdir(value1.get().strip()):
                    printe('Project not found: ' + value1.get().strip())
                    return

                top.withdraw()

                # if I am loading a project
                if 'load' in action:
                    self.autoSave(trigger=False)
                    try:
                        self._loadOMFITproject(value1.get().strip(), persistent_projectID=persistent_projectID.get())
                        top.destroy()
                    except Exception:
                        tk_center(top, self.rootGUI)
                        top.deiconify()
                        raise

                # if I am comparing a project
                else:
                    OMFIT1 = OMFITtree()
                    try:
                        OMFIT1.load(value1.get().strip())
                        top.destroy()
                    except Exception:
                        tk_center(top, self.rootGUI)
                        top.deiconify()
                        raise
                    diffTreeGUI(
                        OMFIT,
                        OMFIT1,
                        'OMFIT',
                        value1.get().strip(),
                        deepcopyOther=False,
                        skipClasses=(OMFITtmp),
                        noloadClasses=(OMFITharvestS3, OMFITharvest, OMFITmds, OMFITrdb),
                    )
                    omfit_log('compare project', OMFIT.filename)

            # ======================
            # LOAD MODULE
            # ======================
            else:
                if not os.path.exists(value1.get().strip()) or os.path.isdir(value1.get().strip()):
                    printe('Module not found: ' + value1.get().strip())
                    return
                try:
                    top.withdraw()
                    OMFIT.loadModule(
                        value1.get().strip(),
                        location.get(),
                        withSubmodules=True,
                        checkLicense=True,
                        developerMode=developerMode.get() and not self.remoteSelectorVariable.get(),
                    )
                    top.destroy()
                except Exception:
                    tk_center(top, self.rootGUI)
                    top.deiconify()
                    raise
                omfit_log('import module', value1.get().strip())

            self.update_treeGUI()
            self.commandSelect()

        def onEscape():
            top.destroy()

        def onButton(isModule, action):
            if os.path.exists(value1.get().strip()):
                if os.path.isdir(value1.get().strip()):
                    tmp = value1.get().strip()
                else:
                    tmp = os.path.split(value1.get().strip())[0]
            else:
                warnings.warn('File/Directory ' + value1.get().strip() + ' does not exist!')
                tmp = None

            if isModule:
                if tmp is None:
                    tmp = os.environ['HOME']
                    for tmp in OMFITmodule.directories():
                        if os.path.exists(tmp):
                            break
                tmp = tkFileDialog.askopenfilename(
                    title='File name',
                    initialdir=tmp,
                    filetypes=[('OMFIT save', 'OMFITsave.txt'), ('OMFIT save', '*.zip'), ('All files', '.*')],
                    parent=top,
                )

            else:
                if 'Remote' in action:
                    tmp = OMFITx.remoteFile(top, transferRemoteFile=OMFITtmpDir)
                else:
                    if tmp is None:
                        if os.path.exists(os.path.abspath(OMFIT['MainSettings']['SETUP']['projectsDir'].rstrip('/\\'))):
                            tmp = os.path.abspath(OMFIT['MainSettings']['SETUP']['projectsDir'].rstrip('/\\'))
                        else:
                            tmp = os.environ['HOME']

                    tmp = tkFileDialog.askopenfilename(
                        title='File name',
                        initialdir=tmp,
                        filetypes=[('OMFIT save', '*.zip'), ('OMFIT save', 'OMFITsave.txt'), ('All files', '.*')],
                        parent=top,
                    )

            if tmp:
                value1.set(tmp)
                e1.icursor(tk.END)
                e1.xview(tk.END)
                top.update_idletasks()
                if isModule is None:
                    selectProject(filename=tmp)
                else:
                    selectModule(filename=tmp)

        def treeview_sort_column(tv, col, reverse):
            def interpret_column(val, col):
                # from human-readable to sortable values
                try:
                    if col == '#1':
                        val = utils_base.convertDateFormat(val, format_in='%d %b %Y  %H:%M', format_out='%s')
                    elif col == '#3' and not isModule:
                        val, mult = val.split(' ')
                        val = float(val)
                        if mult == 'GB':
                            val *= 1024 ** 3
                        if mult == 'MB':
                            val *= 1024 ** 2
                        if mult == 'kB':
                            val *= 1024 ** 1
                except Exception:
                    val = 0
                return val

            # https://stackoverflow.com/questions/1966929/tk-treeview-column-sort
            # https://github.com/RedFantom/gsf-parser/commit/a8bc5e5f9feacbbc08ab4446243b79a0c612a0f6
            if col == '#0':
                children = tv.get_children('')
                data = {iid: tv.item(iid) for iid in children}
                tv.delete(*children)
                iterator = sorted(list(data.items()), reverse=reverse)
                for path, kwargs in iterator:
                    tv.insert('', tk.END, path, **kwargs)
            else:
                l = [(interpret_column(tv.set(k, col), col), k) for k in tv.get_children('')]
                l.sort(reverse=reverse)
                for index, (val, k) in enumerate(l):
                    tv.move(k, '', index)
            tv.heading(col, command=lambda col=col: treeview_sort_column(tv, col, not reverse))

        value1 = tk.StringVar()

        top = tk.Toplevel(self.rootGUI)
        top.withdraw()
        top.transient(self.rootGUI)

        descText = tk.ScrolledText(top, width=50, font=OMFITfont('normal', 0, 'Courier'))
        descText.configure(wrap='word')
        descText.pack(side=tk.RIGHT, expand=tk.NO, fill=tk.Y, padx=5, pady=5)
        descText.tag_configure('historic', foreground='dark slate gray')
        descText.tag_configure('error', foreground='red')
        descText.tag_configure('separator', foreground='blue')
        descText.tag_configure('warning', foreground='dark orange')

        if isModule:
            top.wm_title('Import OMFIT module...')
            value1.set(OMFITmodule.directories()[0])
        else:

            def deleteProject(filename):
                # check write access
                if not os.access(filename, os.W_OK):
                    dialog(
                        title="No write permissions",
                        message=filename + '\n' + permissions(filename),
                        icon="info",
                        answers=['Ok'],
                        parent=top,
                    )
                    return
                # confirm that user wants really to delete it
                if 'No' == dialog(title="Delete project ?", message=filename, answers=['Yes', 'No'], parent=top):
                    return
                # delete of ZIP project
                if zipfile.is_zipfile(filename):
                    printi('Deleting ZIP project: ' + filename)
                    os.remove(filename)
                # delete of deflated project
                else:
                    printi('Deleting project:' + os.path.split(filename)[0])
                    shutil.rmtree(os.path.split(filename)[0])
                # remove project from list of projects
                del projects[filename]
                # update GUI
                insert_entries()
                # if deleted project is open project, show it as unsaved
                if filename == OMFIT.filename:
                    OMFIT.filename = ''
                    self.updateTitle()

            # handle right-click on projects list
            def right_click(event):
                try:
                    self.popup.unpost()
                    self.popup.destroy()
                except Exception:
                    pass
                filename = modProjTreeGUI.identify_row(event.y)
                if filename:
                    modProjTreeGUI.selection_set(filename)
                    self.popup = tk.Menu(self.rootGUI, tearoff=False)
                    self.popup.add_command(label="Delete project", command=lambda filename=filename: deleteProject(filename))
                    self.popup.bind("<FocusOut>", lambda event: self.popup.unpost())
                    self.popup.post(event.x_root, event.y_root)
                    self.popup.focus_set()

            if 'load' in action:
                top.wm_title('Load OMFIT project...')
            else:
                top.wm_title('Compare OMFIT project...')
            value1.set(os.path.abspath(OMFIT['MainSettings']['SETUP']['projectsDir'].rstrip('/\\')))

        if isModule:
            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            ttk.Label(frm, text='Location where to load the module: ').pack(side=tk.LEFT, padx=5, pady=5)
            location = tk.OneLineText(frm, percolator=True)
            location.set("OMFIT['NEW_MODULE']")
            location.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)
            location.icursor(tk.END)
            location.xview(tk.END)

            availableModulesList = [None]

            def update_modules_dir(do_update_gits=True, reset_remote_branch=False):
                if reset_remote_branch:
                    self.remoteSelectorVariable.set('')
                    self.branchSelectorVariable.set('')
                if do_update_gits:
                    update_gits(what=do_update_gits)
                if self.remoteSelectorVariable.get() and not self.branchSelectorVariable.get():
                    availableModulesList[0] = {}
                else:
                    availableModulesList[0] = OMFIT.availableModules(directories=[moduledirSelectorVariableGet().split('@')[0].strip()])
                insert_entries()

            def moduledirSelectorVariableGet():
                if self.branchSelectorVariable.get():
                    directory = work_repo[0].git_dir
                    if os.path.exists(work_repo[0].git_dir + os.sep + 'modules'):
                        directory = work_repo[0].git_dir + os.sep + 'modules'
                    return directory + '  @  ' + self.remoteSelectorVariable.get() + '/' + self.branchSelectorVariable.get()
                else:
                    return moduledirSelectorVariable.get()

            moduledirSelectorVariable = tk.StringVar()
            moduledirSelectorVariable.set(OMFITmodule.directories(return_associated_git_branch=True, separator='  @  ')[0])
            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
            ttk.Label(frm, text='Repository directory: ').pack(side=tk.LEFT)
            moduledirSelector = ttk.Combobox(
                frm,
                state='readonly',
                textvariable=moduledirSelectorVariable,
                values=OMFITmodule.directories(return_associated_git_branch=True, separator='  @  '),
            )
            moduledirSelector.bind('<<ComboboxSelected>>', lambda event: update_modules_dir(reset_remote_branch=True))
            moduledirSelector.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
            ttk.Label(frm, text='Remote: ').pack(side=tk.LEFT)
            remoteSelector = ttk.Combobox(frm, textvariable=self.remoteSelectorVariable, width=50)
            remoteSelector.bind('<<ComboboxSelected>>', lambda event: update_gits(what='remote'))
            remoteSelector.bind('<Return>', lambda event: update_gits(what='remote'))
            remoteSelector.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

            frm = ttk.Frame(top)
            frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
            ttk.Label(frm, text='Branch: ').pack(side=tk.LEFT)
            branchSelector = ttk.Combobox(frm, textvariable=self.branchSelectorVariable)
            branchSelector.bind('<<ComboboxSelected>>', lambda event: update_gits(what='branch'))
            branchSelector.bind('<Return>', lambda event: update_gits(what='branch'))
            branchSelector.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

            work_repo = [repo]

            def update_gits(what=None):
                try:
                    repo = OMFITgit(moduledirSelectorVariable.get().split('@')[0].strip())
                except Exception:
                    if moduledirSelectorVariable.get().split('@')[0].strip().endswith('modules'):
                        try:
                            repo = OMFITgit(moduledirSelectorVariable.get().split('@')[0].strip() + os.sep + '..')
                        except Exception:
                            # not a valid git repository
                            self.remoteSelectorVariable.set('')
                            self.branchSelectorVariable.set('')
                            repo = None
                    else:
                        # not a valid git repository
                        self.remoteSelectorVariable.set('')
                        self.branchSelectorVariable.set('')
                        repo = None

                # cleanup spaces
                self.remoteSelectorVariable.set(self.remoteSelectorVariable.get().strip())
                self.branchSelectorVariable.set(self.branchSelectorVariable.get().strip())

                # if remote is empty then also must be branch
                if what == 'remote' and '/' in self.remoteSelectorVariable.get():
                    self.branchSelectorVariable.set('/'.join(self.remoteSelectorVariable.get().split('/')[1:]))
                    self.remoteSelectorVariable.set(self.remoteSelectorVariable.get().split('/')[0])
                elif what == 'remote' or not self.remoteSelectorVariable.get():
                    self.branchSelectorVariable.set('')

                # create a clone repository unless remoteSelector and branchSelector are empty
                if repo is not None and self.branchSelectorVariable.get() or self.remoteSelectorVariable.get():
                    work_repo[0] = repo.clone()
                    if work_repo[0].is_OMFIT_source():
                        remotes = work_repo[0].get_remotes()
                        if 'gafusion' not in remotes:
                            work_repo[0]('remote add gafusion git@github.com:gafusion/OMFIT-source.git', verbose=True)
                        if 'vali' not in remotes:
                            work_repo[0]('remote add vali git@vali.gat.com:OMFIT/OMFIT.git', verbose=True)
                        if OMFIT['MainSettings']['SERVER']['GITHUB_username'] not in remotes and work_repo[0].is_OMFIT_source():
                            work_repo[0](
                                'remote add %s git@github.com:%s/OMFIT-source.git'
                                % (OMFIT['MainSettings']['SERVER']['GITHUB_username'], OMFIT['MainSettings']['SERVER']['GITHUB_username']),
                                verbose=True,
                            )
                        if self.remoteSelectorVariable.get() not in remotes:
                            work_repo[0](
                                'remote add %s git@github.com:%s/OMFIT-source.git'
                                % (self.remoteSelectorVariable.get(), self.remoteSelectorVariable.get()),
                                verbose=True,
                            )
                    # make sure to always start from scratch if working on the clone
                    work_repo[0]('reset --hard HEAD')
                else:
                    work_repo[0] = repo

                if work_repo[0] is None:
                    update_modules_dir(do_update_gits=False)
                    remoteSelector.configure(state='disabled')
                    branchSelector.configure(state='disabled')
                    moduledirSelector.configure(state='readonly')
                else:
                    # set possible options for GUI elements
                    remoteSelector.configure(state='normal')
                    remoteSelectorOptions = work_repo[0].get_remotes()
                    if work_repo[0].is_OMFIT_source():
                        if 'gafusion' not in remoteSelectorOptions:
                            remoteSelectorOptions['gafusion'] = 'gafusion'
                        if 'vali' not in remoteSelectorOptions:
                            remoteSelectorOptions['vali'] = 'vali'
                        if (
                            OMFIT['MainSettings']['SERVER']['GITHUB_username'] not in remoteSelectorOptions
                            and work_repo[0].is_OMFIT_source()
                        ):
                            remoteSelectorOptions[OMFIT['MainSettings']['SERVER']['GITHUB_username']] = None
                    if 'original_git_repository' not in remoteSelectorOptions:
                        remoteSelectorOptions['original_git_repository'] = None
                    remoteSelectorOptions[''] = None
                    remoteSelectorOptions = sorted(list(remoteSelectorOptions.keys()), key=lambda x: x.lower())
                    remoteSelector.configure(values=tuple(remoteSelectorOptions))
                    branchSelectorOptions = ['']
                    if self.remoteSelectorVariable.get():
                        branchSelectorOptions = list(work_repo[0].get_branches(self.remoteSelectorVariable.get()).keys())
                        branchSelectorOptions = sorted(branchSelectorOptions, key=lambda x: x.lower())
                        branchSelector.configure(state='readonly')
                        moduledirSelector.configure(state='disabled')
                    else:
                        branchSelector.configure(state='disabled')
                        moduledirSelector.configure(state='readonly')
                    branchSelector.configure(values=tuple(branchSelectorOptions))
                    if what:
                        if self.branchSelectorVariable.get():
                            # switch branch (only need to check if branch is set, since if no remote, then work_repo[0]==repo)
                            work_repo[0].switch_branch(self.branchSelectorVariable.get(), self.remoteSelectorVariable.get())
                        if what != 'init':
                            update_modules_dir(do_update_gits=False)

        frm = ttk.Frame(top)

        flts = []
        frm1 = ttk.Frame(frm)
        frm1.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        if isModule:
            text = 'Filter: '
        else:
            text = 'Filter filename and notes: '
        ttk.Label(frm1, text=text).pack(side=tk.LEFT)
        filter = ttk.Entry(frm1)
        filter.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
        if isModule:
            modProjTreeGUI = tk.Treeview(frm, height=15, selectmode='browse')
            modProjTreeGUI.column("#0", minwidth=100, stretch=True)
            modProjTreeGUI.frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
            modProjTreeGUI["columns"] = ('#1', '#2', '#3')
            modProjTreeGUI.column("#1", minwidth=100, stretch=False, anchor=tk.CENTER)
            modProjTreeGUI.column("#2", minwidth=100, stretch=False, anchor=tk.CENTER)
            modProjTreeGUI.column("#3", minwidth=100, stretch=False, anchor=tk.CENTER)
            modProjTreeGUI.heading("#0", text="Module ID")
            modProjTreeGUI.heading("#1", text="Edited")
            modProjTreeGUI.heading("#2", text="Last Developer")
            modProjTreeGUI.heading("#3", text="Commit")

            def selectModule(filename=''):

                if len(modProjTreeGUI.selection()) and modProjTreeGUI.selection()[0] in ['_ID_', '_version_']:
                    return

                if len(filename):
                    modProjTreeGUI.selection_remove(modProjTreeGUI.selection())
                    directory = os.path.split(filename)[0]
                    moduleID = os.path.split(directory)[1]
                    info = OMFITmodule.info(filename)

                elif len(modProjTreeGUI.selection()):
                    tmp = modProjTreeGUI.selection()[0]
                    filename = availableModulesList[0][tmp]['path']
                    moduleID = availableModulesList[0][tmp]['ID']
                    info = availableModulesList[0][tmp]

                description = info.get('description', '').strip()

                if len(filename):
                    descText.configure(state=tk.NORMAL)
                    descText.delete('1.0', 'end')
                    descText.insert('insert', '+-' + '-' * len(moduleID) + '-+', 'separator')
                    descText.insert('insert', '\n| ' + moduleID + ' |', 'separator')
                    descText.insert('insert', '\n+-' + '-' * len(moduleID) + '-+\n', 'separator')
                    if info.get('status', ''):
                        descText.insert(
                            'insert',
                            '\nSTATUS: '
                            + info['status'].strip().split('\n')[0]
                            + '\n\n'
                            + '\n'.join(info['status'].strip().split('\n')[1:])
                            + '\n\n\n',
                            'warning',
                        )
                    descText.insert('insert', description)
                    descText.configure(state=tk.DISABLED)
                    descText.see(1.0)

                    value1.set(filename)
                    e1.icursor(tk.END)
                    e1.xview(tk.END)

                    # automatic naming of where the module will be inserted
                    locmoduleID = moduleID
                    k = 0
                    while locmoduleID in list(OMFIT.keys()):
                        k += 1
                        locmoduleID = moduleID + '_' + str(k)
                    location.set("OMFIT[" + repr(locmoduleID) + "]")

            modProjTreeGUI.bind('<Button-1>', lambda event: modProjTreeGUI.after(10, selectModule))
            modProjTreeGUI.bind('<Up>', lambda event: modProjTreeGUI.after(10, selectModule))
            modProjTreeGUI.bind('<Down>', lambda event: modProjTreeGUI.after(10, selectModule))
        else:
            projects = OMFIT.recentProjects(only_read=True)

            # project type
            frm1 = ttk.Frame(frm)
            frm1.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, pady=2)
            prj_types = ['__all__'] + OMFIT.prj_options_choices['type']
            prj_type = tk.StringVar()
            prj_type.set('__all__')
            ttk.Label(frm1, text='Filter type: ').pack(side=tk.LEFT)
            for text in prj_types:
                flts.append(ttk.Radiobutton(frm1, text=text.strip('_'), variable=prj_type, value=text))
                flts[-1].pack(side=tk.LEFT, anchor=tk.W)

            # project color
            frm1 = ttk.Frame(frm)
            frm1.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, pady=2)
            prj_colors = ['__all__'] + list(OMFIT.prj_options_choices['color'].keys())
            prj_color = tk.StringVar()
            prj_color.set('__all__')
            ttk.Label(frm1, text='Filter color code: ').pack(side=tk.LEFT)
            color_mapper = {'__all__': 'black'}
            color_mapper.update(OMFIT.prj_options_choices['color'])
            for text in prj_colors:
                if text == '__all__':
                    style = 'TRadiobutton'
                else:
                    style = text + '.TRadiobutton'
                    ttk.Style().configure(style, foreground=color_mapper.get(text, text))
                flts.append(ttk.Radiobutton(frm1, text=text.strip('_'), variable=prj_color, value=text, style=style))
                flts[-1].pack(side=tk.LEFT, anchor=tk.W)

            modProjTreeGUI = tk.Treeview(frm, height=15, selectmode='browse')
            modProjTreeGUI.column("#0", minwidth=500, width=500, stretch=True)
            modProjTreeGUI.frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
            modProjTreeGUI["columns"] = ('#1', '#2', '#3')
            modProjTreeGUI.column("#1", minwidth=160, width=160, stretch=False, anchor=tk.CENTER)
            modProjTreeGUI.column("#2", minwidth=80, width=80, stretch=False, anchor=tk.CENTER)
            modProjTreeGUI.column("#3", minwidth=80, width=80, stretch=False, anchor=tk.CENTER)
            modProjTreeGUI.heading("#0", text="Project name", command=lambda: treeview_sort_column(modProjTreeGUI, '#0', False))
            modProjTreeGUI.heading("#1", text="Last modified", command=lambda: treeview_sort_column(modProjTreeGUI, '#1', False))
            modProjTreeGUI.heading("#2", text="Type", command=lambda: treeview_sort_column(modProjTreeGUI, '#2', False))
            modProjTreeGUI.heading("#3", text="Size", command=lambda: treeview_sort_column(modProjTreeGUI, '#3', False))

            def selectProject(filename=''):
                if len(modProjTreeGUI.selection()):
                    if len(filename):
                        modProjTreeGUI.selection_remove(modProjTreeGUI.selection())
                    else:
                        filename = modProjTreeGUI.selection()[0]
                        value1.set(filename)
                        e1.icursor(tk.END)
                        e1.xview(tk.END)

                if len(filename):
                    try:
                        info = OMFITproject.info(filename)

                        descText.configure(state=tk.NORMAL)
                        descText.delete('1.0', 'end')

                        descText.insert('insert', '== EXPERIMENT == (MainSettings)\n', 'separator')
                        for k in info['MainSettings']['EXPERIMENT']:
                            if k not in ['projectID', 'provenanceID'] and info['MainSettings']['EXPERIMENT'][k] is not None:
                                descText.insert('insert', k + ':\t\t' + str(info['MainSettings']['EXPERIMENT'][k]) + '\n', 'historic')

                        descText.insert('insert', '\n== MODULES ==\n', 'separator')
                        for k in info['modules']:
                            descText.insert('insert', k + '\n', 'historic')

                        descText.insert('insert', '\n== NOTES ==\n', 'separator')
                        descText.insert('insert', info['notes'] + '\n\n', 'historic')

                        descText.configure(state=tk.DISABLED)
                        descText.see('insert')

                        persistent_projectID.set(info['persistent_projectID'])

                    except Exception as _excp:
                        raise
                        descText.configure(state=tk.NORMAL)
                        descText.delete('1.0', 'end')
                        descText.insert('insert', repr(_excp) + '\n\n', 'error')
                        descText.insert('insert', 'ERROR previewing project content!\n', 'historic')
                        descText.insert('insert', 'Is this a valid OMFIT project file?\n', 'historic')
                        descText.configure(state=tk.DISABLED)
                        descText.see('insert')

            modProjTreeGUI.bind(f'<{rightClick}>', lambda event: modProjTreeGUI.after(10, lambda event=event: right_click(event)))
            modProjTreeGUI.bind('<Button-1>', lambda event: modProjTreeGUI.after(10, selectProject))
            modProjTreeGUI.bind('<Up>', lambda event: modProjTreeGUI.after(10, selectProject))
            modProjTreeGUI.bind('<Down>', lambda event: modProjTreeGUI.after(10, selectProject))

            for color_name in list(OMFIT.prj_options_choices['color'].keys()):
                modProjTreeGUI.tag_configure('PRJ_' + color_name, foreground=OMFIT.prj_options_choices['color'][color_name])
                modProjTreeGUI.tag_configure('PRJ_' + color_name, foreground=OMFIT.prj_options_choices['color'][color_name])

        frm = ttk.Frame(top)
        if isModule:
            ttk.Label(frm, text='Module path: ', justify=tk.LEFT, anchor=tk.W).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X, padx=5, pady=0)
        else:
            ttk.Label(frm, text='Project path: ', justify=tk.LEFT, anchor=tk.W).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X, padx=5, pady=0)
        e1 = ttk.Entry(frm, textvariable=value1)
        e1.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5)
        e1.icursor(tk.END)
        e1.xview(tk.END)
        ttk.Button(frm, text="File lookup...", command=lambda: onButton(isModule, action)).pack(
            side=tk.LEFT, expand=tk.NO, fill=tk.X, padx=5
        )
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)

        loadFrame = ttk.Frame(top)
        loadFrame.pack(side=tk.TOP, padx=5, pady=2, expand=tk.NO, fill=tk.X)
        ttk.Button(loadFrame, text="Load", command=lambda: onReturn(isModule, action)).pack(
            side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5
        )
        if not isModule:
            persistent_projectID = tk.BooleanVar()
            persistent_projectID.set(False)
            ck = ttk.Checkbutton(loadFrame, variable=persistent_projectID, text='Use previous projectID')
            ck.state(['!alternate'])  # removes color box bg indicating user has not clicked it, which may confuse people
            ck.pack(side=tk.LEFT)
            ck.var = persistent_projectID
            if persistent_projectID.get():
                ck.state(['selected'])
        else:
            developerMode = tk.BooleanVar()
            dev_acceptable = os.access(moduledirSelectorVariable.get().split('@')[0].strip(), os.W_OK) and not os.path.exists(
                os.sep.join([moduledirSelectorVariable.get(), '..', 'public'])
            )
            developerMode.set(OMFIT['MainSettings']['SETUP']['developer_mode_by_default'] & dev_acceptable)
            ck_devel = ttk.Checkbutton(loadFrame, variable=developerMode, text='Developer mode')
            ck_devel.state(['!alternate'])  # removes color box bg indicating user has not clicked it, which may confuse people
            ck_devel.pack(side=tk.LEFT)
            ck_devel.var = developerMode
            if developerMode.get():
                ck_devel.state(['selected'])

        if isModule:

            def insert_entries():
                for item in modProjTreeGUI.get_children():
                    modProjTreeGUI.delete(item)
                flt = re.compile(re.escape(filter.get()), re.I)
                added = []
                for field in ['ID', 'description']:
                    for moduleID in sorted(list(availableModulesList[0].keys()), key=lambda x: availableModulesList[0][x]['ID'].lower()):
                        if (
                            re.search(flt, availableModulesList[0][moduleID].get(field, ''))
                            and not availableModulesList[0][moduleID]['ID'].startswith('_')
                            and moduleID not in added
                        ):
                            warn_text = []
                            tag = ''
                            if moduleID in availableModulesList[0][moduleID]['untracked']:
                                tag = 'FG_red2'
                                warn_text += ['untracked']
                            elif availableModulesList[0][moduleID]['modified']:
                                tag = 'FG_blue'
                                warn_text += ['modified']
                            if availableModulesList[0][moduleID].get('status', ''):
                                tag = 'FG_dark_orange'
                                warn_text += [availableModulesList[0][moduleID]['status'].strip().split('\n')[0]]
                            warn_text = f" ({', '.join(warn_text)})" if len(warn_text) else ''
                            modProjTreeGUI.insert(
                                '',
                                tk.END,
                                availableModulesList[0][moduleID]['path'],
                                text=treeText(availableModulesList[0][moduleID]['ID'] + warn_text, False, -1, False),
                                values=(
                                    str(availableModulesList[0][moduleID]['date']),
                                    str(availableModulesList[0][moduleID]['edited_by']),
                                    str(availableModulesList[0][moduleID]['commit'])[:10],
                                ),
                                tag=tag,
                            )
                            added.append(moduleID)
                    if field == 'ID':
                        modProjTreeGUI.insert(
                            '',
                            tk.END,
                            '_' + field + '_',
                            text=' -- matches based on modules descriptions --',
                            values=('--', '--', '--'),
                            tag='',
                        )

                # remember this directory for next time
                OMFITaux['lastModulesDir'] = moduledirSelectorVariable.get().split('@')[0].strip()

                # do not allow developer mode if public OMFIT install or no write access to module repository
                if os.access(moduledirSelectorVariable.get().split('@')[0].strip(), os.W_OK) and (
                    os.path.abspath(moduledirSelectorVariable.get().split('@')[0].strip())
                    != os.path.abspath(os.sep.join([OMFITsrc, '..', 'modules']))
                    or not os.path.exists(os.sep.join([OMFITsrc, '..', 'public']))
                ):
                    ck_devel.configure(state=tk.NORMAL)
                else:
                    ck_devel.configure(state=tk.DISABLED)
                    ck_devel.state(['!selected'])

            # add entries and select (pretend that the branch entered)
            update_modules_dir(do_update_gits='init')

        else:
            common = os.path.abspath(tolist(OMFIT['MainSettings']['SETUP']['projectsDir'])[0]) + os.sep

            def insert_entries():
                for item in modProjTreeGUI.get_children():
                    modProjTreeGUI.delete(item)
                flt = re.compile(re.escape(filter.get()), re.I)
                for proj in list(projects.keys()):
                    if (
                        (
                            re.search(flt, proj)
                            or re.search(flt, str(projects[proj].get('notes', '')))
                            or re.search(flt, str(projects[proj].get('device', '')))
                            or re.search(flt, str(projects[proj].get('shot', '')))
                            or re.search(flt, str(projects[proj].get('time', '')))
                            or re.search(flt, str(projects[proj].get('modules', '')))
                        )
                        and (prj_type.get() == '__all__' or projects[proj].get('type', '') == prj_type.get())
                        and (prj_color.get() == '__all__' or projects[proj].get('color', '') == prj_color.get())
                    ):
                        modProjTreeGUI.insert(
                            '',
                            tk.END,
                            proj,
                            text=treeText(re.sub('OMFITsave\.txt$', '', re.sub('^' + common, '', proj)), False, -1, False),
                            values=(
                                utils_base.convertDateFormat(os.stat(proj).st_mtime),
                                projects[proj].get('type', ''),
                                re.sub('N/A', '', sizeof_fmt(projects[proj].get('size', ''), ' ')),
                            ),
                            tag='PRJ_' + re.sub(' ', '_', projects[proj].get('color', '')),
                        )

            ttk.Separator(top).pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=10)
            ttk.Button(top, text="Load remote project", command=lambda: onButton(isModule, action + 'Remote')).pack(
                side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=10
            )
            insert_entries()

        filter.bind("<Key>", lambda event: modProjTreeGUI.after(1, insert_entries))
        for item in flts:
            item.configure(command=insert_entries)

        if not isModule:
            # most recent projects first
            treeview_sort_column(modProjTreeGUI, '#1', True)
        modProjTreeGUI.bind('<Return>', lambda event: onReturn(isModule, action))
        modProjTreeGUI.bind('<KP_Enter>', lambda event: onReturn(isModule, action))
        modProjTreeGUI.bind('<Double-1>', lambda event: onReturn(isModule, action))
        top.bind('<Escape>', lambda event: onEscape())
        filter.focus_set()

        top.protocol("WM_DELETE_WINDOW", top.destroy)
        top.update_idletasks()
        tk_center(top, self.rootGUI)
        top.deiconify()
        top.wait_window(top)

    def OMFITmodules(self, action='export'):
        top = tk.Toplevel(self.rootGUI)
        top.withdraw()
        top.transient(self.rootGUI)
        top.geometry(str(int(self.rootGUI.winfo_width() * 8.0 / 9.0)) + "x" + str(int(self.rootGUI.winfo_height() * 8.0 / 9.0)))

        # ====================
        # MODULE EXPORT
        # ====================
        if action == 'export':
            top.wm_title('Select modules to export:')

            def onReturn(quickAction=True):
                # export the individual modules
                modules = [_f for _f in tolist(moduleList.selection()) if _f]
                top.destroy()

                if not len(modules):
                    return

                def deepcopyMissing(A, B):
                    for kid in list(B.keys()):
                        if kid not in A:
                            A[kid] = copy.deepcopy(B[kid])
                        elif isinstance(B[kid], dict) and (not hasattr(B[kid], 'dynaLoad') or not B[kid].dynaLoad):
                            deepcopyMissing(A[kid], B[kid])

                exported = False
                for item in modules:
                    moduleLocation, saveFile = item.split('###')
                    moduleID = moduleDict[moduleLocation]['ID']

                    if self.remoteSelectorVariable.get() and self.branchSelectorVariable.get():
                        # Go back in time to the commit set by root['SETTINGS']['MODULE']['commit'] (if that info is available)
                        # and if it is not (e.g. new module) then checkout destination branch
                        # Note: technically this should be done --ALWAYS-- so that we rely on git to do the merge,
                        #       however for the time being (and backward compatibility) we only do this if the user
                        #       wants to push on a remote branch.
                        found = False
                        if eval('OMFIT' + moduleLocation)['SETTINGS']['MODULE']['commit']:
                            # make sure to start from clear state and try checking out the commit
                            work_repo[0]('reset --hard', verbose=True)
                            work_repo[0]('clean -xdf', verbose=True)
                            checkout_output = work_repo[0](
                                'checkout %s' % eval('OMFIT' + moduleLocation)['SETTINGS']['MODULE']['commit'], verbose=True
                            )
                            if 'error:' not in checkout_output and 'fatal:' not in checkout_output:
                                found = True
                            if not found:  # try finding and checking out the commit in all of the known remotes
                                for remote in unsorted_unique(
                                    [self.remoteSelectorVariable.get(), 'gafusion'] + list(work_repo[0].get_remotes().keys())
                                ):
                                    work_repo[0]('fetch %s' % remote, verbose=True)
                                    checkout_output = work_repo[0](
                                        'checkout %s' % eval('OMFIT' + moduleLocation)['SETTINGS']['MODULE']['commit'], verbose=True
                                    )
                                    if 'error:' not in checkout_output and 'fatal:' not in checkout_output:
                                        found = True
                                        break
                        if not found:
                            work_repo[0]('reset --hard', verbose=True)
                            work_repo[0]('clean -xdf', verbose=True)
                            work_repo[0].switch_branch(self.branchSelectorVariable.get(), self.remoteSelectorVariable.get())
                        # Then branch off to `omfit_work_branch` to temporarily work on the upcoming commit
                        if 'omfit_work_branch' in work_repo[0].get_branches():
                            work_repo[0]('branch -D omfit_work_branch', verbose=True)
                        work_repo[0]('checkout -b omfit_work_branch', verbose=True)

                    # set aside the tree module
                    tmp = eval('OMFIT' + moduleLocation)
                    try:
                        # make a deepcopy of the tree module in tmpNew
                        # independently of quickAction we want to make a copy of the module without __scratch__ directories
                        if quickAction:
                            tmpNew = module_selective_deepcopy('OMFIT' + moduleLocation, classes=['_OMFITpython', 'OMFITsettings'])
                        else:
                            tmpNew = module_noscratch_deepcopy(eval('OMFIT' + moduleLocation))

                        # turn modifyOriginal scripts into normal scripts and apply formatting
                        for location in traverse(tmpNew, onlyLeaf=(_OMFITpython,), skipDynaLoad=True):
                            if eval('tmpNew' + location).modifyOriginal:
                                if os.path.isfile(eval('tmpNew' + location + '.filename')):
                                    cls = eval('tmpNew' + location).__class__.__name__
                                    exec(f'tmpNew{location}={cls}(tmpNew{location}.filename)', globals(), locals())
                                else:
                                    printw(f'No original file for modifyOriginal script {location}: skipping')
                            if self.omfit_format.get():
                                exec(f'tmpNew{location}.format()', globals(), locals())

                        # reload the module from repository in tmpOrig0 and apply formatting
                        # tmpOrig has it's stripped down version (only scripts and settings) if quickAction is set
                        if os.path.exists(saveFile):
                            OMFIT.loadModule(
                                saveFile, 'OMFIT' + moduleLocation, checkLicense=False, withSubmodules=False, developerMode=False
                            )
                            tmpOrig0 = tmpOrig = eval('OMFIT' + moduleLocation)
                            if self.omfit_format.get():
                                for location in traverse(tmpOrig, onlyLeaf=(_OMFITpython,), skipDynaLoad=True):
                                    exec(f'tmpOrig{location}.format()', globals(), locals())
                            if '__SETTINGS_AT_IMPORT__' in tmpOrig:
                                del tmpOrig['__SETTINGS_AT_IMPORT__']
                            if quickAction:
                                tmpOrig = module_selective_deepcopy('OMFIT' + moduleLocation, classes=['_OMFITpython', 'OMFITsettings'])
                                t_tmpQuick = traverse(tmpOrig, skipDynaLoad=True)
                        else:
                            tmpOrig = None

                    finally:
                        # put the module back into the tree
                        exec('OMFIT' + moduleLocation + '=tmp', globals(), locals())

                    # ok, at this point the tmpNew contains a deepcopy of the tree module,
                    # while tmpOrig0 has the module as loaded from the repo (or None if the module did not exist)
                    # and tmpOrig has it's stripped down version (only scripts and settings) if quickAction is set

                    moduleTmp = copy.deepcopy(tmpNew['SETTINGS']['MODULE'])
                    for k in ['defaultGUI', 'contact']:
                        if k in moduleTmp:
                            del moduleTmp[k]

                    if self.remoteSelectorVariable.get() and self.branchSelectorVariable.get():
                        commit_message = ''
                    else:
                        commit_message = False

                    # deleting items will ignore them in the switching GUI
                    # here we just keep defaultGUI and contact
                    for k in list(tmpNew['SETTINGS']['MODULE'].keys()):
                        if k not in ['defaultGUI', 'contact']:
                            del tmpNew['SETTINGS']['MODULE'][k]
                    if '__SETTINGS_AT_IMPORT__' in tmpNew:
                        del tmpNew['__SETTINGS_AT_IMPORT__']

                    if tmpOrig is not None:

                        # deleting items will ignore them in the switching GUI
                        # here we just keep defaultGUI and contact
                        for k in list(tmpOrig['SETTINGS']['MODULE'].keys()):
                            if k not in ['defaultGUI', 'contact']:
                                del tmpOrig['SETTINGS']['MODULE'][k]

                        # copy experiment settings from current module
                        for k in list(OMFIT['MainSettings']['EXPERIMENT'].keys()):
                            if k in tmpNew['SETTINGS'].get('EXPERIMENT', {}):
                                tmpOrig['SETTINGS']['EXPERIMENT'][k] = tmpNew['SETTINGS']['EXPERIMENT'][k]

                        # pick differences to export
                        while True:
                            tmp = diffTreeGUI(
                                tmpOrig,
                                tmpNew,
                                thisName='Modules repository',
                                otherName='In the tree',
                                resultName='Export result',
                                title='OMFIT' + moduleLocation + ' --> Modules repository',
                                diffSubModules=None,
                                precision=0.0,
                                description=commit_message,
                                deepcopyOther=False,
                                skipClasses=(OMFITtmp,),
                                noloadClasses=(OMFITharvest, OMFITharvestS3, OMFITmds, OMFITrdb),
                                always_show_GUI=True,
                                order=not quickAction,
                                favor_my_order=False,
                                modify_order=True,
                            )

                            if isinstance(commit_message, str):
                                switch, commit_message = tmp
                                if switch is None or not len(switch):
                                    break
                                commit_message = commit_message.strip()
                                if len(commit_message):
                                    if '<<<>>>' not in commit_message:
                                        commit_message = commit_message + '\n<<<>>>%s module<<<>>>' % moduleID
                                    break
                                dialog(title='Commit message', message='Please enter a valid commit message', answers=['Ok'], icon='error')
                            else:
                                switch = tmp
                                break

                        # if quick action is set we need to apply changes to module as loaded from the repo
                        if switch is not None and len(switch) and quickAction:
                            t_tmpOrig0 = traverse(tmpOrig0, skipDynaLoad=True)  # what's in the repository
                            t_tmpOrig = traverse(tmpOrig, skipDynaLoad=True)  # the partial export
                            for k in t_tmpOrig:
                                # only create OMFITtrees that do not exist in tmpOrig0
                                if isinstance(eval(f'tmpOrig{k}'), OMFITtree):
                                    if k not in t_tmpOrig0:
                                        exec(f'tmpOrig0{k} = tmpOrig{k}', globals(), locals())
                                # update the python scripts and settings
                                elif isinstance(eval('tmpOrig' + k), (_OMFITpython, OMFITsettings)):
                                    exec(f'tmpOrig0{k} = tmpOrig{k}', globals(), locals())
                            # update the keyOrder based on the partially exported tree
                            for k in t_tmpOrig:
                                if isinstance(eval(f'tmpOrig0{k}'), OMFITtree):
                                    keys = sorted_join_lists(
                                        eval(f'tmpOrig0{k}').keys(),
                                        eval(f'tmpOrig{k}').keys(),
                                        False,
                                        eval(f'tmpOrig0{k}').caseInsensitive or eval(f'tmpOrig{k}').caseInsensitive,
                                    )
                                    exec(f'tmpOrig0{k}.keyOrder = keys', globals(), locals())
                            # remove entries which have been deleted
                            t_tmpOrig0 = traverse(tmpOrig0, skipDynaLoad=True)
                            for k in t_tmpQuick:
                                if k not in t_tmpOrig and k in t_tmpOrig0:
                                    try:
                                        exec('del tmpOrig0' + k, globals(), locals())
                                    except KeyError as _excp:
                                        raise KeyError('%s: you may need to do a `Detailed module export`' % (str(_excp)))
                        tmp = tmpOrig0

                    else:

                        # pick what to export
                        while True:
                            tmp = exportTreeGUI(tmpNew, 'Export module ' + moduleID, description=commit_message)

                            if isinstance(commit_message, str):
                                switch, commit_message = tmp
                                if switch is None or not len(switch):
                                    break
                                commit_message = commit_message.strip()
                                if len(commit_message):
                                    if '<<<>>>' not in commit_message:
                                        commit_message = commit_message + '\n<<<>>>%s module<<<>>>' % moduleID
                                    break
                                dialog(title='Commit message', message='Please enter a valid commit message', answers=['Ok'], icon='error')
                            else:
                                switch = tmp
                                break

                        tmp = tmpNew

                    if switch is not None and len(switch):
                        exported = True
                        # update module info in the OMFIT tree
                        moduleDict[moduleLocation]['edited_by'] = os.environ['USER']
                        moduleDict[moduleLocation]['date'] = utils_base.now()
                        # update module info to be written to file
                        tmp['SETTINGS']['MODULE'].update(moduleTmp)
                        # finally update the files in the repo
                        # note that we are using the `deploy_module` method
                        tmp.deploy_module(saveFile, zip=False)
                        omfit_log('export module', saveFile)
                        # git
                        if isinstance(commit_message, str):
                            # check if there anything has changed
                            if work_repo[0]('; ls modules', returns=['code']) == 0:
                                something_to_commit = work_repo[0]('diff --name-only modules/%s' % moduleID, verbose=True)
                            else:
                                something_to_commit = work_repo[0]('diff --name-only %s' % moduleID, verbose=True)
                            something_to_commit = len(something_to_commit.strip())
                            # check for untracked files too
                            if not something_to_commit:
                                if work_repo[0]('; ls modules', returns=['code']) == 0:
                                    something_to_commit = work_repo[0]('ls-files -o modules/%s' % moduleID, verbose=True)
                                else:
                                    something_to_commit = work_repo[0]('ls-files -o %s' % moduleID, verbose=True)
                                something_to_commit = len(something_to_commit.strip())
                            # if there is something to commit
                            if something_to_commit:
                                if work_repo[0]('; ls modules', returns=['code']) == 0:
                                    work_repo[0]('add -A modules/%s' % moduleID, verbose=True)
                                else:
                                    work_repo[0]('add -A %s' % moduleID, verbose=True)

                                # commit, use --no-verify to skip git hooks (for now)
                                work_repo[0]('commit --no-verify -F - <<__EOF__\n%s\n__EOF__' % commit_message, verbose=True)
                                commit = work_repo[0].get_hash('HEAD')

                                work_repo[0](
                                    'fetch %s %s' % (self.remoteSelectorVariable.get(), self.branchSelectorVariable.get()), verbose=True
                                )
                                # first try rebasing
                                rebase_output = work_repo[0](
                                    'rebase %s/%s' % (self.remoteSelectorVariable.get(), self.branchSelectorVariable.get()), verbose=True
                                )
                                # if rebase fails it's best to handle conflicts with merges
                                if 'error:' in rebase_output or 'fatal:' in rebase_output or 'could not apply' in rebase_output:
                                    work_repo[0]('rebase --abort', verbose=True)
                                    merge_output = work_repo[0](
                                        'merge --no-edit %s/%s' % (self.remoteSelectorVariable.get(), self.branchSelectorVariable.get()),
                                        verbose=True,
                                    )
                                    # manually handle merge conflicts (users need to manually fix conflicts and commit)
                                    while 'merge is not possible' in merge_output or 'fix conflicts' in merge_output:
                                        os.system(
                                            'cd %s\nxterm -e "git merge --no-edit %s/%s; echo \'--> please fix conflicts AND commit <--\'; bash"'
                                            % (work_repo[0].git_dir, self.remoteSelectorVariable.get(), self.branchSelectorVariable.get())
                                        )
                                        merge_output = work_repo[0](
                                            'merge --no-edit %s/%s'
                                            % (self.remoteSelectorVariable.get(), self.branchSelectorVariable.get()),
                                            verbose=True,
                                        )

                                # push
                                if (
                                    self.remoteSelectorVariable.get() == 'original_git_repository'
                                    and work_repo[0].active_branch()[0] == self.branchSelectorVariable.get()
                                ):
                                    # cannot push on active branch of destination repository, so we pull from there instead
                                    tmp_repo = OMFITgit(work_repo[0].get_remotes()['original_git_repository']['url'].split('file://')[1])
                                    tmp_repo(
                                        'remote add tmp_remote_%s file://%s' % (omfit_hash(work_repo[0].git_dir, 10), work_repo[0].git_dir),
                                        verbose=True,
                                    )
                                    tmp_repo(
                                        'fetch tmp_remote_%s %s'
                                        % (omfit_hash(work_repo[0].git_dir, 10), self.branchSelectorVariable.get()),
                                        verbose=True,
                                    )
                                    tmp_repo(
                                        'merge tmp_remote_%s/%s'
                                        % (omfit_hash(work_repo[0].git_dir, 10), self.branchSelectorVariable.get()),
                                        verbose=True,
                                    )
                                    tmp_repo('remote remove tmp_remote_%s' % omfit_hash(work_repo[0].git_dir, 10), verbose=True)
                                else:
                                    work_repo[0](
                                        'push %s omfit_work_branch:%s'
                                        % (self.remoteSelectorVariable.get(), self.branchSelectorVariable.get()),
                                        verbose=True,
                                    )
                                eval('OMFIT' + moduleLocation)['SETTINGS']['MODULE']['commit'] = commit
                            else:
                                printi('Nothing to commit and push')

                if exported:
                    self.update_treeGUI_and_GUI()

        # ====================
        # MODULE RELOAD
        # ====================
        elif action == 'reload':
            top.wm_title('Select modules to reload:')

            def onReturn(quickAction=True):
                # reload the individual modules, reverse order ensures that compound modules are reloaded properly
                modules = tolist(moduleList.selection())
                top.destroy()

                if len(modules):
                    OMFITx.CloseAllGUIs()

                for moduleLocation in modules[::-1]:
                    moduleLocation, saveFile = moduleLocation.split('###')
                    moduleID = moduleDict[moduleLocation]['ID']

                    try:
                        tmpOrig = eval('OMFIT' + moduleLocation)
                        OMFIT.loadModule(saveFile, 'OMFIT' + moduleLocation, checkLicense=False, withSubmodules=True)
                        tmpNew = eval('OMFIT' + moduleLocation)
                    finally:
                        exec('OMFIT' + moduleLocation + '=tmpOrig', globals(), locals())

                    try:
                        moduleTmpOrig = tmpOrig['SETTINGS']['MODULE']
                        moduleTmpNew = tmpNew['SETTINGS']['MODULE']
                        # comment continues to live on
                        moduleTmpNew['comment'] = moduleTmpOrig.get('comment', '')

                        # do not diff anything under MODULE
                        del tmpOrig['SETTINGS']['MODULE']
                        del tmpNew['SETTINGS']['MODULE']

                        switch = diffTreeGUI(
                            tmpOrig,
                            tmpNew,
                            thisName='In the tree',
                            otherName='From modules repository',
                            resultName='Reload result',
                            title='Modules repository --> OMFIT' + moduleLocation,
                            diffSubModules=True,
                            tellDescription=False,
                            deepcopyOther=False,
                            skipClasses=(OMFITtmp),
                            noloadClasses=(OMFITharvest, OMFITharvestS3, OMFITmds, OMFITrdb),
                        )

                    finally:
                        tmpOrig['SETTINGS']['MODULE'] = moduleTmpOrig

                    if switch is not None:
                        tmpOrig['SETTINGS']['MODULE'] = moduleTmpNew
                        omfit_log('reload module', saveFile)

                self.update_treeGUI_and_GUI()

        def onEscape():
            top.destroy()

        moduleDict = OMFIT.moduleDict()

        moduledirSelectorVariable = tk.StringVar()
        if action == 'reload':
            values = OMFITmodule.directories(return_associated_git_branch=True, separator='  @  ', checkIsWriteable=False)
            if len(values):
                moduledirSelectorVariable.set(values[0])
        else:
            # checkIsWriteable='git' will return a directory even if it is not writable, but it is a git repository
            values = OMFITmodule.directories(return_associated_git_branch=True, separator='  @  ', checkIsWriteable='git')
            if len(values):
                moduledirSelectorVariable.set(values[0])
            else:
                top.destroy()
                printe(
                    "You are missing write permissions to the modules directories.\n"
                    + "To export your own modules add a new directory to OMFIT['MainSettings']['SETUP']['modulesDir']\n"
                    + "or consider cloning the OMFIT-source repository:\n"
                    + "https://docs.google.com/document/d/1BcZOQSmcdbXOzZ3Et5UqNK-3dRT9mH4Zq8PNq7fQVSg/edit"
                )
                return

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
        ttk.Label(frm, text='Repository directory: ').pack(side=tk.LEFT)
        moduledirSelector = ttk.Combobox(frm, state='readonly', textvariable=moduledirSelectorVariable, values=values)
        moduledirSelector.bind('<<ComboboxSelected>>', lambda event: updateReloadExport(reset_remote_branch=True))
        moduledirSelector.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

        git_frm = ttk.Frame(top)
        git_frm.pack(side=tk.TOP, expand=tk.NO, anchor=tk.W)

        frm = ttk.Frame(git_frm)
        frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
        ttk.Label(frm, text='Remote: ').pack(side=tk.LEFT)
        remoteSelector = ttk.Combobox(frm, textvariable=self.remoteSelectorVariable, width=50)
        remoteSelector.bind('<<ComboboxSelected>>', lambda event: update_gits(what='remote'))
        remoteSelector.bind('<Return>', lambda event: update_gits(what='remote'))
        remoteSelector.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

        frm = ttk.Frame(git_frm)
        frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
        ttk.Label(frm, text='Branch: ').pack(side=tk.LEFT)
        branchSelector = ttk.Combobox(frm, textvariable=self.branchSelectorVariable)
        branchSelector.bind('<<ComboboxSelected>>', lambda event: update_gits(what='branch'))
        branchSelector.bind('<Return>', lambda event: update_gits(what='branch'))
        branchSelector.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
        moduleList = tk.Treeview(frm)
        moduleList.frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        moduleList["columns"] = ('module', 'repo', 'sign', 'tree')
        moduleList.column("#0", minwidth=200, width=200, stretch=True)
        moduleList.column("module", minwidth=100, width=100, stretch=True, anchor=tk.CENTER)
        moduleList.column("repo", minwidth=200, width=200, stretch=True, anchor=tk.CENTER)
        moduleList.column("sign", minwidth=20, width=20, stretch=False, anchor=tk.CENTER)
        moduleList.column("tree", minwidth=200, width=200, stretch=True, anchor=tk.CENTER)
        moduleList.heading("#0", text="Module location")
        moduleList.heading("module", text="Module ID")
        moduleList.heading("repo", text="Repository version")
        moduleList.heading("tree", text="Tree version")
        moduleList.tag_configure("error", background='light coral')
        moduleList.tag_configure("warning", background='yellow')
        moduleList.tag_configure("update", background='PaleGreen2')
        moduleList.tag_configure("dubious", background='light blue')

        def updateReloadExport(doSelect=False, do_update_gits=True, reset_remote_branch=False):
            if reset_remote_branch:
                self.remoteSelectorVariable.set('')
                self.branchSelectorVariable.set('')
            # update git
            if do_update_gits:
                update_gits(what=do_update_gits)
            # clear existing entries
            for item in moduleList.get_children():
                moduleList.delete(item)
            # stop here if remote is set, but not the branch
            if self.remoteSelectorVariable.get() and not self.branchSelectorVariable.get():
                return
            # selected modules
            modules = tolist(moduleList.selection())
            # list modules available in repository
            tmpAvailableModulesList = OMFIT.availableModules(directories=[moduledirSelectorVariableGet().split('@')[0].strip()])
            # figure out new modules
            newModules = copy.deepcopy(moduleDict)
            for avMod in list(tmpAvailableModulesList.keys()):
                for item in list(newModules.keys()):
                    if newModules[item]['ID'] == tmpAvailableModulesList[avMod]['ID']:
                        del newModules[item]
                        continue
            # add new modules to the list
            for item in newModules:
                tmp = newModules[item]['ID']
                if tmp is None:
                    printe(
                        "OMFIT%s could not be exported because OMFIT%s['SETTINGS']['MODULE']['ID'] should be set to a string with the module name"
                        % (item, item)
                    )
                    tmp = str(id(newModules[item]))
                path = os.sep.join([moduledirSelectorVariableGet().split('@')[0].strip(), tmp, 'OMFITsave.txt'])
                tmpAvailableModulesList[path] = {}
                tmpAvailableModulesList[path].update(newModules[item])
                tmpAvailableModulesList[path]['path'] = path

            # create colored entries (handling different logic for reload/export)
            for item in list(moduleDict.keys()):
                for avMod in list(tmpAvailableModulesList.keys()):
                    if (
                        moduleDict[item]['ID'] is None
                        or moduleDict[item]['ID'] is not None
                        and moduleDict[item]['ID'] != tmpAvailableModulesList[avMod]['ID']
                    ):
                        continue

                    tags = []

                    if eval('OMFIT' + item).date is not None and eval('OMFIT' + item).edited_by is not None:
                        modTree = str(eval('OMFIT' + item).date) + '\t    ' + str(eval('OMFIT' + item).edited_by)
                    else:
                        # if the current date/user is not set, this is a warning when I have to import but it's ok on export
                        modTree = "!!! info not available !!!"
                        if action == 'export':
                            tags = ['update']
                        elif action == 'reload':
                            tags = ['warning']

                    if os.path.exists(tmpAvailableModulesList[avMod]['path']):
                        modRepo = str(tmpAvailableModulesList[avMod]['date']) + '\t    ' + str(tmpAvailableModulesList[avMod]['edited_by'])
                    else:
                        # if the path does not exist it means that I am free to export it or it is an error to reload it
                        modRepo = "!!! does not exist !!!"
                        if action == 'export':
                            tags = ['update']
                        elif action == 'reload':
                            tags = ['error']

                    sign = ''
                    if not len(tags):
                        intRepo = modRepo
                        for fmt in ['%d %b %Y %H:%M', '%d/%m/%Y %H:%M']:
                            try:
                                intRepo = convertDateFormat(' '.join(modRepo.split()[:-1]), format_in=fmt, format_out='%Y %m %d %H %M')
                                break
                            except Exception:
                                pass
                        intTree = modTree
                        for fmt in ['%d %b %Y %H:%M', '%d/%m/%Y %H:%M']:
                            try:
                                intTree = convertDateFormat(' '.join(modTree.split()[:-1]), format_in=fmt, format_out='%Y %m %d %H %M')
                                break
                            except Exception:
                                pass

                        if intRepo < intTree:
                            sign = '<'
                            if action == 'export':
                                tags = ['update']
                            elif action == 'reload':
                                tags = ['warning']
                        elif intRepo > intTree:
                            sign = '>'
                            if action == 'export':
                                tags = ['warning']
                            elif action == 'reload':
                                tags = ['update']
                        else:
                            sign = '='
                            tags = ['dubious']

                    # in all cases but when you are reloading and there is an error
                    if not (action == 'reload' and 'error' in tags):
                        moduleList.insert(
                            '',
                            tk.END,
                            '%s###%s' % (item, tmpAvailableModulesList[avMod]['path']),
                            text=treeText(item, False, -1, False),
                            tags=tuple(tags),
                            values=(moduleDict[item]['ID'], modRepo, sign, modTree),
                        )
                        # remember existing selection
                        for module in modules:
                            if item == module.split('###')[0]:
                                try:
                                    moduleList.selection_set('%s###%s' % (item, tmpAvailableModulesList[avMod]['path']))
                                except tk.TclError:
                                    pass
                        # set selection
                        if doSelect:
                            if withinModule == item:
                                try:
                                    moduleList.selection_set('%s###%s' % (item, tmpAvailableModulesList[avMod]['path']))
                                except tk.TclError:
                                    pass

                    # remember this directory for next time
                    OMFITaux['lastModulesDir'] = moduledirSelectorVariable.get().split('@')[0].strip()

        work_repo = [repo]

        def update_gits(what=None):
            try:
                repo = OMFITgit(moduledirSelectorVariable.get().split('@')[0].strip())
            except Exception:
                if moduledirSelectorVariable.get().split('@')[0].strip().endswith('modules'):
                    try:
                        repo = OMFITgit(moduledirSelectorVariable.get().split('@')[0].strip() + os.sep + '..')
                    except Exception:
                        # not a valid git repository
                        self.remoteSelectorVariable.set('')
                        self.branchSelectorVariable.set('')
                        repo = None
                else:
                    # not a valid git repository
                    self.remoteSelectorVariable.set('')
                    self.branchSelectorVariable.set('')
                    repo = None

            # cleanup spaces
            self.remoteSelectorVariable.set(self.remoteSelectorVariable.get().strip())
            self.branchSelectorVariable.set(self.branchSelectorVariable.get().strip())

            # if remote is empty then also must be branch
            if what == 'remote' and '/' in self.remoteSelectorVariable.get():
                self.branchSelectorVariable.set('/'.join(self.remoteSelectorVariable.get().split('/')[1:]))
                self.remoteSelectorVariable.set(self.remoteSelectorVariable.get().split('/')[0])
            elif what == 'remote' or not self.remoteSelectorVariable.get():
                self.branchSelectorVariable.set('')

            # create a clone repository unless remoteSelector and branchSelector are empty
            if repo is not None and self.branchSelectorVariable.get() or self.remoteSelectorVariable.get():
                work_repo[0] = repo.clone()
                if work_repo[0].is_OMFIT_source():
                    remotes = work_repo[0].get_remotes()
                    if 'gafusion' not in remotes:
                        work_repo[0]('remote add gafusion git@github.com:gafusion/OMFIT-source.git', verbose=True)
                    if 'vali' not in remotes:
                        work_repo[0]('remote add vali git@vali.gat.com:OMFIT/OMFIT.git', verbose=True)
                    if OMFIT['MainSettings']['SERVER']['GITHUB_username'] not in remotes and work_repo[0].is_OMFIT_source():
                        work_repo[0](
                            'remote add %s git@github.com:%s/OMFIT-source.git'
                            % (OMFIT['MainSettings']['SERVER']['GITHUB_username'], OMFIT['MainSettings']['SERVER']['GITHUB_username']),
                            verbose=True,
                        )
                    if self.remoteSelectorVariable.get() not in remotes:
                        work_repo[0](
                            'remote add %s git@github.com:%s/OMFIT-source.git'
                            % (self.remoteSelectorVariable.get(), self.remoteSelectorVariable.get()),
                            verbose=True,
                        )
                # make sure to always start from scratch if working on the clone
                work_repo[0]('reset --hard HEAD')
            else:
                work_repo[0] = repo

            if work_repo[0] is None:
                remoteSelector.configure(state='disabled')
                branchSelector.configure(state='disabled')
                moduledirSelector.configure(state='readonly')
                ckformat.configure(state='disabled')
            else:
                # Possible reasons for disabling export:
                # 1. Does the user have write permission on the work_repo and the repo is not handled by git?
                # 2. Has a remote been selected, but not a branch?
                if action == 'export':
                    ok_write_local = bool(
                        len(
                            OMFITmodule.directories(
                                directories=[work_repo[0].git_dir], checkIsWriteable=True, return_associated_git_branch=False
                            )
                        )
                    )
                    if not ok_write_local or (self.remoteSelectorVariable.get() and not self.branchSelectorVariable.get()):
                        moduleList.unbind('<Return>')
                        moduleList.unbind('<Double-1>')
                        moduleList.unbind('<P_Enter>')
                        qb.configure(state='disabled')
                        db.configure(state='disabled')
                        ckformat.configure(state='disabled')
                    else:
                        moduleList.bind('<Return>', lambda event: onReturn())
                        moduleList.bind('<Double-1>', lambda event: onReturn())
                        moduleList.bind('<KP_Enter>', lambda event: onReturn())
                        qb.configure(state='normal')
                        db.configure(state='normal')
                        ckformat.configure(state='normal')

                    # force formatting when exporting directly to GitHub
                    if self.remoteSelectorVariable.get() or self.branchSelectorVariable.get():
                        self.omfit_format.set(True)
                        ckformat.configure(state='disabled')

                # set possible options for remote/branch GUI elements
                remoteSelector.configure(state='normal')
                remoteSelectorOptions = work_repo[0].get_remotes()
                if work_repo[0].is_OMFIT_source():
                    if 'gafusion' not in remoteSelectorOptions:
                        remoteSelectorOptions['gafusion'] = 'gafusion'
                    if 'vali' not in remoteSelectorOptions:
                        remoteSelectorOptions['vali'] = 'vali'
                    if OMFIT['MainSettings']['SERVER']['GITHUB_username'] not in remoteSelectorOptions and work_repo[0].is_OMFIT_source():
                        remoteSelectorOptions[OMFIT['MainSettings']['SERVER']['GITHUB_username']] = None
                if 'original_git_repository' not in remoteSelectorOptions:
                    remoteSelectorOptions['original_git_repository'] = None
                remoteSelectorOptions[''] = None
                remoteSelectorOptions = sorted(list(remoteSelectorOptions.keys()), key=lambda x: x.lower())
                remoteSelector.configure(values=tuple(remoteSelectorOptions))
                branchSelectorOptions = ['']
                if self.remoteSelectorVariable.get():
                    branchSelectorOptions = list(work_repo[0].get_branches(self.remoteSelectorVariable.get()).keys())
                    branchSelectorOptions = sorted(branchSelectorOptions, key=lambda x: x.lower())
                    branchSelector.configure(state=['readonly', 'normal'][int(action == 'export')])
                    moduledirSelector.configure(state='disabled')
                else:
                    branchSelector.configure(state='disabled')
                    moduledirSelector.configure(state='readonly')
                branchSelector.configure(values=tuple(branchSelectorOptions))
                if what:
                    if self.branchSelectorVariable.get():
                        if self.branchSelectorVariable.get() not in branchSelectorOptions:
                            tmp = work_repo[0].switch_branch_GUI(
                                branch='unstable', remote='origin', parent=top, title='Create new branch from', only_existing_branches=True
                            )
                            if tmp is None:
                                self.branchSelectorVariable.set('')
                                return
                        # switch branch (only need to check if branch is set, since if no remote, then work_repo[0]==repo)
                        work_repo[0].switch_branch(self.branchSelectorVariable.get(), self.remoteSelectorVariable.get())
            updateReloadExport(do_update_gits=False)

        def moduledirSelectorVariableGet():
            if self.branchSelectorVariable.get():
                directory = work_repo[0].git_dir
                if os.path.exists(work_repo[0].git_dir + os.sep + 'modules'):
                    directory = work_repo[0].git_dir + os.sep + 'modules'
                return directory + '  @  ' + self.remoteSelectorVariable.get() + '/' + self.branchSelectorVariable.get()
            else:
                return moduledirSelectorVariable.get()

        # find what module is the tree selection in
        self.force_selection(None)
        tmp = parseLocation(self.focusRoot)
        opts = []
        for k in range(2, len(tmp) + 1):
            opts.append(buildLocation(tmp[:k]))
        withinModule = None
        for k in opts[::-1]:
            if isinstance(eval(k), OMFITmodule):
                withinModule = k[5:]
                break

        # FORMAT
        if action == 'export':
            ckFrame = ttk.Frame(top)
            ckFrame.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            self.omfit_format = tk.BooleanVar()
            self.omfit_format.set(True)
            ckformat = ttk.Checkbutton(ckFrame, text="Enforce OMFIT Python style formatting", variable=self.omfit_format)
            ckformat.state(['!alternate'])  # removes color box bg indicating user has not clicked it, which may confuse people
            ckformat.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)

        btFrame = ttk.Frame(top)
        btFrame.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        # QUICK
        if action == 'export':
            qb = ttk.Button(btFrame, text="Export only module scripts and settings", command=lambda: onReturn(quickAction=True))
            qb.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)

        # DETAILED
        db = ttk.Button(
            btFrame, text=["Reload module", "Detailed module export"][action == 'export'], command=lambda: onReturn(quickAction=False)
        )
        db.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5)
        if action == 'export':
            ttk.Label(frm, text='', justify=tk.LEFT, anchor=tk.W).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            ttk.Label(frm, text='LEGEND:', justify=tk.LEFT, anchor=tk.W).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            ttk.Label(
                frm,
                text=' * Saved version is older than tree version (or it\'s a new module! Yaye!)',
                justify=tk.LEFT,
                anchor=tk.W,
                foreground='chartreuse3',
                font=OMFITfont('bold'),
            ).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            ttk.Label(
                frm,
                text=' * Saved version is up to date, however, tree version may have been modified since',
                justify=tk.LEFT,
                anchor=tk.W,
                foreground='dodger blue',
                font=OMFITfont('bold'),
            ).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            ttk.Label(
                frm,
                text=' * Saved version is newer than tree version',
                justify=tk.LEFT,
                anchor=tk.W,
                foreground='orange2',
                font=OMFITfont('bold'),
            ).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            ttk.Label(
                frm,
                text=" * Module ID has not been set in ['SETTINGS']['MODULE']['ID']",
                justify=tk.LEFT,
                anchor=tk.W,
                foreground='indianRed1',
                font=OMFITfont('bold'),
            ).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            qb.focus()

        elif action == 'reload':
            ttk.Label(frm, text='', justify=tk.LEFT, anchor=tk.W).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            ttk.Label(frm, text='LEGEND:', justify=tk.LEFT, anchor=tk.W).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            ttk.Label(
                frm,
                text=' * Tree version is older than saved version',
                justify=tk.LEFT,
                anchor=tk.W,
                foreground='chartreuse3',
                font=OMFITfont('bold'),
            ).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            ttk.Label(
                frm,
                text=' * Tree version is up to date, however, tree version may have been modified since',
                justify=tk.LEFT,
                anchor=tk.W,
                foreground='dodger blue',
                font=OMFITfont('bold'),
            ).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            ttk.Label(
                frm,
                text=' * Tree version is newer than saved version',
                justify=tk.LEFT,
                anchor=tk.W,
                foreground='orange2',
                font=OMFITfont('bold'),
            ).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            ttk.Label(
                frm,
                text=" * Module ID has not been set in ['SETTINGS']['MODULE']['ID'] or module was never saved",
                justify=tk.LEFT,
                anchor=tk.W,
                foreground='indianRed1',
                font=OMFITfont('bold'),
            ).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            db.focus()

        moduleList.bind('<Return>', lambda event: onReturn())
        moduleList.bind('<Double-1>', lambda event: onReturn())
        moduleList.bind('<KP_Enter>', lambda event: onReturn())
        top.bind('<Escape>', lambda event: onEscape())

        # add entries and select (pretend that the branch entered)
        updateReloadExport(doSelect=withinModule is not None, do_update_gits='branch')

        top.protocol("WM_DELETE_WINDOW", top.destroy)
        top.update_idletasks()
        tk_center(top, self.rootGUI)
        top.deiconify()
        top.wait_window(top)

    def updateCWD(self):
        OMFIT.updateCWD()
        self.update_treeGUI()

    def quit_clean(self, force=False):
        if self.lockSave:
            printi('Wait for ' + self.lockSave + ' to finish')
            return

        if not force:
            if OMFIT.filename != '':
                answer = dialog(
                    title="Save before quitting?",
                    message="Save changes to project\n\n" + OMFIT.projectName() + "\n\nbefore quitting?",
                    answers=['Yes', 'No', 'Cancel'],
                    parent=self.rootGUI,
                )
            else:
                answer = dialog(
                    title="Save before quitting?",
                    message="Save changes to new project before quitting?",
                    answers=['Yes', 'No', 'Cancel'],
                    parent=self.rootGUI,
                )
            if answer == 'Cancel':
                return
            elif answer == 'Yes':
                save_success = self.saveOMFITas(background=False)
                if not save_success:
                    return

        pyplot.close('all')
        OMFITx.CloseAllGUIs()
        OMFITx._harvest_experiment_info()

        try:
            # this is in a try/except because in some extreme circumstances
            # there can be errors if the system cannot allocate memory
            kill_subprocesses()
        except Exception as _excp:
            printe('Cannot kill subprocesses: ' + repr(_excp))

        # delete files in two stages
        # 1. delete files of this session
        # 2. then ask for deepclean if there are remaining files
        printi('Deleting temporary files and directories... ' + OMFITsessionDir)
        onlyRunningCopy = OMFIT.quit()

        printi('Only OMFIT running? ' + str(onlyRunningCopy))
        if onlyRunningCopy and len(glob.glob(OMFITtmpDir + os.sep + '*')):
            message = (
                """
Temporary OMFIT directory is not clean:

{OMFITtmpDir}

Make sure this is the last working copy of OMFIT on {uname}

Purge all OMFIT temporary files?""".format(
                    OMFITtmpDir=OMFITtmpDir, uname=platform.uname()[1]
                )
            ).strip()
            if 'Yes' == dialog(title="Cleanup ?", message=message, answers=['Yes', 'No'], parent=self.rootGUI):
                printi('Deleting all temporary files and directories... ' + OMFITtmpDir)
                OMFIT.quit(deepClean=True)
        if hasattr(self.terminal, 'started') and self.terminal.started.poll() is None:
            self.terminal.started.kill()
        OMFITaux['console'].stop()
        sys.exit()

    def loadOMFITregression(self):
        """
        Method to load OMFIT regression cases

        :return: path to the regression script
        """
        tmp = OMFITx.LoadFileDialog(
            directory=os.sep.join([OMFITsrc, '..', 'regression']),
            pattern='*.py',
            master=OMFITaux['rootGUI'],
            serverPicker='localhost',
            transferRemoteFile=True,
            focus='filterFiles',
        ).how
        if tmp:
            filename = tmp[0]
            dev_acceptable = os.access(filename, os.W_OK) and not os.path.exists(os.sep.join([os.path.split(filename)[0], '..', 'public']))
            OMFIT[os.path.splitext(os.path.split(filename)[1])[0]] = OMFITpythonTest(
                filename, modifyOriginal=OMFIT['MainSettings']['SETUP']['developer_mode_by_default'] & dev_acceptable
            )
            self.update_treeGUI()
            return filename

    # ------------------
    # Plots and figures
    # ------------------
    def selectFigure(self, action='forward'):
        tmp = matplotlib._pylab_helpers.Gcf.get_all_fig_managers()

        if not len(tmp):
            return

        if action == 'lift':
            for k, fig in enumerate(tmp):
                fig.window.deiconify()
                fig.window.lift()
            fig.window.focus_set()

        elif action == 'lower':
            for k, fig in enumerate(tmp):
                fig.window.lower()
                fig.window.withdraw()
            self.rootGUI.lift()
            self.rootGUI.focus_force()

        elif action in ['forward', 'reverse']:
            if action == 'reverse':
                tmp.reverse()

            sortByNumber = lambda tmp=tmp: tmp.canvas.figure.number
            tmp.sort(key=sortByNumber)

            kk = None
            for k, fig in enumerate(tmp):
                fig.window.lower()
                if pyplot.gcf().number == fig.canvas.figure.number:
                    kk = k

            if kk != None:
                if action == 'forward' and kk < len(tmp) - 1:
                    fig = tmp[kk + 1]
                elif action == 'reverse' and kk > 0:
                    fig = tmp[kk - 1]
                else:
                    fig = tmp[kk]
                pyplot.figure(fig.canvas.figure.number)
                fig.window.lift()
                fig.window.focus_force()

    @_lock_OMFIT_preferences
    def run_or_plot(self, defaultVarsGUI=False):
        if isinstance(self.linkToFocus, OMFITmodule):
            if self.linkToFocus.defaultGUI is None:
                printw(
                    'Default GUI has not been assigned in %s'
                    % OMFITx.absLocation("root['SETTINGS']['MODULE']['defaultGUI']", self.linkToFocus)
                )
                return
            try:
                self.linkToFocus = eval(OMFITx.absLocation(self.linkToFocus.defaultGUI, self.linkToFocus))
            except Exception as _excp:
                raise OMFITexception('Default GUI could not be found!: %s' % repr(_excp))
            self.runLinkToFocus(update_selection=False, defaultVarsGUI=defaultVarsGUI)

        elif isinstance(self.linkToFocus, OMFITmdsValue):
            self.quickPlotF(defaultVarsGUI=defaultVarsGUI)

        elif isinstance(self.linkToFocus, _OMFITpython) or isinstance(self.linkToFocus, CollectionsCallable):
            self.runLinkToFocus(defaultVarsGUI=defaultVarsGUI)

        elif isinstance(self.linkToFocus, OMFITmainSettings):
            OMFIT['scratch']['__preferencesGUI__'].run()

        elif isinstance(self.linkToFocus, OMFITnamelist):
            OMFIT['scratch']['__namelistGUI__'].run(nml=self.linkToFocus, singleGUIinstance=False)

        elif isinstance(self.linkToFocus, omfit_classes.omfit_latex.OMFITlatex):
            OMFIT['scratch']['__latexGUI__'].run(tex=self.linkToFocus, singleGUIinstance=False)

        else:
            self.quickPlotF(defaultVarsGUI=defaultVarsGUI)

    @_lock_OMFIT_preferences
    def quickPlotF(self, edit=False, interp='spline', defaultVarsGUI=False):
        self.force_selection()
        linkToFocus = self.linkToFocus
        if isinstance(self.linkToFocus, OMFITmdsValue):
            linkToFocus = self.linkToFocus.data()
        if isinstance(linkToFocus, str):
            printi(linkToFocus)
        plotting = False
        if hasattr(self.linkToFocus, 'plot'):
            pyplot.figure()
            plotting = True
        elif isinstance(linkToFocus, np.ndarray) and ('s' not in linkToFocus.dtype.char.lower()):
            dim_non_deg = np.sum(np.array(linkToFocus.shape) > 1)
            if dim_non_deg in [1, 2, 3]:
                if len(pyplot.gcf().get_children()) > 1:
                    pyplot.figure()
                plotting = True
            else:
                printi('Data array has %d non degenerate dimensions. You can ' 'only plot 1D, 2D and 3D arrays.' % dim_non_deg)
        if plotting:
            self.quickPlot(edit=edit, interp=interp, defaultVarsGUI=defaultVarsGUI)
            # if nothing has been plotted close the figure which was just opened
            if len(pyplot.gcf().get_children()) < 2:
                pyplot.close(pyplot.gcf())
        elif isinstance(self.linkToFocus, OMFITmdsValue):
            self.update_treeGUI_and_GUI()
        elif isinstance(self.linkToFocus, OMFITtoksearch):
            self.update_treeGUI()

    @_lock_OMFIT_preferences
    def quickPlot(self, edit=False, interp='spline', defaultVarsGUI=False):
        self.force_selection()
        self.quickPlotX(action='check')

        linkToFocus = self.linkToFocus
        if isinstance(self.linkToFocus, OMFITmdsValue):
            linkToFocus = self.linkToFocus.data()

        plotting = False
        added = []
        if hasattr(self.linkToFocus, 'plot'):
            if isinstance(self.linkToFocus, _OMFITpython):
                self.linkToFocus.plot(defaultVarsGUI=defaultVarsGUI)
            else:
                execGlobLoc(
                    """
tmp=function_arguments(%s.plot)
kwargs=tmp[1]
if tmp[3]:
    kwargs['**kw']={}
kw=defaultVars(**kwargs)
%s.plot(**kw)
                """
                    % (self.focusRoot, self.focusRoot),
                    {'defaultVarsGUI': defaultVarsGUI},
                    {},
                    {},
                    {},
                )
            plotting = True

        elif isinstance(linkToFocus, np.ndarray) and ('s' not in linkToFocus.dtype.char.lower()):
            # first prepare the data
            tmpx, tmpy, tmpz = [None] * 3
            tmpxName, tmpyName, tmpzName = [None] * 3

            # MDSValue
            if isinstance(self.linkToFocus, OMFITmdsValue):
                tmp = np.squeeze(self.linkToFocus.data())
                tmpx = self.linkToFocus.dim_of(0)
                tmpxName = self.linkToFocus.units_dim_of(0)
                if len(tmp.shape) == 1:
                    tmpyName = self.linkToFocus.units()
                if len(tmp.shape) >= 2:
                    tmpy = self.linkToFocus.dim_of(1)
                    tmpyName = self.linkToFocus.units_dim_of(1)
                if len(tmp.shape) == 3:
                    tmpz = self.linkToFocus.dim_of(2)
                    tmpzName = self.linkToFocus.units_dim_of(2)
                    tmp = tmp.T

            # np array
            else:
                tmp = np.squeeze(self.linkToFocus)

            # override x/y/z
            if self.x is not None:
                tmpx = self.x.copy()
                tmpxName = self.xName
            if self.y is not None:
                tmpy = self.y.copy()
                tmpyName = self.yName
            if self.z is not None:
                tmpz = self.y.copy()
                tmpzName = self.zName

            if tmpx is not None:
                tmpx = np.squeeze(tmpx)
            if tmpy is not None:
                tmpy = np.squeeze(tmpy)
            if tmpz is not None:
                tmpz = np.squeeze(tmpz)

            if self.normPlotAxis.get():
                if len(tmp.shape) >= 1:
                    tmpx = np.linspace(0, 1, tmp.shape[0])
                    tmpxName = 'Normalized'
                if len(tmp.shape) >= 2:
                    tmpy = np.linspace(0, 1, tmp.shape[0])
                    tmpyName = 'Normalized'
                    tmpx = np.linspace(0, 1, tmp.shape[1])
                    tmpxName = 'Normalized'
                if len(tmp.shape) == 3:
                    tmpz = np.linspace(0, 1, tmp.shape[0])
                    tmpzName = 'Normalized'
                    tmpy = np.linspace(0, 1, tmp.shape[1])
                    tmpyName = 'Normalized'
                    tmpx = np.linspace(0, 1, tmp.shape[2])
                    tmpxName = 'Normalized'

            # now do the actual plotting
            # 1D
            if len(tmp.shape) == 1:

                kw = {'marker': '.', 'label': self.focusRoot}
                if tmpx is not None and tmpx.size == tmp.size:
                    if is_uncertain(tmp):
                        if len(tmp) > 20:
                            uband(tmpx, tmp, **kw)
                        else:
                            uerrorbar(tmpx, tmp, **kw)
                    else:
                        pyplot.plot(tmpx, tmp, **kw)
                    pyplot.xlabel(tmpxName)
                else:
                    if is_uncertain(tmp):
                        if len(tmp) > 20:
                            uband(list(range(len(tmp))), tmp, **kw)
                        else:
                            uerrorbar(list(range(len(tmp))), tmp, **kw)
                    else:
                        pyplot.plot(tmp, **kw)
                    pyplot.xlabel('Array element')
                pyplot.ylabel(self.focusRoot)

                if edit == 1:
                    if tmpx is not None and tmpx.size == tmp.size:
                        DragPoints(self.focusRoot, 'OMFIT' + tmpxName)
                    else:
                        DragPoints(self.focusRoot)

                elif edit > 1:
                    if tmpx is not None and tmpx.size == tmp.size:
                        editProfile(self.focusRoot, 'OMFIT' + tmpxName, n=edit, func=interp, showOriginal=False)
                    else:
                        editProfile(self.focusRoot, n=edit, func=interp, showOriginal=False)

                plotting = True

            # 2D
            elif len(tmp.shape) == 2:

                if tmpx is not None and tmpy is not None and tmpx.size == tmp.shape[0] and tmpy.size == tmp.shape[1]:
                    pyplot.gca().set_aspect('equal')

                if tmpy is None:
                    tmpyName = 'Array element'
                    tmpy = np.arange(tmp.shape[0])

                if tmpx is None:
                    tmpxName = 'Array element'
                    tmpx = np.arange(tmp.shape[1])

                CS = image(tmpx, tmpy, tmp, interpolation=['nearest', 'bilinear'][0])
                if not np.all(tmp.T == tmp.flat[0]):
                    pyplot.contour(tmpx, tmpy, tmp, 21, colors='k')
                colorbar(CS, label=self.focusRoot)

                if tmpxName is not None:
                    pyplot.xlabel(tmpxName)

                if tmpyName is not None:
                    pyplot.ylabel(tmpyName)

                plotting = True

            # 3D
            elif len(tmp.shape) == 3:
                if tmpz is None:
                    tmpzName = 'Array element'
                    tmpz = np.arange(tmp.shape[2])

                if tmpy is None:
                    tmpyName = 'Array element'
                    tmpy = np.arange(tmp.shape[1])

                if tmpx is None:
                    tmpxName = 'Array element'
                    tmpx = np.arange(tmp.shape[0])

                View3d(
                    tmp,
                    coords=(tmpx, tmpy, tmpz),
                    axes=pyplot.gca(),
                    xlabels=[tmpxName, tmpyName, tmpzName],
                    label=parseBuildLocation(self.focusRoot)[-1],
                )

                plotting = True

        if plotting:
            pyplot.draw()
            matplotlib._pylab_helpers.Gcf.figs[pyplot.gcf().number].window.lift()
            self.update_treeGUI()

        elif isinstance(self.linkToFocus, OMFITmdsValue):
            self.update_treeGUI()

    def quickPlotX(self, action='check'):
        if action == 'check':
            return
        self.force_selection()
        if action == 'clearX':
            self.x = None
            self.xName = None
            printt('X cleared')
        elif action == 'clearY':
            self.y = None
            self.yName = None
            printt('Y cleared')
        elif action == 'clearZ':
            self.z = None
            self.zName = None
            printt('Z cleared')
        elif action == 'clear':
            self.x = None
            self.xName = None
            self.y = None
            self.yName = None
            self.z = None
            self.zName = None
            printt('X, Y, Z cleared')
        else:
            linkToFocus = self.linkToFocus
            if isinstance(self.linkToFocus, OMFITmdsValue):
                linkToFocus = self.linkToFocus.data()
            tmp = np.squeeze(linkToFocus).copy()
            if action == 'setX':
                self.x = tmp
                self.xName = self.focus
                printt(self.focus + ' set as X')
            elif action == 'setY':
                self.y = tmp
                self.yName = self.focus
                printt(self.focus + ' set as Y')
            elif action == 'setZ':
                self.z = tmp
                self.zName = self.focus
                printt(self.focus + ' set as Z')

    # ------------------
    # TREE GUI AUX
    # ------------------
    def configMainSettings(self, updateUserSettings=False, restore=''):
        OMFIT.addMainSettings(updateUserSettings, restore)
        if len(restore):
            self.update_treeGUI_and_GUI()

    def deployOMFITobj(self, pickleObject=False):
        self.force_selection()

        if hasattr(self.linkToFocus, 'deployGUI') and not pickleObject:
            self.linkToFocus.deployGUI()
            self.update_treeGUI()

        else:
            fd = OMFITx.SaveFileDialog(master=self.rootGUI, directory=OMFITaux['lastBrowsedDirectory'])
            if fd.how is None or not len(fd.how):
                return
            if not is_localhost(fd.how[1]):
                raise NotImplementedError('Saving a file to a remote server is not yet supported.')
            filename = fd.how[0]
            if not os.path.exists(os.path.split(filename)[0]):
                os.makedirs(os.path.split(filename)[0])
            OMFITaux['lastBrowsedDirectory'] = os.path.split(filename)[0]

            if not pickleObject and isinstance(self.linkToFocus, np.ndarray) and isinstance(self.linkToFocus.dtype, list):
                from matplotlib import mlab

                mlab.rec2csv(self.linkToFocus, filename, delimiter=' ')

            elif not pickleObject and isinstance(self.linkToFocus, xarray.Dataset):
                exportDataset(self.linkToFocus, filename)

            elif not pickleObject and isinstance(self.linkToFocus, np.ndarray):
                np.savetxt(filename, self.linkToFocus)

            else:
                pickleObject = True
                with open(filename, 'wb') as f:
                    pickle.dump(self.linkToFocus, f, pickle.OMFIT_PROTOCOL)

            if pickleObject:
                pickleObject = 'as pickle'
            else:
                pickleObject = ''

            printi('Deployed object to `%s` %s' % (filename, pickleObject))

    def reloadOMFITobj(self):
        # ideally OMFITobjects should re-initialize themeselves when .load() is called
        # however this may not always be the case...
        # So, here we force re-initialization.
        # This is preferred in place of .clear() because:
        #   1. not all OMFITobjects also inherit from SortedDict
        #   2. some objects actually set some keys,values pairs at initialization time
        orig_modify = self.linkToFocus.OMFITproperties.get('modifyOriginal', False)
        self.linkToFocus.OMFITproperties['modifyOriginal'] = True
        self.linkToFocus.__init__(self.linkToFocus.filename, **self.linkToFocus.OMFITproperties)
        self.linkToFocus.load()
        self.linkToFocus.modifyOriginal = orig_modify
        self.update_treeGUI_and_GUI()

    def closeOMFITobj(self):
        self.linkToFocus.close()
        self.update_treeGUI_and_GUI()

    def openFile(self, what=None, thisObject=None):

        # handle strings
        if isinstance(thisObject, str) and os.path.exists(os.path.abspath(os.path.expandvars(os.path.expanduser(thisObject)))):
            filename = os.path.abspath(os.path.expandvars(os.path.expanduser(thisObject)))
            linkToFocus = None

        # handle OMFIT objects
        else:
            if thisObject is None:
                linkToFocus = self.linkToFocus
            else:
                linkToFocus = thisObject

            if isinstance(linkToFocus, OMFITpath):
                if isinstance(linkToFocus, OMFITascii) and not isinstance(linkToFocus, _OMFITpython) and hasattr(linkToFocus, 'load'):
                    dont_prompt = OMFIT['MainSettings']['SETUP']['GUIappearance'].setdefault('dont_prompt_edit_ascii', False)
                    if not dont_prompt:
                        ok, prompt = dialog(
                            title="Warning!",
                            message="Editing this file may have\n"
                            "no effect in OMFIT until choosing\n"
                            "'Reload from file'\n"
                            "from the dropdown menu",
                            icon='warning',
                            answers=['Ok'],
                            parent=self.rootGUI,
                            options={'Don\'t prompt again': dont_prompt},
                        )
                        OMFIT['MainSettings']['SETUP']['GUIappearance']['dont_prompt_edit_ascii'] = prompt["Don't prompt again"]
                if isinstance(linkToFocus, _OMFITpython):
                    linkToFocus._tidy()
                    linkToFocus._create_backup_copy()
                else:
                    linkToFocus.save()
                if what == 'original' and hasattr(linkToFocus, 'originalFilename'):
                    filename = linkToFocus.originalFilename
                else:
                    filename = linkToFocus.filename
            else:
                return

        if os.path.exists(filename):

            if os.path.isdir(filename):
                ext = 'directory'
            else:
                ext = os.path.splitext(filename)[1]
                if len(ext):
                    ext = ext[1:].lower()
                if ext not in OMFIT['MainSettings']['SETUP']['EXTENSIONS'] or (
                    ext == 'py'
                    and ext in OMFIT['MainSettings']['SETUP']['EXTENSIONS']
                    and OMFIT['MainSettings']['SETUP']['EXTENSIONS'][ext] in [None, 'IDLE', 'idle']
                ):

                    if isinstance(linkToFocus, OMFITascii):
                        editor = OMFIT['MainSettings']['SETUP']['editor']
                        if '%s' not in editor:
                            editor = editor + ' %s'
                        subprocess.Popen(editor % "'" + filename + "'", shell=True)
                        return

                    printi(
                        "Program to handle "
                        + ext.upper()
                        + " files is not explicitly defined. Fallback on OMFIT['MainSettings']['SETUP']['EXTENSIONS']['DEFAULT']"
                    )
                    ext = 'default'

            program = OMFIT['MainSettings']['SETUP']['EXTENSIONS'][ext]

            if program != None:
                if '%s' not in program:
                    program = program + ' %s'
                printi('Opening file with command: ' + program % "'" + filename + "'")
                subprocess.Popen(program % "'" + filename + "'", shell=True)
                return
            else:
                dialog(
                    title="Error !",
                    message="Setup your program-extension association in\n OMFIT['MainSettings']['SETUP']['EXTENSIONS'][" + ext + "]",
                    icon='error',
                    answers=['Ok'],
                    parent=self.rootGUI,
                )

    def runLinkToFocus(self, update_selection=True, defaultVarsGUI=False):
        if update_selection:
            self.force_selection()
        if isinstance(self.linkToFocus, _OMFITpython):
            # remember what is the last script which was executed
            if isinstance(self.linkToFocus, OMFITpythonTask) or isinstance(self.linkToFocus, OMFITpythonPlot):
                self.lastRunScriptFromGUI = self.focusRoot
            # execute the scirpt
            if isinstance(self.linkToFocus, OMFITpythonPlot):
                OMFITx.manage_user_errors(self.linkToFocus.plotFigure, defaultVarsGUI=defaultVarsGUI)
            else:
                OMFITx.manage_user_errors(self.linkToFocus, defaultVarsGUI=defaultVarsGUI)
        elif isinstance(self.linkToFocus, CollectionsCallable):
            self.linkToFocus()
            self.update_treeGUI()

    def reRunlastRun(self):
        """
        run last script
        """
        try:
            if isinstance(eval(self.lastRunScriptFromGUI), _OMFITpython):
                pass
        except Exception:
            self.lastRunScriptFromGUI = None
            return
        OMFITx.manage_user_errors(eval(self.lastRunScriptFromGUI))

    def showError(self):
        """
        display last error in full
        """
        if OMFITaux['lastUserError'] is not None:
            for k in range(len(OMFITaux['lastUserError'])):
                printe(OMFITaux['lastUserError'][k], end='')

    def showExecDiag(self):
        """
        display execution diagram
        """

        def printMe(tmp, depth):
            for child in tmp:
                filename = re.sub('__console__.py', '', os.path.split(child['filename'])[1])
                printi('* ' * (depth + 1) + " %s %3.3fs [%s]" % (filename, child['time'], sizeof_fmt(child['memory'])))
                printMe(child['child'], depth + 1)

        printi('\nExecution diagram:\n------------------')
        from omfit_classes.omfit_python import ExecDiagPtr

        printMe(ExecDiagPtr, 0)

    # ------------------
    # AUX
    # ------------------
    def sort(self):
        self.force_selection()
        if not isinstance(self.linkToFocus, dict):
            return
        comments = False
        for item in list(self.linkToFocus.keys()):
            if re.match(hide_ptrn, str(item)):
                comments = True
                break
        if not comments or 'Yes' == dialog(
            title="Sort ?",
            message="This node contains some hidden entries. Do you want to continue with sorting?",
            answers=['Yes', 'No'],
            parent=self.rootGUI,
        ):
            self.linkToFocus.sort()
        self.update_treeGUI()

    def clipboard(self, what='location'):
        self.force_selection()

        if len(self.focus):

            def simplify_location(tmp):
                tmp = re.sub("^OMFIT\['MainSettings'\]", 'MainSettings', tmp)
                tmp = re.sub("^OMFIT\['scratch'\]", 'MainScratch', tmp)
                return tmp

            # COPY
            if what in ['location', 'root', 'value', 'S3', 'tip']:
                self.rootGUI.selection_own()
                self.rootGUI.clipboard_clear()
                self.rootGUI.copiedName = self.focusRootRepr
                self.rootGUI.copiedWhat = what

                if what == 'location':
                    tmp = self.focusRootRepr
                    tmp = simplify_location(tmp)
                    printt('Copied location: ' + tmp)

                elif what == 'root':
                    tmp = locationFromRoot(self.focusRootRepr)
                    if tmp.startswith("OMFIT['commandBox']") or tmp.startswith("OMFIT['scriptsRun']") and len(parseLocation(tmp)) > 2:
                        tmp = buildLocation(parseLocation(tmp)[2:])
                    tmp = simplify_location(tmp)
                    printt('Copied location: ' + tmp)

                elif what == 'tip':
                    tmp = repr(parseLocation(self.focusRootRepr)[-1])
                    printt('Copied tip: ' + tmp)

                elif what == 'value':
                    tmp = repr(self.linkToFocus)
                    printt('Copied value: ' + tmp)

                elif what == 'S3':
                    self.linkToFocus.deploy(OMFIT['MainSettings']['SETUP']['email'] + '_' + 'clipboard', s3bucket='omfit')
                    printt('Copied object to global clipboard')

                if what != 'S3':
                    self.rootGUI.clipboard_append(tmp, type='STRING')
                    self.rootGUI.clipboard_append(tmp, type='PRIMARY')

            # PASTE S3
            elif what == 'pasteS3':
                printt('Pasted from global clipboard to location ' + self.focusRootRepr)
                tmp = OMFITobject_fromS3(OMFIT['MainSettings']['SETUP']['email'] + '_' + 'clipboard', s3bucket='omfit')
                buildLocation(parseLocation(self.focusRoot)[:-2])[parseLocation(self.focusRoot)[-1]] = tmp
                self.update_treeGUI_and_GUI()

            # PASTE
            else:
                if len(self.rootGUI.copiedName):
                    try:
                        eval(self.rootGUI.copiedName)
                    except Exception:
                        printt('Could not paste since ' + self.focusRootRepr + ' does not exist anymore!')
                        self.rootGUI.copiedName = ''
                        self.rootGUI.copiedWhat = ''
                        return

                # PASTE inside of a dictionary
                tmp = self.focusRoot
                if 'Inside' in what:
                    if not isinstance(self.linkToFocus, dict):
                        printt('Could not paste inside since ' + self.focusRootRepr + ' is not a dictionary')
                        return
                    else:
                        tmp = self.focusRoot + parseBuildLocation([parseBuildLocation(self.rootGUI.copiedName)[-1]])

                if 'paste' in what and len(self.rootGUI.copiedName):
                    printt('Pasted ' + self.rootGUI.copiedName + ' to location ' + tmp)
                    tmp = parseLocation(tmp)
                    eval(buildLocation(tmp[:-1]))[tmp[-1]] = copy.deepcopy(eval(self.rootGUI.copiedName))
                    self.update_treeGUI_and_GUI()

    @virtualKeys
    def force_selection(self, event=None):
        # focus and selection are two different things
        # focus is what makes things happen, whereas selection is the highligting
        # the purpose of force_selection is to make the two coincide

        self.focus = self.treeGUI.force_selection(event)

        if len(self.focus):
            if len(self.attributes):
                loc = parseLocation(self.focus)
                if len(loc) == 2:
                    loc = loc[1]
                else:
                    loc = buildLocation(loc[1:])
                self.focusRoot = self.attributes['focusRoot'] + '.' + loc
                self.focusRootRepr = self.attributes['focusRootRepr'] + '.' + loc
            else:
                # handle representation of ODS paths in OMFIT
                self.focusRoot = self.focusRootRepr = 'OMFIT' + self.focus
                ods_start, ods_end, path = self.is_part_of_ods()
                if ods_start is not None:
                    self.focusRootRepr = buildLocation(
                        path[:ods_start] + [str(omas.omas_utils.l2i(path[ods_start:ods_end]))]
                    ) + buildLocation([''] + path[ods_end:])
            self.linkToFocus = eval(self.focusRoot)
        else:
            self.focusRoot = self.focusRootRepr = ''
            self.linkToFocus = None

        if self.searchLocation is not None:
            self.browser_label_name.set('Search ' + self.searchLocation)
        else:
            self.browser_label_name.set('Browser : ')
            self.browser_label_text.set(self.focusRootRepr)

        if len(self.focus) and self.searchLocation is not None:
            if 'queryMatchFileContent_action' in self.treeGUI.item(self.focus)['tags']:
                query = eval('re.compile(r".*' + self.browserSearch + '.*",re.I)')
                with open(self.linkToFocus.filename, 'r') as _f:
                    lines = _f.read().split('\n')
                n = str(len(str(len(lines))))
                printi('-=' * 3 + ' ' + self.focusRootRepr + ' ' + '=-' * 3)
                for k, line in enumerate(lines):
                    if re.search(query, line):
                        tag_print(('%' + n + 'd:%s') % (k, line), tag='HIST')

    def keepAlive(self, old_message=None):
        """
        * Keep track of memory usage

        * Print message to the terminal at least once every 10 minutes, so to keep possible ssh connection alive

        * If running in a Docker environment, generate a tk update event every 10 seconds to avoid an X11 timeout error

        :param old_message: message string to be ignored
        """
        # memory usage
        mem = memuse(as_bytes=True)

        # message to print to console
        message = 'OMFIT'
        message += ' - ' + (OMFIT.projectName() if OMFIT.projectName() else 'unsaved')
        message += ' - PID %d' % os.getpid()
        message += ' - RAM ' + sizeof_fmt(mem, format='%.2f', unit='GB')
        message += ' - ' + utils_base.now()

        # history of memory usage
        self.memory_history.append((time.time(), mem))
        self.memory.set(sizeof_fmt(self.memory_history[-1][-1]).ljust(20))

        # print to terminal at least every 10 minutes
        if old_message is None or message[:-1] != old_message[:-1]:
            printt(message)
        old_message = message

        # refresh every minute
        if os.path.exists(os.sep + '.dockerenv'):
            # update_idletasks to avoid an X11 timeout error when running OMFIT through Docker
            self.rootGUI.update_idletasks()
            # refresh every 10 seconds
            self.rootGUI.after(10 * 1000, lambda: self.keepAlive(old_message=old_message))
        else:
            self.rootGUI.after(60 * 1000, lambda: self.keepAlive(old_message=old_message))

    def is_part_of_ods(self):
        """
        returns whether tree GUI selection is part of an ODS or not

        :return: tuple with indexes indicating start and end of ODS in path, as well as the parsed path
        """
        path = parseLocation(self.focusRoot)

        ods_start = None
        ods_end = len(path)
        for k in range(1, len(path)):
            if ods_start is None and isinstance(eval(buildLocation(path[:k])), ODS):
                ods_start = k
            elif ods_start is not None and not isinstance(eval(buildLocation(path[: k + 1])), ODS):
                ods_end = k + 1
                break
        return ods_start, ods_end, path


# --------------------------------
# --------------------------------
# --------------------------------
try:
    OMFITaux['rootGUI'] = tk.Tk()
except Exception as _excp:
    if 'no display name and no $DISPLAY environment variable' in repr(_excp):
        printe('Original error:')
        printe(repr(_excp))
        raise RuntimeError('You must use `ssh -Y <server>` to get the OMFIT GUI')
    elif "connect to display" in repr(_excp):
        for k in range(9):
            try:
                os.environ['DISPLAY'] = re.sub(':[0-9]', f':{k}', os.environ['DISPLAY'])
                OMFITaux['rootGUI'] = tk.Tk()
                print('Running on DISPLAY ' + os.environ['DISPLAY'])
                break
            except Exception:
                if k < 8:
                    pass
                else:
                    raise _excp
    else:
        raise _excp

# set GUI appearance
_GUIappearance = OMFIT['MainSettings']['SETUP']['GUIappearance']
ttk_style = ttk.Style()
if _GUIappearance.get('theme', 'default') in ttk_style.theme_names():
    ttk_style.theme_use(_GUIappearance.get('theme', 'default'))
else:
    ttk_style.theme_use('default')

# ttk themes
try:
    OMFITaux['rootGUI'].tk.eval('source {src}/extras/graphics/themes/pkgIndex.tcl'.format(src=OMFITsrc))
except Exception as _excp:
    print('Error loading ttk themes:' + repr(_excp))

# read fonts based on users setings
OMFITfont()  # ensure defaults are there
if not isinstance(_GUIappearance['GUI_font_size'], int):
    _GUIappearance['GUI_font_size'] = _defaultFont['size']
    OMFIT.addMainSettings(updateUserSettings=True)
if not isinstance(_GUIappearance['GUI_font_family'], str):
    _GUIappearance['GUI_font_family'] = re.sub(r'\\', '', _defaultFont['family'])
    OMFIT.addMainSettings(updateUserSettings=True)
if not isinstance(_GUIappearance['commandBox_font_size'], int):
    _GUIappearance['commandBox_font_size'] = _defaultFont['size']
    OMFIT.addMainSettings(updateUserSettings=True)
if not isinstance(_GUIappearance['commandBox_font_bold'], bool):
    _GUIappearance['commandBox_font_weight'] = _defaultFont['weight']
    OMFIT.addMainSettings(updateUserSettings=True)


def _apply_default_font(_defaultFont, _GUIappearance):
    # override default fonts based on users setings
    _defaultFont['size'] = _GUIappearance['GUI_font_size']
    _defaultFont['size2'] = _GUIappearance['commandBox_font_size'] - _GUIappearance['GUI_font_size']
    if _GUIappearance['commandBox_font_bold']:
        _defaultFont['weight2'] = 'bold'
    else:
        _defaultFont['weight2'] = 'normal'
    _defaultFont['family'] = tkStringEncode(_GUIappearance['GUI_font_family'])
    # OMFITaux['rootGUI'].option_add("*Font", _defaultFont['family'] + ' ' + str(_defaultFont['size']) + ' ' + _defaultFont['weight'])
    ttk.Style().configure('.', font=_defaultFont['family'] + ' ' + str(_defaultFont['size']) + ' ' + _defaultFont['weight'])


# this logic is here because different versions of TK require different string escaping
# and here we try to automatically detect which one is which
try:
    _apply_default_font(_defaultFont, _GUIappearance)
    ttk.Label(text="test no issues")
except tk.TclError as _excp:
    try:
        os.environ['OMFIT_ESCAPE_TK_SPACES'] = str(abs(int(os.environ.get('OMFIT_ESCAPE_TK_SPACES', '1')) - 1))
        _apply_default_font(_defaultFont, _GUIappearance)
        ttk.Label(text="test no issues")
    except tk.TclError:
        os.environ['OMFIT_ESCAPE_TK_SPACES'] = str(abs(int(os.environ.get('OMFIT_ESCAPE_TK_SPACES', '1')) - 1))
        raise _excp

# modify treeview style
OMFITaux['rootGUI'].tk.eval("ttk::style map Treeview -background [list selected #4B6886] -foreground [list selected white]")
OMFITaux['rootGUI'].tk.eval("ttk::style map Row -background [list selected #4B6886] -foreground [list selected white]")
OMFITaux['rootGUI'].tk.eval("ttk::style map Item -background [list selected #4B6886] -foreground [list selected white]")

# modify default appearance of tkInter openFile dialogue
try:
    OMFITaux['rootGUI'].tk.eval("catch {tk_getOpenFile foo bar}")
    OMFITaux['rootGUI'].tk.eval("catch {tk_getSaveFile foo bar}")
    OMFITaux['rootGUI'].tk.eval("set ::tk::dialog::file::showHiddenVar 0")
    OMFITaux['rootGUI'].tk.eval("set ::tk::dialog::file::showHiddenBtn 1")
except Exception:
    pass

# handle all the ttk style setting - live updates
OMFITx.update_gui_theme()

OMFITaux['rootGUI'].withdraw()
_sg = [min([screen_geometry()[0], 1600]), min([screen_geometry()[1], 1200])]
if _sg[0] * 0.618 > _sg[1]:
    _sgw = int(_sg[1] / 0.618 * 7 / 8.0)
    _sgh = _sg[1] * 7 / 8.0
else:
    _sgw = _sg[0] * 7 / 8.0
    _sgh = int(_sg[0] * 0.618 * 7 / 8.0)
OMFITaux['rootGUI'].geometry('%dx%d' % (_sgw, _sgh))

OMFITgui(OMFITaux['rootGUI'])
if safe_eval_environment_variable('OMFIT_NO_CONSOLE', False):
    OMFITaux['console'].stop()
if safe_eval_environment_variable('OMFIT_MIRROR_CONSOLE', False):
    OMFITaux['console'].mirror = True

# replace help method
omfit_classes.omfit_python.help._buildGUI(OMFITaux['rootGUI'], topLevel=True)
helpTip.widget = OMFITaux['rootGUI']

# raise window to the top
OMFITaux['rootGUI'].wm_attributes("-topmost", 1)
OMFITaux['rootGUI'].update()
OMFITaux['rootGUI'].wm_attributes("-topmost", 0)

# icon
_img = tk.PhotoImage(file=OMFITsrc + '/../docs/source/images/OMFIT_logo.gif')
OMFITaux['rootGUI'].tk.call('wm', 'iconphoto', OMFITaux['rootGUI']._w, _img)

# center OMFIT GUI to active screen
OMFITaux['rootGUI'].geometry('%dx%d' % (_sgw, _sgh))

# show GUI
OMFITaux['rootGUI'].deiconify()

# ---------------------
# Add licenses
# ---------------------
OMFITlicenses['OMFIT'] = License(
    'OMFIT', OMFITsrc + os.sep + '..' + os.sep + 'LICENSE.rst', web_address='http://form.omfit.io', rootGUI=OMFITaux['rootGUI']
)

# ---------------------
# Last time OMFIT was run
# ---------------------
with open(OMFITsettingsDir + os.sep + 'OMFITlastRun.txt', 'w') as _f:
    _f.write(str(time.time()))

# ---------------------
# apply startup plot style
# ---------------------
if 'PlotAppearance' in OMFIT['MainSettings']['SETUP'] and 'startup_style' in OMFIT['MainSettings']['SETUP']['PlotAppearance']:
    try:
        pyplot.style.use(OMFIT['MainSettings']['SETUP']['PlotAppearance']['startup_style'])
    except IOError as _excp:
        printw("OMFIT['MainSettings']['SETUP']['PlotAppearance']['startup_style'] " + str(_excp))

# ---------------------
# deal with extra arguments (used also to execute regression cases)
# ---------------------
def _atStartupChecks():
    # check licenses
    try:
        OMFITlicenses['OMFIT'].check()
    except LicenseException as e:
        printt(repr(e))
        sys.exit()

    # check that preferences are ok
    checks = ["OMFIT['MainSettings']['SETUP']", "OMFIT['MainSettings']['SERVER']"]
    showPreferences = False
    for check in checks:
        for k in traverse(eval(check)):
            try:
                value = eval(check + k)
                if evalExpr(value) is None:
                    printe('%s is None' % (check + k))
                    showPreferences = True
            except Exception as _excp:
                printe('Issue when evaluating %s: %s' % (check + k, repr(_excp)))
                showPreferences = True
    # check that at least some username is set
    usernames = [OMFIT['MainSettings']['SERVER'][item] for item in OMFIT['MainSettings']['SERVER'] if item.endswith('_username')]
    if not ''.join(usernames):
        showPreferences = True
        printe('All usernames are empty! -- perhaps you want to setup at least one')

    # show preferences windows
    if showPreferences:
        OMFIT['scratch']['__preferencesGUI__'].run()


if len(sys.argv) <= 1:
    _top = splash(OMFITaux['rootGUI'], onCloseFunction=_atStartupChecks)

else:
    from omfit_parse_args import omfit_parse_args, nice_script_args

    args = omfit_parse_args()
    _tmp = nice_script_args(args)

    def dothis():

        # open the specified project
        if args.project:
            print('Loading project: %s' % args.project)
            OMFITaux['GUI']._loadOMFITproject(args.project)

        # load the specified modules
        if args.module or args.Module:
            OMFIT.availableModules()
            dev_mode = False
            if args.module:
                modules_list = args.module
            else:
                dev_mode = True
                modules_list = args.Module
            print('\nLoading module(s): %s' % ', '.join(map(str, modules_list)))
            for mod in modules_list:
                OMFIT.loadModule(mod, developerMode=dev_mode)
            OMFITaux['GUI'].update_treeGUI()

        # run the specified GUI script
        if args.scriptFile:
            print('\nRunning script: %s' % args.scriptFile)
            OMFIT['__userScript__'] = OMFITpythonTask(args.scriptFile, modifyOriginal=True)
            OMFIT['__userScript__'].run(**_tmp)

        # execute the specified commands
        if args.command:
            printi('\nExecuting command(s):')
            for cmd in args.command:
                tag_print(re.sub(';\ *', '\n', cmd), tag='INFO')
                exec(cmd)
            OMFITaux['GUI'].update_treeGUI()

    OMFITaux['rootGUI'].after(1000, dothis)

# ---------------------
# start the console
# Done as late as possible to ensure that potential errors that may prevent GUI from starting are at least displayed in the terminal
# ---------------------
OMFITaux['console'].start()

# ---------------------
# start Tk loop
# ---------------------
while True:
    try:
        OMFITaux['rootGUI'].mainloop()
    except KeyboardInterrupt:
        pass
