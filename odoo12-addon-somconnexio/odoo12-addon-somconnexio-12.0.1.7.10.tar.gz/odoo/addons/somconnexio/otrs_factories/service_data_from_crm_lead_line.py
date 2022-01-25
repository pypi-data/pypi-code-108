from ..otrs_factories.mobile_data_from_crm_lead_line \
    import MobileDataFromCRMLeadLine
from ..otrs_factories.fiber_data_from_crm_lead_line \
    import FiberDataFromCRMLeadLine
from ..otrs_factories.adsl_data_from_crm_lead_line \
    import ADSLDataFromCRMLeadLine


class ServiceDataFromCRMLeadLine:

    def __init__(self, crm_lead_line):
        self.crm_lead_line = crm_lead_line

    def build(self):
        if self.crm_lead_line.is_mobile:
            service_data = MobileDataFromCRMLeadLine(self.crm_lead_line)
        elif self.crm_lead_line.is_fiber:
            service_data = FiberDataFromCRMLeadLine(self.crm_lead_line)
        elif self.crm_lead_line.is_adsl:
            service_data = ADSLDataFromCRMLeadLine(self.crm_lead_line)

        return service_data.build()
