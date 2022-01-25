from sqlalchemy import orm
from abc import abstractmethod


class SqlQuery(object):
    """
    TODO
    """
    def __init__(self, session: orm.Session, q: orm.Query = None):
        """
        :param session:
        :param q:
        """
        self.session = session
        self.q = q or self._get_base_query()

    @abstractmethod
    def _get_base_query(self) -> orm.Query:
        """
        TODO Describe with example
        """
        raise NotImplementedError

    def __iter__(self):
        return iter(self.q)

    def __getattr__(self, name):
        return getattr(self.q, name)

    def filter(self, *filters):
        """
        TODO Describe with example

        Example usage::

            filter(Model.age==35, Model.country=='Denmark')

        :param filters:
        :return:
        """
        return self.__class__(self.session, self.q.filter(*filters))

    def filter_by(self, **filters):
        """
        TODO Describe with example

        Example usage::

            filter_by(age=35, country='Denmark')

        :param filters:
        :return:
        """
        return self.__class__(self.session, self.q.filter_by(**filters))

    # def unique_join(self, *props, **kwargs):
    #     if props[0] in [c.entity for c in self.q._join_entities]:
    #         return self
    #
    #     return self.__class__(self.session, self.q.join(
    #         *props, **kwargs
    #     ))
    #
    # def lazy_load(self, field):
    #     return self.__class__(self.session, self.q.options(
    #         orm.lazyload(field)
    #     ))
    #
    # def eager_load(self, path, *fields):
    #     if isinstance(path, (list, tuple)):
    #         join = orm.joinedload(*path)
    #     else:
    #         join = orm.joinedload(path)
    #
    #     if fields:
    #         join = join.load_only(*fields)
    #
    #     return self.__class__(self.session, self.q.options(join))
    #
    # def eage_load_path(self, *path):
    #     join = rjoinedload(*path)
    #     if fields:
    #         join = join.load_only(*fields)
    #     return self.__class__(self.session, self.q.options(
    #         join
    #     ))

    def only(self, *fields):
        """
        Narrows down the columns to select.

        TODO Example usage

        :param fields:
        :return:
        """
        return self.__class__(self.session, self.q.options(
            orm.load_only(*fields)
        ))

    def get(self, field):
        """
        Returns value for the field from the first result.

        TODO Example usage

        :param field:
        :return:
        """
        return self.only(field).scalar()

    def exists(self):
        """
        :return: True if result count is >= 1
        """
        return self.count() > 0
