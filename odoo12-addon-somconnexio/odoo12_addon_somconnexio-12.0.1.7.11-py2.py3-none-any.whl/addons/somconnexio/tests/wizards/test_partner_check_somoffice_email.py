from mock import patch
from ..sc_test_case import SCTestCase
from odoo.exceptions import AccessError


class TestContractIBANChangeWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.browse_ref('somconnexio.res_partner_2_demo')

    @patch('odoo.addons.somconnexio.somoffice.user.get')
    def test_get_somoffice_email_ok(self, mock_somoffice_user_get):
        expected_somoffice_user_info = {
            "vat": self.partner.vat,
            "email": "user@somoffice.cat",
            "lang": "es_ES"
        }

        def _side_effect_somoffice_get(vat):
            if vat == self.partner.vat:
                return expected_somoffice_user_info

        mock_somoffice_user_get.side_effect = _side_effect_somoffice_get

        wizard = self.env['partner.check.somoffice.email.wizard'].with_context(
            active_id=self.partner.id
        ).create()

        self.assertEquals(wizard.partner_id, self.partner)
        self.assertEquals(
            wizard.somoffice_email,
            expected_somoffice_user_info.get('email')
        )

    @patch('odoo.addons.somconnexio.somoffice.user.get')
    def test_get_somoffice_email_user_not_found(self, mock_somoffice_user_get):

        def _side_effect_somoffice_get(vat):
            if vat == self.partner.vat:
                return {"msg": "error"}

        mock_somoffice_user_get.side_effect = _side_effect_somoffice_get

        with self.assertRaises(AccessError):
            self.env['partner.check.somoffice.email.wizard'].with_context(
                active_id=self.partner.id
            ).create()
