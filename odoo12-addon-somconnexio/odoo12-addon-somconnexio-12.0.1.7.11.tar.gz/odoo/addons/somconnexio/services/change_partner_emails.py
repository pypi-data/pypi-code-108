from odoo import _

from odoo.addons.somconnexio.somoffice.user import SomOfficeUser


class ChangePartnerEmails:
    def __init__(self, env, partner):
        self.env = env
        self.partner = partner

    def change_contact_email(self, email):
        old_email = self._search_or_create_email()

        contracts = self.env["contract.contract"].search([
            ('partner_id', '=', self.partner.id)
        ]).filtered(lambda c: self.partner in c.email_ids)
        contracts.write(
            {
                'email_ids': [
                    (3, self.partner.id, 0),
                    (4, old_email.id, 0)
                ]
            }
        )
        self.partner.write(
            {'email': email.email}
        )
        message_partner = _("Email changed ({} --> {})")
        self.partner.message_post(
            message_partner.format(
                old_email.email,
                email.email
            )
        )
        return True

    def change_somoffice_email(self, email):
        SomOfficeUser(
            self.partner.ref,
            "",
            self.partner.vat,
            "",
        ).change_email(email.email)
        message_partner = _("OV Email changed to {}")
        self.partner.message_post(
            message_partner.format(
                email.email
            )
        )
        return True

    def change_contracts_emails(
            self,
            contracts,
            emails,
            activity_args):
        for contract in contracts:
            message_partner = _("Email changed ({} --> {}) in partner's contract '{}'")
            self.partner.message_post(
                message_partner.format(
                    ', '.join([email.email for email in contract.email_ids]),
                    ', '.join([email.email for email in emails]),
                    contract.name
                )
            )
            message_contract = _("Contract email changed ({} --> {})")
            contract.message_post(
                message_contract.format(
                    ', '.join([email.email for email in contract.email_ids]),
                    ', '.join([email.email for email in emails]),
                )
            )

            contract.write(
                {'email_ids': [(6, 0, [email.id for email in emails])]}
            )
            self._create_activity(
                contract.id,
                activity_args,
            )

        self._enqueue_OC_email_update(contracts)

        return True

    def _create_activity(self, contract_id, activity_args):
        activity_args.update({
            'res_id': contract_id,
        })
        self.env['mail.activity'].with_context(
            mail_create_nosubscribe=True
        ).create(activity_args)

    def _enqueue_OC_email_update(self, contracts):
        self.env['contract.contract'].with_delay(
            priority=50,
        ).update_subscription(
            contracts,
            "email"
        )

    def _search_or_create_email(self):
        """
        This method avoids duplicating emails.
        """
        email = self.env["res.partner"].search([
            ('parent_id', '=', self.partner.id),
            ('email', '=', self.partner.email),
            ('type', '=', 'contract-email'),
        ], limit=1)
        if not email:
            email = self.env["res.partner"].create(
                {
                    'email': self.partner.email,
                    'parent_id': self.partner.id,
                    'type': 'contract-email',
                }
            )
        return email
