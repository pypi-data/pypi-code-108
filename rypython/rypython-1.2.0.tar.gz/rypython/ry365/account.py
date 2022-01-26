from __future__ import annotations

import logging
import os
import sys
import re

from urllib.parse import parse_qs, urlparse
from rypython.ry365.logger import get_logger

from O365 import Account, FileSystemTokenBackend
from O365.connection import MSGraphProtocol
from pathlib import Path

from rypython.ry365.sharepoint import Sharepoint

logger = get_logger(__file__)

DOMAIN = 'welocalize.sharepoint.com'
TOKEN_PATH = Path(os.environ.get('welo365_token_path')).expanduser()
CREDS = (os.environ.get('welo365_client_id'), os.environ.get('welo365_client_secret'))


class O365Account(Account):
    def __init__(
            self,
            site: str = None,
            creds: tuple[str, str] = CREDS,
            scopes: list[str] = None,
            auth_flow_type: str = 'authorization'
    ):

        TOKEN = TOKEN_PATH / 'o365_token.txt'
        token_backend = None
        if TOKEN.exists():
            logger.debug(f"Using token file {TOKEN}")
            token_backend = FileSystemTokenBackend(token_path=TOKEN_PATH)
            token_backend.load_token()
            token_backend.get_token()
        scopes = scopes or ['offline_access', 'Sites.Manage.All']
        OPTIONS = {
            'token_backend': token_backend
        } if token_backend is not None else {
            'scopes': scopes,
            'auth_flow_type': auth_flow_type
        }
        super().__init__(creds, **OPTIONS)
        if not self.is_authenticated:
            self.authenticate()
        self.drives = self.storage().get_drives()
        self.site = self.get_site(site) if site else None
        self.drive = self.site.get_default_document_library() if self.site else self.storage().get_default_drive()
        self.root_folder = self.drive.get_root_folder()

    def sharepoint(self, *, resource=''):
        if not isinstance(self.protocol, MSGraphProtocol):
            raise RuntimeError(
                'Sharepoint api only works on Microsoft Graph API'
            )
        return Sharepoint(parent=self, main_resource=resource)

    def get_site(self, site: str):
        return self.sharepoint().get_site(DOMAIN, f"/sites/{site}")

    def search(self, query: str):
        u = urlparse(query)
        site = None
        drive = None
        file_name = None
        if (site_query := re.search(r'.*/sites/(?P<site>[\w_\-\d]+)/', u.path)):
            if (site := site_query.group('site')):
                site = self.get_site(site)
                drive = site.get_default_document_library()
        if (q := parse_qs(u.query)):
            file_name = q.get('file', [''])[0]
        drive = drive or self.drive
        query = file_name or query
        results = list(drive.search(query))
        return results[0] if results else results

    def get_folder(self, *subfolders: str, site: str = None):
        if len(subfolders) == 0:
            return self.drive

        site = self.get_site(site) if site else self.site
        drive = site.get_default_document_library() if site else self.drive

        items = drive.get_items()
        for subfolder in subfolders:
            try:
                subfolder_drive = list(filter(lambda x: subfolder in x.name, items))[0]
                items = subfolder_drive.get_items()
            except:
                raise ('Path {} not exist.'.format('/'.join(subfolders)))
        return subfolder_drive

    def get_document_library_by_name(self, document_library_name: str, site: str = None):
        site = self.get_site(site) if site else self.site
        for drive in site.list_document_libraries():
            if drive.name.lower() == document_library_name.lower():
                return drive