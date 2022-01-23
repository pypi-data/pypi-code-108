defaultVars(tex=OMFITlatex('new_tex'), misc_label='Other')

try:
    OMFITx.TitleGUI(relativeLocations(tex)['OMFITlocationName'][-1])
except Exception:
    OMFITx.End()

tex_loc = relativeLocations(tex)['OMFITlocationName'][-1]

OMFITx.Entry(
    "{:}['settings']['mainroot']".format(tex_loc),
    'Main file name (no extension)',
    default='',
    help='If your main file is main.tex, enter "main". If this setting does not correspond to a valid .tex file, then '
    'it will be updated using the first .tex file found in the project. You can force an auto update by making '
    'this blank.',
)

OMFITx.ComboBox(
    "{:}['settings']['default_build_sequence']".format(tex_loc),
    ['full', '2pdflatex', 'pdflatex', 'bibtex'],
    'Build sequence',
    default='full',
    help='full = pdflatex, bibtex, pdflatex, pdflatex;\n' '2pdflatex = pdflatex, pdflatex;\n' 'pdflatex = pdflatex;\n' 'bibtex = bibtex;',
)

OMFITx.CheckBox(
    "{:}['settings']['default_clean_before_build']".format(tex_loc),
    'Clean before build',
    default=False,
    help='Clear temporary files from working directory and delete hidden aux files from OMFIT tree (in __aux__) before '
    'running build commands.',
)

OMFITx.Button('Build', tex.build)

OMFITx.Button('Open output', tex.run, help='Will order a build if output file is not detected.')

OMFITx.Separator()

OMFITx.Entry(
    "{:}['settings']['export_path']".format(tex_loc),
    'Export path',
    default='/tmp/omfit_latex_test/',
    help='This should be a string containing the path to use when exporting the LaTeX project.',
)

OMFITx.CheckBox(
    "{:}['settings']['export_after_build']".format(tex_loc),
    'Automatic export after build',
    default=False,
    help='Call the export command after every build.',
)

OMFITx.Button('Export project', tex.export, help='Deploys the project to the path defined above.')

OMFITx.Separator()
OMFITx.Separator()

OMFITx.Button('Print project/debugging info', tex.debug)

OMFITx.Button(
    'Load sample project', tex.load_sample, help='Loads the LaTeX project from samples for use as an example, template, or test case.'
)
