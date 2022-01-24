try:
    from accpac import *
except ImportError:
    pass

from extools.errors import ExToolsError
from extools.view import ExView
from extools.view.errors import ExViewError
from extools.message import logger_for_module
from extools.report import APChequeReport

class ExReportPrinterError(ExToolsError):
    pass

class SetupError(ExReportPrinterError):
    pass

class ReportGenerationError(ExReportPrinterError):
    pass

class ChequeCommitError(ExReportPrinterError):
    pass

class NoChequesMatchedError(ExReportPrinterError):
    pass

class APOpenError(ExReportPrinterError):
    pass

class APChequePrinter():
    """Print cheques for an AP Batch.

    This class provides a one-call interface for all
    the operations required to correctly print cheques
    for an A/P Payment batch through the AP and BK
    processing views.

    .. code::

        from accpac import *

        from extools.ui.bare import bareui
        from extools.report.printers import (
            APChequePrinter, SetupError,
            ChequeCommitError, ReportGenerationError, )

        batchno = 81

        def main(*args, **kwargs):
            printer = APChequePrinter(batchno)
            try:
                check_report_path = printer.print()
            except SetupError as e:
                # handle a failure to setup the temp tables.
                # e contains details on the failing operation
            except ReportGenerationError as e:
                # handle a failure to generate the report.
            except ChequeCommitError as e:
                # handle a failure to write information back to AP/BK.
                # e contains details on the failing operation

    :param batchno: A/P Payment batch number
    :type batchno: int
    """

    PAYMTYPE = "PY"

    # AP Payment Batch Status Codes
    BTCHSTAT_CQ_PR_INPR = 8 # Cheque Printing in Progress
    BTCHSTAT_READY_TO_POST = 7

    # AP Payment Batch PROCESSCMD Codes
    APBTA_PROCESSCMD_LOCK_EXCL = 2
    APBTA_PROCESSCMD_UNLOCK = 0

    # AR Payment Entry PROCESSCMD Codes
    APTCR_PROCESSCMD_VOID_CHEQUE = 4

    # APCHK actions
    APCHK_BATCH_PROCESS = 2
    APCHK_UPDATE_STATUS = 3
    APCHK_SET_BATCHNO = 4

    # ARCHK Status codes
    APCHK_STATUS_SUCCESS = 0
    APCHK_STATUS_ABORT = 1

    # BKREG statuses
    BKREG_STATUS_NOT_PRINTED = -2
    BKREG_STATUS_ADVICE_NOT_PRINTED = -1
    BKREG_STATUS_PRINTED = 9
    BKREG_STATUS_POSTED = 999

    # BKPROC codes
    BKPROC_PRINT_CHEQUE = 1
    BKPROC_PROC_COMPLETE = 1

    # BK Print Functions codes
    BKPRFUN_FUNC_FIND_MATCHING = 1
    BKPRFUN_FUNC_PREP_SUBRUN = 2
    BKPRFUN_FUNC_MARK_ENTIRE_RANGE = 4
    BKPRFUN_FUNC_POST_ALL_IN_SUBRUN = 5

    # BK Language select mode any
    BKPRFUN_LANG_SELECT_ANY = 1

    def __init__(self, batchno):
        self.batchno = int(batchno)
        self.log = logger_for_module("extools.apchequeprint")

        self.apbta = ExView("AP0030")
        self.apbta.compose()
        self.apbta.seek_to(CNTBTCH=self.batchno, PAYMTYPE=self.PAYMTYPE)
        self.bank = self.apbta.idbank

        self.apchk = ExView("AP0058")
        self.bkreg = ExView("BK0009")
        self.bkprfun = ExView("BK0107")
        self.bkproc = ExView("BK0105")
        self.log.info("initalized new APChequePrinter for batch {} bank {}".format(
                self.batchno, self.bank))

    def print(self):
        """Print cheques for a batch and write back details to AP and BK.

        Call me!  This is the public interface into the class.  When called,
        it will generate the cheques for an A/P batch to PDF through the proper
        Sage processing views.

        :returns: Path() to cheque report PDF
        :rtype: pathlib.Path or None on error.
        :raises SetupError: failed to setup BKREG or APADV tables.
        :raises ReportGenerationError: report generation returned None.
        :raises ChequeCommitError: error writing cheque details to AP or BK.
        """
        # Set the batch up.
        try:
            self.start_cheque_printing()
            self.setup_batch()
        except Exception as e:
            emsg = "Failed to setup batch {}: {}".format(self.batchno, e)
            self.log.error(emsg, exc_info=True)
            raise SetupError(emsg)

        self.log.info("batch setup complete.")

        # Populate the tetmporary tables APADV and BKREG.
        # Allocates check numbers
        try:
            self.setup_apchk()
            self.setup_bkprfun()
            self.prepare_bkprfun()
            self.log.info("cheque printing setup complete. tables populated.")
        except ExViewError as e:
            if e.rotoid == "BK0107" and e.action == "process":
                if e.action_return == 1021:
                    raise NoChequesMatchedError("batch {} already printed.")
        except Exception as e:
            emsg = "failed to setup printing: {}".format(e)
            self.log.error(emsg, exc_info=True)
            raise SetupError(emsg)

        # Write the report to disk.
        report_path = self.generate_cheque_report()

        if not report_path:
            emsg = "report generation failed."
            self.log.error(emsg)
            raise ReportGenerationError

        # Write BK entries, write back to AP PY docs, clean tables.
        try:
            self.bkprfun_mark_printed()
            self.bkprfun_post_cheques()
            self.end_cheque_printing()
            self.complete_apchks()
            self.set_batch_rtp()
        except ExViewError as e:
            if e.rotoid == "AP0030" and e.action == "process":
                if e.action_return == 1026:
                    raise APOpenError(
                            "batch {} currently being edited.".format(
                                self.batchno))
        except Exception as e:
            emsg = "failed to commit cheques: {}".format(e)
            self.log.error(emsg, exc_info=True)
            raise ChequeCommitError(emsg)

        return report_path

    def setup_batch(self):
        """Set the batch status to Cheque Printing in Progress."""
        self.apbta.put("BATCHSTAT", self.BTCHSTAT_CQ_PR_INPR)
        self.apbta.update()

    def set_batch_rtp(self):
        """Set the batch status to Ready to Post."""
        self.apbta.seek_to(CNTBTCH=self.batchno, PAYMTYPE=self.PAYMTYPE)
        self.apbta.read()
        self.apbta.put("PROCESSCMD", self.APBTA_PROCESSCMD_LOCK_EXCL)
        self.apbta.process()
        self.apbta.put("BATCHSTAT", self.BTCHSTAT_READY_TO_POST)
        self.apbta.update()
        self.apbta.put("PROCESSCMD", self.APBTA_PROCESSCMD_UNLOCK)
        self.apbta.process()

    def setup_apchk(self):
        """Setup the APADV table using the APCHK view."""
        self.apchk.recordClear()
        # Set the batch number
        self.apchk.put("SWREQTYPE", self.APCHK_SET_BATCHNO)
        self.apchk.put("CNTBATCHNO", self.batchno)
        self.apchk.process()

        # Start the process for the whole batch.
        self.apchk.put("CNTENTRYNO", 1.0)
        self.apchk.put("IDBANK", self.bank)
        self.apchk.put("DECIMALS", 2)
        self.apchk.put("SWREQTYPE", self.APCHK_BATCH_PROCESS)
        self.apchk.process()

        # Go back to setting the batch number (from rvspy)
        self.apchk.put("SWREQTYPE", self.APCHK_SET_BATCHNO)
        self.apchk.process()
        self.log.info("setup AP check advice information")

    def complete_apchks(self):
        """Complete the APCHK processing - write back check numbers."""
        self.apchk.put("SWREQTYPE", self.APCHK_UPDATE_STATUS)
        self.apchk.put("SWRTRNSTTS", self.APCHK_STATUS_SUCCESS)
        self.apchk.process()
        self.log.info('completed AP check run.')

    def abort_apchk(self):
        """Abort AP cheque processing - undoes all print related flags."""
        self.apchk.put("SWREQTYPE", self.APCHK_UPDATE_STATUS)
        self.apchk.put("SWRTRNSTTS", self.APCHK_STATUS_ABORT)
        self.apchk.process()
        self.log.info('aborted AP check run.')

    def start_cheque_printing(self):
        """Tell BKPROC that cheque printing is starting.

        Initial state dosen't matter, reliably returns 0.
        """
        self.log.info("start_cheque_printing")
        self.bkproc.put("PROCESS", self.BKPROC_PRINT_CHEQUE)
        self.bkproc.process()

    def end_cheque_printing(self):
        """Tell BKPROC that cheque printing is over.

        Initial state dosen't matter, reliably returns 0.
        """
        self.log.info("end_cheque_printing")
        self.bkproc.put("PROCESS", self.BKPROC_PRINT_CHEQUE)
        self.bkproc.put("OPERATION", self.BKPROC_PROC_COMPLETE)
        self.bkproc.process()

    def setup_bkprfun(self):
        """Setup the Bank Printing Functions for the batch.

        Mainly setting up the view with the correct values, as well
        as kicking the partially composed views that don't share a
        first key.
        """

        # Compose and setup the Type and Batch
        self.bkprfun.compose()
        self.bkprfun.put("SRCEAPP", "AP")
        self.bkprfun.put("APPRUNNUM", self.batchno)

        # When MODE is put to, much background processing occurs
        # must be set explicitly before first process.
        self.bkprfun.put("MODE", self.BKPRFUN_LANG_SELECT_ANY)

        # composed views don't really share the same first keys
        # by kicking bk0001 we make all the other seek as well.
        self.bkprfun.bk0001.put("BANK", self.bank)
        self.bkprfun.bk0001.read()

        # except BKFORM - in rvspy fetches first.
        self.bkprfun.bk0008.browse()
        self.bkprfun.bk0008.fetch()

        # set the criteria for the bkprfun action (look for unprinted cheques)
        self.bkprfun.put("CRITERIA", "STATUS = {}".format(
            self.BKREG_STATUS_NOT_PRINTED))

        # check whether any cheques meet the criteria (are not printed)
        # for all matching cheques, create BKREG entry.
        self.bkprfun.process()

    def prepare_bkprfun(self):
        """Prepare the sub-run - sets cheque numbers.

        After execution BKREG is full populated and ready for report
        generation.
        """
        self.bkprfun.put("FUNCTION", self.BKPRFUN_FUNC_PREP_SUBRUN)
        self.bkprfun.put(
                "CRITERIA",
                '(STATUS = {}) OR (STATUS = {})'.format(
                    self.BKREG_STATUS_NOT_PRINTED,
                    self.BKREG_STATUS_ADVICE_NOT_PRINTED))
        self.bkprfun.process()

    def generate_cheque_report(self):
        """Generate the cheque report and save to file."""
        # get serials for report generation bounds
        start_serial, end_serial = self.get_serials()
        self.log.info("Got serials: {} - {}".format(
                start_serial, end_serial))

        if not (start_serial and end_serial):
            self.log.error("serials are 0 or unset, bailing.")
            return

        # generate cheques
        report_path =  APChequeReport(
                APPRUNNUM=str(self.batchno)).generate(
                "BKCHKSTK[APCHK01.RPT]",
                from_id=str(start_serial),
                to_id=str(end_serial))

        self.log.info("report generated to {}".format(report_path))
        return report_path

    def bkprfun_mark_printed(self):
        """Mark entire run printed."""
        # This sets all cheques in run to status 9 (printed) in BKREG
        self.bkprfun.put("FUNCTION", self.BKPRFUN_FUNC_MARK_ENTIRE_RANGE)
        self.bkprfun.put("STATUS", self.BKREG_STATUS_PRINTED)
        self.bkprfun.process()
        self.log.info("Processed 4")

    def bkprfun_post_cheques(self):
        """Post all checks for run.

        Creates bank transaction for each cheque issued."""
        self.bkprfun.put("FUNCTION", self.BKPRFUN_FUNC_POST_ALL_IN_SUBRUN)
        self.bkprfun.process()
        self.log.info("Processed 5")

    def get_serials(self):
        """Get the start and end serials for this batch sub run."""
        serials = []
        try:
            # This order of operations (put/browse) is verbatim rvspy.
            self.bkreg.recordClear()
            self.bkreg.put("APPRUNNUM", self.batchno)
            self.bkreg.put("SRCEAPP", "AP")
            self.bkreg.put("BANK", self.bank)
            # Find all cheques in any state for this run.
            self.bkreg.browse(
                    ('(SRCEAPP = "{}") AND (APPRUNNUM = "{}") AND '
                     '(BANK = "{}") AND ((STATUS = -2) OR (STATUS = -1) '
                     'OR (STATUS = 9))').format(
                        "AP", self.batchno, self.bank), 1)
            while self.bkreg.fetch():
                # Sometimes this returns None - tell it which type to cast.
                serials.append(self.bkreg.get("SERIAL", _type=FT_LONG))
            return min(serials), max(serials)
        except Exception as e:
            self.log.error("failed to get serials: {}".format(e))
        return 0, 0

    def void_batch_cheques(self):
        """Void all cheques in the batch."""
        errors = 0
        self.log.info(
                "voiding all cheques in batch PY {}".format(self.batchno))

        for entry in self.apbta.ap0031.all():
            try:
                self.log.debug("voiding entry {}".format(entry.cntentr))
                entry.put("PROCESSCMD", self.APTCR_PROCESSCMD_VOID_CHEQUE)
                entry.process()
            except ExViewError as e:
                errors += 1
                self.log.error("failed to void entry {}: {}".format(
                        entry.cntentr, e))

        self.log.debug("void batch cheques complete.")
        if errors:
            return False
        return True
