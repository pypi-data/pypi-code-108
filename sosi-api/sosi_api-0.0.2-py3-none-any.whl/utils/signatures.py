import hashlib
import hmac
import urllib


def hmac_sha256(msg:str, key:str)-> str:
    return hmac.new(key.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).hexdigest()


def sign_message(msg:str, kind:str, key:str, **kwargs)-> str:
    """Given a messge string, sign it given the key and name of signing algo.
    
    Note: 
        For arguments other than `params`, it is preferable to pass them as
        keyword arguments, as the order of the arguments cannot be guaranteed in
        future versions.
    """
    # Signing functions available
    signature_func_mapper = dict(
        hmac_sha256 = hmac_sha256,
    )    

    # Determine which function to use to sign the params
    signature_func = signature_func_mapper.get(kind)
    if signature_func is None:
        legal_kinds = list(signature_func_mapper.keys())
        err_msg = f"kind must be one of {legal_kinds}, received {kind}"
        raise ValueError(err_msg)
    
    # Sign message
    return signature_func(msg=msg, key=key, **kwargs)

def sign_params(params: dict, kind: str, key: str, **kwargs)-> str:
    """Given a dict of parameters, it generates a signature for them, given the 
    name of the signing algorithm to use, and the key to sign the message with.
    
    Examples:
        >>> # This is the signing method used by binance API
        >>> params = {'symbol': 'btc', 'from': '2021-12-01'}
        >>> sign_params(params, kind='hmac_sha256', key='abc123')

    Note: 
        For arguments other than `params`, it is preferable to pass them as
        keyword arguments, as the order of the arguments cannot be guaranteed in
        future versions.
    """
    # Sign the params
    msg = urllib.parse.urlencode(params)
    return sign_message(msg, kind=kind, key=key)
