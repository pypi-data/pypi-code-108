import logging

from odoo.addons.component.core import Component
from odoo.exceptions import MissingError
from odoo.fields import Date

from odoo import _

from . import schemas
from .vat_normalizer import VATNormalizer

_logger = logging.getLogger(__name__)


class ResPartnerService(Component):
    _inherit = "base.rest.service"
    _name = "res.partner.service"
    _usage = "partner"
    _collection = "emc.services"
    _description = """
        ResPartner service to expose the partners and filter by VAT number.
    """

    def get(self, _id):
        ref = str(_id)
        domain = [
            ("parent_id", "=", None),
            ("ref", "=", ref),
        ]

        _logger.info("search with domain {}".format(domain))
        partners = self.env["res.partner"].search(domain, limit=1)

        if not partners:
            raise MissingError(_("Partner with ref {} not found.".format(ref)))

        return self._to_dict(partners)

    def search(self, vat):
        domain = [
            ("parent_id", "=", None),
            ("vat", "ilike", VATNormalizer(vat).normalize()),
        ]

        _logger.info("search with domain {}".format(domain))
        partners = self.env["res.partner"].search(domain, limit=1)

        if not partners:
            raise MissingError(_("Partner with VAT {} not found.".format(vat)))

        return self._to_dict(partners)

    def _to_dict(self, partner):
        partner.ensure_one()
        return {
            "id": partner.id,
            "name": partner.name,
            "firstname": partner.firstname or "",
            "lastname": partner.lastname or "",
            "display_name": partner.lastname or "",
            "ref": partner.ref or "",
            "lang": partner.lang or "",
            "vat": partner.vat or "",
            "type": partner.type or "",
            "email": partner.email or "",
            "phone": partner.phone or "",
            "mobile": partner.mobile or "",
            "cooperator_register_number": partner.cooperator_register_number,
            "cooperator_end_date": Date.to_string(partner.cooperator_end_date) or "",
            "sponsor_id": partner.sponsor_id.id or 0,
            "coop_agreement_code": partner.coop_agreement_id.code or "",
            "coop_candidate": partner.coop_candidate,
            "member": partner.member,
        }

    def _validator_get(self):
        return schemas.S_RES_PARTNER_REQUEST_GET

    def _validator_return_get(self):
        return schemas.S_RES_PARTNER_RETURN_GET

    def _validator_search(self):
        return schemas.S_RES_PARTNER_REQUEST_SEARCH

    def _validator_return_search(self):
        return schemas.S_RES_PARTNER_RETURN_GET
