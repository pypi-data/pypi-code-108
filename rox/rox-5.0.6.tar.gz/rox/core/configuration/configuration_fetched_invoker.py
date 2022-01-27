from rox.core.error_handling.exception_trigger import ExceptionTrigger

class ConfigurationFetchedInvoker:
    def __init__(self, user_unhandled_error_invoker):
        self.configuration_fetched_handlers = []
        self.user_unhandled_error_invoker = user_unhandled_error_invoker

    def invoke(self, fetcher_status, creation_date, has_changes):
        self.raise_configuration_fetched_event(ConfigurationFetchedArgs(fetcher_status=fetcher_status, creation_date=creation_date, has_changes=has_changes))

    def invoke_error(self, error_details):
        self.raise_configuration_fetched_event(ConfigurationFetchedArgs(error_details=error_details))

    def register_configuration_fetched_handler(self, handler):
        self.configuration_fetched_handlers.append(handler)

    def raise_configuration_fetched_event(self, args):
        for handler in self.configuration_fetched_handlers:
            try:
                handler(args)
            except Exception as ex:
                self.user_unhandled_error_invoker.invoke(handler, ExceptionTrigger.CONFIGURATION_FETCHED_HANDLER, ex)

class ConfigurationFetchedArgs:
    def __init__(self, fetcher_status=None, creation_date=None, has_changes=None, error_details=None):
        self.fetcher_status = fetcher_status or (FetcherStatus.ERROR_FETCHED_FAILED if error_details else fetcher_status)
        self.creation_date = creation_date
        self.has_changes = False if has_changes is None else has_changes
        self.error_details = error_details or FetcherError.NO_ERROR

    def __repr__(self):
        return "ConfigurationFetchedArgs(%r, %r, %r, %r)" % (self.fetcher_status, self.creation_date, self.has_changes, self.error_details)

    def __str__(self):
        return "ConfigurationFetchedArgs(%s, %s, %s, %s)" % (self.fetcher_status, self.creation_date, self.has_changes, self.error_details)


class FetcherError:
    CORRUPTED_JSON = 'CorruptedJson'
    EMPTY_JSON = 'EmptyJson'
    SIGNATURE_VERIFICATION_ERROR = 'SignatureVerificationError'
    NETWORK_ERROR = 'NetworkError'
    MISMATCH_APP_KEY = 'MismatchAppKey'
    UNKNOWN = 'Unknown'
    NO_ERROR = 'NoError'


class FetcherStatus:
    APPLIED_FROM_EMBEDDED = 'AppliedFromEmbedded'
    APPLIED_FROM_LOCAL_STORAGE = 'AppliedFromLocalStorage'
    APPLIED_FROM_NETWORK = 'AppliedFromNetwork'
    ERROR_FETCHED_FAILED = 'ErrorFetchedFailed'
