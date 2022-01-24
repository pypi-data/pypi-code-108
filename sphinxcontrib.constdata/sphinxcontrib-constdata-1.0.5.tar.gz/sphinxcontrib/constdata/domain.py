from typing import Dict, Mapping

from sphinx.domains import Domain
from sphinx.util import logging

from sphinxcontrib.constdata.label_role import LabelRole
from sphinxcontrib.constdata.link_role import LinkRole
from sphinxcontrib.constdata.table_directive import TableDirective
from sphinxcontrib.constdata.url import Url

logger = logging.getLogger(__name__)


class ConstdataDomain(Domain):
    """Domain in Sphinx groups directives and roles."""

    name = "constdata"
    label = "Constant data templates"
    directives = {"table": TableDirective}
    roles = {
        "label": LabelRole(),
        "link": LinkRole(),
    }
    initial_data: Dict[str, Dict] = {
        "target_records": {},
        "link_records": {},
    }

    def add_link_record(self, refid, targetid, fromdocname, text, url: Url, node):
        """
        Called by link role to store unique :constdata:link: usage identification record in the domain data. Later, will be replaced to real Docutils refs in :py:func:`link_role.process_link_nodes`.

        :param refid: internal unique ref ID, e.g. "foo-document-0"
        :param targetid: RST target as created by :py:func:`table_directive.make_url_safe_target_id`
        :param fromdocname: docname where role used
        :param text: role text (e.g. for :constdata:link:`foo <bar>`, text is foo <bar>)
        :param url: url used in link role (e.g. foo.csv?id)
        :param node: wrapped node
        """
        logger.debug(
            f"[constdata] add_link_record(refid={refid}, targetid={fromdocname}, fromdocname={fromdocname}, text={text}, url={url}, node={node})"
        )
        self.data["link_records"][refid] = {
            "targetid": targetid,
            "fromdocname": fromdocname,
            "text": text,
            "url": url,
            "node": node,
        }

    def get_link_record(self, refid):
        """
        :raises KeyError: if refid not found
        """
        logger.debug(f"[constdata] get_link_record(refid={refid})")
        return self.data["link_records"][refid]

    def add_target_record(self, targetid, docname):
        """
        Called by table directive to store target ID - docname pairs in the domain data.

        E.g.::

            add_target_record(targetid="constdata-conf2-csv-project", docname="index").

        :param targetid: unique target ID as created by :py:func:`table_directive.make_url_safe_target_id`.
        :param docname: where row ID is listed
        """
        logger.debug(
            f"[constdata] add_target_record(targetid={targetid}, docname={docname})"
        )
        self.data["target_records"][targetid] = {"docname": docname}

    def get_target_record(self, targetid) -> Mapping:
        """Lookup target ID - docname pair from the domain data.

        :raises KeyError: if targetid not found"""

        logger.debug(f"[constdata] get_target_record(targetid={targetid})")
        return self.data["target_records"][targetid]
