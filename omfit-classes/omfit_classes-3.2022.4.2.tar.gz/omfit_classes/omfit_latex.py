try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

from omfit_classes.omfit_base import OMFITtree, OMFITexpression
from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.omfit_path import OMFITpath
from omfit_classes.omfit_namelist import OMFITnamelist
from omfit_classes import OMFITx

__all__ = ['OMFITlatex']


class OMFITlatex(OMFITtree):
    """
    Class used to manage LaTeX projects in OMFIT.

    For testing, please see: samples/sample_tex.tex, samples/sample_bib.bib, samples/placeholder.jpb, and
    samples/bib_style_d3dde.bst .

    :param main: string
        Filename of the main .tex file that will be compiled.

    :param mainroot: string
        Filename without the .tex extension. Leave as None to let this be determined
        automatically. Only use this option if you have a confusing filename that breaks the automatic determinator,
        like blah.tex.tex (hint: try not to give your files confusing names).

    :param local_build: bool
        Deploy pdflatex job locally instead of deploying to remote server specified in SETTINGS

    :param export_path: string
        Your LaTeX project can be quickly exported to this path if it is defined. The project can be
        automatically exported after build if this is defined. Can be defined later in the settings namelist.

    :param export_after_build: bool
        Automatically export after building if export_path is defined. Can be updated later in the settings namelist.

    :param hide_style_files: bool
        Put style files in hidden __sty__ sub tree in OMFIT (they still deploy to top level folder on disk)

    :param debug: bool
        Some data will be saved to OMFIT['scratch']
    """

    def __init__(
        self,
        root=None,
        main='main.tex',
        mainroot=None,
        local_build=True,
        export_path=None,
        export_after_build=False,
        hide_style_files=True,
        debug=False,
        **kw,
    ):
        printd('Initializing omfit_latex instance with main file = {:}'.format(main), topic='latex')
        OMFITtree.__init__(self, **kw)
        self.latex_debug = debug

        # Set up basic definitions and structure
        self.ascii_types = ['tex', 'txt', 'bbl', 'bib', 'aux', 'log', 'bst', 'sh', 'dat']
        self.aux_types = ['bbl', 'aux', 'log', 'out', 'backup', 'blg', 'gz']
        self.style_types = ['cls', 'sty', 'clo', 'bst']
        self.no_load = ['OMFIT_run_command.sh', 'OMFITlatex_settings.dat']
        self.pdflatex_flags = '-halt-on-error'  # This string is inserted between pdflatex and command line arguments
        self.hide_style_files = hide_style_files  # Not in settings because ugly to change after init.
        self.__mainroot = mainroot
        self.__export_path = export_path
        self.__main = main
        self.__export_after_build = export_after_build
        self.__hide_style_files = hide_style_files

        # Define sub-folder to isolate LaTeX stuff from other I/O from the module to avoid accidentally picking up
        # unrelated files
        self.latex_folder = 'OMFITlatex_{}'.format(id(self))
        printd('OMFITlatex self.latex_folder = {}'.format(self.latex_folder), topic='latex')

        # Figure out the parent module root
        self.root = OMFIT if root is None else root

        # Deal with servers an directories
        self.lookup_dirs_and_servers()
        if local_build:
            self.server = 'localhost'
            self.tunnel = ''
            self.remotedir = SERVER['localhost']['workDir']

        # Load settings and sub-folders
        self.prepare_settings()
        printd('Done with OMFITlatex initialization', topic='latex')
        return

    def prepare_settings(self):

        main = self.__main
        mainroot = self.__mainroot
        export_path = self.__export_path
        export_after_build = self.__export_after_build
        hide_style_files = self.__hide_style_files

        # Prepare settings
        try:
            self.setdefault('settings', OMFITnamelist('OMFITlatex_settings.dat'))
        except OSError:
            # This can happen if the class is being initialized while OMFIT is still loading.
            # The project load sequence will put settings in for us, so we can skip this part.
            printd('Unable to prepare OMFITlatex settings at this time.', topic='latex')
            return

        printd('Preparing OMFITlatex settings...', topic='latex')

        # These sub-folders should also be loaded by the project if that's what's happening
        self['__aux__'] = OMFITtree()
        if hide_style_files:
            self['__sty__'] = OMFITtree()

        # Set up name of main file
        if main[-4:] != os.extsep + 'tex':
            self['settings']['main'] = main + os.extsep + 'tex'
        else:
            self['settings']['main'] = main

        # Main file is a path to a file on disk, not just a name: attempt to load existing project.
        if os.sep in self['settings']['main']:
            if os.path.exists(self['settings']['main']) and os.path.isfile(self['settings']['main']):
                # The attempt to load a project found a valid file
                printd('Given initial main file as input...', topic='latex')
                main_dir = os.path.split(self['settings']['main'])[0]
                self['settings']['main'] = os.path.split(self['settings']['main'])[1]
                if export_path is None:
                    export_path = main_dir

                self.grab_project(main_dir=main_dir, get_tex=True)

                printd(
                    'Loaded LaTeX project from main file: {:}, export_path = {:}'.format(self['settings']['main'], export_path),
                    topic='latex',
                )

            else:
                # User attempted to load an existing project, but the file was not valid.
                printw(
                    'Warning: could not load LaTeX project using file {:}. Please check path and try again.'.format(
                        self['settings']['main']
                    )
                )
                self['settings']['export_path'] = os.path.split(self['settings']['main'])[0]
                self['settings']['main'] = os.path.split(self['settings']['main'])[1]  # Reduce to filename w/o path

        # Set up root filename of main file
        if mainroot is None:
            self['settings']['mainroot'] = self['settings']['main'].split(os.extsep + 'tex')[0]
        else:
            self['settings']['mainroot'] = mainroot

        self['settings']['main'] = OMFITexpression("return_variable = parent['mainroot'] + '.tex'")
        self['settings']['outfile'] = OMFITexpression("return_variable = parent['mainroot'] + '.pdf'")
        self['settings']['export_path'] = export_path
        self['settings']['export_after_build'] = export_after_build
        self['settings']['default_build_sequence'] = 'full'
        self['settings']['default_clean_before_build'] = False
        printd('Done preparing OMFITlatex settings.', topic='latex')

    def lookup_dirs_and_servers(self, overwrite=False):
        """
        Looks up workdir, remotedir, tunnel, and server

        Tries to link to module or top-level settings to get information.

        :param overwrite: bool
            Overwrite existing attributes. Otherwise, attributes with valid definitions will not be updated.
        """

        printd('Looking up directory and server information...', topic='latex')
        # Link to module settings and define workdir, etc.
        try:
            module_settings = self.root['SETTINGS']
            _ = module_settings['SETUP']['workDir']
            _ = module_settings['REMOTE_SETUP']
        except (KeyError, TypeError):
            printd('  Drawing dir & server info from MainSettings...', topic='latex')
            ref_workdir = evalExpr(OMFIT['MainSettings']['SETUP']['workDir'])
            ref_remotedir = evalExpr(SERVER['default']['workDir'])
            tunnel = evalExpr(SERVER['default']['tunnel'])
            server = evalExpr(SERVER['default']['server'])
        else:
            printd('  Drawing dir & server info from parent module SETTINGS...', topic='latex')
            ref_workdir = evalExpr(module_settings['SETUP']['workDir'])
            ref_remotedir = evalExpr(module_settings['REMOTE_SETUP']['workDir'])
            tunnel = evalExpr(module_settings['REMOTE_SETUP']['tunnel'])
            server = evalExpr(module_settings['REMOTE_SETUP']['server'])

        printd(
            f'  Found ref_workdir = {repr(ref_workdir)}, ref_remotedir = {repr(ref_remotedir)}, '
            f'server = {repr(server)}, tunnel = {repr(tunnel)}',
            topic='latex',
        )
        # If workdir and remotedir are valid directories, extend them by adding the latex_folder
        if ref_workdir is None or isinstance(ref_workdir, NamelistName):
            # Not sure why it comes back as NamelistName sometimes, but it does.
            workdir = None
        else:
            workdir = ref_workdir + os.sep + self.latex_folder
        if ref_remotedir is None or isinstance(ref_workdir, NamelistName):
            remotedir = None
        else:
            remotedir = ref_remotedir + os.sep + self.latex_folder

        # If workdir and remotedir are missing, signal that we shouldn't trust tunnel and server
        if workdir is None and remotedir is None:
            printd(
                "Failed to find useful info about directories & servers. This can happen during project loading. ",
                topic='latex',
            )
            tunnel = server = None

        # Load data
        if (getattr(self, 'workdir', None) is None) or overwrite:
            self.workdir = workdir
            printd(f'  Set self.workdir = {self.workdir}', topic='latex')
        if (getattr(self, 'remotedir', None) is None) or overwrite:
            self.remotedir = remotedir
            printd(f'  Set self.remotedir = {self.remotedir}', topic='latex')
        if (getattr(self, 'tunnel', None) is None) or overwrite:
            self.tunnel = tunnel
            printd(f'  Set self.tunnel = {self.tunnel}', topic='latex')
        if (getattr(self, 'server', None) is None) or overwrite:
            self.server = server
            printd(f'  Set self.server = {self.server}', topic='latex')

    def __call__(self, **kw):
        return self.run(**kw)

    def grab_project(self, main_dir=None, get_tex=False):
        """
        Grabs project files during init or after build

        :param main_dir: string
            Directory with the files to gather

        :param get_tex: bool
            Gather .tex files as well (only recommended during init)
        """
        if main_dir is None:
            if self.workdir is None:
                self.lookup_dirs_and_servers()
            main_dir = self.workdir
        destination = self
        depth = 0

        def gp_loader(gp_dir, gp_destination=self, gp_depth=0):
            printd('Loading LaTeX project from {:} ...'.format(gp_dir), topic='latex')

            files = glob.glob(gp_dir + os.sep + '*')
            if gp_depth > 20:
                printw('Warning: grab project loader reached maximum recursion depth and aborted.')
                return

            for f in files:
                printd('   Load {}: {} ... '.format(os.path.split(f)[1], f), topic='latex')
                d1 = gp_destination
                if os.path.isdir(f):
                    # Is a directory, load contents
                    printd('    This is a directory (current recursion depth = {:})'.format(gp_depth), topic='latex')
                    f2 = os.path.split(f)[1]
                    gp_loader(gp_dir + os.sep + f2, d1.setdefault(f2, OMFITtree()), gp_depth + 1)
                else:
                    # Not a directory, load file
                    if os.path.splitext(f)[1].strip('.') in self.aux_types:
                        # Hide aux files in separate folder
                        printd('    This is an aux file. (recur depth = {})'.format(gp_depth), topic='latex')
                        d1 = d1.setdefault('__aux__', OMFITtree())
                    elif os.path.splitext(f)[1].strip('.') in self.style_types and self.hide_style_files:
                        # Hide style files in separate folder
                        printd('    This is an style file. (recur depth = {})'.format(gp_depth), topic='latex')
                        d1 = d1.setdefault('__sty__', OMFITtree())
                    elif os.path.split(f)[1] in self.no_load:
                        # Skip certain files
                        printd('    This file should be skipped. (recur depth = {})'.format(gp_depth), topic='latex')
                        continue
                    elif os.path.splitext(f)[1].strip('.') == 'tex':
                        if get_tex:
                            printd(
                                '    This is a tex file, and get_tex=True, so it will be gathered. ' '(recur depth = {})'.format(gp_depth),
                                topic='latex',
                            )
                        else:
                            printd(
                                '    This is a tex file, and get_tex=False, so it will be SKIPPED. ' '(recur depth = {})'.format(gp_depth),
                                topic='latex',
                            )
                            continue

                    else:
                        printd('    This is a regular file (recur depth = {})'.format(gp_depth), topic='latex')

                    try:
                        if os.path.splitext(f)[1].strip('.') in self.ascii_types:
                            d1[os.path.split(f)[1]] = OMFITascii(f)
                        else:
                            d1[os.path.split(f)[1]] = OMFITpath(f)
                    except OMFITexception:
                        printe('Could not load %s' % f)

            if not files:
                printd('    This folder appears to be empty: {:}'.format(gp_dir), topic='latex')

            return  # End of gp_loader()

        gp_loader(main_dir, destination, depth)
        return

    def export(self, export_path=None):
        """
        This is a wrapper for .deploy() that uses the export_path in settings by default.

        :param export_path: string
            The path to which files should be exported.
        """
        # from OMFITx import executable
        if self.workdir is None:
            self.lookup_dirs_and_servers()

        if export_path is None:
            export_path = self['settings']['export_path']

        if export_path is None:
            printe("Cannot export until export_path is defined. Please set self['settings']['export_path']")
        else:
            printi('Exporting OMFITlatex project to {:}...'.format(self['settings']['export_path']))
            printi(
                '   Note: this should happen automatically after building if export_path is set, \n'
                'but you can pass export_path to this function as a keyword to export to \n'
                'somewhere else without changing the default export location. Another \n'
                'advantage is that manual export only copies the essential files and not \n'
                'all the LaTeX aux and log files. You can turn off export_after_build. and \n'
                'just export manually.'
            )

            self.deploy(filename=export_path, updateExistingDir=True)

            # Cleanup hidden files
            command = '\n'.join(
                ['cd {:}'.format(export_path), 'rm -rf __aux__', 'mv __sty__/* .', 'rm -rf __sty__', 'rm -rf __*__', 'rm OMFITsave.txt']
            )
            OMFITx.executable(
                self.root,
                inputs=[],
                outputs=[],
                executable=command,
                clean=False,
                server='localhost',
                tunnel='',
                remotedir=self.workdir,
                workdir=self.workdir,
            )
        return

    def load_sample(self):
        """
        Loads sample LaTeX source files for use as a template, example, or test case
        """
        sample_path = os.path.abspath(os.sep.join([OMFITsrc, '..', 'samples', 'tex', ''])) + os.sep
        self.setdefault('figures', OMFITtree())['placeholder.jpg'] = OMFITpath('{:}figures/placeholder.jpg'.format(sample_path))
        self.setdefault('includes', OMFITtree())['include_me.tex'] = OMFITascii('{:}includes/include_me.tex'.format(sample_path))
        self['includes'].setdefault('subsubfolder_lol', OMFITtree())['subsubsub.tex'] = OMFITascii(
            '{:}includes/subsubfolder_lol/subsubsub.tex'.format(sample_path)
        )
        self['sample_tex.tex'] = OMFITascii('{:}sample_tex.tex'.format(sample_path))
        self['sample_bib.bib'] = OMFITascii('{:}sample_bib.bib'.format(sample_path))
        self['bib_style_d3dde.bst'] = OMFITascii('{:}bib_style_d3dde.bst'.format(sample_path))
        return

    def debug(self):
        """Prints info about the project."""
        len1 = 30  # Short length
        len2 = len1 * 2  # Long length
        form = '{{:{:}}} = {{:}}'.format(len1)
        print('=' * len2)
        print('Debug info for OMFITlatex class in omfit_latex.py')
        print('-' * len2)
        print(form.format('self.__class__.__name__', self.__class__.__name__))
        print(form.format("Main file, self['settings']['main']", self['settings']['main']))
        print(form.format("Expected output file, self['settings']['outfile']", self['settings']['outfile']))
        print(form.format('self.keys()', list(self.keys())))
        print(form.format('self.workdir', self.workdir))
        print('=' * len2)
        return

    def clear_aux(self):
        """Deletes aux files, like .log, .aux, .blg, etc."""
        self['__aux__'] = OMFITtree()
        return

    def build_clean(self):
        """Wrapper for build that calls clear_aux first and then calls build with clean keyword."""
        self.clear_aux()
        self.build(clean_before_build=True, sequence='full')
        return

    def build_pdflatex(self):
        """Wrapper for build that selects the pdflatex sequence."""
        self.build(sequence='pdflatex')
        return

    def build_bibtex(self):
        """Wrapper for build that selects the bibtex sequence."""
        self.build(sequence='bibtex')
        return

    def build_full(self):
        """Wrapper for build that selects the full seqeunce."""
        self.build(sequence='full')
        return

    def check_main_file(self):
        """
        Makes sure the file defined by self['settings']['main'] is present in inputs.
        Backup: check if self['settings']['mainroot'] might work.

        :return: bool
            main file is okay (self['settings']['main'] is present) or might be okay
            (self['settings']['mainroot'] is present).
        """
        if self['settings']['main'] in list(self.keys()):
            printd('Main file is present. Everything is okay.', topic='latex')
            return True
        else:
            printd('Main file not found. Checking for mainroot...', topic='latex')
            filenames = [self[k].filename.split(os.sep)[-1] for k in list(self.keys())]
            rootnames = [os.extsep.join(filename.split(os.extsep)[:-1]) for filename in filenames]
            printd('   File name roots (extensions removed): {:}'.format(rootnames), topic='latex')
            if self['settings']['mainroot'] in rootnames:
                printw('LaTeX warning: You may need to set the name of the main LaTeX file.')
                printd('mainroot was in rootnames, so this might be okay, or you might have a bad day.', topic='latex')
                return True
            else:
                printw('LaTeX warning: Main file name not present in inputs. LaTeX will not run!')
                return False

    def search_for_tex_files(self):
        """
        :return: List of .tex files in self
        """
        filenames = [self[k].filename.split(os.sep)[-1] for k in list(self.keys())]
        printd('  Searching, filenames = {:}'.format(filenames), topic='latex')
        tex_files = [filename for filename in filenames if filename.split(os.extsep)[-1].lower() == 'tex']
        printd('  Search result: tex_files = {:}'.format(tex_files), topic='latex')
        return tex_files

    def build(self, clean_before_build=None, sequence=None):
        """
        :param clean_before_build: bool
            clear temporary workDir before deploying; None pulls value from settings.
        :param sequence: string
            'full', 'pdflatex', 'bibtex', '2pdflatex'; None pulls value from settings.
        """

        printd('Building latex project ({:})...'.format(self['settings']['main']), topic='latex')

        if None in [self.workdir, self.remotedir, self.tunnel, self.server]:
            self.lookup_dirs_and_servers()
        if sequence is None:
            sequence = self['settings']['default_build_sequence']
        if clean_before_build is None:
            clean_before_build = self['settings']['default_clean_before_build']

        pdflatex_outputs = [
            self['settings']['mainroot'] + '.pdf',
            self['settings']['mainroot'] + '.aux',
            self['settings']['mainroot'] + '.log',
            self['settings']['mainroot'] + '.out',
        ]
        bibtex_outputs = [self['settings']['mainroot'] + '.bbl', self['settings']['mainroot'] + '.blg']

        if not self.check_main_file():
            tex_files = self.search_for_tex_files()
            if len(tex_files):
                self['settings']['mainroot'] = '.'.join(tex_files[0].split('.')[:-1])
                print('Main LaTeX file definition was invalid. Main file updated to be: {:}'.format(self['settings']['main']))
                printd("Update main file by changing ['settings']['mainroot']    (no extension)", topic='latex')
            else:
                printw('Could not find any .tex files; cannot automatically update main file.')

        # Define the main commands. Some sequences will repeat these commands.
        mov_command = 'mv %s{,.backup} || true' % self['settings']['outfile']
        bib_command = 'bibtex {:} || true'.format(self['settings']['mainroot'])
        tex_command = 'pdflatex {flags:} {args:}'.format(flags=self.pdflatex_flags, args=self['settings']['mainroot'])

        if sequence == 'pdflatex':
            # Commands for building LaTeX project (just one pass of pdflatex, for minor changes)
            latex_commands = ['echo "OMFIT is trying to build a latex project (one pass pdflatex)..."', mov_command, tex_command]
            outputs = pdflatex_outputs
        elif sequence == '2pdflatex':
            # Commands for building LaTeX project (two passes of pdflatex, for changes that don't affect bibliography)
            latex_commands = [
                'echo "OMFIT is trying to build a latex project (two pass pdflatex)..."',
                mov_command,
                tex_command,
                tex_command,
            ]
            outputs = pdflatex_outputs
        elif sequence == 'bibtex':
            # Commands for building LaTeX project (just bibtex, in case you want to go through the sequence manually)
            latex_commands = ['echo "OMFIT is trying to build a latex project (solo bibtex)..."', mov_command, bib_command]
            outputs = bibtex_outputs
        else:
            # Commands for building LaTeX project (full build) (this is the default if the if/elif statements all fail)
            latex_commands = [
                'echo "OMFIT is trying to build a latex project (FULL BUILD)..."',
                mov_command,
                tex_command,
                bib_command,
                tex_command,
                tex_command,
            ]
            outputs = pdflatex_outputs + bibtex_outputs

        # Make sure outputs exist so that OMFITx.executable doesn't fail if one of them isn't generated
        for output_file in outputs:
            latex_commands = ['touch {}'.format(output_file)] + latex_commands

        latex_commands = ['%s || exit %d' % (v, k + 1) for k, v in enumerate(latex_commands)]
        command = '\n'.join(latex_commands)

        inputs = [self[k] for k in list(self.keys()) if hasattr(self[k], 'filename') and self[k].filename]

        def extend_inputs_from_subfolder(folder, sub, e_inputs, e_outputs, pre='', depth=0):
            if depth > 20:
                printw('Maximum recursion depth reached in extend_inputs_from_subfolder(). Aborting...', topic='latex')
                return e_inputs, e_outputs

            if isinstance(folder[sub], OMFITtree):
                printd('  Checking subfolder {:} ... (recursion depth = {:})'.format(sub, depth), topic='latex')
                i2 = [
                    (
                        folder[sub][kk],
                        '{:}{:}{:}{:}'.format(pre, sub, os.sep, os.path.split(folder[sub][kk].filename)[1])
                        .replace('__aux__', '')
                        .replace('__sty__', ''),
                    )  # Prevent nested __aux__/__aux__/__aux__/...
                    for kk in list(folder[sub].keys())
                    if hasattr(folder[sub][kk], 'filename') and folder[sub][kk].filename
                ]
                e_inputs += i2
                e_outputs += [ii[1].replace('.tex', '.*') for ii in i2 if ii[1].endswith('.tex')]
                printd('   Added more files from subfolder {:}: {:}'.format(sub, i2), topic='latex')
                for kk in list(folder[sub].keys()):
                    e_inputs, e_outputs = extend_inputs_from_subfolder(folder[sub], kk, e_inputs, e_outputs, pre + sub + os.sep, depth + 1)
            return e_inputs, e_outputs

        for k in list(self.keys()):
            if k in ['__aux__', '__sty__']:
                # Special treatment; don't deploy an __aux__ folder but instead dump aux files into main folder.
                # Subfolders in __aux__ will not be supported nor should they exist.
                inputs += [
                    (self[k][m], os.path.basename(self[k][m].filename).replace(k, ''))
                    for m in list(self[k].keys())
                    if hasattr(self[k][m], 'filename') and self[k][m].filename
                ]
            else:
                inputs, outputs = extend_inputs_from_subfolder(self, k, inputs, outputs, '', 0)

        printd('Executing LaTeX commands, \n\n   inputs = \n{:} \n\n   outputs = \n{:}'.format(inputs, outputs), topic='latex')

        if self.latex_debug:
            oscratch = OMFIT['scratch'].setdefault('omfit_latex_test', OMFITtree())
            exa = oscratch.setdefault('executable_arguments', OMFITtree())
            exa['inputs'] = inputs
            exa['outputs'] = outputs
            exa['command'] = command

        OMFITx.executable(
            self.root,
            inputs=inputs,
            outputs=outputs,
            executable=command,
            clean=clean_before_build,
            server=self.server,
            tunnel=self.tunnel,
            remotedir=self.remotedir,
            workdir=self.workdir,
            ignoreReturnCode=False,
        )

        self.grab_project(main_dir=self.workdir)

        printd('Items in OMFITlatex project after build: {:}'.format(list(self.keys())), topic='latex')

        if self['settings']['export_path'] is not None and self['settings']['export_after_build']:
            self.export()
        return

    def run(self):
        """
        Shortcut for opening the output file. If the output file has not been generated yet, a build will be attempted.
        This lets the user easily open the output from the top level context menu for the OMFITlatex instance, which is
        convenient.
        """
        if self['settings']['outfile'] not in list(self.keys()):
            self.build()
        filename = self[self['settings']['outfile']]
        if OMFITaux['GUI'] is not None:
            OMFITaux['GUI'].openFile(thisObject=filename)
        else:
            program = OMFIT['MainSettings']['SETUP']['Extensions'].get('pdf', None)
            if program is not None:
                subprocess.Popen("{} '{}'".format(program, filename), shell=True)
            else:
                printe('Could not identify a program for opening PDF output. You can try to open the file manually:')
                print(filename)
        return

    def open_gui(self):
        OMFIT['scratch']['__latexGUI__'].run(tex=self, singleGUIinstance=False)
        return

    def __popup_menu__(self):
        def run_and_update(command):
            getattr(self, command)()
            OMFITaux['GUI'].update_treeGUI()

        return [
            ['LaTeX>controls...', self.open_gui],
            ['LaTeX>Build (default sequence)', lambda command='build': run_and_update(command)],
            ['LaTeX>Full Build (pdflatex, bibtex, pdflatex, pdflatex)', lambda command='build_full': run_and_update(command)],
            ['LaTeX>Clear aux files', lambda command='clear_aux': run_and_update(command)],
            ['LaTeX>Open PDF', self.run],
            ['LaTeX>Export project', self.export],
        ]
