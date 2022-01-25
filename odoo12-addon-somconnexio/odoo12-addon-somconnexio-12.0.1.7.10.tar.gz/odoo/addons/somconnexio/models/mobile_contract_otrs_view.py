from odoo import models


class MobileContractOTRSView(models.Model):
    _name = 'mobile.contract.otrs.view'
    _auto = False

    def init(self):
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                %s
            )
        ''' % (
            self._table, self._query()
        ))

    def _query(self):
        return '''
        SELECT DISTINCT ON (contract.id)
            contract.id AS contract_id,
            contract.code AS contract_code,
            contract.create_date AS contract_create_date,
            contract.is_terminated AS contract_is_terminated,
            contract.phone_number AS contract_phone_number,
            partner.vat AS partner_vat,
            partner.name AS partner_name,
            partner.ref AS partner_ref,
            partner.email AS partner_email,
            product.custom_name AS contract_current_tariff,
            contract_partner_rel.emails AS contract_emails,
            product.default_code AS contract_product_code
        FROM contract_contract contract
        INNER JOIN res_partner partner ON partner.id=contract.partner_id
        LEFT JOIN (
                SELECT rel.contract_contract_id, string_agg(p.email , ', ') AS emails
                FROM contract_contract_res_partner_rel AS rel
                INNER JOIN res_partner as p ON p.id = rel.res_partner_id
                GROUP BY rel.contract_contract_id
        ) contract_partner_rel ON contract_partner_rel.contract_contract_id=contract.id
        INNER JOIN contract_line line ON line.contract_id=contract.id
        INNER JOIN product_product product ON product.id=line.product_id
        INNER JOIN product_template prod_tmpl ON prod_tmpl.id=product.product_tmpl_id
        INNER JOIN product_category prod_categ ON prod_categ.id=prod_tmpl.categ_id
        WHERE contract.mobile_contract_service_info_id IS NOT NULL
            AND (
                (line.date_start <= CURRENT_DATE AND line.date_end IS NULL)
                OR (line.date_start <= CURRENT_DATE AND line.date_end >= CURRENT_DATE)
            )
            AND prod_categ.name='Mobile Service'
        ORDER BY contract.id
        '''
