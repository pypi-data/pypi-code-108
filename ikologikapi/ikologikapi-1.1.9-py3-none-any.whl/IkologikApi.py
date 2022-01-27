from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.services.AbstractIkologikCustomerService import AbstractIkologikCustomerService
from ikologikapi.services.AlertService import AlertService
from ikologikapi.services.AlertTypeService import AlertTypeService
from ikologikapi.services.BatchService import BatchService
from ikologikapi.services.BatchTypeService import BatchTypeService
from ikologikapi.services.DashboardService import DashboardService
from ikologikapi.services.DashboardWidgetService import DashboardWidgetService
from ikologikapi.services.DashboardWidgetTypeService import DashboardWidgetTypeService
from ikologikapi.services.DataImportService import DataImportService
from ikologikapi.services.DataImportTypeService import DataImportTypeService
from ikologikapi.services.InstallationService import InstallationService
from ikologikapi.services.ReportService import ReportService
from ikologikapi.services.ReportTypeService import ReportTypeService
from ikologikapi.services.TagAlertTypeService import TagAlertTypeService
from ikologikapi.services.TagService import TagService


class IkologikAPI:

    def __init__(self, url: str, username: str, password: str):
        self.apiCredentials = IkologikApiCredentials(url, username, password)
        self.alert = AlertService(self.apiCredentials)
        self.alertType = AlertTypeService(self.apiCredentials)
        self.batch = BatchService(self.apiCredentials)
        self.batchType = BatchTypeService(self.apiCredentials)
        self.dashboard = DashboardService(self.apiCredentials)
        self.dashboardWidget = DashboardWidgetService(self.apiCredentials)
        self.dashboardWidgetType = DashboardWidgetTypeService(self.apiCredentials)
        self.dataImport = DataImportService(self.apiCredentials)
        self.dataImportType = DataImportTypeService(self.apiCredentials)
        self.installation = InstallationService(self.apiCredentials)
        self.report = ReportService(self.apiCredentials)
        self.reportType = ReportTypeService(self.apiCredentials)
        self.tag = TagService(self.apiCredentials)
        self.tagAlertType = TagAlertTypeService(self.apiCredentials)
