from otrs_somconnexio.otrs_models.coverage.adsl import ADSLCoverage
from otrs_somconnexio.otrs_models.coverage.mm_fibre import MMFibreCoverage
from otrs_somconnexio.otrs_models.coverage.vdf_fibre import VdfFibreCoverage

from ..sc_test_case import SCTestCase

from ...otrs_factories.adsl_data_from_crm_lead_line \
    import ADSLDataFromCRMLeadLine


class ADSLDataFromCRMLeadLineTest(SCTestCase):
    "ADSLDataFromCRMLeadLineTest"

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.crm_lead_line_args = {
            'name': 'New CRMLeadLine',
            'description': 'description test',
            'product_id': self.ref('somconnexio.ADSL20MB100MinFixMobile'),
            'mobile_isp_info': None,
            'broadband_isp_info': None,
        }

    def test_build(self):
        broadband_isp_info = self.env['broadband.isp.info'].create({
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
            'type': 'new',
            "service_street": "Calle Repet",
            "service_street2": "1 5º A",
            "service_zip_code": "01003",
            "service_city": "Madrid",
            "service_state_id": self.ref(
                'base.state_es_m'
            ),
            "service_country_id": self.ref(
                'base.es'
            ),
        })
        self.crm_lead_line_args['broadband_isp_info'] = broadband_isp_info.id
        crm_lead_line = self.env['crm.lead.line'].create(
            self.crm_lead_line_args)

        self.env['crm.lead'].create({
            'name': 'Test Lead',
            'description': 'Test description',
            'iban': 'ES9420805801101234567891',
            'email': 'crm_lead_email@test.com',
            'lead_line_ids': [(6, 0, [crm_lead_line.id])]
        })

        adsl_data = ADSLDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(adsl_data.order_id, crm_lead_line.id)
        self.assertFalse(adsl_data.phone_number)
        self.assertEqual(
            adsl_data.service_address,
            broadband_isp_info.service_full_street)
        self.assertEqual(
            adsl_data.service_city,
            broadband_isp_info.service_city)
        self.assertEqual(
            adsl_data.service_zip,
            broadband_isp_info.service_zip_code)
        self.assertEqual(
            adsl_data.service_subdivision,
            "Madrid")
        self.assertEqual(
            adsl_data.service_subdivision_code,
            "ES-M")
        self.assertEqual(
            adsl_data.shipment_address,
            broadband_isp_info.delivery_full_street)
        self.assertEqual(
            adsl_data.shipment_city,
            broadband_isp_info.delivery_city)
        self.assertEqual(
            adsl_data.shipment_zip,
            broadband_isp_info.delivery_zip_code)
        self.assertEqual(
            adsl_data.shipment_subdivision,
            broadband_isp_info.delivery_state_id.name)
        self.assertEqual(adsl_data.notes, crm_lead_line.lead_id.description)
        self.assertEqual(adsl_data.iban, crm_lead_line.lead_id.iban)
        self.assertEqual(adsl_data.email, crm_lead_line.lead_id.email_from)
        self.assertEqual(adsl_data.landline_phone_number, 'new_number')
        self.assertEqual(adsl_data.product, crm_lead_line.product_id.default_code)

    def test_portability_build(self):
        broadband_isp_info = self.env['broadband.isp.info'].create({
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
            "service_street": "Calle Repet",
            "service_street2": "1 5º A",
            "service_zip_code": "01003",
            "service_city": "Madrid",
            "service_state_id": self.ref(
                'base.state_es_m'
            ),
            "service_country_id": self.ref(
                'base.es'
            ),
            'keep_phone_number': True,
            'previous_owner_name': 'Mora',
            'previous_owner_first_name': 'Josep',
            'previous_owner_vat_number': '61518707D',
            'previous_provider': self.ref('somconnexio.previousprovider3'),
        })
        self.crm_lead_line_args['broadband_isp_info'] = broadband_isp_info.id
        crm_lead_line = self.env['crm.lead.line'].create(
            self.crm_lead_line_args)

        adsl_data = ADSLDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(adsl_data.phone_number, broadband_isp_info.phone_number)
        self.assertEqual(adsl_data.landline_phone_number, 'current_number')
        self.assertEqual(
            adsl_data.previous_owner_vat,
            broadband_isp_info.previous_owner_vat_number)
        self.assertEqual(
            adsl_data.previous_owner_name,
            broadband_isp_info.previous_owner_first_name)
        self.assertEqual(
            adsl_data.previous_owner_surname,
            broadband_isp_info.previous_owner_name)
        self.assertEqual(
            adsl_data.previous_provider,
            broadband_isp_info.previous_provider.code)
        self.assertEqual(
            adsl_data.previous_service,
            "Fibra")

    def test_change_address_build(self):
        service_supplier = self.browse_ref(
            "somconnexio.service_supplier_vodafone"
        )
        broadband_isp_info = self.env['broadband.isp.info'].create({
            "type": "portability",
            "service_street": "Calle Repet",
            "service_street2": "1 5º A",
            "service_zip_code": "01003",
            "service_city": "Madrid",
            "service_state_id": self.ref('base.state_es_m'),
            "service_country_id": self.ref('base.es'),
            "previous_contract_address": "Carrer Test",
            "previous_contract_phone": "666666666",
            "change_address": True,
            "service_supplier_id": service_supplier.id,
            "mm_fiber_coverage": MMFibreCoverage.VALUES[2][0],
            "vdf_fiber_coverage": VdfFibreCoverage.VALUES[3][0],
            "adsl_coverage": ADSLCoverage.VALUES[6][0],
            "previous_provider": self.ref('somconnexio.previousprovider52'),
        })
        self.crm_lead_line_args['broadband_isp_info'] = broadband_isp_info.id
        crm_lead_line = self.env['crm.lead.line'].create(
            self.crm_lead_line_args)

        adsl_data = ADSLDataFromCRMLeadLine(crm_lead_line).build()

        self.assertEqual(adsl_data.change_address, 'yes')
        self.assertEqual(adsl_data.previous_internal_provider, service_supplier.ref)
        self.assertEqual(adsl_data.mm_fiber_coverage, MMFibreCoverage.VALUES[2][0])
        self.assertEqual(adsl_data.vdf_fiber_coverage, VdfFibreCoverage.VALUES[3][0])
        self.assertEqual(adsl_data.adsl_coverage, ADSLCoverage.VALUES[6][0])
        self.assertEqual(adsl_data.previous_contract_address, "Carrer Test")
        self.assertEqual(adsl_data.previous_contract_phone, "666666666")
