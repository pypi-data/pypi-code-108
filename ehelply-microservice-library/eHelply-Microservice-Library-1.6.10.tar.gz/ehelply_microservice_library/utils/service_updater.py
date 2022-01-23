from ehelply_updater.updater import Updater, Config
from pathlib import Path
from ehelply_microservice_library.integrations.fact import get_fact_endpoint


class ServiceUpdater:
    """
    Wrapper class for ehelply_updater
    """
    def __init__(self, access_key: str, secret_key: str, root_path: Path) -> None:
        self.config: Config = Config(
            api_base_url=get_fact_endpoint('ehelply-templates') + '/templates',
            update_dir=str(root_path),
            package_file=str(root_path.joinpath("ehelply-package.json")),
            access_key=access_key,
            secret_key=secret_key,
        )
        self.updater: Updater = Updater(config=self.config)

    def is_update_available(self) -> bool:
        return self.updater.is_update_required()

    def preview(self):
        return self.updater.preview()

    def update(self):
        return self.updater.update()
