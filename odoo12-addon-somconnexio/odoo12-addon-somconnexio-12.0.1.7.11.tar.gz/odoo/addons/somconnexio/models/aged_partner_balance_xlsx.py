from odoo import _, models


class AgedPartnerBalanceXslx(models.AbstractModel):
    _inherit = 'report.a_f_r.report_aged_partner_balance_xlsx'

    def _get_report_columns(self, report):
        if not report.show_move_line_details:
            ret = {
                0: {'header': _('Partner'), 'field': 'partner', 'width': 70},
                1: {'header': _('VAT'),
                    'field': 'vat',
                    'width': 14},
                2: {'header': _('Residual'),
                    'field': 'amount_residual',
                    'field_footer_total': 'cumul_amount_residual',
                    'type': 'amount',
                    'width': 14},
                3: {'header': _('Current'),
                    'field': 'current',
                    'field_footer_total': 'cumul_current',
                    'field_footer_percent': 'percent_current',
                    'type': 'amount',
                    'width': 14},
                4: {'header': _('Due'),
                    'field': 'amount_due',
                    'field_footer_total': 'cumul_amount_due',
                    'field_footer_percent': 'percent_amount_due',
                    'type': 'amount',
                    'width': 14},
                5: {'header': _(u'Age ≤ 30 d.'),
                    'field': 'age_30_days',
                    'field_footer_total': 'cumul_age_30_days',
                    'field_footer_percent': 'percent_age_30_days',
                    'type': 'amount',
                    'width': 14},
                6: {'header': _(u'Age ≤ 60 d.'),
                    'field': 'age_60_days',
                    'field_footer_total': 'cumul_age_60_days',
                    'field_footer_percent': 'percent_age_60_days',
                    'type': 'amount',
                    'width': 14},
                7: {'header': _(u'Age ≤ 90 d.'),
                    'field': 'age_90_days',
                    'field_footer_total': 'cumul_age_90_days',
                    'field_footer_percent': 'percent_age_90_days',
                    'type': 'amount',
                    'width': 14},
                8: {'header': _(u'Age ≤ 120 d.'),
                    'field': 'age_120_days',
                    'field_footer_total': 'cumul_age_120_days',
                    'field_footer_percent': 'percent_age_120_days',
                    'type': 'amount',
                    'width': 14},
                9: {'header': _('Older'),
                    'field': 'older',
                    'field_footer_total': 'cumul_older',
                    'field_footer_percent': 'percent_older',
                    'type': 'amount',
                    'width': 14},
            }
            if report.group_by_select == 'partner':
                ret[0]['field'] = 'name'
            return ret
        return {
            0: {'header': _('Date'), 'field': 'date', 'width': 11},
            1: {'header': _('Entry'), 'field': 'entry', 'width': 18},
            2: {'header': _('Journal'), 'field': 'journal', 'width': 8},
            3: {'header': _('Account'), 'field': 'account', 'width': 9},
            4: {'header': _('Partner'), 'field': 'partner', 'width': 25},
            5: {'header': _('VAT'), 'field': 'vat', 'width': 14},
            6: {'header': _('Ref - Label'), 'field': 'label', 'width': 40},
            7: {'header': _('Due date'), 'field': 'date_due', 'width': 11},
            8: {'header': _('Residual'),
                'field': 'amount_residual',
                'field_footer_total': 'cumul_amount_residual',
                'field_final_balance': 'amount_residual',
                'type': 'amount',
                'width': 14},
            9: {'header': _('Current'),
                'field': 'current',
                'field_footer_total': 'cumul_current',
                'field_footer_percent': 'percent_current',
                'field_final_balance': 'current',
                'type': 'amount',
                'width': 14},
            10: {'header': _('Due'),
                 'field': 'amount_due',
                 'field_footer_total': 'cumul_amount_due',
                 'field_footer_percent': 'percent_amount_due',
                 'field_final_balance': 'amount_due',
                 'type': 'amount',
                 'width': 14},
            11: {'header': _(u'Age ≤ 30 d.'),
                 'field': 'age_30_days',
                 'field_footer_total': 'cumul_age_30_days',
                 'field_footer_percent': 'percent_age_30_days',
                 'field_final_balance': 'age_30_days',
                 'type': 'amount',
                 'width': 14},
            12: {'header': _(u'Age ≤ 60 d.'),
                 'field': 'age_60_days',
                 'field_footer_total': 'cumul_age_60_days',
                 'field_footer_percent': 'percent_age_60_days',
                 'field_final_balance': 'age_60_days',
                 'type': 'amount',
                 'width': 14},
            13: {'header': _(u'Age ≤ 90 d.'),
                 'field': 'age_90_days',
                 'field_footer_total': 'cumul_age_90_days',
                 'field_footer_percent': 'percent_age_90_days',
                 'field_final_balance': 'age_90_days',
                 'type': 'amount',
                 'width': 14},
            14: {'header': _(u'Age ≤ 120 d.'),
                 'field': 'age_120_days',
                 'field_footer_total': 'cumul_age_120_days',
                 'field_footer_percent': 'percent_age_120_days',
                 'field_final_balance': 'age_120_days',
                 'type': 'amount',
                 'width': 14},
            15: {'header': _('Older'),
                 'field': 'older',
                 'field_footer_total': 'cumul_older',
                 'field_footer_percent': 'percent_older',
                 'field_final_balance': 'older',
                 'type': 'amount',
                 'width': 14},
        }

    def _generate_report_content(self, workbook, report):
        if not report.show_move_line_details:
            if report.group_by_select == 'account':
                super()._generate_report_content(workbook, report)
            else:
                self.write_array_header()
                for partner in report.partner_cummuls_ids:
                    self.write_line(partner)
        else:
            if report.group_by_select == 'account':
                super()._generate_report_content(workbook, report)
            else:
                for partner in report.partner_cummuls_ids:
                    # Write partner title
                    self.write_array_title(partner.name)

                    # Display array header for move lines
                    self.write_array_header()

                    # Display account move lines
                    for line in partner.move_line_ids:
                        self.write_line(line)

                    # Display ending balance line for partner
                    self.write_ending_balance(partner)

                    # Line break
                    self.row_pos += 1
