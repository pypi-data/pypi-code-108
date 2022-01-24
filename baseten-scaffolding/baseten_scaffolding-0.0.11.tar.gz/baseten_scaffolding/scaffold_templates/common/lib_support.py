try:
    import kfserving
    KFSERVING_LIB = True
except ModuleNotFoundError:
    KFSERVING_LIB = False

try:
    import sentry_sdk
    SENTRY_SDK = True
except ModuleNotFoundError:
    SENTRY_SDK = False

def ensure_kfserving_installed():
    if not KFSERVING_LIB:
        raise ModuleNotFoundError('Could not successfully import "kfserving" package, check your Python environment')
    return True

def ensure_sentry_sdk_installed():
    if not SENTRY_SDK:
        raise ModuleNotFoundError('Could not successfully import "sentry_sdk" package, check your Python environment')
    return True
