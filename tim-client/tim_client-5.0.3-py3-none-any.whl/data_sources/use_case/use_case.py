from tim.types import Id
from tim.core.api import execute_request
from tim.core.credentials import Credentials
from .types import UseCaseConfiguration


def create_use_case(credentials: Credentials, configuration: UseCaseConfiguration) -> Id:
  return Id(
      id=execute_request(credentials=credentials, method='post', path='/use-cases', body=configuration)['id']
  )
