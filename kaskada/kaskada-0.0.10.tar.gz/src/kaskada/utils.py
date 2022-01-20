"""
Copyright (C) 2021 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express 
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""

import unicodedata
import re

def normalize_col_name(column: str) -> str:
    """
    Normalize column name by replacing invalid characters with underscore
    strips accents and make lowercase
    """
    n = re.sub(r"[ ,;{}()\n\t=]+", '_', column.lower())
    return unicodedata.normalize('NFKD', n).encode('ASCII', 'ignore').decode()
