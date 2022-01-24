"""Tools for generating reports.

They are often required, but who ever remembers the params and
criteria?  These classes are designed to capture that knowledge
for re-use.

They should be pretty strightforward to use:

.. code-block:: python

    report = POPurchaseOrderReport("PO0001", "PO0003")
    report.generate(destination="preview")

To print to a file:

.. code-block:: python

    report = POPurchaseOrderReport("PO0001", "PO0003")
    report.generate(destination="file", path="C:\\Temp\\report.pdf")

To open the print dialogue, pass the UI instance:

.. code-block:: python

    report = POPurchaseOrderReport("PO0001", "PO0003", ui=self)
    report.generate(destination="file", path="C:\\Temp\\report.pdf")

To override a parameter:

.. code-block:: python

    report = POPurchaseOrderReport("PO0001", "PO0003", ONHOLD="1")
    report.generate(destination="file", path="C:\\Temp\\report.pdf")

To override the selection criteria:

.. code-block:: python

    criteria = "((POPORH.ORDNUMBER = 'ORD00001'))"

    report = POPurchaseOrderReport("PO0001", "PO0003",
            **{"@SELECTION_CRITERIA": criteria})
    report.generate(destination="file", path="C:\\Temp\\report.pdf")


"""
try:
    from accpac import Report, getOrgPath, showMessageBox
except ImportError:
    pass

import time
from pathlib import Path
from datetime import datetime

from extools.message import logger_for_module

def get_report_class_for_report_name(name):
    for klass in REPORT_CLASSES:
        if name in klass.reports:
            return klass
    return None

def get_report_class_for_parameter_set(paramset):
    for klass in REPORT_CLASSES:
        if klass.parameter_set == paramset:
            return klass
    return None

def get_report_class_for(report_name):
    try:
        parameter_set, _rest = report_name.split("[")
        report = _rest.rstrip("]")
    except ValueError as e:
        return None

    for klass in REPORT_CLASSES:
        if klass.parameter_set == parameter_set and report in klass.reports:
            return klass
    return None

class ReportWrapper(object):

    parameter_set = ""
    reports = []
    selection_criteria = ""
    parameters = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.log = logger_for_module('extools')

    def generate(self, report_name, from_id="", to_id="",
                 destination="file", path="", ui=None):
        report = Report()
        report.reportName = report_name
        report.destination = destination.lower()
        if destination.lower() == "file":
            if not path:
                now = datetime.now().strftime("%Y%m%dT%H%M")
                path = Path(getOrgPath(), '{}-report.pdf'.format(now))
            report.printDirectory = str(path)
            ui = None

        criteria = self.selection_criteria.format(
                from_id=from_id, to_id=to_id)

        try:
            for key, value in self.parameters.items():
                if key not in self.kwargs:
                    val = value.replace(
                            "{to_id}", to_id
                            ).replace("{from_id}", from_id)
                    report.setParameter(key, val)

            if criteria and not "@SELECTION_CRITERIA" in self.kwargs:
                report.setParameter("@SELECTION_CRITERIA", criteria)

            for key, value in self.kwargs.items():
                val = value.replace(
                        "{to_id}", to_id
                        ).replace("{from_id}", from_id)
                report.setParameter(key, val)

            result = report.print(ui)

        except Exception as err:
            self.log.error("Failed to print {}: {}".format(report_name, err))

        if destination == 'file':
            if self.wait_for(path):
                return path

        return None

    def wait_for(self, path, tries=5, sleep=3):
        run = 0
        while run < tries:
            if path.exists():
                return True
            time.sleep(sleep)
            run += 1
        return False

class OEInvoiceReport(ReportWrapper):

    parameter_set = "OEINV03"
    reports = ("OEINV03.RPT", )
    selection_criteria = ('(({{OEINVH.INVNUMBER}} >= "{from_id}") AND '
                          '({{OEINVH.INVNUMBER}} <= "{to_id}"))')
    parameters = {
        "SORTFROM": "{from_id}",
        "SORTTO": "{to_id}",
        "PRINTED": "1",
        "QTYDEC": "0",
        "PRINTKIT": "0",
        "PRINTBOM": "0",
        "SERIALLOTNUMBERS": "0",
        "SWDELMETHOD": "3",
        "ECENABLED": "0",
    }


class POPurchaseOrderReport(ReportWrapper):

    parameter_set = "POPOR04"
    reports = ("POPOR04.RPT", )
    selection_critieria = """
        (({{POPORH1.PONUMBER}} >= "{from_id}")
        AND ({{POPORH1.PONUMBER}} <= "{to_id}"))
    """
    parameters = {
        "PORFROM": "{from_id}",
        "PORTO": "{to_id}",
        "ACTIVE": "1",
        "BLANKET": "1",
        "FUTURE": "1",
        "STANDING": "1",
        "PRINTED": "1",
        "DPRINTED": "1",
        "ECENABLED": "0",
        "DIRECTEC": "0",
        "DELMETHOD": "1",
        "SORTFROM": "{from_id}",
        "SORTTO": "{ponumber}",
        "SWDELMETHOD": "3",
        "QTYDEC": "0",
    }

class EFTVendorRemittanceReport(ReportWrapper):

    parameter_set = "ELPAY01"
    reports = ("ELPAY04.RPT", )
    parameters = {
        "BATCHTYPE": "PY",
        "FROMBTCH": 0,
        "TOBTCH": 0,
        "FROMENTRY": 0,
        "TOENTRY": 0,
        "UNPOSTED": "0",
        "DELMETHOD": "1",
    }

class APChequeReport(ReportWrapper):

    parameter_set = "BKCHKSTK"
    reports = ("APCHK01.RPT", )
    parameters = {
            "STARTSERIAL": "{from_id}",
            "ENDSERIAL": "{to_id}",
            "APPRUNNUM": "",
            "EXTPARAM1": "2", # Cheque Number
            "EXTPARAM2": " ",
            "EXTPARAM3": " ",
    }

class PayrollChequeReportGenerator(ReportWrapper):

    parameter_set = "BKCHKSTK"
    reports = ("CPCHK4A.RPT", )
    parameters = {
            "STARTSERIAL": "{from_id}",
            "ENDSERIAL": "{to_id}",
            "APPRUNNUM": "",
            "EXTPARAM1": "2",
            "EXTPARAM2": "True",
            "EXTPARAM3": " ",
    }

REPORT_CLASSES = (
        POPurchaseOrderReport,
        OEInvoiceReport,
        EFTVendorRemittanceReport,
        PayrollChequeReportGenerator,
    )

class InvoiceActionsReport(ReportWrapper):

    parameter_set = "OEINACTS"
    reports = ("OEINACTS.RPT", )
    params = {
            "REPORTTYPE": "1",
            "FROMSHIPMENT": "{from_id}",
            "TOSHIPMENT": "{to_id}",
            "THENBY": "1",
            "THENBYFROM": " ",
            "THENBYTO": " ",
            "FROMDATE": "0",
            "TODATE": "20500101",
            "PRINTAMTIN": "1",
            "FUNCDECS": "2",
            "QTYDECS": "4",
            "SWMULTICURR": "0",
            "SWPMACTIVE": "0",
            "SWINCLJOB": "0",
            "LEVEL1NAME": " ",
            "LEVEL2NAME": " ",
            "LEVEL3NAME": " ",
        }
