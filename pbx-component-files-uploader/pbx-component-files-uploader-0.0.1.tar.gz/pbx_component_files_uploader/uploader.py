from .exceptions.errors import NotAllowed
from .ext.selectel.selectel import Selectel


class Uploader:

    SERVICE_SELECTEL = 'selectel'

    def __init__(self, service: str, auth: dict = {}, options: dict = {}) -> None:
        if self.is_allowed_services(service=service):
            self.service = service
        else:
            raise NotAllowed('Service ' + service + ' is not allowed')
        self.auth = auth
        self.options = options

    def is_allowed_services(self, service: str) -> bool:
        return service in [self.SERVICE_SELECTEL]

    def upload(self, srcFilePath, dstName) -> str:
        if self.service == self.SERVICE_SELECTEL:
            selectel = Selectel(self.auth, self.options)
            return selectel.upload(srcFilePath=srcFilePath, dstFileName=dstName)
