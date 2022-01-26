"""Classes representing log objects in the application"""

# app imports
from ntbk.entities.templates import Template


class LogDate():
    """This class represents a day in the log/ directory. It has 1-n LogFiles.

    Arguments:
        config -- Config instance
        filesystem -- Filesystem instance
        date_obj -- date object for the day this log belongs to

    Attributes:
        config -- Config instance
        filesystem -- Filesystem instance
        date_obj -- date object for the day this log belongs to
    """

    def __init__(self, config, filesystem, date_obj):
        self.config = config
        self.filesystem = filesystem
        self.date_obj = date_obj

    def get_path(self):
        """Get the pathlib.Path object to this log date (will be a folder)"""
        return (self.filesystem.get_log_base_path() /
            f"{self.date_obj.strftime('%Y/%m-%B/%Y-%m-%d').lower()}")

    def get_contents(self, recursive=False):
        """Get all the files and folders as Path objects for this date"""
        pattern = '**/*' if recursive else '*'
        return list(self.get_path().glob(pattern))

    def get_files(self):
        """Get all the files for this log date"""
        return [LogFile(self.config, self.filesystem, self.date_obj, child.stem)
            for child in self.get_path().glob('*.md')]

    def get_date(self):
        """Return the date object for this LogDate"""
        return self.date_obj

    def create_directories(self):
        """Create all the directories for this log date on disk"""
        self.get_path().mkdir(parents=True, exist_ok=True)


class LogFile():
    """This class represents a file inside a LogDate.

    Arguments:
        config -- Config instance
        filesystem -- Filesystem instance
        date_obj -- date object for the day this file belongs to
        filename -- string name of file

    Attributes:
        config -- Config instance
        filesystem -- Filesystem instance
        logdate -- LogDate instance for the day this file belongs to
        filename -- string name of file
    """

    EXTENSION = '.md'

    def __init__(self, config, filesystem, date_obj, filename):
        self.config = config
        self.filesystem = filesystem
        self.logdate = LogDate(config, filesystem, date_obj)
        self.filename = filename

    def get_path(self):
        """Get the pathlib.Path object to this log date file"""
        fname = self.filename if self.is_dir() else f'{self.filename}{self.EXTENSION}'
        return self.logdate.get_path() / fname

    def get_name(self):
        """Get the name of this file (without extension)"""
        return self.filename

    def is_dir(self):
        """This is awkward, but sometimes the LogFile is actually a dir"""
        return (self.logdate.get_path() / self.filename).is_dir()

    def get_contents(self, recursive):
        """If this is a dir, not file, then this will print its contents"""
        if not self.is_dir():
            raise Exception(f'{self.filename} is a file')

        pattern = '**/*' if recursive else '*'
        return list(self.get_path().glob(pattern))

    def get_logdate(self):
        """Get the LogDate object this file belongs to"""
        return self.logdate

    def exists(self):
        """Whether or not this file exists on disk"""
        return self.get_path().exists()

    def is_empty(self):
        """
        Whether or not this file exists and has any content in it.
        Spaces and newlines dont count.
        """
        if not self.get_path().exists():
            return True
        return bool(self.get_path().read_text().strip())

    def get_default_template_name(self):
        """
        Get the default template name for this file as defined in the config file.
        Returns None if there isn't one.
        """
        # i'd like to find a more elegant solution for accessing these nested dicts
        if not self.config.get('default_templates'):
            return None
        if not self.config.get('default_templates').get('log'):
            return None
        return self.config.get('default_templates').get('log').get(self.filename)

    def has_default_template(self):
        """Whether or not this file has a default template defined in the config file"""
        return self.get_default_template_name() is not None

    def get_default_template(self):
        """
        Get the default template Template object for this file.
        Returns None if there isn't one.
        """
        if not self.has_default_template():
            return None
        return Template(self.config, self.filesystem, self.get_default_template_name())

    def create_directories(self):
        """Creates all the parent directories for this file (does not actually create the file)"""
        self.get_path().parent.mkdir(parents=True, exist_ok=True)
