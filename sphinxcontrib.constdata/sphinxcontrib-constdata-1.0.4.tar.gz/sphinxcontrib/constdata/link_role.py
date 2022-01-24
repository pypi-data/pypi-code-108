from typing import List, Tuple, cast

from docutils import nodes
from docutils.nodes import Node, system_message
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.util.docutils import ReferenceRole
from sphinx.util.nodes import make_refnode

from sphinxcontrib.constdata.settings import Settings
from sphinxcontrib.constdata.table_directive import make_url_safe_target_id
from sphinxcontrib.constdata.templating import resolve_template
from sphinxcontrib.constdata.url import Url
from sphinxcontrib.constdata.utils import ConstdataError, render_inline_rst

logger = logging.getLogger(__name__)


class constdatalinknode(nodes.generated):
    """Empty node placed to the doctree by :py:class:`LinkRole`. Node just flags a place where constdata:link: role has been used. Node will be replaced in doctree-resolved event handler :py:func:`process_link_nodes` to actual Docutils reference node."""


class LinkRole(ReferenceRole):
    def run(self) -> Tuple[List[Node], List[system_message]]:
        try:
            return self._run()
        except ConstdataError as ex:
            msg = self.inliner.reporter.error(ex, line=self.lineno)
            return [nodes.inline(text=self.target)], [msg]

    def _run(self) -> Tuple[List[Node], List[system_message]]:
        settings = Settings(self.env)
        # self.target for e.g. ':constdata:link:`menu/file.csv?FileSaveAll`' is
        # 'menu.csv?FileSaveAll'
        url = Url(self.target)
        rel_path = url.get_rel_path()  # e.g. "menu/file.csv"
        row_id = url.get_id()  # e.g. "FileSaveAll"

        # Use title if passed (e.g. "foo" in :constdata:link:`foo <url>`)
        if self.has_explicit_title:
            template_string = self.title
        else:
            # otherwise, lookup for a template, e.g. ":guilabel:`${Field}`"
            template_string = settings.get_ref_template(rel_path)

        # in all cases, resolve role title or template to final rst
        rst = resolve_template(settings, template_string, row_id, rel_path)

        # Child nodes and messages from title, or resolved template
        child_nodes, child_messages = render_inline_rst(rst, self.lineno, self.inliner)
        # Wrap child nodes to single node
        child_nodes_wrapper = nodes.generated()
        child_nodes_wrapper += child_nodes

        # Safe to domain data
        from sphinxcontrib.constdata import (  # local import to prevent circular reference
            ConstdataDomain,
        )

        # the same way as target ID was constructed in table:: directive
        targetid = make_url_safe_target_id(rel_path, row_id)
        # unique :constdata:link: identification
        refid = f"{self.env.docname}-{self.env.new_serialno('constdata')}"
        domain = cast(ConstdataDomain, self.env.get_domain(ConstdataDomain.name))
        domain.add_link_record(
            refid=refid,
            targetid=targetid,
            fromdocname=self.env.docname,
            text=self.text,
            url=url,
            node=child_nodes_wrapper.deepcopy(),
        )

        return [constdatalinknode(refid=refid)], child_messages


def process_link_nodes(app: Sphinx, doctree: nodes.document, docname: str):
    """Called after doctree-resolved event, replaces :constdata:link: nodes with actual Docutils ref nodes pointing to row in the table where referred ID is listed."""

    from sphinxcontrib.constdata import (  # local import to prevent circular reference
        ConstdataDomain,
    )

    assert app.env
    domain = cast(ConstdataDomain, app.env.get_domain(ConstdataDomain.name))

    for node in doctree.traverse(constdatalinknode):
        # lookup ref record
        # use refid to lookup original :constdata:link: occurrence
        refid = node["refid"]
        link_record = domain.get_link_record(refid)
        targetid = link_record["targetid"]
        text = link_record["text"]
        url: Url = link_record["url"]
        child_nodes_wrapper = link_record["node"]

        # Final node could be real ref, if target exists
        try:
            # lookup target record
            target_record = domain.get_target_record(targetid)
            todocname = target_record["docname"]

            # Build ref node
            assert app.builder
            final_node = make_refnode(
                app.builder,
                docname,
                todocname,
                targetid,
                child=child_nodes_wrapper,
                title=url.get_id(),  # tooltip (e.g. <a title> in HTML)
            )

        except KeyError:
            # Or, title as plain text, if target not found
            final_node = nodes.inline(text=text)

            logger.error(
                f"Reference to non-existing row with ID '{url.get_id()}'. If you didn't make a typo, it usually means '{url.get_rel_path()}' showing '{url.get_id()}' is not anywhere listed with :constdata:table:: directive.",
                location=node,
            )

        node.replace_self(final_node)
