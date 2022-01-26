from edc_adverse_event.pdf_reports import AeReport as BaseAeReport

from .inte_pdf_report_mixin import InteCrfReportMixin


class AeReport(InteCrfReportMixin, BaseAeReport):

    pass
