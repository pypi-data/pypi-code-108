# ext/declarative/extensions.py
# Copyright (C) 2005-2022 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
"""Public API functions and helpers for declarative."""


from ... import inspection
from ... import util
from ...orm import exc as orm_exc
from ...orm import registry
from ...orm import relationships
from ...orm.base import _mapper_or_none
from ...orm.clsregistry import _resolver
from ...orm.decl_base import _DeferredMapperConfig
from ...orm.util import polymorphic_union
from ...schema import Table
from ...util import OrderedDict


@util.deprecated(
    "2.0",
    "the instrument_declarative function is deprecated "
    "and will be removed in SQLAlhcemy 2.0.  Please use "
    ":meth:`_orm.registry.map_declaratively",
)
def instrument_declarative(cls, cls_registry, metadata):
    """Given a class, configure the class declaratively,
    using the given registry, which can be any dictionary, and
    MetaData object.

    """
    registry(metadata=metadata, class_registry=cls_registry).map_declaratively(
        cls
    )


class ConcreteBase(object):
    """A helper class for 'concrete' declarative mappings.

    :class:`.ConcreteBase` will use the :func:`.polymorphic_union`
    function automatically, against all tables mapped as a subclass
    to this class.   The function is called via the
    ``__declare_last__()`` function, which is essentially
    a hook for the :meth:`.after_configured` event.

    :class:`.ConcreteBase` produces a mapped
    table for the class itself.  Compare to :class:`.AbstractConcreteBase`,
    which does not.

    Example::

        from sqlalchemy.ext.declarative import ConcreteBase

        class Employee(ConcreteBase, Base):
            __tablename__ = 'employee'
            employee_id = Column(Integer, primary_key=True)
            name = Column(String(50))
            __mapper_args__ = {
                            'polymorphic_identity':'employee',
                            'concrete':True}

        class Manager(Employee):
            __tablename__ = 'manager'
            employee_id = Column(Integer, primary_key=True)
            name = Column(String(50))
            manager_data = Column(String(40))
            __mapper_args__ = {
                            'polymorphic_identity':'manager',
                            'concrete':True}


    The name of the discriminator column used by :func:`.polymorphic_union`
    defaults to the name ``type``.  To suit the use case of a mapping where an
    actual column in a mapped table is already named ``type``, the
    discriminator name can be configured by setting the
    ``_concrete_discriminator_name`` attribute::

        class Employee(ConcreteBase, Base):
            _concrete_discriminator_name = '_concrete_discriminator'

    .. versionadded:: 1.3.19 Added the ``_concrete_discriminator_name``
       attribute to :class:`_declarative.ConcreteBase` so that the
       virtual discriminator column name can be customized.

    .. versionchanged:: 1.4.2 The ``_concrete_discriminator_name`` attribute
       need only be placed on the basemost class to take correct effect for
       all subclasses.   An explicit error message is now raised if the
       mapped column names conflict with the discriminator name, whereas
       in the 1.3.x series there would be some warnings and then a non-useful
       query would be generated.

    .. seealso::

        :class:`.AbstractConcreteBase`

        :ref:`concrete_inheritance`


    """

    @classmethod
    def _create_polymorphic_union(cls, mappers, discriminator_name):
        return polymorphic_union(
            OrderedDict(
                (mp.polymorphic_identity, mp.local_table) for mp in mappers
            ),
            discriminator_name,
            "pjoin",
        )

    @classmethod
    def __declare_first__(cls):
        m = cls.__mapper__
        if m.with_polymorphic:
            return

        discriminator_name = (
            getattr(cls, "_concrete_discriminator_name", None) or "type"
        )

        mappers = list(m.self_and_descendants)
        pjoin = cls._create_polymorphic_union(mappers, discriminator_name)
        m._set_with_polymorphic(("*", pjoin))
        m._set_polymorphic_on(pjoin.c[discriminator_name])


class AbstractConcreteBase(ConcreteBase):
    """A helper class for 'concrete' declarative mappings.

    :class:`.AbstractConcreteBase` will use the :func:`.polymorphic_union`
    function automatically, against all tables mapped as a subclass
    to this class.   The function is called via the
    ``__declare_last__()`` function, which is essentially
    a hook for the :meth:`.after_configured` event.

    :class:`.AbstractConcreteBase` does produce a mapped class
    for the base class, however it is not persisted to any table; it
    is instead mapped directly to the "polymorphic" selectable directly
    and is only used for selecting.  Compare to :class:`.ConcreteBase`,
    which does create a persisted table for the base class.

    .. note::

        The :class:`.AbstractConcreteBase` class does not intend to set up  the
        mapping for the base class until all the subclasses have been defined,
        as it needs to create a mapping against a selectable that will include
        all subclass tables.  In order to achieve this, it waits for the
        **mapper configuration event** to occur, at which point it scans
        through all the configured subclasses and sets up a mapping that will
        query against all subclasses at once.

        While this event is normally invoked automatically, in the case of
        :class:`.AbstractConcreteBase`, it may be necessary to invoke it
        explicitly after **all** subclass mappings are defined, if the first
        operation is to be a query against this base class.  To do so, invoke
        :func:`.configure_mappers` once all the desired classes have been
        configured::

            from sqlalchemy.orm import configure_mappers

            configure_mappers()

        .. seealso::

            :func:`_orm.configure_mappers`


    Example::

        from sqlalchemy.ext.declarative import AbstractConcreteBase

        class Employee(AbstractConcreteBase, Base):
            pass

        class Manager(Employee):
            __tablename__ = 'manager'
            employee_id = Column(Integer, primary_key=True)
            name = Column(String(50))
            manager_data = Column(String(40))

            __mapper_args__ = {
                'polymorphic_identity':'manager',
                'concrete':True}

        configure_mappers()

    The abstract base class is handled by declarative in a special way;
    at class configuration time, it behaves like a declarative mixin
    or an ``__abstract__`` base class.   Once classes are configured
    and mappings are produced, it then gets mapped itself, but
    after all of its descendants.  This is a very unique system of mapping
    not found in any other SQLAlchemy system.

    Using this approach, we can specify columns and properties
    that will take place on mapped subclasses, in the way that
    we normally do as in :ref:`declarative_mixins`::

        class Company(Base):
            __tablename__ = 'company'
            id = Column(Integer, primary_key=True)

        class Employee(AbstractConcreteBase, Base):
            employee_id = Column(Integer, primary_key=True)

            @declared_attr
            def company_id(cls):
                return Column(ForeignKey('company.id'))

            @declared_attr
            def company(cls):
                return relationship("Company")

        class Manager(Employee):
            __tablename__ = 'manager'

            name = Column(String(50))
            manager_data = Column(String(40))

            __mapper_args__ = {
                'polymorphic_identity':'manager',
                'concrete':True}

        configure_mappers()

    When we make use of our mappings however, both ``Manager`` and
    ``Employee`` will have an independently usable ``.company`` attribute::

        session.query(Employee).filter(Employee.company.has(id=5))

    .. versionchanged:: 1.0.0 - The mechanics of :class:`.AbstractConcreteBase`
       have been reworked to support relationships established directly
       on the abstract base, without any special configurational steps.

    .. seealso::

        :class:`.ConcreteBase`

        :ref:`concrete_inheritance`

    """

    __no_table__ = True

    @classmethod
    def __declare_first__(cls):
        cls._sa_decl_prepare_nocascade()

    @classmethod
    def _sa_decl_prepare_nocascade(cls):
        if getattr(cls, "__mapper__", None):
            return

        to_map = _DeferredMapperConfig.config_for_cls(cls)

        # can't rely on 'self_and_descendants' here
        # since technically an immediate subclass
        # might not be mapped, but a subclass
        # may be.
        mappers = []
        stack = list(cls.__subclasses__())
        while stack:
            klass = stack.pop()
            stack.extend(klass.__subclasses__())
            mn = _mapper_or_none(klass)
            if mn is not None:
                mappers.append(mn)

        discriminator_name = (
            getattr(cls, "_concrete_discriminator_name", None) or "type"
        )
        pjoin = cls._create_polymorphic_union(mappers, discriminator_name)

        # For columns that were declared on the class, these
        # are normally ignored with the "__no_table__" mapping,
        # unless they have a different attribute key vs. col name
        # and are in the properties argument.
        # In that case, ensure we update the properties entry
        # to the correct column from the pjoin target table.
        declared_cols = set(to_map.declared_columns)
        for k, v in list(to_map.properties.items()):
            if v in declared_cols:
                to_map.properties[k] = pjoin.c[v.key]

        to_map.local_table = pjoin

        m_args = to_map.mapper_args_fn or dict

        def mapper_args():
            args = m_args()
            args["polymorphic_on"] = pjoin.c[discriminator_name]
            return args

        to_map.mapper_args_fn = mapper_args

        m = to_map.map()

        for scls in cls.__subclasses__():
            sm = _mapper_or_none(scls)
            if sm and sm.concrete and cls in scls.__bases__:
                sm._set_concrete_base(m)

    @classmethod
    def _sa_raise_deferred_config(cls):
        raise orm_exc.UnmappedClassError(
            cls,
            msg="Class %s is a subclass of AbstractConcreteBase and "
            "has a mapping pending until all subclasses are defined. "
            "Call the sqlalchemy.orm.configure_mappers() function after "
            "all subclasses have been defined to "
            "complete the mapping of this class."
            % orm_exc._safe_cls_name(cls),
        )


class DeferredReflection(object):
    """A helper class for construction of mappings based on
    a deferred reflection step.

    Normally, declarative can be used with reflection by
    setting a :class:`_schema.Table` object using autoload_with=engine
    as the ``__table__`` attribute on a declarative class.
    The caveat is that the :class:`_schema.Table` must be fully
    reflected, or at the very least have a primary key column,
    at the point at which a normal declarative mapping is
    constructed, meaning the :class:`_engine.Engine` must be available
    at class declaration time.

    The :class:`.DeferredReflection` mixin moves the construction
    of mappers to be at a later point, after a specific
    method is called which first reflects all :class:`_schema.Table`
    objects created so far.   Classes can define it as such::

        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.ext.declarative import DeferredReflection
        Base = declarative_base()

        class MyClass(DeferredReflection, Base):
            __tablename__ = 'mytable'

    Above, ``MyClass`` is not yet mapped.   After a series of
    classes have been defined in the above fashion, all tables
    can be reflected and mappings created using
    :meth:`.prepare`::

        engine = create_engine("someengine://...")
        DeferredReflection.prepare(engine)

    The :class:`.DeferredReflection` mixin can be applied to individual
    classes, used as the base for the declarative base itself,
    or used in a custom abstract class.   Using an abstract base
    allows that only a subset of classes to be prepared for a
    particular prepare step, which is necessary for applications
    that use more than one engine.  For example, if an application
    has two engines, you might use two bases, and prepare each
    separately, e.g.::

        class ReflectedOne(DeferredReflection, Base):
            __abstract__ = True

        class ReflectedTwo(DeferredReflection, Base):
            __abstract__ = True

        class MyClass(ReflectedOne):
            __tablename__ = 'mytable'

        class MyOtherClass(ReflectedOne):
            __tablename__ = 'myothertable'

        class YetAnotherClass(ReflectedTwo):
            __tablename__ = 'yetanothertable'

        # ... etc.

    Above, the class hierarchies for ``ReflectedOne`` and
    ``ReflectedTwo`` can be configured separately::

        ReflectedOne.prepare(engine_one)
        ReflectedTwo.prepare(engine_two)

    """

    @classmethod
    def prepare(cls, engine):
        """Reflect all :class:`_schema.Table` objects for all current
        :class:`.DeferredReflection` subclasses"""

        to_map = _DeferredMapperConfig.classes_for_base(cls)

        with inspection.inspect(engine)._inspection_context() as insp:
            for thingy in to_map:
                cls._sa_decl_prepare(thingy.local_table, insp)
                thingy.map()
                mapper = thingy.cls.__mapper__
                metadata = mapper.class_.metadata
                for rel in mapper._props.values():
                    if (
                        isinstance(rel, relationships.RelationshipProperty)
                        and rel.secondary is not None
                    ):
                        if isinstance(rel.secondary, Table):
                            cls._reflect_table(rel.secondary, insp)
                        elif isinstance(rel.secondary, str):

                            _, resolve_arg = _resolver(rel.parent.class_, rel)

                            rel.secondary = resolve_arg(rel.secondary)
                            rel.secondary._resolvers += (
                                cls._sa_deferred_table_resolver(
                                    insp, metadata
                                ),
                            )

                            # controversy!  do we resolve it here? or leave
                            # it deferred?   I think doing it here is necessary
                            # so the connection does not leak.
                            rel.secondary = rel.secondary()

    @classmethod
    def _sa_deferred_table_resolver(cls, inspector, metadata):
        def _resolve(key):
            t1 = Table(key, metadata)
            cls._reflect_table(t1, inspector)
            return t1

        return _resolve

    @classmethod
    def _sa_decl_prepare(cls, local_table, inspector):
        # autoload Table, which is already
        # present in the metadata.  This
        # will fill in db-loaded columns
        # into the existing Table object.
        if local_table is not None:
            cls._reflect_table(local_table, inspector)

    @classmethod
    def _sa_raise_deferred_config(cls):
        raise orm_exc.UnmappedClassError(
            cls,
            msg="Class %s is a subclass of DeferredReflection.  "
            "Mappings are not produced until the .prepare() "
            "method is called on the class hierarchy."
            % orm_exc._safe_cls_name(cls),
        )

    @classmethod
    def _reflect_table(cls, table, inspector):
        Table(
            table.name,
            table.metadata,
            extend_existing=True,
            autoload_replace=False,
            autoload_with=inspector,
            schema=table.schema,
        )
