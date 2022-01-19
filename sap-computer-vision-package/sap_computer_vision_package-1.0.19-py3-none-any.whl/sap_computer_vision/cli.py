"""This module creates the cli for this package."""
import pathlib
from re import M

from ai_core_content_package_utils.cli import create_cli_for_module

import sap_computer_vision.pipelines
from sap_computer_vision import SAP_COMPUTER_VISION_DIR, DISCLAIMER, LICENSE

# TODO: provide an example pipeline-config yaml for the template generation (as it's unusable otherwise)

PIPELINES_DIR = SAP_COMPUTER_VISION_DIR / 'pipelines'
EXAMPLES_DIR = SAP_COMPUTER_VISION_DIR / 'examples'

cli = create_cli_for_module(sap_computer_vision,
                            sap_computer_vision.pipelines,
                            PIPELINES_DIR / 'pipelines.yaml',
                            examples_dir=EXAMPLES_DIR,
                            show_files={
                                'disclaimer': DISCLAIMER,
                                'license': LICENSE,
                            })
if __name__ == '__main__':
    cli() # pylint: disable=E1120
