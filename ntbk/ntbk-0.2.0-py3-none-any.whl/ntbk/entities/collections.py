"""Classes to represent Collection entities in the app"""

# app imports
from ntbk.entities.templates import Template


class Collection():
    """Represents a folder in the /collections directory. It can contain multiple files

    Arguments:
        config - Config instance
        filesystem - Filesystem instance
        name - string collection name

    Attributes:
        config - Config instance
        filesystem - Filesystem instance
        name - string collection name
    """

    def __init__(self, config, filesystem, name):
        self.config = config
        self.filesystem = filesystem
        self.name = name

    def get_path(self):
        """Get the pathlib.Path object for this collection"""
        return self.filesystem.get_collection_base_path() / self.name

    def get_name(self):
        """Get the string name for this collection"""
        return self.name

    def has_default_template(self):
        """Whether or not this collection has a default template defined in the config file"""
        return self.get_default_template_name() is not None

    def get_default_template_name(self):
        """Get the default template name in the config file or None if there isn't one."""
        # i'd like to find a more elegant solution for accessing these nested dicts
        if not self.config.get('default_templates'):
            return None
        if not self.config.get('default_templates').get('collection'):
            return None
        return self.config.get('default_templates').get('collection').get(self.name)

    def get_default_template(self):
        """Get the default template Template object or None if there isn't one."""
        if not self.has_default_template():
            return None
        return Template(self.config, self.filesystem, self.get_default_template_name())

    def get_contents(self, recursive = False):
        """Gets a list of files and folders inside this collection"""
        pattern = '**/*' if recursive else '*'
        return list(self.get_path().glob(pattern))

    def get_files(self):
        """Get a list of CollectionFile objects for each file in this collection"""
        return [CollectionFile(self.config, self.filesystem, self.name, child.stem)
            for child in self.get_path().glob('*')]

    def get_file_count(self):
        """Get int number of files in this collection"""
        return len(self.get_files())

    def create_directories(self):
        """Create all the directories for this collection on disk"""
        self.get_path().mkdir(parents=True, exist_ok=True)


class CollectionFile():
    """Represents a file within a collection

    Arguments:
        config - Config instance
        filesystem - Filesystem instance
        collection_name - string name of the collection
        filename - string name of the file inside the collection

    Attributes:
        config - Config instance
        collection - Collection object - collection file belongs to
        filename - string name of the file inside the collection
    """

    EXTENSION = '.md'

    def __init__(self, config, filesystem, collection_name, filename):
        self.config = config
        self.collection = Collection(config, filesystem, collection_name)
        self.filename = filename

    def get_path(self):
        """Get the pathlib.Path object for this collection file"""
        return self.collection.get_path() / f'{self.filename}{self.EXTENSION}'

    def get_name(self):
        """Get the name of this file (without extension)"""
        return self.filename

    def get_collection(self):
        """Get Collection object that this file belongs to"""
        return self.collection

    def exists(self):
        """Whether or not this file exists on disk yet"""
        return self.get_path().exists()

    def is_empty(self):
        """
        Whether or not this file exists and contains any content.
        Spaces and newlines don't count.
        """
        if not self.get_path().exists():
            return True
        return bool(self.get_path().read_text().strip())

    def has_default_template(self):
        """Whether or not this file belongs to a collection that has a default template"""
        return self.collection.has_default_template()

    def get_default_template_name(self):
        """Get the default template name for the collection this file belongs to"""
        return self.collection.get_default_template_name()

    def get_default_template(self):
        """Get the Template object for default template for the collection this file belongs to"""
        return self.collection.get_default_template()

    def create_directories(self):
        """Create all the parent directories for this file on disk (does not create the file)"""
        self.collection.create_directories()


def get_all_collections(config, filesystem):
    """Get a list of Collection objects for all collections in the notebook

    Arguments:
        config - Config instance
        filesystem - Filesystem instance
    """
    collections = [Collection(config, filesystem, child.stem)
        for child in filesystem.get_collection_base_path().glob('*/')]

    return sorted(collections, key=lambda col: col.get_name().lower())
