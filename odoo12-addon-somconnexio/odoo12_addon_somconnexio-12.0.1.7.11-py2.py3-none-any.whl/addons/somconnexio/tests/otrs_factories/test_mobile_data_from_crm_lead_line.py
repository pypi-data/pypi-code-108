from ..sc_test_case import SCTestCase

from ...otrs_factories.mobile_data_from_crm_lead_line \
    import MobileDataFromCRMLeadLine


class MobileDataFromCRMLeadLineTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.crm_lead_line_args = {
            'name': 'New CRMLeadLine',
            'description': 'description test',
            'product_id': self.ref('somconnexio.150Min1GB'),
            'mobile_isp_info': None,
            'broadband_isp_info': None,
        }

    def test_build(self):
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'type': 'new',
        })
        self.crm_lead_line_args['mobile_isp_info'] = mobile_isp_info.id
        crm_lead_line = self.env['crm.lead.line'].create(
            self.crm_lead_line_args)

        self.env['crm.lead'].create({
            'name': 'Test Lead',
            'description': 'Test description',
            'iban': 'ES9420805801101234567891',
            'email': 'crm_lead_email@test.com',
            'lead_line_ids': [(6, 0, [crm_lead_line.id])]
        })

        mobile_data = MobileDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(mobile_data.order_id, crm_lead_line.id)
        self.assertFalse(mobile_data.portability)
        self.assertEqual(mobile_data.iban, crm_lead_line.lead_id.iban)
        self.assertEqual(mobile_data.email, crm_lead_line.lead_id.email_from)
        self.assertEqual(mobile_data.notes, crm_lead_line.lead_id.description)
        self.assertEqual(mobile_data.product, crm_lead_line.product_id.default_code)

    def test_portability_build(self):
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'phone_number': '666666666',
            "delivery_street": "Carrer Nogal",
            "delivery_street2": "55 Principal",
            "delivery_zip_code": "08008",
            "delivery_city": "Barcelona",
            "delivery_state_id": self.ref(
                'base.state_es_b'
            ),
            "delivery_country_id": self.ref(
                'base.es'
            ),
            'type': 'portability',
            'previous_owner_name': 'Mora',
            'previous_owner_first_name': 'Josep',
            'previous_owner_vat_number': '61518707D',
            'previous_provider': self.ref('somconnexio.previousprovider3'),
            'previous_contract_type': 'contract',
            'icc_donor': '4343434',
            'icc': '123123421',
        })
        self.crm_lead_line_args['mobile_isp_info'] = mobile_isp_info.id
        crm_lead_line = self.env['crm.lead.line'].create(
            self.crm_lead_line_args)

        mobile_data = MobileDataFromCRMLeadLine(crm_lead_line).build()

        self.assertTrue(mobile_data.portability)
        self.assertEqual(mobile_data.phone_number, mobile_isp_info.phone_number)
        self.assertEqual(
            mobile_data.previous_owner_vat,
            mobile_isp_info.previous_owner_vat_number)
        self.assertEqual(
            mobile_data.previous_owner_name,
            mobile_isp_info.previous_owner_first_name)
        self.assertEqual(
            mobile_data.previous_owner_surname,
            mobile_isp_info.previous_owner_name)
        self.assertEqual(
            mobile_data.previous_provider,
            mobile_isp_info.previous_provider.code)
        self.assertEqual(mobile_data.sc_icc, mobile_isp_info.icc)
        self.assertEqual(mobile_data.icc, mobile_isp_info.icc_donor)
