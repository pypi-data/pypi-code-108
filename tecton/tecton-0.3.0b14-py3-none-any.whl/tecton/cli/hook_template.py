PLAN_TEMPLATE = """
from typing import Optional

def run() -> Optional[int]:
    # No-op plan hook that returns None indicating no tests we run.
    # See https://docs.tecton.ai/v2/examples/using-plan-hooks.html for more info.
    return None
"""
