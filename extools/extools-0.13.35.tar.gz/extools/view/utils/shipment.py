from extools.view import exview
from extools.view.errors import ExViewError

def shiuniq_for(shinumber):
    """Get the shipment uniquifier for a shipment number.

    :param shinumber: shipment number.
    :type shinumber: str
    :returns: shipment uniquifier or 0.0 is no such shipment
    :rtype: float
    """
    if not shinumber:
        return 0.0
    try:
        with exview("OE0692", seek_to={'SHINUMBER': shinumber}) as shipment:
            return shipment.shiuniq
    except ExViewError as e:
        # showMessageBox("Failed to find SHIUNIQ for '{}': {}".format(
        #        shinumber, e))
        pass
    return 0.0

