from odoo import api, models


class IrModelData(models.TransientModel):
    _name = 'somconnexio.module'

    @api.model
    def load_fiscal_location(self):
        account = self.env['account.account'].search([
            ('code', '=', '12000017')
        ])
        if account:
            return True

        chart_template_id = self.env.ref("somconnexio.account_chart_template_sc")
        chart_template_id.load_for_current_company(15.0, 15.0)

    @api.model
    def import_bank_data(self):
        bank_data_wizard = self.sudo().env["l10n.es.partner.import.wizard"].create({})
        bank_data_wizard.execute()

    @api.model
    def install_languages(self):
        installer = self.sudo().env['base.language.install'].create({'lang': 'es_ES'})
        installer.lang_install()
        installer = self.sudo().env['base.language.install'].create({'lang': 'ca_ES'})
        installer.lang_install()

    @api.model
    def disable_company_noupdate(self):
        company_imd = self.env['ir.model.data'].search([
            ('name', '=', 'main_company')
        ])
        company_imd.noupdate = False

    @api.model
    def clean_demo_data(self):
        account_invoice_ids = [
            imd.res_id
            for imd in
            self.env['ir.model.data'].search([
                ('model', '=', 'account.invoice'),
                ('module', '=', 'l10n_generic_coa')
            ])
        ]
        bank_statement_ids = [
            imd.res_id
            for imd in
            self.env['ir.model.data'].search([
                ('model', '=', 'account.bank.statement'),
                ('module', '=', 'l10n_generic_coa')
            ])
        ]
        account_invoices = self.env['account.invoice'].search(
            [('id', 'in', account_invoice_ids)]
        )
        bank_statements = self.env['account.bank.statement'].search(
            [('id', 'in', bank_statement_ids)]
        )
        if account_invoices or bank_statements:
            self.env.cr.execute('DELETE FROM account_move_line')
            self.env.cr.execute(
                'DELETE FROM account_invoice WHERE id IN %s',
                (tuple(account_invoices.mapped('id')),)
            )
            self.env.cr.execute(
                'DELETE FROM account_bank_statement WHERE id IN %s',
                (tuple(bank_statements.mapped('id')),)
            )

        pricelists = self.env['product.pricelist'].search(
            [('code', '=', False)]
        )

        if pricelists:
            self.env.cr.execute(
                'DELETE FROM product_pricelist_item WHERE pricelist_id IN %s',
                (tuple(pricelists.mapped('id')),)
            )
            self.env.cr.execute(
                'DELETE FROM sale_order_line '
                'WHERE id in ('
                'SELECT sol.id FROM sale_order_line sol '
                'INNER JOIN sale_order so ON so.id = sol.order_id '
                'WHERE so.pricelist_id IN %s)',
                (tuple(pricelists.mapped('id')),)
            )
            self.env.cr.execute(
                'DELETE FROM sale_order WHERE pricelist_id IN %s',
                (tuple(pricelists.mapped('id')),)
            )
            self.env.cr.execute(
                'DELETE FROM product_pricelist WHERE id IN %s',
                (tuple(pricelists.mapped('id')),)
            )

    @api.model
    def disable_admin_noupdate(self):
        admin_imd = self.env['ir.model.data'].search([
            ('name', '=', 'user_admin'),
            ('module', '=', 'base'),
        ])
        admin_imd.noupdate = False

    @api.model
    def restore_admin_noupdate(self):
        admin_imd = self.env['ir.model.data'].search([
            ('name', '=', 'user_admin'),
            ('module', '=', 'base'),
        ])
        admin_imd.noupdate = True

    @api.model
    def disable_crm_lead_stages_noupdate(self):
        stages = self.env['ir.model.data'].search([
            ('name', 'in', ('stage_lead2', 'stage_lead3')),
            ('module', '=', 'crm'),
        ])
        for stage in stages:
            stage.noupdate = False

    @api.model
    def restore_crm_lead_stages_noupdate(self):
        stages = self.env['ir.model.data'].search([
            ('name', 'in', ('stage_lead2', 'stage_lead3')),
            ('module', '=', 'crm'),
        ])
        for stage in stages:
            stage.noupdate = True
