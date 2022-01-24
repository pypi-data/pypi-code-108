import re

from extools.view import exview, exgen
from extools.view import ExViewError

ITEMNO_SEGMENT_SEP_CLASS = r'[\*\-/\\.\(\)#]'

def category_for(itemno):
    """Get the category for an item."""
    try:
        with exview("IC0310", seek_to={'ITEMNO': itemno}) as exv:
            return exv.get("CATEGORY")
    except ExViewError:
        return ""

def unformat_itemno(itemno):
    """Unformat an item number.

    :param itemno: formatted item number.
    :type itemno: str
    :returns: item number with formatting characters removed.
    """
    return re.sub(ITEMNO_SEGMENT_SEP_CLASS, '', itemno)

def vendors_for(unfmtitemno):
    """Get a list of all vendors.

    The returned list is sparse: Vendor 1 at index 0, Vendor 2 at index 1,
    etc.  Vendors that are not set will be None.

    :param unfmtitemno: Unformatted item number.
    :type unfmtitemno: str
    """
    vendors = [None for _ in range(0, 10)]
    for vendor in exgen("IC0340", seek_to={"ITEMNO": unfmtitemno}):
        idx = int(vendor.vendtype) - 1
        vendors[idx] = vendor.vendnum
    return vendors

def uoms_for(itemno):
    """Get a list of all UOMs for an item.
    :param itemno: formatted item number.
    :type itemno: str
    :returns: ExQuery(ITEMNO=itemno)
    """
    try:
        with exview("IC0750") as exv:
            return exv.where(ITEMNO=unformat_itemno(itemno))
    except ExViewError:
        return {}

def item_optfield(itemno, optfield):
    """Get an item's optional field value.

    :param itemno: the I/C item number.
    :type itemno: str
    :param optfield: the optional field name.
    :type optfield: str
    :returns: value if set, else None
    """
    try:
        with exview("IC0313", seek_to={
                "ITEMNO": itemno,
                "OPTFIELD": optfield}) as itemoptf:
                    return itemoptf.get("VALUE")
    except ExViewError as e:
        return None
