__author__ = "Daniel von Eßen"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Daniel von Eßen", "Thomas Steinbach"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "daniel.von-essen@deutschebahn.com"


from typing import List


def sops_export_decrypted_values(
    path: str,
    *,
    install_sops: bool = True,
    download_url: str = "https://github.com/mozilla/sops/releases/download/v3.7.1/sops-v.3.7.1.linux",
) -> List[str]:
    """Returns a helper string to be embedded into jobs to allow exporting
    values which are decrypted by `sops`. e.g. 'export $(sops -d sops/encrypted_file.env)'

    This function is usefull, if you want to use environment variables to login to e.g. a container registry.

    The script is successfully tested with SOPS 3.7 and knowingly NOT WORKING with SOPS 3.6, as in the latter
    version is a bug which wraps the values to export into quotes.

    Args:
        path (str): Path to `sops` encrypted file, must be relative to project directory.
        install_sops (bool): Enable downloading `sops` from provided `download_url` defaults to True.
        download_url (str): Download URL to download `sops` from. Defaults to Github mozilla sops releases.
    Returns:
        List[str]: Export string of sops decrypted file.
    """
    sops_cmd: List[str] = []
    if install_sops:
        sops_cmd.append(f"curl -L {download_url} -o /usr/local/bin/sops")
        sops_cmd.append("chmod +x /usr/local/bin/sops")
    sops_cmd.append(f"set -eo pipefail; SOPS_OUTPUT=$(sops -d {path}); export $SOPS_OUTPUT")
    return sops_cmd
