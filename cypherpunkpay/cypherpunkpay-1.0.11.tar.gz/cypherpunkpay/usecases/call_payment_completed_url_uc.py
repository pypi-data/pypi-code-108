import logging as log

from cypherpunkpay.usecases.call_merchant_base_uc import CallMerchantBaseUC


class CallPaymentCompletedUrlUC(CallMerchantBaseUC):

    def exec(self):
        if not self._config.merchant_enabled() or \
           not self._charge.merchant_order_id or \
           not self._charge.is_completed():
            return

        log.debug(f'Notifying merchant on status=completed for {self._charge.short_uid()}')

        url = self._config.payment_completed_notification_url()
        body = f"""
{{
  "untrusted": {{
    "merchant_order_id": "{self._charge.merchant_order_id}",
    "total": "{format(self._charge.total, 'f')}",
    "currency": "{self._charge.currency.casefold()}"
  }},
  "status": "completed",
  "cc_total": "{format(self._charge.cc_total, 'f')}",
  "cc_currency": "{self._charge.cc_currency.casefold()}"
}}""".strip()

        self.call_merchant_and_mark_as_done(url, body)
