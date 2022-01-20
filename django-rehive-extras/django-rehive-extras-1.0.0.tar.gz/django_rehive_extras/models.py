from copy import deepcopy

from django.db import models, transaction
from django.db.models import Case, When, Value, ProtectedError
from django.db.models.expressions import Func, Expression, F
from django.contrib.postgres.fields import ArrayField

from .exceptions import (
    CannotModifyObjectWithArchivedParentError,
    CannotModifyArchivedObjectError,
    CannotDeleteUnarchivedObjectError,
    CannotDeleteObjectError
)


class BaseFunc(Func):
    """
    Base function class for basic database func() expressions.
    """

    def __init__(self, field, *values, **extra):
        if not isinstance(field, Expression):
            field = F(field)
            if values and not isinstance(values[0], Expression):
                values = [Value(v) for v in values]
        super().__init__(field, *values, **extra)


class ArrayAppend(BaseFunc):
    """
    Expression for the postgres array append function.
    """

    function = 'array_append'


class ArrayRemove(BaseFunc):
    """
    Expressionf for the postgres array remove function.
    """

    function = 'array_remove'


class ArchiveNode():
    """
    A single direction cascade node for django models. Expanding this
    node will create a tree that can be used to cascade changes through
    all related tables in one direction.
    """

    def __init__(self, model, parent=None, relation_field=None):
        """
        Initiate the node. Only a model is required. a parent and relation will
        be added when expand is invoked.
        """

        self.model = model
        self.parent = parent
        self.relation_field = relation_field
        self.children = []

    def __str__(self):
        """
        String value for a node instance.
        """

        return str(self.model)

    def _get_relation_fields(self, fields=None):
        """
        Build a list of relationship fields by ascending up the node tree.

        The resulting list can then be used to construct a Django
        "query param" filter field.
        """

        if not fields:
            fields = []

        if self.parent:
            fields.append(self.relation_field)
            return self.parent._get_relation_fields(fields)

        return fields

    def expand(self, parsed_rel_fields=None):
        """
        Expand relationships from the node.
        Uses introspection to build a single-direction tree of related models.
        """

        # Instantiate a parsed_rel_fields list.
        if parsed_rel_fields is None:
            parsed_rel_fields = []

        def _get_f_key(model, f):
            rel_model_name = f.related_model.__name__.lower() \
                if f.related_model else None
            return "{}:{}".format(model.__name__.lower(), rel_model_name)

        # Get the current node's (model's) dependent relationship fields.
        # 1. The field must be a relationship field.
        # 2. The related field's model must be a BaseModel type.
        # 3. The relationship must not have been parsed already.
        fields = [f for f in self.model._meta.get_fields()
                 if (f.related_model != self.model
                     and (_get_f_key(self.model, f) not in parsed_rel_fields)
                     and (f.one_to_many or f.one_to_one)
                     and (issubclass(f.related_model, ArchiveModel)))]

        for f in fields:
            if hasattr(f, 'field'):
                name = f.field.name
            else:
                name = f.remote_field.name

            # Create a new node with the correct parent and relationship field.
            node = self.__class__(
                f.related_model, parent=self, relation_field=name
            )

            # Prevent circular dependencies by adding the field to the list.
            parsed_rel_fields.append(_get_f_key(self.model, f))
            node.expand(parsed_rel_fields=parsed_rel_fields)

            # Append the completed child node (and tree) to the parent node.
            self.children.append(node)

    def update_queryset(self, queryset, archived, point):
        # If archiving the related objects. Then ensure the new `point`
        # is added to the related objects.
        if archived is True:
            queryset.update(
                archived=True,
                archive_points=Case(
                    When(
                        archive_points__contains=[point],
                        then=F('archive_points')
                    ),
                    default=ArrayAppend('archive_points', point),
                    output_field=ArrayField(
                        models.CharField(max_length=50),
                    )
                )
            )

        # If unarchiving the related objects. Then ensure the current
        # `point` is removed from the related objects. Only set the
        # archived field to false if there are no points.
        elif archived is False:
            queryset.update(
                archived=Case(
                    When(
                        archive_points__contains=[point],
                        archive_points__len=1,
                        then=False
                    ),
                    default=F('archived'),
                    output_field=ArrayField(
                        models.CharField(max_length=50),
                    )
                ),
                archive_points=ArrayRemove('archive_points', point)
            )

    def update(self, instance, archived=None):
        """
        Update the node by cascading down the tree. Requires an instance id.
        """

        if archived is None:
            raise Exception("The archived kwarg should be a boolean.")

        # Get the model name of the instance that triggered the update action.
        # This is used to track what object caused another object to be updated.
        point = instance.__class__.__name__.lower()

        for node in self.children:
            # Build filters for specific model and run an update.
            filters = {}
            fields = node._get_relation_fields()
            filters["".join(("__".join(fields), '__id'))] = instance.id

            # Update the queryset.
            self.update_queryset(
                node.model.objects.filter(**filters), archived, point
            )

            # Cascade down to next node.
            node.update(instance, archived)


class DateModel(models.Model):
    """
    Abstract model that stores a created and updated date for each object.
    """

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.created)


class StateModel(models.Model):
    """
    Abstract model that stores a temporary model state on instantiation.
    """

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """
        Set the original state of the model on instantiation.
        """

        super().__init__(*args, **kwargs)
        self.original = deepcopy(self)


class ArchiveModel(StateModel):
    """
    Abstract model that handles archiving of related data.
    """

    archived = models.BooleanField(db_index=True, default=False)
    archive_points = ArrayField(
        models.CharField(max_length=50),
        size=10,
        null=True,
        blank=True
    )

    _must_be_archived_to_delete = True
    _must_be_unarchived_to_modify = True

    class Meta:
        abstract = True

    @transaction.atomic
    def save(self, force=False, *args, **kwargs):
        """
        Save the instance and handle archiving if necessary. Run save in a
        transaction so that failed inserts are rolled back.
        """

        # Only fire off additional archive logic if this is an existing
        # instance.
        if not self._state.adding:
            # Check if the archived value is changed from the original value.
            if self.original and self.archived != self.original.archived:
                node = ArchiveNode(self.__class__)

                # Archive the object and all related/dependent objects.
                if self.archived and not self.original.archived:
                    node.expand()
                    node.update(self, archived=True)

                # Unarchive the object and all related/dependent objects.
                elif not self.archived and self.original.archived:
                    # Ensure that a parent is not already archived.
                    if self.archive_points:
                        raise CannotModifyObjectWithArchivedParentError()

                    node.expand()
                    node.update(self, archived=False)

            # Check if the object may be modified due to the archived value.
            elif (not force
                    and (self._must_be_unarchived_to_modify and self.archived)):
                raise CannotModifyArchivedObjectError()

        return super().save(*args, **kwargs)

    def delete(self, force=False):
        """
        Delete the instance and handle model specific delete preferences.
        """

        # Ensure the object is already archived before deleting.
        if (not force
                and (self._must_be_archived_to_delete and not self.archived)):
            raise CannotDeleteUnarchivedObjectError()

        try:
            super().delete()
        except ProtectedError:
            raise CannotDeleteObjectError()


class IntegratedModel(DateModel, ArchiveModel):
    """
    Generic abstract model that includes date, original state, and
    archive related functionality.
    """

    class Meta:
        abstract = True
