"""
Providers
"""

# Alliance Auth
from esi.clients import EsiClientProvider

# Alliance Auth AFAT
from afat.constants import USER_AGENT

esi = EsiClientProvider(app_info_text=USER_AGENT)
