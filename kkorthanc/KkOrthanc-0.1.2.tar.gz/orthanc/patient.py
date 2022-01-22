from orthanc.orthanc import Orthanc

class Patient:
    def __init__(self, ID: str, orthanc: Orthanc, MainDicomTags: dict):
        self.orthanc = orthanc
        self.ID = ID
        self.MainDicomTags = MainDicomTags