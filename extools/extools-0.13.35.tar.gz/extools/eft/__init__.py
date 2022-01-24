""" Tools for working with EFT."""
from datetime import datetime
from extools.view import exview
from extools.view.exsql import exsql_result
from extools.view.errors import ExViewError
from extools.message import logger_for_module

AP_PAYMENT_BATCH_TYPE = 1
PAYSTUB_BATCH_TYPE = 4

EFT_EMAIL_ERROR_SENDING = 2
EFT_EMAIL_ERROR_ADDRESS = 1
EFT_EMAIL_SUCCESS = 0

EDELMETHOD_EFT_EMAIL = 1
EDELMETHOD_CP_EMAIL = 2

# log = logger_for_module("extools.eft")

def log_eft_email(batch_type, batch, entry, vendor, report_name, email="",
                  delmethod=1, status=EFT_EMAIL_ERROR_SENDING):
    _time = datetime.now().strftime("%H%M%S%f")[:8]
    _date = datetime.now().strftime("%Y%m%d")
    try:
        with exview("EL0016") as elelog:
            elelog.recordGenerate()
            elelog.put("BATCHTYPE", batch_type)
            elelog.put("BATCH", batch)
            elelog.put("ENTRY", entry)
            elelog.put("DATERUN", _date)
            elelog.put("TIMERUN", _time)
            elelog.put("DELMETHOD", delmethod)
            elelog.put("REPORT", report_name)
            elelog.put("STATUS", status)
            elelog.put("IDCUST", vendor)
            elelog.put("EADDR", email)
            elelog.insert()
            return True
    except ExViewError as e:
        return False

def eft_email_sent(batch_type, batch, entry, vendor,
                   delmethod=1, status=EFT_EMAIL_SUCCESS):
    sql = """SELECT * FROM ELPRINT WHERE
                 BATCHTYPE = {} AND BATCH = {} AND
                 ENTRY = {} AND IDCUST = '{}' AND
                 DELMETHOD = {} AND STATUS = {}""".format(
                    batch_type, batch, entry, vendor, delmethod, status)
    log = logger_for_module("extools.eft")
    log.debug("checking sent emails: {}".format(sql))
    try:
        with exsql_result(sql) as exs:
            return True
    except ExViewError as e:
        return False

def eft_employee_email(employee):
    with exview("EL0116", seek_to={'IDEMP': employee}) as emp:
        if emp.edelmethod == EDELMETHOD_EFT_EMAIL:
            return emp.emailto
        elif emp.edelmethod == EDELMETHOD_CP_EMAIL:
            with exview("CP0014", seek_to={"EMPLOYEE": employee}) as cpemp:
                return cpemp.email
    return None