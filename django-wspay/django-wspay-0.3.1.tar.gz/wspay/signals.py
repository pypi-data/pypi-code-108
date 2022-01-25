from django.dispatch import Signal

pay_request_created = Signal()
pay_request_updated = Signal()
transaction_updated = Signal()
process_response_pre_redirect = Signal()
