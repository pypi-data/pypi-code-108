import inspect
import logging

log = logging.getLogger(__name__)

class ValidateArgs:
    """
    Decorator for validating parameters of function
    """
    def __init__(self, validator, throw=True):
        self.__dict__.update({k: v for k, v in locals().items() if not (k.startswith("__") or k is "self")})

    def __call__(self, fn):
        self.sig = inspect.signature(fn)

        def _validate(*args, **kwargs):
            try:
                args_ = self.sig.bind(*args, **kwargs)
                args_.apply_defaults()
                self.validator(**args_.arguments)
            except Exception as ex:
                if not self.throw:
                    log.warning(f"Validator failed for {fn}", exc_info=ex)
                else:
                    raise ex

            return fn(*args, **kwargs)
        return _validate