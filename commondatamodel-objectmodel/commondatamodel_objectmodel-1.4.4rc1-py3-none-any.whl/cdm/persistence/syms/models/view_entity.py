# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator 0.17.0.0
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from .md_entity import MDEntity


class ViewEntity(MDEntity):
    """View entity.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param name: Entity Name.
    :type name: str
    :param type: Possible values include: 'DATABASE', 'TABLE', 'SCHEMA',
     'VIEW', 'FUNCTION', 'PARTITIONINFO', 'RELATIONSHIP'
    :type type: str or :class:`SASEntityType
     <Microsoft.ADF.SyMSAPIClient.models.SASEntityType>`
    :ivar id: Entity Resource Id.
    :vartype id: str
    :param properties:
    :type properties: object
    """ 

    _validation = {
        'name': {'required': True},
        'type': {'required': True},
        'id': {'readonly': True},
    }

    def __init__(self, name, type, properties=None):
        super(ViewEntity, self).__init__(name=name, type=type, properties=properties)
