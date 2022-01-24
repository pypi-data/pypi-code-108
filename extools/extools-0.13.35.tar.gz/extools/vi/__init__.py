"""VI Scripts Helpers

A small collection of tools for working with the Extender site configuration.
"""
from pathlib import Path

from extools.view import exview, ExView, exgen
from extools.view.errors import ExViewError, ExViewRecordDoesNotExist

VICUSTH = "VI0011"
VISCRIPT = "VI0014"
VIFILES = "VI0015"
VIBIN = "VI0030"

FIELD_SIZE = 250
SEGMENT_FIELDS = 15
SEGMENT_SIZE = FIELD_SIZE * SEGMENT_FIELDS

def vidir():
    import accpac
    return Path(accpac.__file__).resolve().parent

def site_packages():
    return vidir / "python" / "lib" / "site-packages"

def import_script(filename, content):
    """Import a script into Extender.

    Chunks the script up and inserts it.

    :param filename: the script filename in extender.
    :type filename: str
    :param content: the script content.
    :type content: str
    :returns: True if imported, else False.
    :rtype: bool
    """
    vifiles = ExView(VIFILES)
    try:
        vifiles.seek_to(UPPRNAME=filename.upper())
        # already exists - undo checkout
        vifiles.put("FILENAME", filename)
        vifiles.put("STATUS", 0)
        vifiles.put("COBY", "")
        vifiles.update()
        for entry in exgen(VISCRIPT, seek_to={"ID": str(vifiles.get("ID"))}):
            entry.delete()
        for entry in exgen(VIBIN, seek_to={"ID": str(vifiles.get("ID"))}):
            entry.delete()
    except ExViewRecordDoesNotExist:
        vifiles.create(FILENAME=filename)

    fileid = vifiles.get("ID")

    try:
        with exview(VISCRIPT) as viscript:
            segment = 0
            for i in range(0, len(content), FIELD_SIZE):
                if i % SEGMENT_SIZE == 0:
                    if i:
                        viscript.insert()

                    segment = int((i / SEGMENT_SIZE) + 1)
                    viscript.recordClear()
                    viscript.put("ID", fileid)
                    viscript.put("SEGMENT", segment)

                index = int(((i % SEGMENT_SIZE) / FIELD_SIZE) + 1)
                viscript.put("TEXT{}".format(index),
                             content[i:i+FIELD_SIZE])
            viscript.insert()
    except ExViewError:
        return False

    vifiles.put("HASH", "")
    vifiles.put("CTYPE", 0)
    vifiles.put("FUNCTION", 4) # get latest
    vifiles.process()
    vifiles.update() # update hash

    return True

def remove_script(filename):
    """Remove a script fromExtender.

    Remove a script from the Extender registry.

    :param filename: the script filename in extender.
    :type filename: str
    :returns: True if removed, else False.
    :rtype: bool
    """
    vifiles = ExView(VIFILES)
    try:
        vifiles.seek_to(UPPRNAME=filename.upper())
        # already exists - undo checkout
        vifiles.put("FILENAME", filename)
        vifiles.put("STATUS", 0)
        vifiles.put("COBY", "")
        vifiles.update()
        for entry in exgen(VISCRIPT, seek_to={"ID": str(vifiles.get("ID"))}):
            entry.delete()
        for entry in exgen(VIBIN, seek_to={"ID": str(vifiles.get("ID"))}):
            entry.delete()
        vifiles.delete()
    except ExViewRecordDoesNotExist:
        pass
    except ExViewError:
        return False

    return True

def viewid_for_table(table):
    """Get the View ID for a table in the current company.

    :param table: Extender Custom Table name.
    :type table: str
    :returns: View ID
    :rtype: str
    """
    try:
        with exview(VICUSTH, seek_to={"TABLENAME": table}) as exv:
            return exv.get("VIEWID")
    except ExViewRecordDoesNotExist:
        return ""

def program_for_script(path):
    """Get the Sage program (i.e. OE1100) from a script file.

    :param path: path to file to determine program for.
    :type path: pathlib.Path or str
    :returns: program code or ""
    :rtype: str
    """
    path = Path(path)
    if path.exists():
        with path.open('r') as f:
            return f.readline().split()[-1]
    return ""
