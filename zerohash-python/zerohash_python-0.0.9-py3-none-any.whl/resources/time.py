from zerohash.resources.abstract.api_resource import APIResource


class Time(APIResource):
    OBJECT_NAME = "time"

    @classmethod
    def retrieve(cls, **kwargs):
        instance = cls(**kwargs)
        instance.refresh()
        return instance
