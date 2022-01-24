import logging
import subprocess
from contextlib import closing
from glob import glob
from pathlib import Path
from tempfile import TemporaryDirectory

import sphinx
from babel.messages.catalog import Catalog
from babel.messages.extract import extract, pathmatch
from babel.messages.pofile import write_po
from ocds_babel.extract import extract_codelist, extract_extension_metadata, extract_schema
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace, patch_docutils
from sphinx.util.osutil import cd

from ocdsextensionregistry import EXTENSION_VERSIONS_DATA, EXTENSIONS_DATA
from ocdsextensionregistry.cli.commands.base import BaseCommand

logger = logging.getLogger('ocdsextensionregistry')


class Command(BaseCommand):
    name = 'generate-pot-files'
    help = 'generates POT files (message catalogs) for versions of extensions'

    def add_arguments(self):
        self.add_argument('output_directory',
                          help='the directory in which to write the output')
        self.add_argument('versions', nargs='*',
                          help="the versions of extensions to process (e.g. 'bids' or 'lots==master')")
        self.add_argument('-v', '--verbose', action='store_true',
                          help='print verbose output')
        self.add_argument('--extensions-url', default=EXTENSIONS_DATA,
                          help="the URL of the registry's extensions.csv")
        self.add_argument('--extension-versions-url', default=EXTENSION_VERSIONS_DATA,
                          help="the URL of the registry's extension_versions.csv")
        self.add_argument('--versions-dir',
                          help="a directory containing versions of extensions")
        self.add_argument('-W', dest='warningiserror', action='store_true',
                          help='turn Sphinx warnings into errors')

    def handle(self):
        output_directory = Path(self.args.output_directory)

        if self.args.versions_dir:
            versions_directory = Path(self.args.versions_dir)

        # We simulate pybabel and sphinx-build commands. Variable names are chosen to match upstream code.

        # For sphinx-build, the code path is:
        #
        # * bin/sphinx-build calls main() in sphinx.cmd.build, which calls build_main(), which calls Sphinx(…).build(…)

        # https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-suppress_warnings
        warning_type = 'image.not_readable'

        kwargs = {
            # sphinx-build -E …
            'freshenv': True,
            # sphinx-build -D suppress_warnings=image.not_readable …
            'confoverrides': {
                'suppress_warnings': [warning_type],
            },
        }
        # These options are useful for debugging.
        if not self.args.verbose:
            # sphinx-build -q …
            kwargs['status'] = None
        if self.args.warningiserror:
            # sphinx-build -W …
            kwargs['warningiserror'] = True

        # For pybabel, the code path is:
        #
        # * bin/pybabel calls main() in babel.messages.frontend
        # * main() calls CommandLineInterface().run(sys.argv)
        # * CommandLineInterface() calls extract_messages(), which:
        #   1. Reads the input path and method map from command-line options
        #   2. Instantiates a catalog
        #   3. Calls extract_from_dir() in babel.messages.extract to extract messages
        #   4. extract_from_dir() calls check_and_call_extract_file() to find the method in the method map
        #   5. check_and_call_extract_file() calls extract_from_file() to open a file for extraction
        #   6. extract_from_file() calls extract() to extract messages
        #   7. Adds the messages to the catalog
        #   8. Writes a POT file

        options = {
            'headers': 'Title,Description,Extension',
            'ignore': 'currency.csv',
        }

        # 1. Reads the input path and method map from command-line options
        arguments = [
            # pybabel extract -F babel_ocds_codelist.cfg . -o $(POT_DIR)/$(DOMAIN_PREFIX)codelists.pot
            ('codelists.pot', [
                ('codelists/*.csv', extract_codelist, options),
            ]),
            # pybabel extract -F babel_ocds_schema.cfg . -o $(POT_DIR)/$(DOMAIN_PREFIX)schema.pot
            ('schema.pot', [
                ('*-schema.json', extract_schema, None),
                ('extension.json', extract_extension_metadata, None),
            ]),
        ]

        for version in self.versions():
            if self.args.versions_dir:
                download_dir = versions_directory / version.id / version.version
                if not download_dir.is_dir():
                    logger.warning(
                        'Not processing %s==%s (not in %s)', version.id, version.version, versions_directory
                    )
                    continue
                version.download_url = download_dir.as_uri()
            else:
                if not version.download_url:
                    logger.warning(
                        'Not processing %s==%s (no Download URL)', version.id, version.version
                    )
                    continue

            outdir = output_directory / version.id / version.version

            outdir.mkdir(parents=True, exist_ok=True)

            # See the `files` method of `ExtensionVersion` for similar code.
            with closing(version.zipfile()) as zipfile:
                names = zipfile.namelist()
                start = len(names[0])

                for output_file, method_map in arguments:
                    # 2. Instantiates a catalog
                    catalog = Catalog()

                    # 3. Calls extract_from_dir() in babel.messages.extract to extract messages
                    for name in names[1:]:
                        filename = name[start:]

                        # 4. extract_from_dir() calls check_and_call_extract_file()
                        for pattern, method, options in method_map:
                            if not pathmatch(pattern, filename):
                                continue

                            # 5. check_and_call_extract_file() calls extract_from_file()
                            with zipfile.open(name) as fileobj:
                                # 6. extract_from_file() calls extract() to extract messages
                                for lineno, message, comments, context in extract(method, fileobj, options=options):
                                    # 7. Adds the messages to the catalog
                                    catalog.add(message, None, [(filename, lineno)],
                                                auto_comments=comments, context=context)

                            break

                    # 8. Writes a POT file
                    if catalog:
                        with open(outdir / output_file, 'wb') as outfile:
                            write_po(outfile, catalog)

                # This section is equivalent to running:
                #
                # echo -e '.. toctree::\n   :hidden:\n\n   README' > index.rst
                # sphinx-build -v -b gettext -a -E -C -D extensions=myst_parser . outdir
                # msgcat outdir/*.pot
                with TemporaryDirectory() as srcdir:
                    infos = zipfile.infolist()
                    start = len(infos[0].filename)

                    for info in infos[1:]:
                        filename = info.filename[start:]
                        if filename == 'README.md':
                            # This avoids writing an unnecessary directory.
                            info.filename = filename
                            zipfile.extract(info, srcdir)
                            break

                    with cd(srcdir):
                        # Eliminates a warning, without changing the output.
                        with open('index.rst', 'w') as f:
                            f.write('.. toctree::\n   :hidden:\n\n   README')

                        # Sphinx's config.py pop()'s extensions.
                        # https://github.com/sphinx-doc/sphinx/issues/6848
                        kwargs['confoverrides']['extensions'] = ['myst_parser']

                        with patch_docutils(), docutils_namespace():
                            try:
                                # sphinx-build -b gettext $(DOCS_DIR) $(POT_DIR)
                                app = Sphinx('.', None, 'outdir', '.', 'gettext', **kwargs)
                                # sphinx-build -a …
                                app.build(True)
                            except sphinx.errors.SphinxWarning as e:
                                raise Exception(str(outdir)) from e

                        # https://stackoverflow.com/questions/15408348
                        content = subprocess.run(['msgcat', *glob('outdir/*.pot')],
                                                 check=True, stdout=subprocess.PIPE).stdout

                with open(outdir / 'docs.pot', 'wb') as f:
                    f.write(content)
