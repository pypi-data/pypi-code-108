from edc_adverse_event.pdf_reports import DeathReport as BaseDeathReport

from .inte_pdf_report_mixin import InteCrfReportMixin


class DeathReport(InteCrfReportMixin, BaseDeathReport):

    pass
