"""Tools for working with the G/L."""
try:
    from extools.message import logger_for_module
    from accpac import FT_BYTE
except ImportError:
    FT_BYTE = 2
    pass

import binascii

def drilldown_from(view, field="DRILLDWNLK"):
    """Get the drilldown string at the given view field.

    :param view: view to extract the drilldown from.
    :type view: accpac.View
    :param field: drilldown field in view.
    :type view: str"""
    log = logger_for_module('extools', box=None)
    byte_value = view.get(field, fieldType=FT_BYTE)
    decoded = binascii.hexlify(byte_value).decode()[1:-1]
    log.debug("drilldown: {} [{}] ({})".format(
            decoded, type(decoded), byte_value))
    return str(decoded)

def parse_ap_ar_drilldown(drilldown):
    """Parse a GL AP/AR drilldown to extract the batch and entry numbers.

    :param drilldown: drilldown link value
    :type drilldown: str
    """
    log = logger_for_module('extools', box=None)
    log.debug("parsing drilldown {}".format(drilldown))

    len_posting_seq = int(drilldown[0])
    len_batchnum = int(drilldown[1])
    ps_start = 2

    ps_end = ps_start + len_posting_seq
    posting_seq = drilldown[ps_start:ps_end]

    batch_start = ps_end
    batch_end = batch_start + len_batchnum
    batchnum = drilldown[batch_start:batch_end]

    entry_start = max(batch_end, len(drilldown) - 4)
    entry = drilldown[entry_start:]

    log.debug("{} {}, {} - {}, {} - {}, {} - {}, {} {} {}".format(
        len_posting_seq, len_batchnum, ps_start, ps_end,
        batch_start, batch_end, entry_start, len(drilldown),
        posting_seq, batchnum, entry))

    return batchnum, entry
