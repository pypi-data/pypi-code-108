import asyncio

async def time_to_minute(str) -> int:
    """Sometime API returning movie length as str e.g. \'1:46\'. So that this function just getting minuts from it string"""
    return (x * int(t) for x, t in zip([60, 1], str.split(':')))