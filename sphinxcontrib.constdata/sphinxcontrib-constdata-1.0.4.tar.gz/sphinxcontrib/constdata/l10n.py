import os
import re
from pathlib import Path
from typing import Iterable, Optional, Tuple

from babel.messages import Catalog
from babel.messages.pofile import write_po
from sphinx.builders.gettext import MessageCatalogBuilder
from sphinx.locale import init
from sphinx.util import logging

from sphinxcontrib.constdata.flatfiles import FlatfileReader, rglob_flatfiles_from
from sphinxcontrib.constdata.settings import CONFIG_POT_MSG_FLAGS, Settings

logger = logging.getLogger(__name__)


CONSTDATA_ROOT_CATALOG = "constdata"
"""Messages from flatfiles"""

CONSTDATA_EXTENSION_CATALOG = "sphinxcontrib-constdata"
"""Messages of the sphinxcontrib-constdata extension itself"""


def gettext(settings: Settings):
    """
    Creates and returns function that for an original (msgid), returns a translation (msgstr).

    Usage::

        _ = gettext(settings)
        print(_(header))

    If returning function gots translatable string (between ``_(`` and ``)``), returns its translation. If it is not found, returns 'foo'.
    """

    # abs dirs of all locales dirs (e.g. locales/en/)
    dirs = [
        os.path.join(settings.env.srcdir, directory)
        for directory in settings.env.config.locale_dirs
    ]
    catalog, has_catalog = init(
        dirs, settings.env.config.language, CONSTDATA_ROOT_CATALOG
    )

    def _(message: Optional[str]):
        # is it translatable message? I.e. contains _('')
        if not message:
            return message

        match = msg_pattern.match(message)
        if not match:
            return message

        msgid = match.group("msg")

        if not has_catalog:
            return msgid

        msgstr = catalog.gettext(msgid)
        return msgstr

    return _


# Valid messages examples:

# _('''Minim nostrud elit aute Lorem aliquip occaecat do eu.
#
# Duis nulla laborum Lorem fugiat voluptate. Cupidatat sit cupidatat ullamco et exercitation. Lorem sit qui consequat ea id commodo non fugiat amet.
#
# * Culpa pariatur quis esse elit officia eiusmod sit.
# * Cillum sit ad tempor cillum proident.''')

# _('Cillum sit ad tempor cillum proident.')

# _("Cillum sit ad tempor cillum proident.")
# _("""Cillum sit ad tempor
# cillum proident""")
msg_pattern = re.compile(
    r"""
     ^                               # beginning of string
     _\(                             # starts with _(
     (?P<quote>'''|'|\"\"\"|\")      # start-string is triple/single '/"
     (?P<msg>.+)                     # message to translate
     (?P=quote)                      # same end-string as was start-string
     \)                              # expression ends with )
     $                               # end of string
 """,
    re.VERBOSE | re.DOTALL,
)


class CsvMessageCatalogBuilder(MessageCatalogBuilder):
    """
    Runs unmodified Sphinx builtin gettext builder, after it extract messages from constdata_root folder.
    """

    def finish(self) -> None:
        # run original gettext builder
        super().finish()

        # run Babel extract command
        # equivalent of
        # $ pybabel extract -o build\gettext\const.pot --mapping sphinxcontrib-const\sphinxcontrib\const\babel-mapping.ini --no-wrap _const
        # e.g. /path/to/sphinx/_build/gettext/constdata.pot
        abs_pot_path = Path(self.outdir, f"{CONSTDATA_ROOT_CATALOG}.pot")

        catalog = Catalog(
            project=self.config.project,
            version=self.config.version,
            copyright_holder=self.config.author,
        )
        flags: tuple = getattr(self.config, CONFIG_POT_MSG_FLAGS)

        for msg, location, recordno, comment in self._extract_messages():
            # Creates the following in .pot file
            #       #. id=ThisIsId
            #       #: _constdata/Configuration.csv:3
            #       #, flag1, flag2
            #       msgid "Please go to ..."
            #       msgstr ""
            catalog.add(
                id=msg,
                string=None,
                locations=[(location, recordno)],
                auto_comments=(comment,),
                flags=flags,
            )

        with open(abs_pot_path, "wb") as f:
            # e.g. constdata.pot
            rel_pot_path = abs_pot_path.relative_to(self.outdir)
            logger.info(f"writing constdata catalog {rel_pot_path}")

            write_po(
                f,
                catalog,
                # no line wrapping
                width=0,
            )

    def _extract_messages(self) -> Iterable[Tuple[str, str, int, str]]:
        """
        Search flatfiles for translatable messages and returns itrable where
        each item is (message, filepath, recordno, extracted_comment) tuple.

        Extracted comment is a comment directed at the translator with the instructions that might help understand the translated string.
        """
        translatables = []
        assert self.env
        settings = Settings(self.env)
        flatfiles = rglob_flatfiles_from(settings.get_root())

        for abs_path in flatfiles:
            rel_path = abs_path.relative_to(settings.get_root())

            # relative path to source e.g.,
            # '_constdata/entities/IvrScript.cs.csv'
            location = str(abs_path.relative_to(self.app.srcdir))

            flatfile = FlatfileReader(settings, rel_path)
            for i, row in enumerate(flatfile.iterate_rows()):
                # pick header from first row
                if i == 0:
                    for col_name in row.keys():
                        match = msg_pattern.match(str(col_name))
                        if match:
                            msg = match.group("msg")
                            comment = f"In {location} on header row"
                            translatables.append((msg, location, i, comment))

                # first and further rows
                for col_val in row.values():
                    match = msg_pattern.match(str(col_val))
                    if match:
                        msg = match.group("msg")

                        # comment
                        # first column is ID column but we can't "row[0]", so this will detect
                        # first column key name in dict (from https://www.kite.com/python/answers/how-to-get-the-first-key-value-in-a-dictionary-in-python)
                        id_col_name = next(iter(row.keys()))
                        id_col_value = row[id_col_name]
                        comment = f"In {location} on {id_col_name} = {id_col_value}"

                        translatables.append((msg, location, i + 1, comment))

        return translatables
