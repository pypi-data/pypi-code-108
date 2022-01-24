from extools.view import exview
from extools.view.errors import ExViewError

def customer_group_for(customer_id):
    """Get the customer group for a given customer ID.

    :param customer_id: the customer ID to find the group for.
    :type customer_id: str
    :returns: customer group or an empty string.
    :rtype: str
    """
    try:
        with exview("AR0024", seek_to={"IDCUST": customer_id}) as exv:
            return exv.get("IDGRP")
    except ExViewError:
        return ""
