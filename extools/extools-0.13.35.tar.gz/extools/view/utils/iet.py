from extools.view import exview
from extools.view.exsql import exsql_result
from extools.view.errors import ExViewRecordDoesNotExist

from accpac import Company

TTYPE_OE_TO_PO_ORDER = 0
TTYPE_SH_TO_PO_RECEIPT = 1
TTYPE_PO_TO_OE_ORDER = 10
TTYPE_PO_RC_TO_OE_SH = 11
TTYPE_PO_INV_TO_OE_INV = 12

TTYPES = ((TTYPE_OE_TO_PO_ORDER, "O/E Order to Purchase Order"),
          (TTYPE_SH_TO_PO_RECEIPT, "O/E Shipment to P/O Receipt"),
          (TTYPE_PO_TO_OE_ORDER, "Purchase Order to O/E Order"),
          (TTYPE_PO_RC_TO_OE_SH, "Purchase Order Receipt to O/E Shipment"),
          (TTYPE_PO_INV_TO_OE_INV, "Purchase Order Invoice to O/E Invoice"),
          )
"""Inter-Entity Transaction Types"""

PATYPE_ACCT_TO_ACCT = 0
PATYPE_SHIPVIA_TO_ACCT = 1
PATYPE_ACCT_TO_SHIPVIA = 2

PATYPES = ((PATYPE_ACCT_TO_ACCT, "Account to Account"),
           (PATYPE_SHIPVIA_TO_ACCT, "Ship-via to Account"),
           (PATYPE_ACCT_TO_SHIPVIA, "Account to Ship-via"),
          )
"""Inter-Entity Partner Account Types"""

def trade_document_number_for(org, transtype, paccttype, docnum):
    """Get the corresponding document number from a partner org.

    :param partner_org: the partner organisation of the document.
    :type partner_org: str
    :param transtype: the Inter-Entity Transaction Type.
    :type transtype: int
    :param paccttype: the Inter-Entity Partner Account Type.
    :type paccttype: int
    :param docnum: the document number in the local company.
    :type docnum: str
    """
    query = """
        SELECT TRDOCNUM FROM IYOEPOAU
        WHERE ORGID = '{org}'
        AND TRANSTYPE = {transtype}
        AND PACCTTYPE = {paccttype}
        AND DOCNUM = '{docnum}'
    """.format(org=org, transtype=transtype, paccttype=paccttype,
               docnum=docnum)
    try:
        with exsql_result(query) as exs:
            return exs.get("TRDOCNUM")
    except ExViewRecordDoesNotExist:
        pass
    except ExViewError as e:
        pass
    return ""

def document_number_for(org, transtype, paccttype, trdocnum):
    """Get the corresponding document number from a partner org.

    :param partner_org: the partner organisation of the document.
    :type partner_org: str
    :param transtype: the Inter-Entity Transaction Type.
    :type transtype: int
    :param paccttype: the Inter-Entity Partner Account Type.
    :type paccttype: int
    :param docnum: the trade document number in the local company.
    :type docnum: str
    """
    query = """
        SELECT DOCNUM FROM IYOEPOAU
        WHERE ORGID = '{org}'
        AND TRANSTYPE = {transtype}
        AND PACCTTYPE = {paccttype}
        AND TRDOCNUM = '{trdocnum}'
    """.format(org=org, transtype=transtype, paccttype=paccttype,
               trdocnum=trdocnum)
    try:
        with exsql_result(query) as exs:
            return exs.get("DOCNUM")
    except ExViewRecordDoesNotExist:
        pass
    except ExViewError as e:
        pass
    return ""

def open_company(company):
    """Open another company using the credentials in IYORG.

    :param company: Company Code
    :type company: str
    :returns: Company object or None if cannot connect.
    :rtype: accpac.Company
    """
    with exview("IY0018", seek_to={'ORGID': company}) as iyorg:
        password = iyorg.password.decode().strip()
        c = Company()
        c.open(company, iyorg.userid, password)
        return c
    return None
