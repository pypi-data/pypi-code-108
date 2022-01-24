# Used to craft the redirect destination for the UI after OIDC login
# NOTE: Use this line for local testing only!!
# DK_REDIRECT_URL = "http://localhost:4200/dk/index.html"
# Use this line for environments and normal prod
DK_REDIRECT_URL = "https://{subdomain}.datakitchen.io/dk/index.html"

# Used to craft the Discovery Document endpoint for getting OIDC Provider information
OIDC_WELL_KNOWN_ENDPOINT_SUFFIX = ".well-known/openid-configuration"
