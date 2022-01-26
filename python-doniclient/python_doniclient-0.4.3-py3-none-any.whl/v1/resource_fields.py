"""Define fields for Doni resources."""


class Resource(object):
    """Resource class.

    This class is used to manage the various fields that a resource (e.g.
    Chassis, Node, Port) contains.  An individual field consists of a
    'field_id' (key) and a 'label' (value).  The caller only provides the
    'field_ids' when instantiating the object.
    Ordering of the 'field_ids' will be preserved as specified by the caller.
    It also provides the ability to exclude some of these fields when they are
    being used for sorting.
    """

    FIELDS = {
        "name": "Name",
        "uuid": "UUID",
        "project_id": "Project ID",
        "hardware_type": "Hardware Type",
        "properties": "Properties",
        "created_at": "Created At",
        "updated_at": "Updated At",
        "workers": "Workers",
    }

    def __init__(self, field_ids, sort_excluded=None, override_labels=None):
        """Create a Resource object.

        :param field_ids:  A list of strings that the Resource object will
                           contain.  Each string must match an existing key in
                           FIELDS.
        :param sort_excluded: Optional. A list of strings that will not be used
                              for sorting.  Must be a subset of 'field_ids'.
        :param override_labels: Optional. A dictionary, where key is a field ID
                                and value is the label to be used. If
                                unspecified, uses the labels associated with
                                the fields from global FIELDS.
        :raises: ValueError if sort_excluded or override_labels contains values
                 not in field_ids
        """
        self._fields = tuple(field_ids)
        self._labels = tuple([self.FIELDS[x] for x in field_ids])

    @property
    def fields(self):
        return self._fields

    @property
    def labels(self):
        return self._labels


HARDWARE_RESOURCE = Resource(
    [
        "uuid",
        "name",
        "properties",
    ]
)


HARDWARE_DETAILED_RESOURCE = Resource(
    [
        "uuid",
        "name",
        "project_id",
        "hardware_type",
        "created_at",
        "updated_at",
        "properties",
    ]
)
