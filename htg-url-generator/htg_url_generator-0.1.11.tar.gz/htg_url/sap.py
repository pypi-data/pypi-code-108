from abc import ABC, abstractmethod


class AbstractFetchDataFromSap(ABC):
    @staticmethod
    @abstractmethod
    def fetch_document_from_sap(**properties):
        """
        Implement logic for fetching document data from SAP and return base64 string
        :param properties:
        :return: base64 string
        """
