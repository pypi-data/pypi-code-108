"""Provides class that represents a Notebook in the application"""

# system imports
from pathlib import Path


class Notebook():
    """Represents the notebook (the directory defined in the ntbk_dir config var).

    Arguments:
        config -- Config instance

    Attributes:
        config -- Config instance
        notebook_path -- Path object to the root notebook dir
    """

    def __init__(self, config):
        self.config = config
        self.notebook_path = Path(self.config.get('ntbk_dir')).expanduser()

    def exists(self):
        """Whether or not this notebook exists on the disk yet"""
        return self.notebook_path.exists()

    def create(self):
        """Create the notebook, scaffolding the folders and a default template file"""
        template_dir = self.config.get('template_dir')
        subfolders = [template_dir, 'collections', 'log']

        self.notebook_path.mkdir(parents=True, exist_ok=True)

        for sub in subfolders:
            (self.notebook_path / sub).mkdir(exist_ok=True)

        # create a basic template for new log entries
        default_log_template = self.notebook_path / template_dir / 'log_default.md'
        default_log_template.write_text("# {{ log_date.strftime('%A, %B %d, %Y') }}")

        print(f'Created notebook at {self.notebook_path}')
