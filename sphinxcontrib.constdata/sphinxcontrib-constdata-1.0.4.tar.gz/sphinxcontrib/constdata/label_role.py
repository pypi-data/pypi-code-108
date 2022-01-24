from typing import List, Tuple

from docutils import nodes
from docutils.nodes import Node, system_message
from sphinx.util import logging
from sphinx.util.docutils import SphinxRole

from sphinxcontrib.constdata.settings import Settings
from sphinxcontrib.constdata.templating import resolve_template
from sphinxcontrib.constdata.url import Url
from sphinxcontrib.constdata.utils import ConstdataError, render_inline_rst

logger = logging.getLogger(__name__)


class LabelRole(SphinxRole):
    def run(self) -> Tuple[List[Node], List[system_message]]:
        try:
            return self._run()
        except ConstdataError as ex:
            msg = self.inliner.reporter.error(ex, line=self.lineno)
            return [nodes.inline(text=self.text)], [msg]

    def _run(self) -> Tuple[List[Node], List[system_message]]:
        settings = Settings(self.env)
        # self.text for e.g. ':constdata:label:`menu/file.csv?FileSaveAll`' is
        # 'menu.csv?FileSaveAll'
        url = Url(self.text)
        csv_file_path = url.get_rel_path()  # e.g. "menu/file.csv"
        row_id = url.get_id()  # e.g. "FileSaveAll"

        # e.g. ":menuselection:`{label}`"
        template_string = settings.get_label_template(csv_file_path)

        rst = resolve_template(settings, template_string, row_id, csv_file_path)

        return render_inline_rst(rst, self.lineno, self.inliner)
