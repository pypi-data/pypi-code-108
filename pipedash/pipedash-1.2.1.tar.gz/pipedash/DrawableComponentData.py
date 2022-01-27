from pipedash.helper import Serializable

class DrawableDataInfo(Serializable):
    fields: []
    registry: {}
    group: {}
    query: {}
    aggregation: {}
    pass

class DrawableComponentData(Serializable):
    pass