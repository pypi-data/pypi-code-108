if '__tmpstyle__' not in MainScratch:
    MainScratch['__tmpstyle__'] = SortedDict(sorted=True)
    if not os.path.exists(os.sep.join([matplotlib.get_configdir(), 'stylelib'])):
        os.makedirs(os.sep.join([matplotlib.get_configdir(), 'stylelib']))

OMFITx.CheckBox("MainScratch['__tmpstyle__']['__showfigure__']", 'Show sample figure', default=True, updateGUI=True)
if MainScratch['__tmpstyle__']['__showfigure__']:
    OMFITx.CheckBox(
        "MainScratch['__tmpstyle__']['__samplefigmultipanel__']", 'Show several subplots on sample figure', default=True, updateGUI=True
    )

# =========================================================
# sample figure (please, keep it simple for speeds's sake)
# =========================================================

if MainScratch['__tmpstyle__']['__showfigure__']:
    try:
        x = linspace(0, 1, 11)
        y = linspace(0, 1, 101)
        ybig = y * 10 ** 3  # Make y bigger to test x10^3 axis multiplier stuff
        fig = OMFITx.Figure(toolbar=False, returnFigure=True, figsize=matplotlib.rcParams['figure.figsize'])
        ax = []
        if MainScratch['__tmpstyle__']['__samplefigmultipanel__']:
            for k in range(1, 4):
                ax.append(fig.add_subplot(2, 2, k))
                ax[-1].set_xlabel('$x$')
                ax[-1].set_ylabel('$y$')
            ax.append(fig.add_subplot(2, 2, 4, projection='3d'))
            ax[-1].set_xlabel('$x$')
            ax[-1].set_ylabel('$y$')
            ax[-1].set_zlabel('$z$')
            fig.suptitle('Suptitle')
        else:
            ax.append(fig.add_subplot(1, 1, 1))
            ax[-1].set_xlabel('$x$')
            ax[-1].set_ylabel('$y$')

        # ax0
        uband(ybig, uarray(cos(y * 5 * pi) * y, 1.0 / (1.0 + y)), ax=ax[0], label='uncertain')
        ax[0].plot(ybig, cos(y * 5 * pi) * y + 1, label='certain')  # This plot will have a multiplier (x10^3) with default style
        for k in range(7):
            ax[0].plot(ybig, cos(y * 5 * pi) * y + 2 + k)
        ax[0].legend()
        ax[0].set_title(r'title$_\perp$')
        if MainScratch['__tmpstyle__']['__samplefigmultipanel__']:
            # ax1
            X, Y = meshgrid(x, y)
            CS = ax[1].contourf(cos(X) + cos(Y))
            fig.colorbar(CS, ax=ax[1])
            # ax2
            ax[2].scatter(rand(5) + 10 ** 3, rand(5), c=rand(5))  # Add 10**3 to test offset settings
            ax[2].errorbar(rand(5) + 10 ** 3, rand(5), rand(5))  # This plot will have an offset (+10^3) with default style
            # ax3
            theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
            z = np.linspace(-2, 2, 100)
            r = z ** 2 + 1
            x = r * np.sin(theta)
            y = r * np.cos(theta)
            ax[3].plot(x, y, z, label='parametric curve')
            ax[3].set_title('title')
    except Exception as _excp:
        printe(repr(_excp))

# =========================================================


def load_style(location):
    if eval(location):
        eval_location = eval(location).split(os.sep)[-1].split(os.extsep)[0]
        printi('Loaded user style: ' + eval_location)
        MainScratch['__tmpstyle__'].update(matplotlib.style.core.library[eval_location])
        for item in MainScratch['__tmpstyle__']:
            if isinstance(MainScratch['__tmpstyle__'][item], str):
                MainScratch['__tmpstyle__'][item] = str(MainScratch['__tmpstyle__'][item])

        MainScratch['__tmpstyle__']['__load__'] = ''
        MainScratch['__tmpstyle__']['__stylename__'] = str(eval_location)
        MainScratch['__tmpstyle__']['__entries__'] = matplotlib.style.core.library[eval_location].keys()
        update_properties_list()
    style.reload_library()


def save_style(event=None):
    def strstr(inv):
        if isinstance(inv, str):
            return str(inv)
        return inv

    name = MainScratch['__tmpstyle__']['__stylename__']
    printi('Save user style: ' + os.sep.join([matplotlib.get_configdir(), 'stylelib', name + '.mplstyle']))
    with open(os.sep.join([matplotlib.get_configdir(), 'stylelib', name + '.mplstyle']), 'w') as f:
        for item in MainScratch['__tmpstyle__']:
            if not item.startswith('__'):
                value = str(list(map(strstr, tolist(MainScratch['__tmpstyle__'][item])))).strip('[]()')
                tmp = item + ' : ' + re.sub("[#'\"]", '', value)
                printi('- ' + tmp)
                f.write(tmp + '\n')
    style.reload_library()


def delete_style(location):
    if eval(location):
        printi('Deleted user style: ' + eval(location))
        os.remove(eval(location))
        MainScratch['__tmpstyle__']['__delete__'] = ''
    style.reload_library()


def update_properties_list(**kw):
    for item in MainScratch['__tmpstyle__']['__entries__']:
        if item not in MainScratch['__tmpstyle__']:
            MainScratch['__tmpstyle__'][item] = matplotlib.rcParamsDefault[item]
    for item in MainScratch['__tmpstyle__'].keys():
        if not item.startswith('__') and item not in MainScratch['__tmpstyle__']['__entries__']:
            del MainScratch['__tmpstyle__'][item]

    MainScratch['__tmpstyle__']['__entries__'] = []
    for item in MainScratch['__tmpstyle__']:
        if not item.startswith('__') and item not in MainScratch['__tmpstyle__']['__entries__']:
            MainScratch['__tmpstyle__']['__entries__'].append(item)

    matplotlib.rcParams.update(matplotlib.rcParamsDefault)
    stl = copy.deepcopy(MainScratch['__tmpstyle__'])
    for item in stl.keys():
        if item.startswith('__'):
            del stl[item]
    pyplot.style.use(stl)
    OMFITx.UpdateGUI()


# =========================================================

OMFITx.TitleGUI('Plot styles editor')

# load
styles = {}
for item in sorted(style.available, key=lambda x: x.lower()):
    if os.path.exists(os.sep.join([matplotlib.get_configdir(), 'stylelib', item + '.mplstyle'])):
        styles[' (User) ' + item] = os.sep.join([matplotlib.get_configdir(), 'stylelib', item + '.mplstyle'])
    elif os.path.exists(os.sep.join([OMFITsrc, 'extras', 'styles', item + '.mplstyle'])):
        styles['(OMFIT) ' + item] = os.sep.join([OMFITsrc, 'extras', 'styles', item + '.mplstyle'])
    else:
        styles[item] = item
styles[''] = ''
OMFITx.ComboBox("MainScratch['__tmpstyle__']['__load__']", styles, 'Add style', default='', postcommand=load_style)

# edit
OMFITx.Separator()

OMFITx.ListEditor(
    "MainScratch['__tmpstyle__']['__entries__']",
    matplotlib.rcParams.keys(),
    lbl='plot properties',
    default=None,
    unique=True,
    ordered=True,
    postcommand=update_properties_list,
    updateGUI=False,
)

for item in MainScratch['__tmpstyle__']:
    if not item.startswith('__'):
        OMFITx.Entry("MainScratch['__tmpstyle__'][%s]" % repr(item), item, postcommand=update_properties_list, updateGUI=False)

# save
OMFITx.Separator()
OMFITx.Entry("MainScratch['__tmpstyle__']['__stylename__']", 'Style name', default='', check=lambda x: not len(re.findall(r'\s', x)))
OMFITx.Button('Save user style', save_style, updateGUI=True)

# delete
OMFITx.Separator()
options = SortedDict(sorted=True)
options.insert(0, '', '')
for filename, stl in matplotlib.style.core.iter_style_files(os.sep.join([matplotlib.get_configdir(), 'stylelib'])):
    options[stl] = filename
OMFITx.ComboBox(
    "MainScratch['__tmpstyle__']['__delete__']", options, 'Delete user style', default='', postcommand=delete_style, updateGUI=True
)
