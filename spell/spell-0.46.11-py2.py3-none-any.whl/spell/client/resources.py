class ResourcesService:
    """A class for managing Spell resources."""

    def __init__(self, client):
        self.client = client
        self.owner = self.client.api.owner

    def ls(self, path):
        """Lists resources in a path.

        Parameters:
            path (str): resource path to list (examples: ``runs/419``, ``uploads/my_files``).

        Returns:
            An iterator over ``LsLine`` objects.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        path = path.rstrip("/")  # "uploads/" and "uploads" should both be valid inputs
        return self.client.api.get_ls(path)

    def cp(self, path, dest, quiet=False):
        """Downloads files from ``path`` to ``dest``.

        Parameters:
            path (str): resource path to download files from.
            dest (str): local path to download files to.
            quiet (optional): whether or not to suppress output to ``stdout``
                (default: ``False``).

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        path = path.rstrip("/")  # "uploads/" and "uploads" should both be valid inputs
        self.client.api.download_resources([path], dest, echo=print, quiet=quiet)
