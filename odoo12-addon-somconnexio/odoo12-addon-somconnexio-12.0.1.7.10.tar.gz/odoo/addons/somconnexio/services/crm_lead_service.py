import logging
from werkzeug.exceptions import BadRequest
from odoo.addons.base_rest.http import wrapJsonException
from odoo.addons.component.core import Component
from . import schemas

_logger = logging.getLogger(__name__)


class CRMLeadService(Component):
    _inherit = "base.rest.service"
    _name = "crm.lead.services"
    _usage = "crm-lead"
    _collection = "emc.services"
    _description = """
        CRMLead requests
    """

    def create(self, **params):
        params = self._prepare_create(params)
        # tracking_disable=True in context is needed
        # to avoid to send a mail in CRMLead creation
        sr = self.env["crm.lead"].with_context(tracking_disable=True).create(params)
        return self._to_dict(sr)

    def _validator_create(self):
        return schemas.S_CRM_LEAD_CREATE

    def _validator_return_create(self):
        return schemas.S_CRM_LEAD_RETURN_CREATE

    @staticmethod
    def _to_dict(crm_lead):
        return {
            "id": crm_lead.id
        }

    def _get_country(self, code):
        country = self.env["res.country"].search([("code", "=", code)])
        if country:
            return country
        else:
            raise wrapJsonException(
                BadRequest("No country for isocode %s" % code),
                include_description=True,
            )

    def _get_state(self, code, country_id):
        state = self.env["res.country.state"].search([
            ("code", "=", code),
            ("country_id", "=", country_id)])
        if state:
            return state
        else:
            raise wrapJsonException(
                BadRequest(
                    "No state for isocode %s and country id %s" %
                    (code, str(country_id))
                ),
                include_description=True,
            )

    def _prepare_adresss_from_partner(self, partner, key):
        country_id = partner.country_id.id
        state_id = partner.state_id.id
        return {
            "{}_street".format(key): partner.street,
            "{}_street2".format(key): partner.street2,
            "{}_zip_code".format(key): partner.zip,
            "{}_city".format(key): partner.city,
            "{}_state_id".format(key): state_id,
            "{}_country_id".format(key): country_id
        }

    def _prepare_address(self, address, key):
        country_id = self._get_country(address["country"]).id
        state_id = self._get_state(
            address["state"],
            country_id).id
        return {
            "{}_street".format(key): address["street"],
            "{}_street2".format(key): address.get("street2"),
            "{}_zip_code".format(key): address["zip_code"],
            "{}_city".format(key): address["city"],
            "{}_state_id".format(key): state_id,
            "{}_country_id".format(key): country_id
        }

    def _prepare_delivery_address(self, isp_info):
        if isp_info.get("delivery_address"):
            return self._prepare_address(
                isp_info["delivery_address"],
                "delivery"
            )
        else:
            if isp_info.get("icc"):
                return {}
            elif self.partner_id:
                partner = self.env['res.partner'].browse(self.partner_id)
                invoice_address = self.env['res.partner'].search([
                    ('parent_id', '=', self.partner_id),
                    ('type', '=', 'invoice')
                ])
                return self._prepare_adresss_from_partner(
                    invoice_address or partner,
                    "delivery"
                )
        raise wrapJsonException(
            BadRequest(
                "ISP Info with neither delivery_address nor partner_id"
            ),
            include_description=True,
        )

    def _prepare_create_isp_info(self, isp_info):
        delivery_address_dict = self._prepare_delivery_address(isp_info)
        isp_info.update(delivery_address_dict)

        if "service_address" in isp_info.keys():
            service_address_dict = self._prepare_address(
                isp_info["service_address"],
                "service"
            )
            isp_info.pop("service_address")
            isp_info.update(service_address_dict)

        if "invoice_address" in isp_info.keys():
            invoice_address_dict = self._prepare_address(
                isp_info["invoice_address"],
                "invoice"
            )
            isp_info.pop("invoice_address")
            isp_info.update(invoice_address_dict)

        if "icc" in isp_info.keys():
            isp_info["has_sim"] = True

        return isp_info

    def _prepare_create_line(self, line):
        product = self.env["product.product"].search(
            [('default_code', '=', line["product_code"])]
        )
        if not product:
            raise wrapJsonException(
                BadRequest(
                    'Product with code %s not found' % (
                        line['product_code'], )
                ),
                include_description=True,
            )
        response_line = {
            "name": product.name,
            "product_id": product.id,
            "product_tmpl_id": product.product_tmpl_id.id,
            "category_id": product.categ_id.id
        }
        if line.get("broadband_isp_info"):
            response_line["broadband_isp_info"] = self.env["broadband.isp.info"].create(
                self._prepare_create_isp_info(line["broadband_isp_info"])).id
        elif not self._needs_mobile_isp_info(product):
            raise wrapJsonException(
                BadRequest(
                    'Broadband product %s needs a broadband_isp_info' % (
                        line['product_code'], )
                ),
                include_description=True,
            )

        if line.get("mobile_isp_info"):
            response_line["mobile_isp_info"] = self.env["mobile.isp.info"].create(
                self._prepare_create_isp_info(line["mobile_isp_info"])).id
        elif self._needs_mobile_isp_info(product.product_tmpl_id):
            raise wrapJsonException(
                BadRequest(
                    'Mobile product %s needs a mobile_isp_info' % (
                        line['product_code'], )
                ),
                include_description=True,
            )
        return response_line

    def _needs_mobile_isp_info(self, product_tmpl):
        mobile = self.env.ref('somconnexio.mobile_service')
        if mobile.id == product_tmpl.categ_id.id:
            return True

    def _subscription_request_id(self, sr_id):
        if not sr_id:
            return False

        sr = self.env["subscription.request"].search(
            [("_api_external_id", "=", sr_id)]
        )
        if not sr:
            raise wrapJsonException(
                BadRequest('SubscriptionRequest with id %s not found' % (sr_id)),
                include_description=True,
            )
        else:
            return sr.id

    def _partner_id(self, partner_id):
        if not partner_id:
            return False

        partner = self.env['res.partner'].search([
            ("ref", "=", partner_id)
        ])
        if not partner:
            raise wrapJsonException(
                BadRequest('Partner with id %s not found' % (partner_id)),
                include_description=True,
            )
        return partner.id

    def _prepare_create(self, params):
        self.partner_id = self._partner_id(params.get("partner_id"))

        crm_line_ids = [
            self.env["crm.lead.line"].create(self._prepare_create_line(line)).id
            for line in params["lead_line_ids"]
        ]
        return {
            # TODO: What do we want to put in the CRMLead name and CRMLeadName?
            "name": "New CRMLead",
            "partner_id": self.partner_id,
            "subscription_request_id": self._subscription_request_id(
                params.get("subscription_request_id")),
            "iban": params.get("iban"),
            "lead_line_ids": [(6, 0, crm_line_ids)]
        }
