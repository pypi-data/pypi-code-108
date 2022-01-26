from msal_extensions import TokenCache

from .config import SAVED_MSAL_TOKEN_CACHE_PATH

token_cache = TokenCache(SAVED_MSAL_TOKEN_CACHE_PATH)
