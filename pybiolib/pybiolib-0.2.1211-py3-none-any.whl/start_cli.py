# -*- coding: utf-8 -*-
import re
import sys
from biolib import call_cli
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(call_cli())  # type: ignore
