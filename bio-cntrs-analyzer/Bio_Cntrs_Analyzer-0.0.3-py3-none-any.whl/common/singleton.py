class Singleton(type):
    """
    Singleton class.

    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Call function of Singleton.

        Parameters
        ----------
        args: Non-Keyword Arguments.
        kwargs: Keyword Arguments.

        Returns
        -------
        The instanced Singleton.

        """
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
