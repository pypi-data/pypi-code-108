from spell.client.model import SpellModel


class ModelsService:
    """A class for managing Spell models."""

    def __init__(self, client):
        self.client = client
        self.owner = self.client.api.owner

    def get(self, name, version=None):
        """Get a model or model version.

        Parameters:
            name (str): model name
            version (str): optional model version. If this parameter is set, returns only the
                specified model version. Otherwise, returns all versions of the model.

        Returns:
            A :py:class:`SpellModel` object if ``version`` is ``None``.
            A :py:class:`ModelVersion` object otherwise.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        if version is None:
            model = self.client.api.get_model(self.owner, name)
            return Model(self.client.api, model)
        else:
            model_version = self.client.api.get_model_version(self.owner, name, version)
            return ModelVersion(self.client.api, model_version)

    def list(self):
        """List models.

        Returns:
            A :obj:`list` of :py:class:`Model` objects.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        return self.client.api.list_models(self.owner)

    def new(self, name, resource, version=None, files=[], description=None):
        """Create a model version.

        Parameters:
            name (str): model name
            resource (str): path to a top-level resource, ``runs/168`` for example.
            files (list of :obj:`str`, optional): specific files or folders within the run which
                should be included in the model artifact. By default, this parameter is left
                blank, and all files written to disk by the run are included in the model
                artifact. If this parameter is set, all files not included in ``files`` are
                excluded. Each entry should be a valid path from within the run. Example:
                ``checkpoints/checkpoint.pk``.
            version (str, optional): the model version. By default, will auto-increment
                (e.g. ``v1``, ``v2``...).
            description (str, optional): an optional model description.

        Returns:
            A :py:class:`Model` object.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        self.client.api.new_model(self.owner, name, resource, version, files, description)
        return self.get(name)

    def rm(self, name, version=None):
        """Remove a model or model version.

        Parameters:
            name (str): model name
            version (str, optional): model version. By default, *all* versions of the model
                will be archived.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        if version is None:
            self.client.api.rm_model(self.owner, name)
        else:
            self.client.api.rm_model_version(self.owner, name, version)


class Model(SpellModel):
    """Object representing a Spell model.

    Attributes:
        id (int) : model id
        name (str): model name
        creator (`User`): the model creator
        created_at (`datetime.datetime`): the model creation time
        model_versions (list of `ModelVersion`): list of model versions for this model
    """

    # NOTE(aleksey): the SpellModel base class uses the "model" object property, which we cannot
    # overwrite. So we assign it to "spell_model" instead.
    model = "spell_model"

    def __init__(self, api, model):
        self._api = api
        self.__set_from_api_model_object(api, model)

    def __set_from_api_model_object(self, api, model):
        model.model_versions = [ModelVersion(api, version) for version in model.model_versions]
        self.spell_model = model


class ModelVersion(SpellModel):
    """Object representing a Spell model version.

    Attributes:
        id (int): the model version id
        model_id (int) : model id
        model_name (str): model name
        formatted_version (str): the model version
        creator (`User`): the model version creator
        created_at (`datetime.datetime`): the model version creation time
        resource (str): path to the top-level resource associated with this mode, for example
            ``runs/168``
        files (list of str, optional): specific files or folders within the run included in the
            model artifact. If set to empty list `[]`, all files from the resource are included in
            the model, otherwise, only ones included in `files` are.
    """

    model = "model_version"

    def __init__(self, api, model_version):
        self._api = api
        self.model_version = model_version

    def download(self, dest=None, quiet=False):
        """Download the model to disk.

        Parameters:
            dest (str, optional): the destination folder. By default, downloads to the current
                directory.
            quiet (bool, optional): enables or disables print-out. Helpful for interactive usage.
                Defaults to `False`.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException`: an error occured.
        """
        if not quiet:
            print("Downloading model. This may take some time...")

        if dest is None:
            dest = "./"
        self._api.download_model_version(self.model_version, dest, echo=print, quiet=quiet)

        if not quiet:
            print("Done!")
