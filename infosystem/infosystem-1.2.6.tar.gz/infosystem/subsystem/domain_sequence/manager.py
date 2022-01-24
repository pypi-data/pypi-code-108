from infosystem.common import exception
from infosystem.common.subsystem import operation, manager


class GetNextVal(operation.Operation):
    def pre(self, session, id, name, **kwargs):
        domain = self.manager.api.domains().get(id=id)
        if not domain:
            raise exception.NotFound('ERROR! Domain not found')
        self.domain_id = domain.id

        if not name:
            raise exception.BadRequest('ERROR! Invalid name')
        self.name = name

        return True

    def do(self, session, **kwargs):
        nextval = self.driver.get_nextval(session, self.domain_id, self.name)

        if nextval is None:
            raise exception.InfoSystemException(
                'Was not possible retrive next val')

        return nextval


class Manager(manager.Manager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.get_nextval = GetNextVal(self)
