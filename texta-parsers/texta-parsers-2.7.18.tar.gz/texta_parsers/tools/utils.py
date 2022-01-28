from enum import Enum
import subprocess
from ..settings import META_FIELD
from texta_parsers.tools.extension import Extension


class ParserOutputType(Enum):
     EMAIL = 1
     COLLECTION = 2
     FILE = 3

def get_output_type(item):
    #item is from email generator in the form of (email_dict, [attachment_dict])
    #can not check extension here because input can come directly from email parser as well
    #which does not have that field
    if(type(item) == tuple):
        return ParserOutputType.EMAIL
    #item is from docparser generator, find type by checking extension
    else:
        extension = item[META_FIELD]["extension"]
        if(extension in Extension.COLLECTION_EXTENSIONS):
            return ParserOutputType.COLLECTION
        else:
            return ParserOutputType.FILE


def check_digidoc_exists():
    try:
        p = subprocess.run(["digidoc-tool"], stdout=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False
