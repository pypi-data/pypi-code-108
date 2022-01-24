from extools.view import exview, ExView
from extools.view.errors import ExViewError

def orduniq_for(ordnumber):
    """Get the Unique Order Key (ORDUNIQ) given an Order Number.

    :param ordnumber: Order number to get the unique key for.
    :type ordnumber: str
    :returns: ORDUNIQ or 0.0
    :rtype: float
    """
    try:
        with exview("OE0520", seek_to={'ORDNUMBER': ordnumber}) as exv:
            return exv.get("ORDUNIQ")
    except ExViewError as e:
        return 0.0

def order_from_quotes(customer, quotes):
    """Create an order for a customer from a list of quotes.
    
    :param customer: customer number
    :type customer: str
    :param quotes: list of quote numbers
    :type quotes: list
    :returns: new order (not yet inserted)
    :rtype: ExView("OE0520")
    """
    order = ExView("OE0520", index=77)
    order.compose()
    order.recordGenerate()
    order.put("CUSTOMER", customer)
    order.put("MULTIQUO", 1)
    # order.put("QUOS", len(quotes))
    for quote in quotes:
        order.oe0526.recordGenerate()
        order.oe0526.put("QUOUNIQ", orduniq_for(quote))
        order.oe0526.put("QUONUMBER", quote)
        order.oe0526.insert()
    order.put("GOQUOTOORD", 1)
    order.put("OECOMMAND", 11)
    order.process()
    return order