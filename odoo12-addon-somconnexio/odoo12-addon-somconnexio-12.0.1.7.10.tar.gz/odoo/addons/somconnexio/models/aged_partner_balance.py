from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class AgedPartnerBalanceReport(models.TransientModel):
    _inherit = 'report_aged_partner_balance'
    partner_cummuls_ids = fields.One2many(
        comodel_name='report_aged_partner_balance_partner_cummul',
        inverse_name='report_id'
    )
    group_by_select = fields.Selection([
        ('account', _('Account')),
        ('partner', _('Partner')),
    ], 'Group by', default='account')


class AgedPartnerBalanceReportAccount(models.TransientModel):
    _inherit = 'report_aged_partner_balance_account'
    cumul_amount_due = fields.Float(digits=(16, 2))
    percent_amount_due = fields.Float(digits=(16, 2))


class AgedPartnerBalanceReportLine(models.TransientModel):
    _inherit = 'report_aged_partner_balance_line'
    amount_due = fields.Float(digits=(16, 2))
    vat = fields.Char()


class AgedPartnerBalanceReportMoveLine(models.TransientModel):
    _inherit = 'report_aged_partner_balance_move_line'
    amount_due = fields.Float(digits=(16, 2))
    partner_cummul_id = fields.Many2one(
        'report_aged_partner_balance_partner_cummul',
        index=True
    )
    vat = fields.Char()


class AgedPartnerBalanceReportCompute(models.TransientModel):
    _inherit = 'report_aged_partner_balance'

    def _inject_account_values(self):
        """Inject report values for report_aged_partner_balance_account"""
        query_inject_account = """
INSERT INTO
    report_aged_partner_balance_account
    (
    report_id,
    create_uid,
    create_date,
    account_id,
    code,
    name
    )
SELECT
    %s AS report_id,
    %s AS create_uid,
    NOW() AS create_date,
    rao.account_id,
    rao.code,
    rao.name
FROM
    report_open_items_account rao
WHERE
    rao.report_id = %s
        """
        query_inject_account_params = (
            self.id,
            self.env.uid,
            self.open_items_id.id,
        )
        self.env.cr.execute(query_inject_account, query_inject_account_params)

    def _inject_line_values(self, only_empty_partner_line=False):
        """ Inject report values for report_aged_partner_balance_line.

        The "only_empty_partner_line" value is used
        to compute data without partner.
        """
        query_inject_line = """
WITH
    date_range AS
        (
            SELECT
                DATE %s AS date_current,
                DATE %s - INTEGER '30' AS date_less_30_days,
                DATE %s - INTEGER '60' AS date_less_60_days,
                DATE %s - INTEGER '90' AS date_less_90_days,
                DATE %s - INTEGER '120' AS date_less_120_days
        )
INSERT INTO
    report_aged_partner_balance_line
    (
        report_partner_id,
        create_uid,
        create_date,
        partner,
        vat,
        amount_residual,
        current,
        age_30_days,
        age_60_days,
        age_90_days,
        age_120_days,
        older,
        amount_due
    )
SELECT
    rp.id AS report_partner_id,
    %s AS create_uid,
    NOW() AS create_date,
    rp.name,
    MAX(p.vat),
    SUM(rlo.amount_residual) AS amount_residual,
    SUM(
        CASE
            WHEN rlo.date_due >= date_range.date_current
            THEN rlo.amount_residual
        END
    ) AS current,
    SUM(
        CASE
            WHEN
                rlo.date_due >= date_range.date_less_30_days
                AND rlo.date_due < date_range.date_current
            THEN rlo.amount_residual
        END
    ) AS age_30_days,
    SUM(
        CASE
            WHEN
                rlo.date_due >= date_range.date_less_60_days
                AND rlo.date_due < date_range.date_less_30_days
            THEN rlo.amount_residual
        END
    ) AS age_60_days,
    SUM(
        CASE
            WHEN
                rlo.date_due >= date_range.date_less_90_days
                AND rlo.date_due < date_range.date_less_60_days
            THEN rlo.amount_residual
        END
    ) AS age_90_days,
    SUM(
        CASE
            WHEN
                rlo.date_due >= date_range.date_less_120_days
                AND rlo.date_due < date_range.date_less_90_days
            THEN rlo.amount_residual
        END
    ) AS age_120_days,
    SUM(
        CASE
            WHEN rlo.date_due < date_range.date_less_120_days
            THEN rlo.amount_residual
        END
    ) AS older,
    SUM(
        CASE
            WHEN rlo.date_due < date_range.date_current
            THEN rlo.amount_residual
        END
    ) AS amount_due
FROM
    date_range,
    report_open_items_move_line rlo
INNER JOIN
    report_open_items_partner rpo ON rlo.report_partner_id = rpo.id
INNER JOIN
    report_open_items_account rao ON rpo.report_account_id = rao.id
INNER JOIN
    report_aged_partner_balance_account ra ON rao.code = ra.code
INNER JOIN
    report_aged_partner_balance_partner rp
        ON
            ra.id = rp.report_account_id
INNER JOIN
    res_partner p
        ON
            p.id = rp.partner_id
        """
        if not only_empty_partner_line:
            query_inject_line += """
        AND rpo.partner_id = rp.partner_id
            """
        elif only_empty_partner_line:
            query_inject_line += """
        AND rpo.partner_id IS NULL
        AND rp.partner_id IS NULL
            """
        query_inject_line += """
WHERE
    rao.report_id = %s
AND ra.report_id = %s
GROUP BY
    rp.id
        """
        query_inject_line_params = (self.date_at,) * 5
        query_inject_line_params += (
            self.env.uid,
            self.open_items_id.id,
            self.id,
        )
        self.env.cr.execute(query_inject_line, query_inject_line_params)

    def _inject_move_line_values(self, only_empty_partner_line=False):
        """ Inject report values for report_aged_partner_balance_move_line

        The "only_empty_partner_line" value is used
        to compute data without partner.
        """
        query_inject_move_line = """
    WITH
        date_range AS
            (
                SELECT
                    DATE %s AS date_current,
                    DATE %s - INTEGER '30' AS date_less_30_days,
                    DATE %s - INTEGER '60' AS date_less_60_days,
                    DATE %s - INTEGER '90' AS date_less_90_days,
                    DATE %s - INTEGER '120' AS date_less_120_days
            )
    INSERT INTO
        report_aged_partner_balance_move_line
        (
            report_partner_id,
            create_uid,
            create_date,
            move_line_id,
            date,
            date_due,
            entry,
            journal,
            account,
            partner,
            vat,
            label,
            amount_residual,
            current,
            age_30_days,
            age_60_days,
            age_90_days,
            age_120_days,
            older,
            amount_due
        )
    SELECT
        rp.id AS report_partner_id,
        %s AS create_uid,
        NOW() AS create_date,
        rlo.move_line_id,
        rlo.date,
        rlo.date_due,
        rlo.entry,
        rlo.journal,
        rlo.account,
        rlo.partner,
        p.vat,
        rlo.label,
        rlo.amount_residual AS amount_residual,
        CASE
            WHEN rlo.date_due >= date_range.date_current
            THEN rlo.amount_residual
        END AS current,
        CASE
            WHEN
                rlo.date_due >= date_range.date_less_30_days
                AND rlo.date_due < date_range.date_current
            THEN rlo.amount_residual
        END AS age_30_days,
        CASE
            WHEN
                rlo.date_due >= date_range.date_less_60_days
                AND rlo.date_due < date_range.date_less_30_days
            THEN rlo.amount_residual
        END AS age_60_days,
        CASE
            WHEN
                rlo.date_due >= date_range.date_less_90_days
                AND rlo.date_due < date_range.date_less_60_days
            THEN rlo.amount_residual
        END AS age_90_days,
        CASE
            WHEN
                rlo.date_due >= date_range.date_less_120_days
                AND rlo.date_due < date_range.date_less_90_days
            THEN rlo.amount_residual
        END AS age_120_days,
        CASE
            WHEN rlo.date_due < date_range.date_less_120_days
            THEN rlo.amount_residual
        END AS older,
        CASE
            WHEN rlo.date_due < date_range.date_current
            THEN rlo.amount_residual
        END AS amount_due
    FROM
        date_range,
        report_open_items_move_line rlo
    INNER JOIN
        report_open_items_partner rpo ON rlo.report_partner_id = rpo.id
    INNER JOIN
        report_open_items_account rao ON rpo.report_account_id = rao.id
    INNER JOIN
        report_aged_partner_balance_account ra ON rao.code = ra.code
    INNER JOIN
        report_aged_partner_balance_partner rp
            ON
                ra.id = rp.report_account_id
    INNER JOIN
        res_partner p
            ON p.id=rp.partner_id
        """
        if not only_empty_partner_line:
            query_inject_move_line += """
        AND rpo.partner_id = rp.partner_id
            """
        elif only_empty_partner_line:
            query_inject_move_line += """
        AND rpo.partner_id IS NULL
        AND rp.partner_id IS NULL
            """
        query_inject_move_line += """
    WHERE
        rao.report_id = %s
    AND ra.report_id = %s
            """
        query_inject_move_line_params = (self.date_at,) * 5
        query_inject_move_line_params += (
            self.env.uid,
            self.open_items_id.id,
            self.id,
        )
        self.env.cr.execute(query_inject_move_line,
                            query_inject_move_line_params)

    def _compute_accounts_cumul(self):
        """ Compute cumulative amount for
        report_aged_partner_balance_account.
        """
        query_compute_accounts_cumul = """
WITH
    cumuls AS
        (
            SELECT
                ra.id AS report_account_id,
                SUM(rl.amount_residual) AS cumul_amount_residual,
                SUM(rl.current) AS cumul_current,
                SUM(rl.age_30_days) AS cumul_age_30_days,
                SUM(rl.age_60_days) AS cumul_age_60_days,
                SUM(rl.age_90_days) AS cumul_age_90_days,
                SUM(rl.age_120_days) AS cumul_age_120_days,
                SUM(rl.older) AS cumul_older,
                SUM(rl.amount_due) as cumul_amount_due
            FROM
                report_aged_partner_balance_line rl
            INNER JOIN
                report_aged_partner_balance_partner rp
                    ON rl.report_partner_id = rp.id
            INNER JOIN
                report_aged_partner_balance_account ra
                    ON rp.report_account_id = ra.id
            WHERE
                ra.report_id = %s
            GROUP BY
                ra.id
        )
UPDATE
    report_aged_partner_balance_account
SET
    cumul_amount_residual = c.cumul_amount_residual,
    cumul_current = c.cumul_current,
    cumul_amount_due = c.cumul_amount_due,
    cumul_age_30_days = c.cumul_age_30_days,
    cumul_age_60_days = c.cumul_age_60_days,
    cumul_age_90_days = c.cumul_age_90_days,
    cumul_age_120_days = c.cumul_age_120_days,
    cumul_older = c.cumul_older,
    percent_current =
        CASE
            WHEN c.cumul_amount_residual != 0
            THEN 100 * c.cumul_current / c.cumul_amount_residual
        END,
    percent_amount_due =
        CASE
            WHEN c.cumul_amount_residual != 0
            THEN 100 * c.cumul_amount_due / c.cumul_amount_residual
        END,
    percent_age_30_days =
        CASE
            WHEN c.cumul_amount_residual != 0
            THEN 100 * c.cumul_age_30_days / c.cumul_amount_residual
        END,
    percent_age_60_days =
        CASE
            WHEN c.cumul_amount_residual != 0
            THEN 100 * c.cumul_age_60_days / c.cumul_amount_residual
        END,
    percent_age_90_days =
        CASE
            WHEN c.cumul_amount_residual != 0
            THEN 100 * c.cumul_age_90_days / c.cumul_amount_residual
        END,
    percent_age_120_days =
        CASE
            WHEN c.cumul_amount_residual != 0
            THEN 100 * c.cumul_age_120_days / c.cumul_amount_residual
        END,
    percent_older =
        CASE
            WHEN c.cumul_amount_residual != 0
            THEN 100 * c.cumul_older / c.cumul_amount_residual
        END
FROM
    cumuls c
WHERE
    id = c.report_account_id
        """
        params_compute_accounts_cumul = (self.id,)
        self.env.cr.execute(query_compute_accounts_cumul,
                            params_compute_accounts_cumul)

    def _compute_partners_cumul(self):
        """ Compute cumulative amount for
        report_aged_partner_balance_partner.
        """
        query_compute_partners_cumul = """
WITH
    cumuls AS
        (
            SELECT
                MAX(ra.report_id) AS report_id,
                rp.partner_id AS partner_id,
                SUM(rl.amount_residual) AS amount_residual,
                SUM(rl.current) AS current,
                SUM(rl.age_30_days) AS age_30_days,
                SUM(rl.age_60_days) AS age_60_days,
                SUM(rl.age_90_days) AS age_90_days,
                SUM(rl.age_120_days) AS age_120_days,
                SUM(rl.older) AS older,
                SUM(rl.amount_due) as amount_due
            FROM
                report_aged_partner_balance_line rl
            INNER JOIN
                report_aged_partner_balance_partner rp
                    ON rl.report_partner_id = rp.id
            INNER JOIN
                report_aged_partner_balance_account ra
                    ON rp.report_account_id = ra.id
            WHERE
                ra.report_id = %s
            GROUP BY
                rp.partner_id
        )
INSERT INTO
    report_aged_partner_balance_partner_cummul
    (
        create_uid,
        create_date,
        report_id,
        partner_id,
        name,
        vat,
        amount_residual,
        current,
        amount_due,
        age_30_days,
        age_60_days,
        age_90_days,
        age_120_days,
        older,
        percent_current,
        percent_amount_due,
        percent_age_30_days,
        percent_age_60_days,
        percent_age_90_days,
        percent_age_120_days,
        percent_older
    )
SELECT
    %s AS create_uid,
    NOW() AS create_date,
    c.report_id AS report_id,
    rp.id AS partner_id,
    rp.name AS name,
    rp.vat AS vat,
    c.amount_residual AS amount_residual,
    c.current AS current,
    c.amount_due AS amount_due,
    c.age_30_days AS age_30_days,
    c.age_60_days AS age_60_days,
    c.age_90_days AS age_90_days,
    c.age_120_days AS age_120_days,
    c.older AS older,
    CASE
        WHEN c.amount_residual != 0
        THEN 100 * c.current / c.amount_residual
    END AS percent_current,
    CASE
        WHEN c.amount_residual != 0
        THEN 100 * c.amount_due / c.amount_residual
    END AS percent_amount_due,
    CASE
        WHEN c.amount_residual != 0
        THEN 100 * c.age_30_days / c.amount_residual
    END AS percent_age_30_days,
    CASE
        WHEN c.amount_residual != 0
        THEN 100 * c.age_60_days / c.amount_residual
    END AS percent_age_60_days,
    CASE
        WHEN c.amount_residual != 0
        THEN 100 * c.age_90_days / c.amount_residual
    END AS percent_age_90_days,
    CASE
        WHEN c.amount_residual != 0
        THEN 100 * c.age_120_days / c.amount_residual
    END AS percent_age_120_days,
    CASE
        WHEN c.amount_residual != 0
        THEN 100 * c.older / c.amount_residual
    END AS percent_older
FROM
    cumuls c
INNER JOIN
    res_partner rp
        ON rp.id = c.partner_id
        """
        params_compute_partners_cumul = (
            self.id, self.env.uid
        )
        self.env.cr.execute(query_compute_partners_cumul,
                            params_compute_partners_cumul)

    def _compute_partners_move_line_cummul(self):
        """ Link report_aged_partner_balance_move_line
        report_aged_partner_balance_partner_cummul.
        """
        query_compute_move_line_cumul = """
    WITH
        cumuls AS
            (
                SELECT
                    rml.id AS report_move_line_id,
                    rpc.id AS partner_cummul_id
                FROM
                    report_aged_partner_balance_move_line rml
                INNER JOIN
                    report_aged_partner_balance_partner rp
                        ON rml.report_partner_id = rp.id
                INNER JOIN
                    report_aged_partner_balance_account ra
                        ON rp.report_account_id = ra.id
                INNER JOIN
                    report_aged_partner_balance_partner_cummul rpc
                        ON rp.partner_id = rpc.partner_id
                            AND rpc.report_id = ra.report_id
                WHERE
                    ra.report_id = %s
            )
    UPDATE
        report_aged_partner_balance_move_line
    SET
        partner_cummul_id = c.partner_cummul_id
    FROM
        cumuls c
    WHERE
        id = c.report_move_line_id
        """
        params_compute_move_line_cumul = (
            self.id,
        )
        self.env.cr.execute(
            query_compute_move_line_cumul,
            params_compute_move_line_cumul
        )

    def _inject_partner_values(self):
        """Inject report values for report_aged_partner_balance_partner"""
        query_inject_partner = """
    INSERT INTO
        report_aged_partner_balance_partner
        (
        report_account_id,
        create_uid,
        create_date,
        partner_id,
        name,
        vat
        )
    SELECT
        ra.id AS report_account_id,
        %s AS create_uid,
        NOW() AS create_date,
        rpo.partner_id,
        rpo.name,
        rp.vat
    FROM
        report_open_items_partner rpo
    INNER JOIN
        res_partner rp ON rpo.partner_id = rp.id
    INNER JOIN
        report_open_items_account rao ON rpo.report_account_id = rao.id
    INNER JOIN
        report_aged_partner_balance_account ra ON rao.code = ra.code
    WHERE
        rao.report_id = %s
    AND ra.report_id = %s
        """
        query_inject_partner_params = (
            self.env.uid,
            self.open_items_id.id,
            self.id,
        )
        self.env.cr.execute(query_inject_partner, query_inject_partner_params)

    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()
        # Compute Open Items Report Data.
        # The data of Aged Partner Balance Report
        # are based on Open Items Report data.
        model = self.env['report_open_items']
        self.open_items_id = model.create(self._prepare_report_open_items())
        self.open_items_id.compute_data_for_report()

        # Compute report data
        self._inject_account_values()
        self._inject_partner_values()
        self._inject_line_values()
        self._inject_line_values(only_empty_partner_line=True)
        if self.show_move_line_details:
            self._inject_move_line_values()
            self._inject_move_line_values(only_empty_partner_line=True)
        if self.group_by_select == 'partner':
            self._compute_partners_cumul()
            if self.show_move_line_details:
                self._compute_partners_move_line_cummul()
        else:
            self._compute_accounts_cumul()
        # Refresh cache because all data are computed with SQL requests
        self.invalidate_cache()


class AgedPartnerBalanceReportPartnerCummul(models.TransientModel):
    _name = 'report_aged_partner_balance_partner_cummul'
    _inherit = 'account_financial_report_abstract'
    # Data fields, used to keep link with real object
    partner_id = fields.Many2one(
        'res.partner',
        index=True
    )

    # Data fields, used for report display
    name = fields.Char()
    vat = fields.Char()
    report_id = fields.Many2one(
        comodel_name='report_aged_partner_balance',
        ondelete='cascade',
        index=True
    )
    move_line_ids = fields.One2many(
        comodel_name='report_aged_partner_balance_move_line',
        inverse_name='partner_cummul_id'
    )

    amount_residual = fields.Float(digits=(16, 2))
    amount_due = fields.Float(digits=(16, 2))
    current = fields.Float(digits=(16, 2))
    age_30_days = fields.Float(digits=(16, 2))
    age_60_days = fields.Float(digits=(16, 2))
    age_90_days = fields.Float(digits=(16, 2))
    age_120_days = fields.Float(digits=(16, 2))
    older = fields.Float(digits=(16, 2))

    percent_current = fields.Float(digits=(16, 2))
    percent_age_30_days = fields.Float(digits=(16, 2))
    percent_age_60_days = fields.Float(digits=(16, 2))
    percent_age_90_days = fields.Float(digits=(16, 2))
    percent_age_120_days = fields.Float(digits=(16, 2))
    percent_older = fields.Float(digits=(16, 2))
    percent_amount_due = fields.Float(digits=(16, 2))


class AgedPartnerBalanceReportPartner(models.TransientModel):
    _inherit = 'report_aged_partner_balance_partner'
    vat = fields.Char()
