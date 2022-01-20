import yaml
import os

class AppsReader:

    secModulesMapping: dict = {}
    appModulesMapping: dict = {}
    intModulesMapping: dict = {}

    def __init__(self) -> None:
        pass

    @staticmethod
    def readApplications():
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "applications-details.yaml"), 'r') as file:
            applicationsDetails = yaml.safe_load(file)
            return applicationsDetails

    @staticmethod
    def parseApplicationsDetails(applicationsDetails: dict = None):
        if ("SEC" in applicationsDetails.keys()):
            for app in applicationsDetails["SEC"]:
                AppsReader.secModulesMapping.update({[*app.keys()][0]: [*app.values()][0]["LABEL"]})
        if ("ECC" in applicationsDetails.keys()):
            for app in applicationsDetails["ECC"]:
                AppsReader.appModulesMapping.update({[*app.keys()][0]: [*app.values()][0]["LABEL"]})
        if ("INT" in applicationsDetails.keys()):
            for app in applicationsDetails["INT"]:
                AppsReader.intModulesMapping.update({[*app.keys()][0]: [*app.values()][0]["LABEL"]})