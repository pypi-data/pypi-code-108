import logging

logger = logging.getLogger(__name__)

class RPCRequest:
    def __init__(self, _dict):
        if _dict:
            for key, value in _dict.items():
                if isinstance(value, (list, tuple)):
                    setattr(self, key, [RPCRequest(x) if isinstance(x, dict) else x for x in value])
                else:
                    try:
                        setattr(self, key, RPCRequest(value) if isinstance(value, dict) else value)
                    except AttributeError:
                        logger.warning(f'key:{key} value: {value} do not recorded')
