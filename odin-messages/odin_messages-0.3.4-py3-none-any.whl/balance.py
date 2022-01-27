from pydantic import BaseModel

class CoinBalance(BaseModel):
    coin: str
    balance: float
    used_balance: float