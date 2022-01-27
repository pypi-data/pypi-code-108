import json

from importlib import import_module
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from slai.modules.parameters import from_config
from slai.clients.cli import get_cli_client
from slai.exceptions import IntegrationError


def get_google_drive_client():
    import_path = from_config(
        "GOOGLE_DRIVE_CLIENT",
        "slai.clients.gdrive.GoogleDriveClient",
    )
    class_ = import_path.split(".")[-1]
    path = ".".join(import_path.split(".")[:-1])
    return getattr(import_module(path), class_)()


class GoogleDriveClient:
    def __init__(self):
        self.cli_client = get_cli_client()

        gauth = self._authenticate()
        self.drive_client = GoogleDrive(gauth)

    def _authenticate(self):
        user = self.cli_client.get_user()

        if user.get("identity_user_google_auth") is not None:
            with open(".slai/gauth/creds.json", "w") as f_out:
                json.dump(user["identity_user_google_auth"]["gauth_creds"], f_out)
        else:
            raise IntegrationError("google_drive_integration_not_found")

        # TODO: handle failed auth
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile(".slai/gauth/creds.json")
        gauth.Authorize()

        return gauth

    def _format_parents(self, parent_ids):
        parents = []
        if parent_ids is not None:
            for _id in parent_ids:
                parents.append({"id": _id})
        return parents

    def upload_file(self, *, filename, local_path, parent_ids, file_id=None):
        parents = self._format_parents(parent_ids)

        _file = None
        if file_id is None:
            _file = self.drive_client.CreateFile(
                {"title": f"{filename}", "parents": parents}
            )
        else:
            _file = self.drive_client.CreateFile(
                {"title": f"{filename}", "parents": parents, "id": file_id}
            )

        _file.SetContentFile(local_path)
        _file.Upload()

        return _file["id"]

    def create_folder(self, *, name, parent_ids=None):
        parents = self._format_parents(parent_ids)
        folder_file = self.drive_client.CreateFile(
            {
                "title": name,
                "parents": parents,
                "mimeType": "application/vnd.google-apps.folder",
            }
        )
        folder_file.Upload()
        return folder_file["id"]

    def download_file(self, *, file_id, local_path):
        _file = self.drive_client.CreateFile({"id": file_id})
        _file.GetContentFile(local_path)
        return _file
