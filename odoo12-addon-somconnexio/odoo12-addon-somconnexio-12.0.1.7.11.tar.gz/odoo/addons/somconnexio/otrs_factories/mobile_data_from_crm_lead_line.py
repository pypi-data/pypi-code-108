from otrs_somconnexio.otrs_models.mobile_data import MobileData


class MobileDataFromCRMLeadLine:

    def __init__(self, crm_lead_line):
        self.crm_lead_line = crm_lead_line

    def build(self):
        isp_info = self.crm_lead_line.mobile_isp_info

        return MobileData(
            order_id=self.crm_lead_line.id,
            phone_number=isp_info.phone_number,
            iban=self.crm_lead_line.lead_id.iban,
            email=self.crm_lead_line.lead_id.email_from,
            notes=self.crm_lead_line.lead_id.description,
            previous_provider=isp_info.previous_provider.code or 'None',
            previous_owner_vat=isp_info.previous_owner_vat_number or '',
            previous_owner_name=isp_info.previous_owner_first_name or '',
            previous_owner_surname=isp_info.previous_owner_name or '',
            sc_icc=isp_info.icc,
            icc=isp_info.icc_donor,
            portability=self._portability(),
            product=self.crm_lead_line.product_id.default_code,
            has_sim=isp_info.has_sim,
        )

    def _portability(self):
        if self.crm_lead_line.mobile_isp_info.type == 'new':
            return False
        return True
