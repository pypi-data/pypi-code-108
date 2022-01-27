from security.throttling.validators import PerRequestThrottlingValidator


default_validators = (
    PerRequestThrottlingValidator(60, 2),
)
