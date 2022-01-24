"""Work with SYSACCESS."""
try:
    from accpac import (SYSACCESS_NORMAL, SYSACCESS_IMPORT, SYSACCESS_EXPORT,
                        SYSACCESS_INTCHK, SYSACCESS_MACRO, SYSACCESS_ACTIVATE,
                        SYSACCESS_CONVERT, SYSACCESS_FINDER, SYSACCESS_POST,  )
except ImportError:
    SYSACCESS_NORMAL = 0
    SYSACCESS_IMPORT = 1
    SYSACCESS_EXPORT = 2
    SYSACCESS_INTCHK = 3
    SYSACCESS_MACRO = 4
    SYSACCESS_ACTIVATE = 5
    SYSACCESS_CONVERT = 6
    SYSACCESS_FINDER = 7
    SYSACCESS_POST = 10

SYSACCESS_TEXT = {
        SYSACCESS_NORMAL: "Normal",
        SYSACCESS_IMPORT: "Import",
        SYSACCESS_EXPORT: "Export",
        SYSACCESS_INTCHK: "Integrity Check",
        SYSACCESS_MACRO: "Macro",
        SYSACCESS_ACTIVATE: "Activate",
        SYSACCESS_CONVERT: "Convert",
        SYSACCESS_FINDER: "Finder",
        SYSACCESS_POST: "Post",
    }

def sysaccess_text(sysaccess):
    return SYSACCESS_TEXT.get(sysaccess, "Unknown")
