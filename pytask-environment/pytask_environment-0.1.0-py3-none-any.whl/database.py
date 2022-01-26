from _pytask.database import db
from pony import orm


class Environment(db.Entity):
    """Collects all information of the environment which should be checked."""

    name = orm.PrimaryKey(str)
    version = orm.Required(str)
    path = orm.Required(str)
