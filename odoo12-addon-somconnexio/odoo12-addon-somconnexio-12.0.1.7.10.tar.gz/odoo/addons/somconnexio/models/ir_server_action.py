# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

from odoo.addons.queue_job.job import job

_log = logging.getLogger(__name__)


class ServerActions(models.Model):
    """ Add email option in server actions. """
    _name = 'ir.actions.server'
    _description = 'Server Action'
    _inherit = ['ir.actions.server']

    state = fields.Selection(selection_add=[
        ('background_email', 'Send Email in Background'),
    ])

    def run_action_background_email(self, action, eval_context=None):
        self.with_delay()._send_background_email(
            action,
            _active_id=self.env.context["active_id"]
        )

    @job
    def _send_background_email(self, action, _active_id):
        self = self.with_context({
            "active_id": _active_id
        })
        eval_context = self._get_eval_context(action)

        _log.info("Sending email in background with context:\n{}".format(self._context))
        self.run_action_email(action, eval_context)
