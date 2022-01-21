from zygoat_django.settings.environment import prod_required_env, DEBUG, env

# production must use SMTP. others will use DJANGO_EMAIL_BACKEND or default to "console"
EMAIL_BACKEND = "django.core.mail.backends.{}.EmailBackend".format(
    env.str("DJANGO_EMAIL_BACKEND", default="console") if DEBUG else "smtp"
)
EMAIL_HOST = "email-smtp.us-east-1.amazonaws.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = prod_required_env("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = prod_required_env("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = True
