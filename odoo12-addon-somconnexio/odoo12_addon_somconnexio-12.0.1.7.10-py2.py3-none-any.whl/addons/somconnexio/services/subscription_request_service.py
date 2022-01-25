import logging
from odoo.addons.component.core import Component
from . import schemas
from werkzeug.exceptions import BadRequest
from odoo.addons.base_rest.http import wrapJsonException


_logger = logging.getLogger(__name__)


class SubscriptionRequestService(Component):
    _inherit = "subscription.request.services"

    def _prepare_create(self, params):
        address = params["address"]
        country = self._get_country(address["country"])
        state_id = self._get_state(address["state"], country.id)
        nationality_id = self._get_nationality(params["nationality"])
        payment_type = self._get_payment_type(params["payment_type"])
        sr_create_values = {
            "name": params["name"],
            "firstname": params.get("firstname"),
            "lastname": params.get("lastname"),
            "email": params["email"],
            "phone": params.get("phone"),
            "address": address["street"],
            "zip_code": address["zip_code"],
            "city": address["city"],
            "country_id": country.id,
            "state_id": state_id,
            "lang": params["lang"],
            "iban": params.get("iban"),
            "vat": params["vat"],
            "discovery_channel_id": params["discovery_channel_id"],
            "nationality": nationality_id,
            "payment_type": payment_type,
            "voluntary_contribution": params.get(
                "voluntary_contribution", False
            ),
            "is_company": params.get("is_company"),
            "company_name": params.get("company_name"),
            "company_email": params.get("company_email") or params["email"],
        }
        if not params.get("is_company"):
            sr_create_values["birthdate"] = "{} 00:00:00".format(params["birthdate"])
            sr_create_values["gender"] = params["gender"]
        if params["type"] == "new":
            sr_create_values["share_product_id"] = self.env.ref(
                "somconnexio.cooperator_share_product").product_variant_id.id
            sr_create_values["ordered_parts"] = 1
        elif params["type"] == "sponsorship":
            sr_create_values["ordered_parts"] = 0
            sponsor = self._get_sponsor(
                params["sponsor_vat"]
            )
            coop_agreement = self._get_coop_agreement(sponsor)
            if coop_agreement:
                sr_create_values["coop_agreement_id"] = coop_agreement.id
                sr_create_values["type"] = "sponsorship_coop_agreement"
            else:
                sr_create_values["sponsor_id"] = sponsor.id
                sr_create_values["type"] = "sponsorship"
        return sr_create_values

    def _validator_create(self):
        create_schema = super()._validator_create()
        create_schema.update(schemas.S_SUBSCRIPTION_REQUEST_CREATE_SC_FIELDS)
        return create_schema

    def _validator_return_create(self):
        create_schema = super()._validator_return_create()
        create_schema.update(schemas.S_SUBSCRIPTION_REQUEST_RETURN_CREATE_SC_FIELDS)
        return create_schema

    def _get_share_product(self, share_product):
        """
        Overwrite the method of EMC:
        https://github.com/coopiteasy/vertical-cooperative/blob/12.0/easy_my_coop_api/services/subscription_request_service.py#L133  # noqa
        We can accept requests without share_product.
        This method cover the logic  of the sponsored customers.
        """
        if share_product:
            return share_product

    def _get_state(self, state, country_id):
        state_id = self.env['res.country.state'].search([
            ('code', '=', state),
            ('country_id', '=', country_id),
        ]).id
        if not state_id:
            raise wrapJsonException(
                BadRequest(
                    'State %s not found' % (state)
                ),
                include_description=True,
            )
        return state_id

    def _get_nationality(self, nationality):
        nationality_id = self.env['res.country'].search([
            ('code', '=', nationality)
        ]).id
        if not nationality_id:
            raise wrapJsonException(
                BadRequest(
                    'Nationality %s not found' % (nationality)
                ),
                include_description=True,
            )
        return nationality_id

    def _get_payment_type(self, payment_type):
        if payment_type not in [
            pm[0]
            for pm
            in self.env['subscription.request']._fields['payment_type'].selection
        ]:
            raise wrapJsonException(
                BadRequest(
                    'Payment type %s not valid' % (payment_type)
                ),
                include_description=True,
            )
        return payment_type

    def _get_coop_agreement(self, sponsor):
        coop_agreement = self.env['coop.agreement'].search([
            ('partner_id', '=', sponsor.id)
        ])
        if not coop_agreement:
            return None
        return coop_agreement

    def _get_sponsor(self, sponsor_vat):
        sponsor = self.env['res.partner'].search([
            ('vat', 'ilike', sponsor_vat),
            '|',
            ('member', '=', True),
            ('coop_candidate', '=', True),
        ])
        if not sponsor:
            raise wrapJsonException(
                BadRequest(
                    'Sponsor VAT number %s not found' % (sponsor_vat)
                ),
                include_description=True
            )
        return sponsor

    def _to_dict(self, sr):
        response = super()._to_dict(sr)
        del response['share_product']
        return response
