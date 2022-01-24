import locale
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Union

from sphinx.environment import BuildEnvironment
from sphinx.util import logging

from sphinxcontrib.constdata.utils import ConstdataError

logger = logging.getLogger(__name__)


CONFIG_ROOT = "constdata_root"
"""Reference to folder relative to conf.py with CSV files."""

CONFIG_ROOT_DEFAULT = "_constdata"

CONFIG_FILES_ENCODING = "constdata_files_encoding"
"""Flatfiles encoding"""
CONFIG_FILES_ENCODING_DEFAULT: str = locale.getpreferredencoding(
    False
)  # platform dependent encoding

# No defaults for CSV format. For all options see
# https://docs.python.org/3/library/csv.html#csv-fmt-params
CONFIG_CSV_FORMAT = "constdata_csv_format"
CONFIG_CSV_FORMAT_DEFAULT: Dict[str, str] = {}

CONFIG_TARGET_TEMPLATE = "constdata_target_template"
"""Template for creating targets to items. Must be valid RST label."""

CONFIG_TARGET_TEMPLATE_DEFAULT = "constdata-${filename}-${id}"
"""Default target template. E.g. "const-agent-MaxMissedCalls"."""

CONFIG_FILES = "constdata_files"
"""Dict specifying files and their configuration (ID column name, reStructuredText templates for constdata roles and directives)."""

CONFIG_TEMPLATES_DEFAULT: Dict[str, Dict] = {}

CONFIG_ID_COL_NAME = "id"
"""Key for constdata_files saying what is the name of ID column."""

CONFIG_ID_COL_NAME_DEFAULT = "id"
"""ID column default name."""

CONFIG_TEMPLATES_LABEL = "label"
"""Key for ``:const:link:`` role template."""

CONFIG_TEMPLATES_REF = "link"
"""Key for ``:const:link:`` role template."""

CONFIG_TEMPLATES_TABLE = "table"

CONFIG_POT_MSG_FLAGS = "constdata_pot_message_flags"
CONFIG_POT_MSG_FLAGS_DEFAULT = ()  # empty tuple


_CONN_ATTR = "_constdata_cachedb_conn"
"""Attribute name to sqlite3.Connection to cachedb in a Sphinx instance"""


class Settings:
    """Comfort reading constdata's conf.py variables. Pass-in Sphinx :py:class:`~sphinx.environment.BuildEnvironment` object."""

    def __init__(self, env: BuildEnvironment) -> None:
        self.env = env

    def get_root(self) -> Path:
        """Returns an absolute path to the constdata files root"""

        # root folder is relative to conf.py
        rel_path = getattr(self.env.config, CONFIG_ROOT)
        if not rel_path:
            raise ConstdataError(f"You must set {CONFIG_ROOT} configuration")

        # transform to absolute
        abs_path = Path(self.env.app.confdir).joinpath(rel_path).resolve()

        return abs_path

    def get_id_col_name(self, flatfile_path: Union[str, Path]) -> str:
        """The name of ID column for a specified file."""
        flatfile_path = str(flatfile_path)
        id_col_name = self._get_file_config(flatfile_path, CONFIG_ID_COL_NAME)
        if not id_col_name:
            id_col_name = CONFIG_ID_COL_NAME_DEFAULT

        return id_col_name

    def get_label_template(self, csv_file_path: str) -> str:
        template_string = self._get_file_config(csv_file_path, CONFIG_TEMPLATES_LABEL)
        if not template_string:
            raise ConstdataError(
                f"Missing :constdata:label: template for '{csv_file_path}'."
            )

        return template_string

    def get_ref_template(self, csv_file_path: str) -> str:
        template_string = self._get_file_config(csv_file_path, CONFIG_TEMPLATES_REF)
        if not template_string:
            raise ConstdataError(
                f"Missing :constdata:link: template for '{csv_file_path}'."
            )

        return template_string

    def _get_file_config(self, flatfile_path: str, key_name: str):
        """Obtain settings object for specified flatfile.

        For example, for::

            constdata_files = {
                "foo.csv":  {
                    "label": ":guilabel:`{Path}`",
                    "table: {
                        "__title__": "Foo options reference",
                        "Name of item": "{Name}"
                    }
                }
            }

        returns

        * string ":guilabel:`{Path}`" for _get_template("...", "label")
        * dict ``{ "__title__": "Foo options reference", "Name of item": "{Name}" }`` for _get_template("...", "table")

        :param csv_file_path: CSV file including suffix relative to const_root
        :raise KeyError: if config object not found
        """

        config_dict: Optional[dict] = getattr(self.env.config, CONFIG_FILES, None)

        # Fallback to "${id}" if
        if (not config_dict) or (  # not present/empty, or
            flatfile_path not in config_dict
        ):  # filename not present
            return None

        # Obtain config object for the passed file
        try:
            config_value = config_dict[flatfile_path][key_name]
        except KeyError:
            return None

        return config_value

    def get_files_encoding(self) -> str:
        return getattr(self.env.config, CONFIG_FILES_ENCODING)

    def get_csv_fmt_params(self) -> Dict:
        """CSV formatting parameters suitable for reader() and DictReader()"""
        return getattr(self.env.config, CONFIG_CSV_FORMAT)

    def get_cachedb_conn(self) -> sqlite3.Connection:
        conn = getattr(self.env.app, _CONN_ATTR)
        return conn
