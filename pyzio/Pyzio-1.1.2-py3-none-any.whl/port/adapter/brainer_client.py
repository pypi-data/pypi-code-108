import base64
import random
import secrets
import string
import uuid

import requests

from ..phasio_control_port import PhasioControlPort
from ...config.brainer_config import BrainerConfig
from ...domain.job import Job
from ...enums.print_file_type import PrintFileType


class BrainerClient(PhasioControlPort):
    GCODE_FILE_EXTENSION = '.gcode'
    PRINTER_REG_ENDPOINT = 'printer'
    JOB_ENDPOINT = 'part'

    def __init__(self, brainer_config: BrainerConfig):
        self._brainer_config = brainer_config

    def get_file(self, printer_id: str, secret: str, job: Job) -> str:
        host, storage_dir = self._brainer_config.host(), self._brainer_config.file_storage()
        team_id, print_file = job.team_id, job.printFile

        download_url = f"{host}/part/{team_id}/{print_file}".encode()
        to_file = f"{storage_dir}{print_file}"

        r = requests.get(download_url, headers=self._generate_auth_credentials(printer_id, secret))
        r.raise_for_status()
        with open(to_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return to_file

    def register_candidate(self, brand: str, model: str, material: str, file_type: PrintFileType) -> (int, str, str):
        r_id = str(uuid.uuid4())
        pairing_code = random.randint(9999, 999999)
        secret = self._generate_secret()
        pairing_request = self._generate_pairing_request(r_id, pairing_code, brand, model, material, file_type, secret)
        url = f"{self._brainer_config.host()}/{self.PRINTER_REG_ENDPOINT}".encode()
        r = requests.post(url, json=pairing_request)
        r.raise_for_status()
        return pairing_code, r.content.decode(), secret

    @staticmethod
    def _generate_secret() -> str:
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(20))
        return password

    @staticmethod
    def _generate_pairing_request(r_id: str, pairing_code: int, brand: str, model: str, material: str,
                                  file_type: PrintFileType, secret: str):
        return {
            "requestId": r_id,
            "pairingCode": pairing_code,
            "brand": brand,
            "model": model,
            "material": material,
            "printFileType": file_type.name,
            "secret": secret,
        }

    @staticmethod
    def _generate_auth_credentials(printer_id: str, secret: str):
        token = f"{printer_id}:{secret}".encode("ascii")
        encoded_token = base64.b64encode(token).decode("ascii")
        return {"Authorization": f"Basic {encoded_token}"}
