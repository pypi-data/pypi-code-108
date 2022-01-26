import os
from mock import patch, Mock

from ..sc_test_case import SCComponentTestCase


@patch.dict(os.environ, {
    'SOMOFFICE_URL': 'https://somoffice.coopdevs.org/',
})
@patch('odoo.addons.somconnexio.somoffice.user.requests', spec=['request'])
class TestPartnerListener(SCComponentTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestPartnerListener, cls).setUpClass()
        # disable tracking test suite wise
        cls.env = cls.env(context=dict(
            cls.env.context,
            tracking_disable=True,
            test_queue_job_no_delay=False,
        ))

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.browse_ref('somconnexio.res_partner_2_demo')

    def test_create_user_if_customer_and_cooperator(self, mock_requests):
        mock_requests.request.return_value = Mock(spec=['status_code', 'json'])
        mock_requests.request.return_value.status_code = 200

        queue_jobs_before = self.env['queue.job'].search_count([])

        self.env['res.partner'].create({
            'parent_id': None,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'cooperator': True,
            'email': 'test@example.com',
            'lang': 'ca_ES',
        })

        queue_jobs_after = self.env['queue.job'].search_count([])

        self.assertEqual(queue_jobs_before, queue_jobs_after-1)

    def test_not_create_user_if_not_customer_and_cooperator(self, mock_requests):
        mock_requests.request.return_value = Mock(spec=['status_code', 'json'])
        mock_requests.request.return_value.status_code = 200

        queue_jobs_before = self.env['queue.job'].search_count([])

        self.env['res.partner'].create({
            'parent_id': None,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': False,
            'cooperator': True,
            'email': 'test@example.com',
            'lang': 'ca_ES',
        })

        queue_jobs_after = self.env['queue.job'].search_count([])

        self.assertEqual(queue_jobs_before, queue_jobs_after)

    def test_not_create_user_if_not_customer_and_not_cooperator(self, mock_requests):
        mock_requests.request.return_value = Mock(spec=['status_code', 'json'])
        mock_requests.request.return_value.status_code = 200

        queue_jobs_before = self.env['queue.job'].search_count([])

        self.env['res.partner'].create({
            'parent_id': None,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': False,
            'cooperator': False,
            'email': 'test@example.com',
            'lang': 'ca_ES',
        })

        queue_jobs_after = self.env['queue.job'].search_count([])

        self.assertEqual(queue_jobs_before, queue_jobs_after)

    def test_not_create_user_if_partner_already_exists(self, mock_requests):
        mock_requests.request.return_value = Mock(spec=['status_code', 'json'])
        mock_requests.request.return_value.status_code = 200

        queue_jobs_before = self.env['queue.job'].search_count([])

        self.env['res.partner'].create({
            'parent_id': self.partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'cooperator': False,
            'email': 'test@example.com',
            'lang': 'ca_ES',
        })

        queue_jobs_after = self.env['queue.job'].search_count([])

        self.assertEqual(queue_jobs_before, queue_jobs_after)
