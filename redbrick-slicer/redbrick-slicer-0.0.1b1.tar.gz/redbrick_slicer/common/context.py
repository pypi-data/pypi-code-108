"""Container for low-level methods to communicate with API."""


class RBContext:
    """Basic context for accessing low level functionality."""

    def __init__(self, url: str) -> None:
        """Construct RedBrick client singleton."""
        # pylint: disable=import-outside-toplevel
        from .client import RBClient
        from .export import ExportControllerInterface
        from .labeling import LabelingControllerInterface
        from .project import ProjectRepoInterface

        self.client = RBClient(url)

        self.export: ExportControllerInterface
        self.labeling: LabelingControllerInterface
        self.project: ProjectRepoInterface
