"""RedBrick Slicer Integration Package."""
from redbrick_slicer.common.constants import DEFAULT_URL, DEFAULT_REGION
from redbrick_slicer.slicer import RBSlicer


__version__ = "0.0.1b2"


def get_slicer(
    username: str,
    password: str,
    client_id: str,
    url: str = DEFAULT_URL,
    region: str = DEFAULT_REGION,
) -> RBSlicer:
    """Interact with a RedBrick task in 3D Slicer application."""
    # pylint: disable=import-outside-toplevel
    from redbrick_slicer.common.context import RBContext
    from redbrick_slicer.repo import ProjectRepo, LabelingRepo, ExportRepo

    context = RBContext(url)
    context.export = ExportRepo(context.client)
    context.labeling = LabelingRepo(context.client)
    context.project = ProjectRepo(context.client)
    return RBSlicer(context, username, password, client_id, url, region)
