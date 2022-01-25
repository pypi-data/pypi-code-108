from odoo.addons.mail.models.mail_activity import MailActivity
from odoo import api, fields
from odoo.addons.account_payment_return_import.wizard.payment_return_import import PaymentReturnImport # noqa
from odoo.addons.base_rest.http import HttpRestRequest
import logging
import json
_logger = logging.getLogger(__name__)
try:
    import pyquerystring
except (ImportError, IOError) as err:
    _logger.debug(err)


def post_load_hook():

    def new_action_feedback(self, feedback=False):

        if 'done' not in self._fields:
            return self.action_feedback_original_sc(feedback=feedback)
        message = self.env['mail.message']
        if feedback:
            self.write(dict(feedback=feedback))
        for activity in self:
            record = self.env[activity.res_model].browse(activity.res_id)
            activity.done = True
            if not activity.date_done:
                activity.date_done = fields.Date.today()
            record.message_post_with_view(
                'mail.message_activity_done',
                values={'activity': activity},
                subtype_id=self.env.ref('mail.mt_activities').id,
                mail_activity_type_id=activity.activity_type_id.id,
            )
            message |= record.message_ids[0]
        return message.ids and message.ids[0] or False

    if not hasattr(MailActivity, 'action_feedback_original_sc'):
        MailActivity.action_feedback_original_sc = MailActivity.action_feedback
        MailActivity.action_feedback = new_action_feedback

    @api.model
    def _get_journal(self, bank_account_id):
        """ Find the journal """
        # Find the journal from context, wizard or bank account
        journal_id = self.env.context.get('journal_id') or self.journal_id.id
        return journal_id

    if not hasattr(PaymentReturnImport, '_get_journal_original'):
        PaymentReturnImport._get_journal_original = PaymentReturnImport._get_journal
        PaymentReturnImport._get_journal = _get_journal

    def __init__(self, httprequest):
        _logger.info("Enter patched constructor")
        super(HttpRestRequest, self).__init__(httprequest)
        if self.httprequest.mimetype == "application/json":
            data = self.httprequest.get_data().decode(self.httprequest.charset)
            if data[0:5] == "body=":
                data = data.replace("body=", "")
            self.params = json.loads(data)
        else:
            # We reparse the query_string in order to handle data structure
            # more information on https://github.com/aventurella/pyquerystring
            self.params = pyquerystring.parse(
                self.httprequest.query_string.decode("utf-8")
            )
        self._determine_context_lang()

    if not hasattr(HttpRestRequest, '__init__original'):
        HttpRestRequest.__init__original = HttpRestRequest.__init__
        HttpRestRequest.__init__ = __init__
