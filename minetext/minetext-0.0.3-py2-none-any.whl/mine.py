class Mine(object):
    """
    This class represent the Mine Object
    """

    def __init__(self, d):
        """
        
        :param d:
        """
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [Mine(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, Mine(b) if isinstance(b, dict) else b)

    class Index:
        name = 'goescholar'
