from odoo.tests.common import SavepointCase
from odoo.addons.component.tests.common import ComponentMixin


class SCTestCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(SCTestCase, cls).setUpClass()
        # disable tracking test suite wise
        cls.env = cls.env(context=dict(
            cls.env.context,
            tracking_disable=True,
            test_queue_job_no_delay=True,  # no jobs thanks
        ))

    def setUp(self):
        # resolve an inheritance issue (SavepointCase does not call super)
        SavepointCase.setUp(self)


class SCComponentTestCase(SCTestCase, ComponentMixin):

    @classmethod
    def setUpClass(cls):
        super(SCComponentTestCase, cls).setUpClass()
        cls.setUpComponent()

    def setUp(self):
        # resolve an inheritance issue (SavepointCase does not call super)
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)
