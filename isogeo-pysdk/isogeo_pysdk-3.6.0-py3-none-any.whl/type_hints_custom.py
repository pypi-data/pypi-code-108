# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Custom type hints used in the SDK
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from typing import List, Tuple
from uuid import UUID

# Package
from isogeo_pysdk.models import Metadata

# #############################################################################
# ########## Globals ###############
# ##################################
Uuids = List[UUID]
Metadatas = Tuple[Metadata, ...]


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    pass
