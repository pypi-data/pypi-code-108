from sqlalchemy import func, select
from infosystem.common.subsystem import driver


class Driver(driver.Driver):

    def get_nextval(self, session, domain_id, name):
        result = None
        get_nextval_func = func.domain_seq_nextval
        statement = select(get_nextval_func(domain_id, name))
        row_tuple = session.execute(statement).first()
        if len(row_tuple) > 0:
            result = row_tuple[0]
        return result
